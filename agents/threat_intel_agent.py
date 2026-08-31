# agents/threat_intel_agent.py
import json
from pathlib import Path

class ThreatIntelAgent:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent
        self.kb_path = self.project_root / "knowledge_base" / "mitre_ics_ocpp.json"
        
        # Load knowledge base into memory
        if self.kb_path.exists():
            with open(self.kb_path, 'r') as f:
                self.knowledge_base = json.load(f)
        else:
            self.knowledge_base = {}
            print(f"Warning: Knowledge base not found at {self.kb_path}")

    def correlate_threat(self, detection_report: dict) -> dict:
        """
        Takes the detection report from Agent 1 and correlates the predicted label 
        with MITRE ATT&CK for ICS threat intelligence.
        """
        is_anomaly = detection_report.get("is_anomaly", False)
        predicted_label = detection_report.get("predicted_label", "Unknown")
        
        # If no anomaly, return a clean bill of health
        if not is_anomaly or predicted_label == "Benign":
            return {
                "threat_correlated": False,
                "message": "No active threat detected. Traffic is benign."
            }
            
        # Perform retrieval from Knowledge Base
        threat_intel = self.knowledge_base.get(predicted_label)
        
        if threat_intel:
            return {
                "threat_correlated": True,
                "attack_type": predicted_label,
                "mitre_tactic": threat_intel["tactic"],
                "mitre_technique": threat_intel["technique"],
                "ocpp_impact": threat_intel["ocpp_impact"],
                "base_severity": threat_intel["severity"]
            }
        else:
            # Fallback if attack type isn't in our DB
            return {
                "threat_correlated": True,
                "attack_type": predicted_label,
                "mitre_tactic": "Unknown",
                "mitre_technique": "Unknown",
                "ocpp_impact": "Unclassified anomaly detected in network flow.",
                "base_severity": "Unknown"
            }