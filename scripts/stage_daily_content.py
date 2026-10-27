#!/usr/bin/env python3
"""Materialize a pre-reviewed daily editorial JSON; never invent facts or sources."""
import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True)
    p.add_argument("--queue", default="editorial/approved")
    p.add_argument("--output", default="content")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    day = dt.date.fromisoformat(args.date).isoformat()
    source = pathlib.Path(args.queue) / (day + ".json")
    target = pathlib.Path(args.output) / (day + ".json")
    if not source.is_file():
        print("STATUS=BLOCKED_NO_APPROVED_EDITORIAL_INPUT", file=sys.stderr)
        return 2
    if target.exists():
        print("STATUS=BLOCKED_TARGET_ALREADY_EXISTS", file=sys.stderr)
        return 3
    raw = source.read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("date") != day:
        print("STATUS=BLOCKED_DATE_OR_SCHEMA", file=sys.stderr)
        return 4
    if not isinstance(data.get("sources"), list) or not data["sources"]:
        print("STATUS=BLOCKED_NO_SOURCES", file=sys.stderr)
        return 5
    if not isinstance(data.get("media"), list) or not data["media"]:
        print("STATUS=BLOCKED_NO_MEDIA", file=sys.stderr)
        return 6
    if args.dry_run:
        print("STATUS=DRY_RUN_READY; NO_WRITES=YES")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    try:
        subprocess.run([sys.executable, "scripts/validate_content.py", str(target)], check=True)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    print("STATUS=STAGED_AND_VALIDATED; PUBLICATION=NONE")
    return 0

if __name__ == "__main__":
    sys.exit(main())
