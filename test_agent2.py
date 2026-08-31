# test_agent2.py
from agents.detection_agent import DetectionAgent
from agents.threat_intel_agent import ThreatIntelAgent
import pandas as pd
from pathlib import Path
import json

def test_pipeline_1_and_2():
    print("Initializing Agents...")
    agent1 = DetectionAgent()
    agent2 = ThreatIntelAgent()
    
    # Load 1 Attack row from test set
    test_csv = Path("data/test_unbalanced.csv")
    df = pd.read_csv(test_csv)
    
    attack_sample = df[df['Label'] == 'SYN_Stealth_Scan'].drop('Label', axis=1).iloc[0].to_dict()
    
    print("\n[Step 1] Agent 1 - ML Detection:")
    detection_result = agent1.analyze(attack_sample)
    print(json.dumps(detection_result, indent=2))
    
    print("\n[Step 2] Agent 2 - Threat Correlation:")
    threat_result = agent2.correlate_threat(detection_result)
    print(json.dumps(threat_result, indent=2))

if __name__ == "__main__":
    test_pipeline_1_and_2()