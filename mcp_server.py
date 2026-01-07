import os
import pandas as pd
from typing import Optional, Dict, Any, List

from rca_scoring import OllamaClient, evaluate_incident

# MCP server
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("RCA Quality Analyst")

CSV_PATH = os.getenv("RCA_CSV_PATH", "./data/example_incidents.csv")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

_df_cache: Optional[pd.DataFrame] = None


def load_df() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        _df_cache = pd.read_csv(CSV_PATH).fillna("")
    return _df_cache


@mcp.tool()
def list_columns() -> List[str]:
    """List all columns in the configured RCA CSV."""
    return list(load_df().columns)


@mcp.tool()
def list_incidents(limit: int = 20) -> List[Dict[str, str]]:
    """List incident IDs and summaries (best-effort heuristic)."""
    df = load_df().head(limit)
    cols = list(df.columns)
    id_col = cols[0]
    sum_col = cols[1] if len(cols) > 1 else cols[0]
    return [{"incident_id": str(r[id_col]), "summary": str(r[sum_col])} for _, r in df.iterrows()]


@mcp.tool()
def get_incident(
    incident_id: str,
    incident_id_col: str,
    summary_col: str,
    description_col: str,
    root_cause_col: str,
    resolution_col: str,
    preventive_action_col: str,
) -> Dict[str, Any]:
    """Fetch a single incident by id using explicit column mapping."""
    df = load_df()
    hit = df[df[incident_id_col].astype(str) == str(incident_id)]
    if hit.empty:
        return {"error": f"Incident {incident_id} not found"}
    r = hit.iloc[0]
    return {
        "incident_id": str(r[incident_id_col]),
        "summary": str(r[summary_col]),
        "description": str(r[description_col]),
        "root_cause": str(r[root_cause_col]),
        "resolution": str(r[resolution_col]),
        "preventive_action": str(r[preventive_action_col]),
    }


@mcp.tool()
def evaluate_incident_by_id(
    incident_id: str,
    incident_id_col: str,
    summary_col: str,
    description_col: str,
    root_cause_col: str,
    resolution_col: str,
    preventive_action_col: str,
) -> Dict[str, Any]:
    """Evaluate RCA for one incident by ID."""
    incident = get_incident(
        incident_id=incident_id,
        incident_id_col=incident_id_col,
        summary_col=summary_col,
        description_col=description_col,
        root_cause_col=root_cause_col,
        resolution_col=resolution_col,
        preventive_action_col=preventive_action_col,
    )
    if "error" in incident:
        return incident

    client = OllamaClient(model=OLLAMA_MODEL, host=OLLAMA_HOST)
    return evaluate_incident(client, incident)


def main():
    # stdio transport for desktop MCP hosts
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
