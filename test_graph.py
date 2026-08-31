# test_graph.py
import json
import pandas as pd
from pathlib import Path
from workflow.graph import app

def run_end_to_end_test():
    print("="*60)
    print(" END-TO-END PIPELINE TEST ")
    print("="*60)
    
    # 1. Load Data
    test_csv = Path("data/test_unbalanced.csv")
    df = pd.read_csv(test_csv)
    
    # We will test an active attack scenario
    attack_sample = df[df['Label'] == 'SYN_Flood'].drop('Label', axis=1).iloc[0].to_dict()
    
    # 2. Define Context
    context = {
        "charger_id": "CS-MALL-04",
        "charger_type": "AC_Level_2",
        "location": "Suburban Shopping Mall",
        "current_session": "Active",
        "grid_load_status": "Normal (40% Capacity)",
        "priority": "Standard Public Infrastructure"
    }
    
    # 3. Create Initial State
    initial_state = {
        "telemetry_data": attack_sample,
        "charger_context": context
    }
    
    # 4. Invoke the Graph
    print(f"Ingesting Telemetry for Charger {context['charger_id']}...\n")
    
    final_state = app.invoke(initial_state)
    
    # 5. Print Results
    print(f"--- Final System State ---")
    print(f"Anomaly Detected: {final_state.get('is_anomaly')}")
    if final_state.get('is_anomaly'):
        print(f"Attack Type:      {final_state['detection_report']['predicted_label']}")
        print(f"Risk Level:       {final_state.get('risk_level')}")
        print(f"Mitigation Executed:\n{json.dumps(final_state.get('mitigation_report'), indent=2)}")

if __name__ == "__main__":
    run_end_to_end_test()