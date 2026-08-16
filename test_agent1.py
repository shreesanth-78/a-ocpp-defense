# test_agent1.py
from agents.detection_agent import DetectionAgent
import pandas as pd
from pathlib import Path
import json

def test_detection():
    print("Initializing Detection Agent...")
    agent = DetectionAgent()
    
    # Load 1 Benign row and 1 Attack row from our test set
    test_csv = Path("data/test_unbalanced.csv")
    df = pd.read_csv(test_csv)
    
    benign_sample = df[df['Label'] == 'Benign'].drop('Label', axis=1).iloc[0].to_dict()
    attack_sample = df[df['Label'] != 'Benign'].drop('Label', axis=1).iloc[0].to_dict()
    
    print("\n--- Testing Benign Sample ---")
    benign_result = agent.analyze(benign_sample)
    print(json.dumps(benign_result, indent=2))
    
    print("\n--- Testing Attack Sample ---")
    attack_result = agent.analyze(attack_sample)
    print(json.dumps(attack_result, indent=2))

if __name__ == "__main__":
    test_detection()