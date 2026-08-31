# agents/triage_agent.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env securely
load_dotenv()

class TriageAgent:
    def __init__(self):
        # Provider-independent initialization
        api_key = os.environ.get("LLM_API_KEY")
        base_url = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
        self.model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
        
        if not api_key or api_key == "your_actual_api_key_here":
            raise ValueError("LLM_API_KEY is not set correctly in the .env file.")

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def assess_risk(self, detection_report: dict, threat_intel: dict, station_context: dict) -> dict:
        """
        Uses an LLM to synthesize detection, threat intel, and grid context into a final Risk Score.
        """
        if not detection_report.get("is_anomaly"):
            return {
                "risk_level": "None",
                "reasoning": "No active threat detected. Routine operation."
            }

        prompt = f"""
        You are an expert Cybersecurity Analyst for an Electric Vehicle (EV) Charge Point Operator (CPO).
        Evaluate the cyber-physical risk of the following event.
        
        [1] ML DETECTION: {json.dumps(detection_report)}
        [2] THREAT INTELLIGENCE: {json.dumps(threat_intel)}
        [3] STATION CONTEXT: {json.dumps(station_context)}
        
        Task:
        Determine the final risk level considering both the attack's base severity and the physical station/grid context.
        
        Output MUST be in strictly valid JSON format with exactly two keys:
        - "risk_level": Must be exactly one of ["Low", "Medium", "High", "Critical"]
        - "reasoning": A brief, professional 2-sentence explanation of why this level was chosen based on the inputs.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a specialized JSON-output EV cybersecurity AI."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2 # Low temperature for highly deterministic reasoning
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error during LLM Triage: {e}")
            return {
                "risk_level": "Unknown",
                "reasoning": f"LLM assessment failed: {str(e)}"
            }