# RCA Quality Analyst
**Local AI-powered RCA evaluation for Jira Incidents & Defects (Streamlit + Ollama + MCP)**

RCA Quality Analyst is a **local, privacy-friendly AI tool** that evaluates the quality of Root Cause Analyses (RCAs) for Jira incidents/defects.
It provides **consistent scoring**, highlights gaps, and suggests concrete improvements — without sending sensitive incident data to the cloud.

The system can be used via:
- a **human-friendly Web UI (Streamlit)** for reviews
- a **batch mode** for large exports
- a **machine-friendly MCP Server** for AI agents & integrations

---

## 🎯 Problem Statement

In many IT organizations:
- Root Cause Analyses are inconsistent
- Symptoms are confused with causes
- Preventive actions are weak or missing
- The same incidents happen again

This tool helps answer:
> *“Is this RCA actually good — and how can it be improved?”*

---

## ✅ Key Capabilities

For each incident/defect, the tool can:
- Score RCA quality (**0–100**)
- Evaluate five dimensions:
  - clarity & structure
  - root cause depth
  - evidence & specificity
  - corrective action quality
  - preventive action strength
- Provide:
  - strengths
  - gaps
  - improvements
  - executive summary
- Produce improved RCA text **without inventing facts**
  - missing evidence is marked as `[NEEDED: ...]`


---

## 🧠 Architecture Overview


            ┌──────────────┐
            │ Streamlit UI │  (Human-in-the-loop)
            └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐
            │ Core Logic   │  rca_scoring.py
            └──────┬───────┘
                   │
    ┌──────────────┴──────────────┐
    ▼                             ▼
┌──────────────┐              -------------         
│ LLM (Ollama) │                MCP-Server
└──────┬───────┘              -------------

---


---

## 🧩 Components

### `app.py` (Streamlit UI)
Human-facing interface:
- Upload Jira CSV exports
- Map columns
- Review scores & feedback
- Generate critic review + improved RCA versions

### `rca_scoring.py` (Core Logic)
Reusable evaluation engine:
- builds prompts from `prompts.py`
- calls local LLM (Ollama)
- returns structured JSON output

### `prompts.py`
Defines the RCA quality rubric:
- evaluation criteria
- critic logic
- improvement instructions (no hallucinations)

### `mcp_server.py` (MCP Tools API)
Machine-facing interface exposing tools like:
- `list_columns`
- `list_incidents`
- `get_incident`
- `evaluate_incident_by_id`

### `batch.py`
Batch processing for Jira exports:
- scores many incidents in one run
- outputs `out/results.csv` + `out/report.md`

### `tools/`
Developer utilities:
- `tools/mcp_test_client.py` (current client)
- `tools/mcp_test_client_old.py` (legacy / documentation)

---

## 🔒 Privacy & Security

- Runs **entirely locally**
- No cloud LLM required
- No incident data leaves the device
- Ideal for sensitive operational data

---

## 🚀 Quick Start (macOS)

### Requirements
- Python 3.11+
- Ollama

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.1:8b

▶️ Run Streamlit UI
streamlit run app.py

▶️ Run Batch Scoring
python batch.py --csv data/sample_export.csv --outdir out
Outputs:
out/results.csv
out/report.md

▶️ Run MCP Server
export RCA_CSV_PATH="./data/example_incidents.csv"
python mcp_server.py

▶️ Run MCP Test Client
python tools/mcp_test_client.py

🔧 Convenience Start Scripts
Start UI
./start.sh

Start MCP Server
./start_mcp.sh

Stop any running service with:
CTRL + C


export RCA_CSV_PATH="./data/example_incidents.csv"
python mcp_server.py
---
🛣️ Roadmap
Batch critic & improvement reports
Trend dashboards (RCA quality over time)
Auto-mapping for common Jira exports
Direct Jira API integration via MCP
Evaluation metrics & regression testing
⚠️ Disclaimer
This tool supports RCA reviews but does not replace:
incident ownership
engineering judgment
post-incident accountability
It is designed to augment, not automate responsibility.
