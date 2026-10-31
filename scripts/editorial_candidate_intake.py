#!/usr/bin/env python3
"""Read-only, fail-closed editorial candidate intake. No automatic factual approval."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

SLOTS = {
    "tal-dia": ("", "-detalle", "-sabias"),
    "tu-perro": ("", "-educacion", "-sabias"),
}

def normalized(value):
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()

def validate(candidate, day, slot):
    if not isinstance(candidate, dict) or candidate.get("date") != day or candidate.get("slot") != slot:
        raise ValueError("candidate date or slot mismatch")
    title = candidate.get("title")
    if not isinstance(title, str) or len(title.strip()) < 12:
        raise ValueError("title missing or too short")
    if not isinstance(candidate.get("claims"), list) or not candidate["claims"]:
        raise ValueError("claims required")
    for claim in candidate["claims"]:
        if not isinstance(claim, dict) or not isinstance(claim.get("text"), str) or len(claim["text"].strip()) < 20:
            raise ValueError("invalid claim")
        citations = claim.get("evidence")
        if not isinstance(citations, list) or not citations:
            raise ValueError("claim has no evidence")
        for citation in citations:
            if not isinstance(citation, dict) or not citation.get("quote") or not citation.get("retrieved_at"):
                raise ValueError("missing source excerpt or retrieval date")
            url = citation.get("url")
            if not isinstance(url, str):
                raise ValueError("missing source URL")
            parsed = urlsplit(url)
            if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError("source URL must be HTTPS")
            dt.date.fromisoformat(citation["retrieved_at"])
    media = candidate.get("media")
    if not isinstance(media, list) or not media:
        raise ValueError("media candidate required")
    for asset in media:
        if not isinstance(asset, dict) or not asset.get("origin_url") or not asset.get("license") or not asset.get("author"):
            raise ValueError("media attribution incomplete")
        if urlsplit(asset["origin_url"]).scheme != "https":
            raise ValueError("media origin must be HTTPS")
    return normalized(title)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=SLOTS, required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--candidates", default="editorial/candidates")
    parser.add_argument("--history", default="content/published_history.json")
    args = parser.parse_args()
    day = dt.date.fromisoformat(args.date).isoformat()
    history_path = Path(args.history)
    history = history_path.read_text(encoding="utf-8") if history_path.exists() else ""
    seen = set()
    for suffix in SLOTS[args.profile]:
        path = Path(args.candidates) / (day + suffix + ".json")
        if not path.is_file():
            raise ValueError("missing candidate: " + str(path))
        candidate = json.loads(path.read_text(encoding="utf-8"))
        key = validate(candidate, day, suffix or "principal")
        fingerprint = hashlib.sha256(key.encode()).hexdigest()
        if key in seen or fingerprint in history or candidate["title"] in history:
            raise ValueError("duplicate candidate title: " + str(path))
        seen.add(key)
        print("CANDIDATE_SCHEMA=PASS", path, "TITLE_SHA256=" + fingerprint)
    print("CANDIDATE_INTAKE=PASS; FACTS_VERIFIED=NO; MEDIA_RIGHTS_VERIFIED=NO; EDITORIAL_APPROVED=NO; WRITES=0; PUBLICATION=NONE")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("CANDIDATE_INTAKE=BLOCKED", str(exc), file=sys.stderr)
        sys.exit(1)
