# workflow/graph.py
from typing import TypedDict, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

# Import our 4 core agents
from agents.detection_agent import DetectionAgent
from agents.threat_intel_agent import ThreatIntelAgent
from agents.triage_agent import TriageAgent
from agents.response_agent import ResponseAgent

# 1. Define the State Schema (The shared memory)
class CyberDefenseState(TypedDict):
    # Inputs
    telemetry_data: Dict[str, Any]
    charger_context: Dict[str, Any]
    
    # Agent Outputs
    detection_report: Optional[Dict[str, Any]]
    is_anomaly: Optional[bool]
    
    threat_intel: Optional[Dict[str, Any]]
    
    triage_assessment: Optional[Dict[str, Any]]
    risk_level: Optional[str]
    
    mitigation_report: Optional[Dict[str, Any]]

# 2. Initialize Agents Globally for the Graph
agent1 = DetectionAgent()
agent2 = ThreatIntelAgent()
agent3 = TriageAgent()
agent4 = ResponseAgent()

# 3. Define the Nodes (Wrappers around our agents)
def detect_node(state: CyberDefenseState) -> dict:
    report = agent1.analyze(state["telemetry_data"])
    return {"detection_report": report, "is_anomaly": report.get("is_anomaly", False)}

def threat_intel_node(state: CyberDefenseState) -> dict:
    intel = agent2.correlate_threat(state["detection_report"])
    return {"threat_intel": intel}

def triage_node(state: CyberDefenseState) -> dict:
    assessment = agent3.assess_risk(
        state["detection_report"], 
        state["threat_intel"], 
        state["charger_context"]
    )
    return {"triage_assessment": assessment, "risk_level": assessment.get("risk_level", "Unknown")}

def response_node(state: CyberDefenseState) -> dict:
    decision = agent4.determine_action(
        state["triage_assessment"], 
        state["charger_context"].get("charger_id", "Unknown")
    )
    return {"mitigation_report": decision}

# 4. Define the Routing Logic
def route_after_detection(state: CyberDefenseState) -> str:
    """If ML flags an anomaly, proceed to Threat Intel. Otherwise, stop."""
    if state.get("is_anomaly"):
        return "threat_intel"
    return END

# 5. Build the Graph
builder = StateGraph(CyberDefenseState)

# Add Nodes
builder.add_node("detect", detect_node)
builder.add_node("threat_intel", threat_intel_node)
builder.add_node("triage", triage_node)
builder.add_node("response", response_node)

# Add Edges (The Pipeline Flow)
builder.add_edge(START, "detect")
builder.add_conditional_edges("detect", route_after_detection) # Conditional branch
builder.add_edge("threat_intel", "triage")
builder.add_edge("triage", "response")
builder.add_edge("response", END)

# 6. Compile into an executable application
app = builder.compile()