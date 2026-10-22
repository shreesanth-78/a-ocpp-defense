# 4-Agent Autonomous OCPP Cyber Defense Framework (A-OCPP)

The 4-Agent Autonomous OCPP Cyber Defense Framework (A-OCPP) is an agentic AI pipeline designed to autonomously detect, correlate, assess, and simulate mitigations for cyberattacks targeting Electric Vehicle (EV) charging infrastructure[cite: 3]. Moving beyond traditional standalone machine learning classifiers, this system incorporates multi-dimensional threat intelligence and operational grid context to scale its response proportionately, operating within strict deterministic safety constraints[cite: 3]. 

## Project Objective
* To move beyond passive statistical anomaly detection in EV charging systems by implementing a modular 4-agent pipeline that combines machine learning detection with LLM-based cyber-physical reasoning and automated, guardrailed response execution[cite: 4].
* To eliminate monolithic decision-making by decoupling detection, threat correlation, contextual triage, and policy-governed mitigation into verifiable stages orchestrated via LangGraph[cite: 2, 3].

## System Architecture: The 4-Agent Pipeline
![A-OCPP 4-Agent Architecture](Architecture%20Diagram.png)
The system follows a streamlined 4-agent pipeline coordinated as a Directed Acyclic Graph (DAG) using LangGraph[cite: 2, 4]:

* **Agent 1: Detection Agent (ML)**: Evaluates incoming OCPP network/flow telemetry using a trained classifier (e.g., XGBoost) to generate anomaly scores and feature attributions[cite: 4]. It serves as the line-rate anomaly screener, encapsulating a trained multi-class XGBoost classifier[cite: 2].
* **Agent 2: Threat Intelligence Agent (RAG/Retrieval)**: Correlates detected anomalies with known OCPP attack signatures (MITRE ATT&CK / CVEs) and recent station events[cite: 4]. The repository correlates network-level attacks with the MITRE ATT&CK for ICS taxonomy[cite: 2].
* **Agent 3: Risk Triage Agent (LLM)**: Synthesizes threat intelligence, charger criticality, and power-grid context to compute an incident severity index and natural-language summary[cite: 4]. It is implemented using an OpenAI-compatible endpoint serving openai/gpt-oss-120b[cite: 2].
* **Agent 4: Response Agent (LLM + Policy Engine)**: Selects an optimal mitigation strategy (`alert_operator`, `throttle_charger_power`, `soft_reset_charger`, `drop_websocket_session`) and passes it through a deterministic policy validation layer[cite: 4]. It operates entirely in user space as a standard application-level Python component[cite: 2].

## Experimental Methodology & Results
* The framework utilizes the public CICEVSE2024 dataset, consisting of 1,277,367 instances[cite: 2].
* The system achieved 99.66% classification accuracy and 0.00% Benign FPR on CICEVSE2024 test data[cite: 2].
* The conditional routing mechanism processes benign traffic in ~17–40 ms with zero token consumption[cite: 2].
* Operational impact metrics show a 72.6% reduction in unnecessary downtime[cite: 3].
* The 4-agent system eliminated 100% of over-reactions, dynamically choosing alerts or throttling based on grid context[cite: 4].

## Repository Structure
* `agents/`: Autonomous agent definitions (LangGraph nodes)[cite: 4].
* `tools/`: Deterministic execution tools & policy engine[cite: 4].
* `workflow/`: LangGraph state machine & pipeline routing[cite: 4].
* `simulator/`: OCPP traffic replay & simulation harness[cite: 4].
* `models/`: Trained ML baseline model artifacts[cite: 4].
* `notebooks/`: Data exploration & baseline training notebooks[cite: 4].
* `data/`: Local datasets (ignored by Git)[cite: 4].
* `main.py`: Main entry point[cite: 4].
* `requirements.txt`: Project dependencies[cite: 4].

## How to Run a Demo (Quick Start)

Follow these steps to clone the repository and run the end-to-end traffic simulation showcasing the 4-agent pipeline.

### 1. Clone the Repository
Clone the project to your local machine:
```bash
git clone [https://github.com/shreesanth-78/a-ocpp-defense.git](https://github.com/shreesanth-78/a-ocpp-defense.git)
cd a-ocpp-defense
```

## Set Up a Virtual Environment
Isolate the project dependencies by creating a Python virtual environment:
## For Windows:
```bash
python -m venv ocpp_defence
.\ocpp_defence\Scripts\activate
```
## For macOS/Linux:

```Bash
python3 -m venv ocpp_defence
source ocpp_defence/bin/activate
```
## Install Dependencies
Install the required libraries (including xgboost, langgraph, openai, and pandas):

```Bash
pip install -r requirements.txt
```

## Configure Environment Variables
The Risk Triage and Response agents require an LLM API to perform reasoning. Create a .env file in the root directory and configure it with your API provider details (the project natively uses openai/gpt-oss-120b via Groq):

```Code snippet
LLM_API_KEY=your_actual_api_key_here
LLM_BASE_URL=[https://api.groq.com/openai/v1](https://api.groq.com/openai/v1)
LLM_MODEL=openai/gpt-oss-120b
```
## Run the End-to-End Traffic Simulator
The traffic simulator replays pre-configured telemetry samples from the dataset to demonstrate how the agentic pipeline responds dynamically to different attacks and grid contexts.

```Bash
python simulator/traffic_simulator.py
```
## What to Expect:
The simulator will output three distinct scenarios:

Normal Daytime Charging (Benign): Bypasses the LLM entirely, exiting in ~17-41 ms with zero API token cost.

Reconnaissance on Critical Fleet Hub (SYN_Stealth_Scan): A medium-severity scan is upgraded to High Risk by Agent 3 due to peak grid load, triggering Agent 4 to throttle the charger power.

Volumetric DoS Attack (TCP_Flood): A high-severity flood on an idle commercial charger triggers a proportionate alert_operator action rather than a hard disconnect.

## Run the Comparative Evaluation (Optional)
To see how the 4-agent pipeline statistically compares against a rigid, standalone ML baseline across a 10-sample benchmark:

```Bash
python evaluation/evaluate_pipeline.py
```
This will output a side-by-side comparative table demonstrating the agentic framework's ability to eliminate over-reactions on minor reconnaissance scans[cite: 2].

## Authors
* **Students**: Kirupashankar Chockkanathan, Shree Santh B[cite: 4].
* **Guides**: Dr. Manimaran S, Dr. David Amar Raj[cite: 4].
