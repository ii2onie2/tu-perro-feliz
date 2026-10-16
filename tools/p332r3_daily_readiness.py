#!/usr/bin/env python3
"""P3.32R3 read-only daily readiness inventory. No model, network, rendering or publication."""
import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

SUFFIXES = {
    "history": ("", "-detalle", "-sabias"),
    "dogs": ("", "-educacion", "-sabias"),
}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--brand", choices=SUFFIXES, required=True)
    p.add_argument("--repo-dir", required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--report", required=True)
    a = p.parse_args()
    root = pathlib.Path(a.repo_dir).resolve()
    report = pathlib.Path(a.report).resolve()
    if report == root or root in report.parents:
        print("BLOCKED_REPORT_INSIDE_REPOSITORY")
        return 2
    try:
        day = dt.date.fromisoformat(a.date).isoformat()
    except ValueError:
        print("BLOCKED_INVALID_DATE")
        return 2
    content = [root / "content" / (day + suffix + ".json") for suffix in SUFFIXES[a.brand]]
    dossier = root / "evidence" / "approved" / (day + "-three-dossiers.json")
    draft = root / "evidence" / "approved" / (day + "-gemini-draft.json")
    files = [{"path": str(path.relative_to(root)), "exists": path.is_file()} for path in [*content, dossier, draft]]
    preflight = root / "scripts" / "p3_2_daily_preflight.py"
    preflight_status = "BLOCKED_MISSING_PREFLIGHT"
    if preflight.is_file() and all(path.is_file() for path in content):
        try:
            proc = subprocess.run(
                [sys.executable, "-B", str(preflight), "--date", day, "--content-dir", str(root / "content")],
                cwd=str(root), capture_output=True, text=True, timeout=20, check=False,
            )
            preflight_status = "PASS" if proc.returncode == 0 else "BLOCKED_INVALID_CONTENT"
        except (OSError, subprocess.TimeoutExpired):
            preflight_status = "BLOCKED_PREFLIGHT_ERROR"
    elif preflight.is_file():
        preflight_status = "BLOCKED_MISSING_CONTENT"
    result = {
        "phase": "P3.32R3", "brand": a.brand, "date": day,
        "mode": "READ_ONLY", "files": files, "content_preflight": preflight_status,
        "result": "PASS" if all(path.is_file() for path in [*content, dossier]) and preflight_status == "PASS" else "BLOCKED",
        "model_calls": 0, "network_calls": 0, "publications": 0, "github_writes": 0,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"P332R3_RESULT={result['result']} BRAND={a.brand} DATE={day} PREFLIGHT={preflight_status} REPORT={report}")
    return 0 if result["result"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
