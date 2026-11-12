#!/usr/bin/env python3
"""Validate research-only secondary drafts; never approve, render or publish."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

SLOTS = {"educacion": ("Buenos modales", "16:00"), "sabias": ("¿Sabías esto de tu perro?", "19:00")}
FILE_RE = re.compile(r"^(20[0-9]{2}-[0-9]{2}-[0-9]{2})-(educacion|sabias)\.json$")

def check(path: Path):
    m = FILE_RE.fullmatch(path.name)
    if not m or path.parent.as_posix() != "editorial/research":
        raise ValueError(f"Invalid research-only path: {path}")
    date, slot_type = m.groups()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Expected an object")
    if data.get("date") != date or (data.get("series"), data.get("slot")) != SLOTS[slot_type]:
        raise ValueError("Date, series or slot mismatch")
    required = ("title", "hook", "narration", "caption", "hashtags", "sources", "media", "cta", "topic_family")
    if any(not data.get(k) for k in required):
        raise ValueError("Empty required field")
    if not 100 <= len(data["narration"].split()) <= 250:
        raise ValueError("Narration outside research draft length bounds")
    if data.get("editorial_status") != "RESEARCH_DRAFT_UNAPPROVED":
        raise ValueError("Proposal cannot claim editorial approval")
    if data.get("media_rights_status") != "NOT_VERIFIED":
        raise ValueError("Proposal cannot claim media clearance")
    for src in data["sources"]:
        if not isinstance(src, dict) or not isinstance(src.get("name"), str):
            raise ValueError("Missing source name")
        url = urlsplit(src.get("url", ""))
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError("Invalid research source URL")
    for item in data["media"]:
        if (not isinstance(item, dict)
                or item.get("asset_status") != "NOT_SELECTED"
                or item.get("license_note") != "RIGHTS_UNVERIFIED_NO_RENDER"
                or any(k in item for k in ("path", "commons_title", "source", "sha256", "flow_asset"))):
            raise ValueError("Research draft must not pretend to have selected or cleared media")
    history = json.loads(Path("content/published_history.json").read_text(encoding="utf-8"))
    existing = {str(x.get("topic_family", "")).casefold() for x in history if isinstance(x, dict)}
    if str(data["topic_family"]).casefold() in existing:
        raise ValueError("Repeated previously published topic_family")
    if (Path("content") / path.name).exists():
        raise ValueError("Target daily content file already exists; manual reconciliation required")
    print(f"DRAFT_SCHEMA_PASS={path} FACT_REVIEW=MANUAL MEDIA_RIGHTS=BLOCKED RENDER=NO")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("No files specified")
    for raw in sys.argv[1:]:
        check(Path(raw))
