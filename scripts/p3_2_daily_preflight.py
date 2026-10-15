#!/usr/bin/env python3
"""Fail-closed, offline P3.2 daily input preflight. Does not write files."""
import argparse
import datetime as dt
import json
from pathlib import Path

SUFFIXES = ["","-educacion","-sabias"]
SLOTS = ["10:00", "16:00", "19:00"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="ISO local calendar date")
    parser.add_argument("--content-dir", default="content")
    args = parser.parse_args()
    try:
        date = dt.date.fromisoformat(args.date)
    except ValueError:
        parser.error("invalid --date")
    folder = Path(args.content_dir)
    missing = []
    invalid = []
    for suffix, slot in zip(SUFFIXES, SLOTS):
        path = folder / (date.isoformat() + suffix + ".json")
        if not path.is_file():
            missing.append(path.as_posix())
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("date") != date.isoformat() or data.get("slot") != slot:
                invalid.append(path.as_posix() + ": wrong date/slot")
            for field in ("series", "title", "hook", "narration", "sources", "media"):
                if not data.get(field):
                    invalid.append(path.as_posix() + ": missing " + field)
        except (ValueError, OSError) as exc:
            invalid.append(path.as_posix() + ": " + type(exc).__name__)
    print("MODE=OFFLINE_READ_ONLY")
    print("DATE=" + date.isoformat())
    print("SLOTS_EXPECTED=3")
    print("MISSING_COUNT=" + str(len(missing)))
    print("INVALID_COUNT=" + str(len(invalid)))
    for item in missing:
        print("MISSING=" + item)
    for item in invalid:
        print("INVALID=" + item)
    ok = not missing and not invalid
    print("RESULT=" + ("PASS_INPUTS_EXIST" if ok else "BLOCKED_INPUTS"))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
