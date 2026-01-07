# RCA Quality Analyst
**Local AI-powered RCA evaluation for Jira Incidents & Defects**

This project provides a **local, privacy-friendly AI tool** to evaluate the quality of Root Cause Analyses (RCA) from Jira incidents or defects.

It scores RCAs, identifies gaps, suggests improvements, and exposes the same capabilities via:
- a **human-friendly Web UI**
- a **machine-friendly MCP Server** (for AI agents & tools)

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

## ✅ What This Tool Does

For each Incident / Defect, it can:

- Score RCA quality (**0–100**)
- Evaluate five dimensions:
  - Clarity & structure
  - Root cause depth
  - Evidence & specificity
  - Corrective action quality
  - Preventive action strength
- Highlight **strengths and gaps**
- Propose **concrete improvements**
- Rewrite RCAs **without inventing facts**
  - Missing evidence is explicitly marked as `[NEEDED: …]`

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


---

## 🧩 Components

### `prompts.py`
Defines the **RCA quality standard**:
- Evaluation rubric
- Critic logic
- Improvement rules (no hallucinations)

This file represents the **policy layer** of the system and is intentionally
kept separate from code for governance and versioning.

---

### `rca_scoring.py`
Core domain logic:
- Communicates with the local LLM (Ollama)
- Evaluates RCAs
- Runs critic & improvement steps

This module is **UI-agnostic** and **API-agnostic**.

---

### `app.py` (Streamlit UI)
Human-facing interface:
- Upload Jira CSV exports
- Map columns
- Review scores & feedback
- Run critic and improvement steps

Designed for **human-in-the-loop** usage.

---

### `mcp_server.py`
Machine-facing interface:
- Exposes RCA evaluation as MCP tools
- Enables AI agents to call:
  - `list_incidents`
  - `get_incident`
  - `evaluate_incident_by_id`

This makes the project **platform-ready** and future-proof.

---

### `batch.py`
CLI batch processing:
- Score many incidents at once
- Export CSV results
- Useful for reporting and trend analysis

---

## 🔒 Privacy & Security

- Runs **entirely locally**
- No cloud LLMs required
- No data leaves the machine
- Ideal for sensitive incident data

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

streamlit run app.py

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
