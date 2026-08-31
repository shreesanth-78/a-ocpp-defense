# test_agent3.py
from agents.detection_agent import DetectionAgent
from agents.threat_intel_agent import ThreatIntelAgent
from agents.triage_agent import TriageAgent
import pandas as pd
from pathlib import Path
import json

def test_pipeline_to_triage():
    print("Initializing Agents (including LLM)...")
    agent1 = DetectionAgent()
    agent2 = ThreatIntelAgent()
    try:
        agent3 = TriageAgent()
    except ValueError as e:
        print(f"Setup Error: {e}")
        return
    
    # Load 1 Attack row (e.g., SYN_Stealth_Scan)
    test_csv = Path("data/test_unbalanced.csv")
    df = pd.read_csv(test_csv)
    attack_sample = df[df['Label'] == 'SYN_Stealth_Scan'].drop('Label', axis=1).iloc[0].to_dict()
    
    # Mock Station Context (Critical Scenario)
    critical_context = {
        "charger_id": "CS-BLDG-HQ-01",
        "charger_type": "DC_Fast_150kW",
        "location": "Downtown Central Hub",
        "current_session": "Active",
        "grid_load_status": "Peak Load (92% Substation Capacity)",
        "priority": "Critical Fleet Infrastructure"
    }

    print("\n[Step 1] Detection:")
    det = agent1.analyze(attack_sample)
    print(f"Detected: {det['predicted_label']} (Anomaly: {det['is_anomaly']})")
    
    print("\n[Step 2] Threat Intel:")
    intel = agent2.correlate_threat(det)
    print(f"Base Severity: {intel['base_severity']} | Technique: {intel['mitre_technique']}")
    
    print("\n[Step 3] LLM Risk Triage (Evaluating against Critical Context)...")
    triage = agent3.assess_risk(det, intel, critical_context)
    print(json.dumps(triage, indent=2))

if __name__ == "__main__":
    test_pipeline_to_triage()