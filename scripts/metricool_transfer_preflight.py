#!/usr/bin/env python3
"""P3.15 offline-only Metricool transfer preflight. Never sends network requests."""
import argparse
import hashlib
import json
import pathlib
import re
import sys
from urllib.parse import urlparse

BRAND = "7173924"
ACCOUNT = "tuperrofelizofficial"

def check(manifest, planned):
    errors = []
    if str(manifest.get("brand_id")) != BRAND or manifest.get("account") != ACCOUNT:
        errors.append("wrong Metricool brand/account")
    day, slot = manifest.get("editorial_date", ""), manifest.get("slot", "")
    if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", day) or not re.fullmatch(r"\d{2}:\d{2}", slot):
        errors.append("invalid date/slot")
    url = manifest.get("video_url", "")
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        errors.append("video must have a public HTTPS URL")
    if any(x in parsed.netloc.lower() for x in ("github.com", "githubusercontent.com", "api.github.com")):
        errors.append("GitHub URLs are not assumed to be publicly downloadable media")
    digest = manifest.get("video_sha256", "")
    if not re.fullmatch(r"[a-f0-9]{64}", digest):
        errors.append("missing video SHA256")
    if not manifest.get("caption") or not manifest.get("sources") or not manifest.get("credits"):
        errors.append("caption, sources and credits required")
    key = hashlib.sha256(f"{BRAND}|{ACCOUNT}|{day}|{slot}|{digest}".encode()).hexdigest()
    if not isinstance(planned, list):
        errors.append("planned-post snapshot missing")
    else:
        for post in planned:
            if post.get("idempotency_key") == key or (
                post.get("editorial_date") == day and post.get("slot") == slot
            ):
                errors.append("duplicate planned slot or content")
                break
    return {"status": "BLOCKED" if errors else "PREFLIGHT_PASS_NO_TRANSFER", "idempotency_key": key, "errors": errors, "network_calls": 0, "posts_created": 0}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--planned", required=True)
    args = ap.parse_args()
    try:
        manifest = json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8"))
        planned = json.loads(pathlib.Path(args.planned).read_text(encoding="utf-8"))
        result = check(manifest, planned)
    except (OSError, ValueError, TypeError) as exc:
        result = {"status": "BLOCKED", "errors": [str(exc)], "network_calls": 0, "posts_created": 0}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PREFLIGHT_PASS_NO_TRANSFER" else 2

if __name__ == "__main__":
    sys.exit(main())
