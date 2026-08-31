# simulator/traffic_simulator.py
import sys
from pathlib import Path

# Add project root to Python path so it can find 'workflow' and 'agents'
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import time
import json
import pandas as pd
from workflow.graph import app

TEST_DATA_PATH = PROJECT_ROOT / "data" / "test_unbalanced.csv"

# ... (Keep your OCPPTrafficSimulator class and main() exactly the same below this) ...


class OCPPTrafficSimulator:
    def __init__(self):
        if not TEST_DATA_PATH.exists():
            raise FileNotFoundError(f"Test dataset not found at {TEST_DATA_PATH}")
        print("Loading test dataset for live simulation...")
        self.df = pd.read_csv(TEST_DATA_PATH)

    def get_sample_by_label(self, label: str) -> dict:
        """Extracts a telemetry feature vector matching a specific label."""
        matching_rows = self.df[self.df["Label"] == label]
        if matching_rows.empty:
            raise ValueError(f"Label '{label}' not found in dataset.")
        sample = matching_rows.sample(1, random_state=int(time.time())).drop("Label", axis=1).iloc[0].to_dict()
        return sample

    def run_scenario(self, scenario_name: str, label: str, context: dict):
        print("\n" + "=" * 70)
        print(f" SCENARIO: {scenario_name}")
        print("=" * 70)
        print(f"Target Charger: {context['charger_id']} ({context['location']})")
        print(f"Grid Condition: {context['grid_load_status']} | Priority: {context['priority']}")
        print(f"Ground-Truth Label: {label}")
        print("-" * 70)

        # 1. Fetch telemetry
        telemetry = self.get_sample_by_label(label)

        # 2. Build initial state
        state_input = {
            "telemetry_data": telemetry,
            "charger_context": context,
        }

        # 3. Measure pipeline latency
        start_time = time.time()
        result = app.invoke(state_input)
        latency = (time.time() - start_time) * 1000

        # 4. Print stage-by-stage results
        print(f"[1] Detection: {'MALICIOUS' if result.get('is_anomaly') else 'BENIGN'}")
        if not result.get("is_anomaly"):
            print("    -> No threat detected. LLM triage skipped (Saved API latency & cost).")
        else:
            det = result["detection_report"]
            intel = result["threat_intel"]
            triage = result["triage_assessment"]
            mitigation = result["mitigation_report"]

            print(f"    -> Predicted Attack: {det['predicted_label']} (Confidence: {det['confidence']}%)")
            print(f"[2] Threat Intel: {intel.get('mitre_technique')} ({intel.get('base_severity')} Severity)")
            print(f"[3] Risk Triage:  {triage.get('risk_level')} Risk")
            print(f"    -> Reasoning: {triage.get('reasoning')}")
            print(f"[4] Response:     {mitigation.get('selected_action')} ({mitigation.get('policy_validation')})")
            print(f"    -> Action Status: {mitigation['execution_result']['status']}")

        print(f"\nPipeline Latency: {latency:.2f} ms")


def main():
    sim = OCPPTrafficSimulator()

    # Scenario 1: Normal Everyday Charging (Benign)
    sim.run_scenario(
        scenario_name="1. Normal Daytime Charging Session",
        label="Benign",
        context={
            "charger_id": "CS-SUBURB-01",
            "charger_type": "AC_Level_2",
            "location": "Residential Zone A",
            "current_session": "Active",
            "grid_load_status": "Normal (35% Capacity)",
            "priority": "Low",
        },
    )

    # Scenario 2: Network Reconnaissance on High-Priority Fleet
    sim.run_scenario(
        scenario_name="2. Reconnaissance Scan on Critical Fleet Hub",
        label="SYN_Stealth_Scan",
        context={
            "charger_id": "CS-AIRPORT-BUS-01",
            "charger_type": "DC_Fast_350kW",
            "location": "Airport EV Shuttle Hub",
            "current_session": "Active",
            "grid_load_status": "Peak Load (94% Capacity)",
            "priority": "Critical Public Transport",
        },
    )

    # Scenario 3: Heavy Volumetric DoS Attack
    sim.run_scenario(
        scenario_name="3. Volumetric DoS Attack During Normal Grid Load",
        label="TCP_Flood",
        context={
            "charger_id": "CS-HIGHWAY-09",
            "charger_type": "DC_Fast_150kW",
            "location": "Highway Rest Stop 12",
            "current_session": "Idle",
            "grid_load_status": "Normal (50% Capacity)",
            "priority": "Standard Commercial",
        },
    )


if __name__ == "__main__":
    main()