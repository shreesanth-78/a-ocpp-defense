# evaluation/evaluate_pipeline.py
import sys
from pathlib import Path
import time
import json
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from workflow.graph import app
from agents.detection_agent import DetectionAgent

TEST_DATA_PATH = PROJECT_ROOT / "data" / "test_unbalanced.csv"

def run_comparative_evaluation(num_samples: int = 10):
    print("=" * 70)
    print(f" RUNNING COMPARATIVE EVALUATION ({num_samples} Mixed Test Samples)")
    print("=" * 70)

    if not TEST_DATA_PATH.exists():
        print(f"Error: Dataset not found at {TEST_DATA_PATH}")
        return

    df = pd.read_csv(TEST_DATA_PATH)
    
    # Stratified mini-batch: include benign, scan, and flood
    test_labels = ["Benign", "SYN_Stealth_Scan", "TCP_Flood", "SYN_Flood", "TCP_Port_Scan"]
    samples = []
    
    for lbl in test_labels:
        matched = df[df["Label"] == lbl]
        if not matched.empty:
            sample_df = matched.sample(min(2, len(matched)), random_state=42)
            samples.append(sample_df)
            
    eval_df = pd.concat(samples).sample(frac=1, random_state=42).reset_index(drop=True)

    raw_ml_agent = DetectionAgent()

    results = []

    print(f"Evaluating {len(eval_df)} samples across baseline vs 4-agent system...\n")

    for idx, row in eval_df.iterrows():
        label = row["Label"]
        telemetry = row.drop("Label").to_dict()

        # Context assignment based on sample index
        is_critical = idx % 2 == 0
        context = {
            "charger_id": f"CS-EVAL-{idx:02d}",
            "charger_type": "DC_Fast_150kW" if is_critical else "AC_Level_2",
            "location": "Fleet Hub" if is_critical else "Public Parking",
            "current_session": "Active",
            "grid_load_status": "Peak Load (95%)" if is_critical else "Normal (45%)",
            "priority": "Critical Fleet" if is_critical else "Standard Commercial",
        }

        # --- Baseline ML Pipeline (Hardcoded Rule: Flagged anomaly -> Hard Action) ---
        t0 = time.time()
        ml_res = raw_ml_agent.analyze(telemetry)
        ml_latency = (time.time() - t0) * 1000
        baseline_action = "drop_websocket_session" if ml_res["is_anomaly"] else "none"

        # --- 4-Agent Pipeline ---
        t1 = time.time()
        agentic_state = app.invoke({"telemetry_data": telemetry, "charger_context": context})
        agentic_latency = (time.time() - t1) * 1000

        agentic_action = "none"
        risk_level = "None"
        if agentic_state.get("is_anomaly"):
            risk_level = agentic_state["triage_assessment"].get("risk_level", "Unknown")
            agentic_action = agentic_state["mitigation_report"].get("selected_action", "none")

        results.append({
            "Sample_ID": idx + 1,
            "True_Label": label,
            "Context_Priority": context["priority"],
            "ML_Prediction": ml_res["predicted_label"],
            "Baseline_Action": baseline_action,
            "Baseline_Latency_ms": round(ml_latency, 3),
            "Agentic_Risk": risk_level,
            "Agentic_Action": agentic_action,
            "Agentic_Latency_ms": round(agentic_latency, 2),
        })

    results_table = pd.DataFrame(results)
    
    print("\n" + "=" * 70)
    print(" COMPARATIVE EVALUATION RESULTS ")
    print("=" * 70)
    print(results_table[["True_Label", "Context_Priority", "Baseline_Action", "Agentic_Risk", "Agentic_Action", "Agentic_Latency_ms"]].to_string(index=False))

    # Save evaluation summary to CSV for documentation/reports
    output_eval = PROJECT_ROOT / "evaluation" / "benchmark_results.csv"
    results_table.to_csv(output_eval, index=False)
    print(f"\nSaved benchmark metrics to: {output_eval}")

if __name__ == "__main__":
    run_comparative_evaluation()