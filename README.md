# 4-Agent Autonomous OCPP Cyber Defense Framework (A-OCPP)

An Agentic AI framework designed for autonomous detection, threat correlation, grid-aware risk triage, and policy-validated mitigation of OCPP-based cyberattacks in Electric Vehicle (EV) charging infrastructure.

## Project Objective
To move beyond passive statistical anomaly detection in EV charging systems by implementing a modular 4-agent pipeline that combines machine learning detection with LLM-based cyber-physical reasoning and automated, guardrailed response execution.

## Proposed Architecture
The system follows a streamlined 4-agent pipeline:
1. **Detection Agent (ML):** Evaluates incoming OCPP network/flow telemetry using a trained classifier (e.g., XGBoost) to generate anomaly scores and feature attributions.
2. **Threat Intelligence Agent (RAG/Retrieval):** Correlates detected anomalies with known OCPP attack signatures (MITRE ATT&CK / CVEs) and recent station events.
3. **Risk Triage Agent (LLM):** Synthesizes threat intelligence, charger criticality, and power-grid context to compute an incident severity index and natural-language summary.
4. **Response Agent (LLM + Policy Engine):** Selects an optimal mitigation strategy (`alert_operator`, `throttle_charger_power`, `soft_reset_charger`, `drop_websocket_session`) and passes it through a deterministic policy validation layer.

## Repository Structure
## Repository Structure

```text
a-ocpp-defense/
│
├── agents/
│   ├── detection_agent.py
│   ├── threat_intel_agent.py
│   ├── triage_agent.py
│   └── response_agent.py
│
├── tools/
│   └── mitigation_tools.py
│
├── workflow/
│   └── graph.py
│
├── simulator/
│
├── models/
│
├── notebooks/
│
├── data/
│
├── .env
├── .gitignore
├── main.py
└── requirements.txt

## Current Status
- **Phase:** Initializing project structure, environment, and dataset research.
- **Environment:** Python 3.10+ virtual environment (`ocpp_defence`).

## Authors
- **Students:** Kirupashankar Chockkanathan, Shree Santh B
- **Guides:** Dr. Manimaran S, Dr. David Amar Raj
