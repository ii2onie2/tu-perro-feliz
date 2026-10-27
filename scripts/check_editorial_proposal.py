#!/usr/bin/env python3
"""Read-only schema preflight for unapproved editorial proposals."""
import argparse
import datetime
import json
from pathlib import Path
from urllib.parse import urlparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    data = json.loads(args.file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object")
    date = datetime.date.fromisoformat(data["date"]).isoformat()
    if args.file.name != date + ".json":
        raise ValueError("Date does not match filename")
    required = ("series", "title", "slot", "hook", "narration", "caption", "hashtags", "sources", "media", "cta")
    if any(not data.get(k) for k in required):
        raise ValueError("Missing editorial field")
    sources = data["sources"]
    if not isinstance(sources, list) or not all(isinstance(x, dict) and x.get("name") and urlparse(x.get("url", "")).scheme == "https" and urlparse(x["url"]).hostname for x in sources):
        raise ValueError("Invalid source metadata")
    media = data["media"]
    if not isinstance(media, list) or not all(isinstance(x, dict) and x.get("commons_title") and x.get("license_note") for x in media):
        raise ValueError("Invalid media metadata")
    if (Path("content") / args.file.name).exists() or (Path("editorial/approved") / args.file.name).exists():
        raise ValueError("Date already used")
    print("PROPOSAL_PREFLIGHT=PASS")
    print("FACT_CHECK=NOT_PERFORMED")
    print("MEDIA_LICENSE_CHECK=NOT_PERFORMED")
    print("PROMOTION=NONE; PUBLICATION=NONE")

if __name__ == "__main__":
    main()
