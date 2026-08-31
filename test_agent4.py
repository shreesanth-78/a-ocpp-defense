# test_agent4.py
from agents.response_agent import ResponseAgent
import json

def test_response():
    print("Initializing Response Agent...")
    agent4 = ResponseAgent()
    
    # Using the exact output from our Agent 3 test
    mock_triage = {
      "risk_level": "High",
      "reasoning": "Although the base severity is Medium, the scan targets a critical, actively charging DC fast charger operating at peak grid load."
    }
    
    charger_id = "CS-BLDG-HQ-01"
    
    print("\n[Step 4] LLM Response & Mitigation Selection...")
    decision = agent4.determine_action(mock_triage, charger_id)
    print("\n--- Final Mitigation Report ---")
    print(json.dumps(decision, indent=2))

if __name__ == "__main__":
    test_response()