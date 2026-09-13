# notebooks/validate_knowledge_base.py
import json
import pandas as pd
from pathlib import Path

def validate_kb():
    # Paths
    project_root = Path(__file__).resolve().parent.parent
    data_path = project_root / "data" / "train_balanced.csv"
    kb_path = project_root / "knowledge_base" / "mitre_ics_ocpp.json"

    print("=" * 60)
    print(" THREAT INTELLIGENCE KNOWLEDGE BASE VALIDATION ")
    print("=" * 60)

    # 1. Load Dataset Labels
    if not data_path.exists():
        print(f"Error: Dataset not found at {data_path}")
        return
    
    df = pd.read_csv(data_path)
    dataset_labels = set(df['Label'].unique())
    # Remove 'Benign' as it doesn't need a threat mapping
    if 'Benign' in dataset_labels:
        dataset_labels.remove('Benign')
        
    print(f"Total distinct attack labels in dataset: {len(dataset_labels)}")

    # 2. Load Knowledge Base
    if not kb_path.exists():
        print(f"Error: KB not found at {kb_path}")
        return
        
    with open(kb_path, 'r') as f:
        kb = json.load(f)
        
    kb_labels = set(kb.keys())
    print(f"Total mapped attacks in Knowledge Base:  {len(kb_labels)}\n")

    # 3. Coverage Analysis
    missing_in_kb = dataset_labels - kb_labels
    unused_in_kb = kb_labels - dataset_labels
    
    coverage_pct = ((len(dataset_labels) - len(missing_in_kb)) / len(dataset_labels)) * 100

    print(f"Coverage: {coverage_pct:.1f}%\n")
    
    if missing_in_kb:
        print("CRITICAL: Missing from Knowledge Base (Agent 2 will fail on these):")
        for m in missing_in_kb:
            print(f"  - {m}")
    else:
        print("Dataset Coverage: PERFECT (100%)")

    if unused_in_kb:
        print("\nWARNING: Unused in Knowledge Base (Mapped but not in dataset):")
        for u in unused_in_kb:
            print(f"  - {u}")

    # 4. MITRE ICS ID Audit
    print("\n--- MITRE ATT&CK for ICS ID Audit ---")
    suspicious_mappings = 0
    for attack, data in kb.items():
        technique = data.get("technique", "")
        # T0842 is actually Network Sniffing in ICS, not Service Scanning
        if "T0842" in technique and "Scan" in attack:
            print(f"  [!] ID Mismatch: '{attack}' mapped to {technique}.")
            print("      Correction needed: Scanning in ICS is typically mapped to T0846 or related Discovery tactics.")
            suspicious_mappings += 1

    if suspicious_mappings == 0:
        print("No obvious MITRE ID mismatches found.")
    else:
        print(f"\nTotal suspicious MITRE mappings flagged: {suspicious_mappings}")

if __name__ == "__main__":
    validate_kb()