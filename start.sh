#!/bin/bash
cd "$(dirname "$0")"

source .venv/bin/activate

echo "Starting Streamlit UI..."
streamlit run app.py
