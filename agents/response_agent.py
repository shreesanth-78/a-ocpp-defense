# agents/response_agent.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools.mitigation_tools import MitigationTools

load_dotenv()

class ResponseAgent:
    def __init__(self):
        api_key = os.environ.get("LLM_API_KEY")
        base_url = os.environ.get("LLM_BASE_URL")
        self.model = os.environ.get("LLM_MODEL")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.tools = MitigationTools()

    def determine_action(self, triage_assessment: dict, charger_id: str) -> dict:
        """
        Uses an LLM to select an action, validates it, and executes the simulated mitigation.
        """
        risk_level = triage_assessment.get("risk_level", "Unknown")
        
        if risk_level == "None":
             return {"selected_action": "none", "policy_validation": "Passed", "execution": "Skipped - No Risk"}

        prompt = f"""
        You are the Response Agent for an EV Charging Security System.
        Current Risk Assessment: {json.dumps(triage_assessment)}
        Target Charger ID: {charger_id}

        Select the MOST appropriate mitigation action from this exact list:
        {self.tools.allowed_actions}

        Rules:
        - "Critical" risk -> drop_websocket_session or soft_reset_charger
        - "High" risk -> throttle_charger_power or alert_operator
        - "Medium"/"Low" risk -> alert_operator

        Output MUST be in strictly valid JSON format with:
        - "selected_action": (must be exactly one string from the list)
        - "reasoning": (1 brief sentence explaining the choice)
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a JSON-output mitigation decision AI."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            decision = json.loads(response.choices[0].message.content)
            
            # Deterministic Policy Validation
            proposed_action = decision.get("selected_action")
            if proposed_action not in self.tools.allowed_actions:
                decision["selected_action"] = "alert_operator" # Safe fallback
                decision["policy_validation"] = f"Failed - Invalid action '{proposed_action}'. Fallback applied."
            else:
                decision["policy_validation"] = "Passed - Action authorized."
                
            # Execute tool
            decision["execution_result"] = self.tools.execute(decision["selected_action"], charger_id)
            
            return decision
            
        except Exception as e:
            return {
                "selected_action": "alert_operator", 
                "policy_validation": "Error", 
                "reasoning": str(e),
                "execution_result": self.tools.execute("alert_operator", charger_id)
            }