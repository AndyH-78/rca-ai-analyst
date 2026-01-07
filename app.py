import os
import pandas as pd
import streamlit as st

from rca_scoring import OllamaClient, evaluate_incident, critic_review, improve_rca

st.set_page_config(page_title="RCA Quality Analyst", layout="wide")
st.title("RCA Quality Analyst (lokal, CSV → Score/Feedback/Improve)")

with st.sidebar:
    st.header("LLM (Ollama)")
    model = st.text_input("Model", value=os.getenv("OLLAMA_MODEL", "llama3.1:8b"))
    host = st.text_input("Host", value=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    st.caption("Tipp: `ollama pull llama3.1:8b`")
    st.divider()
    st.header("CSV Mapping")
    st.caption("Ordne deine Jira-Export-Spalten zu.")

uploaded = st.file_uploader("CSV hochladen (Jira Export)", type=["csv"])
if not uploaded:
    st.info("CSV hochladen → Spalten mappen → Incident wählen → bewerten.")
    st.stop()

# robust read
try:
    df = pd.read_csv(uploaded).fillna("")
except UnicodeDecodeError:
    df = pd.read_csv(uploaded, encoding="latin-1").fillna("")

st.success(f"CSV geladen: {df.shape[0]} Zeilen, {df.shape[1]} Spalten")

cols = list(df.columns)
if len(cols) < 2:
    st.error("CSV hat zu wenige Spalten.")
    st.stop()

with st.sidebar:
    incident_id_col = st.selectbox("Incident ID", options=cols, index=0)
    summary_col = st.selectbox("Summary", options=cols, index=min(1, len(cols)-1))
    description_col = st.selectbox("Description", options=cols, index=min(2, len(cols)-1))
    root_cause_col = st.selectbox("Root Cause", options=cols, index=min(3, len(cols)-1))
    resolution_col = st.selectbox("Resolution/Fix", options=cols, index=min(4, len(cols)-1))
    preventive_col = st.selectbox("Preventive Action", options=cols, index=min(5, len(cols)-1))

left, right = st.columns([1, 1])

with left:
    st.subheader("Incidents (Preview)")
    st.dataframe(df[[incident_id_col, summary_col]].head(200), use_container_width=True)

    incident_ids = df[incident_id_col].astype(str).tolist()
    chosen = st.selectbox("Wähle Incident", options=incident_ids)

row_df = df[df[incident_id_col].astype(str) == str(chosen)]
if row_df.empty:
    st.error("Incident nicht gefunden (Mapping prüfen).")
    st.stop()

row = row_df.iloc[0]
row_obj = {
    "incident_id": str(row[incident_id_col]),
    "summary": str(row[summary_col]),
    "description": str(row[description_col]),
    "root_cause": str(row[root_cause_col]),
    "resolution": str(row[resolution_col]),
    "preventive_action": str(row[preventive_col]),
}

with right:
    st.subheader("Incident Details")
    st.markdown(f"**ID:** {row_obj['incident_id']}")
    st.markdown(f"**Summary:** {row_obj['summary']}")
    with st.expander("Description", expanded=False):
        st.write(row_obj["description"])
    with st.expander("Root Cause", expanded=True):
        st.write(row_obj["root_cause"])
    with st.expander("Resolution/Fix", expanded=False):
        st.write(row_obj["resolution"])
    with st.expander("Preventive Action", expanded=False):
        st.write(row_obj["preventive_action"])

st.divider()
st.subheader("Analyse")

client = OllamaClient(model=model, host=host)

for k in ["evaluation", "critic", "improved"]:
    if k not in st.session_state:
        st.session_state[k] = None

colA, colB, colC = st.columns([1, 1, 1])
do_eval = colA.button("1) Bewerten")
do_critic = colB.button("2) Critic Review")
do_improve = colC.button("3) Verbesserte Version")

if do_eval:
    with st.spinner("Bewertung läuft..."):
        st.session_state["evaluation"] = evaluate_incident(client, row_obj)
        st.session_state["critic"] = None
        st.session_state["improved"] = None

if do_critic:
    if not st.session_state["evaluation"]:
        st.warning("Bitte erst bewerten (Schritt 1).")
    else:
        with st.spinner("Critic Review läuft..."):
            st.session_state["critic"] = critic_review(client, row_obj, st.session_state["evaluation"])

if do_improve:
    with st.spinner("Verbesserung läuft..."):
        st.session_state["improved"] = improve_rca(client, row_obj)

eval_json = st.session_state["evaluation"]
if eval_json:
    s = eval_json.get("scores", {})
    total = eval_json.get("total", None)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("RCA Score", value=total if total is not None else "—")
        st.write("**Teil-Scores (0–20)**")
        st.write(s)

    with c2:
        st.write("**Executive Summary**")
        st.write(eval_json.get("executive_summary", ""))
        st.write("**Stärken**")
        st.write(eval_json.get("strengths", []))
        st.write("**Lücken**")
        st.write(eval_json.get("gaps", []))
        st.write("**Verbesserungen**")
        st.write(eval_json.get("improvements", []))

    with st.expander("Raw JSON: Evaluation"):
        st.json(eval_json)

critic_json = st.session_state["critic"]
if critic_json:
    st.divider()
    st.subheader("Critic Review")
    st.write("**Confidence:**", critic_json.get("confidence", "—"))
    st.write("**Top Risks**")
    st.write(critic_json.get("top_risks", []))
    st.write("**Missing Evidence Requests**")
    st.write(critic_json.get("missing_evidence_requests", []))
    with st.expander("Raw JSON: Critic"):
        st.json(critic_json)

improved_json = st.session_state["improved"]
if improved_json:
    st.divider()
    st.subheader("Verbesserte Version (ohne Fakten zu erfinden)")
    st.write("**Improved Root Cause**")
    st.write(improved_json.get("improved_root_cause", ""))
    st.write("**Improved Resolution**")
    st.write(improved_json.get("improved_resolution", ""))
    st.write("**Improved Preventive Action**")
    st.write(improved_json.get("improved_preventive_action", ""))
    st.write("**Notes**")
    st.write(improved_json.get("notes", []))
    with st.expander("Raw JSON: Improved"):
        st.json(improved_json)
