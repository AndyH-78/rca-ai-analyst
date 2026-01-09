#!/bin/bash
cd "$(dirname "$0")"

export RCA_CSV_PATH="./data/example_incidents.csv"
source .venv/bin/activate

echo "Starting MCP Server..."
python mcp_server.py
