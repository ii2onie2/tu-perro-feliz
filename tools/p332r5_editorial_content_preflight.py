#!/usr/bin/env python3
"""P3.32R5 offline editorial-to-content preflight. Never writes content or publishes."""
import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--brand",required=True,choices=("history","dogs"))
    p.add_argument("--repo-dir",required=True)
    p.add_argument("--date",required=True)
    p.add_argument("--draft",required=True)
    p.add_argument("--dossiers",required=True)
    a=p.parse_args()
    root=pathlib.Path(a.repo_dir).resolve()
    try: day=dt.date.fromisoformat(a.date).isoformat()
    except ValueError: print("BLOCKED_INVALID_DATE");return 2
    draft=pathlib.Path(a.draft).resolve()
    dossiers=pathlib.Path(a.dossiers).resolve()
    expected_dossiers=root/"evidence"/"approved"/(day+"-three-dossiers.json")
    if dossiers!=expected_dossiers:
        print("BLOCKED_UNEXPECTED_DOSSIER_PATH");return 2
    if not draft.is_file() or not dossiers.is_file():
        print("BLOCKED_MISSING_APPROVED_INPUTS");return 1
    try:
        document=json.loads(draft.read_text(encoding="utf-8"))
        evidence=json.loads(dossiers.read_text(encoding="utf-8"))
    except (OSError,ValueError):
        print("BLOCKED_INVALID_INPUT_JSON");return 1
    if document.get("date")!=day or evidence.get("date")!=day:
        print("BLOCKED_DATE_MISMATCH");return 1
    if evidence.get("publication_approved") is True:
        print("BLOCKED_PUBLICATION_ENABLED");return 1
    gate=root/"tools"/"daily_editorial_evidence_gate.py"
    generator=root/"scripts"/"p3_2_prepare_daily_content.py"
    if not gate.is_file() or not generator.is_file():
        print("BLOCKED_MISSING_VALIDATORS");return 1
    steps=[
        ("DOSSIER_GATE",[sys.executable,"-B",str(gate),"--input",str(dossiers),"--brand",a.brand]),
        ("GENERATOR_DRY_RUN",[sys.executable,"-B",str(generator),"--input",str(draft),"--content-dir",str(root/"content")]),
    ]
    for label,command in steps:
        try:
            r=subprocess.run(command,cwd=str(root),capture_output=True,text=True,timeout=30,check=False)
        except (OSError,subprocess.TimeoutExpired):
            print("BLOCKED_"+label+"_EXECUTION");return 1
        if r.returncode!=0:
            print("BLOCKED_"+label)
            print((r.stdout+"\n"+r.stderr).strip()[:1500])
            return 1
        print(label+"=PASS")
    print("P332R5_RESULT=PASS_DRY_RUN_ONLY")
    print("CONTENT_WRITES=0 MODEL_CALLS=0 PUBLICATIONS=0")
    return 0

if __name__=="__main__":sys.exit(main())
