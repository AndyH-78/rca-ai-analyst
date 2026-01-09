import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd

from rca_scoring import OllamaClient, evaluate_incident


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch RCA Quality Scoring (CSV -> scores + report)")
    p.add_argument("--csv", required=True, help="Path to input CSV (Jira export or sample)")
    p.add_argument("--outdir", default="out", help="Output directory (default: out)")
    p.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "llama3.1:8b"), help="Ollama model")
    p.add_argument("--host", default=os.getenv("OLLAMA_HOST", "http://localhost:11434"), help="Ollama host")

    # Column mapping (defaults match our sample)
    p.add_argument("--col-id", default="issue_key")
    p.add_argument("--col-summary", default="summary")
    p.add_argument("--col-description", default="description")
    p.add_argument("--col-root-cause", default="root_cause")
    p.add_argument("--col-resolution", default="resolution")
    p.add_argument("--col-preventive", default="preventive_action")

    p.add_argument("--limit", type=int, default=0, help="Limit rows for quick runs (0 = all)")
    p.add_argument("--fail-fast", action="store_true", help="Stop on first error")
    return p.parse_args()


def ensure_cols(df: pd.DataFrame, cols: List[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in CSV: {missing}\nAvailable: {list(df.columns)}")


def row_to_obj(row: pd.Series, colmap: Dict[str, str]) -> Dict[str, Any]:
    return {
        "incident_id": str(row[colmap["id"]]),
        "summary": str(row[colmap["summary"]]),
        "description": str(row[colmap["description"]]),
        "root_cause": str(row[colmap["root_cause"]]),
        "resolution": str(row[colmap["resolution"]]),
        "preventive_action": str(row[colmap["preventive"]]),
    }


def main() -> int:
    args = parse_args()

    in_path = Path(args.csv)
    if not in_path.exists():
        print(f"ERROR: CSV not found: {in_path}", file=sys.stderr)
        return 2

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Read CSV robustly
    try:
        df = pd.read_csv(in_path).fillna("")
    except UnicodeDecodeError:
        df = pd.read_csv(in_path, encoding="latin-1").fillna("")

    if args.limit and args.limit > 0:
        df = df.head(args.limit)

    colmap = {
        "id": args.col_id,
        "summary": args.col_summary,
        "description": args.col_description,
        "root_cause": args.col_root_cause,
        "resolution": args.col_resolution,
        "preventive": args.col_preventive,
    }

    ensure_cols(df, list(colmap.values()))

    client = OllamaClient(model=args.model, host=args.host)

    results: List[Dict[str, Any]] = []
    started = datetime.utcnow().isoformat() + "Z"

    for idx, r in df.iterrows():
        incident = row_to_obj(r, colmap)

        try:
            evaluation = evaluate_incident(client, incident)
            scores = evaluation.get("scores", {}) or {}
            results.append(
                {
                    "incident_id": incident["incident_id"],
                    "summary": incident["summary"],
                    "total": evaluation.get("total"),
                    "clarity": scores.get("clarity"),
                    "depth": scores.get("depth"),
                    "evidence": scores.get("evidence"),
                    "corrective": scores.get("corrective"),
                    "preventive": scores.get("preventive"),
                    "executive_summary": evaluation.get("executive_summary", ""),
                }
            )
            print(f"[OK] {incident['incident_id']} -> {evaluation.get('total')}")
        except Exception as e:
            print(f"[ERR] {incident['incident_id']}: {e}", file=sys.stderr)
            if args.fail_fast:
                raise
            results.append(
                {
                    "incident_id": incident["incident_id"],
                    "summary": incident["summary"],
                    "total": None,
                    "clarity": None,
                    "depth": None,
                    "evidence": None,
                    "corrective": None,
                    "preventive": None,
                    "executive_summary": f"ERROR: {e}",
                }
            )

    res_df = pd.DataFrame(results)
    results_csv = outdir / "results.csv"
    res_df.to_csv(results_csv, index=False)

    # Simple markdown report
    finished = datetime.utcnow().isoformat() + "Z"
    report_md = outdir / "report.md"

    valid = res_df[res_df["total"].notna()]
    avg = float(valid["total"].mean()) if len(valid) else 0.0
    p50 = float(valid["total"].median()) if len(valid) else 0.0
    top = valid.sort_values("total", ascending=False).head(5)
    bottom = valid.sort_values("total", ascending=True).head(5)

    def md_table(df_: pd.DataFrame) -> str:
        if df_.empty:
            return "_(no data)_"
        cols = ["incident_id", "total", "summary"]
        df2 = df_[cols].copy()
        return df2.to_markdown(index=False)

    report = f"""# RCA Batch Report

**Input:** `{in_path}`
**Model:** `{args.model}`
**Host:** `{args.host}`
**Rows processed:** {len(res_df)}
**Started (UTC):** {started}
**Finished (UTC):** {finished}

## Summary Metrics
- Average score: **{avg:.1f}**
- Median score (P50): **{p50:.1f}**

## Top 5 (Highest Scores)
{md_table(top)}

## Bottom 5 (Lowest Scores)
{md_table(bottom)}

## Output Files
- Results CSV: `{results_csv}`
- This report: `{report_md}`
"""
    report_md.write_text(report, encoding="utf-8")

    print(f"\nWrote: {results_csv}")
    print(f"Wrote: {report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
