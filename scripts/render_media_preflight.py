#!/usr/bin/env python3
"""Fail-closed preflight for *rendering*, not copyright/publication clearance.

Prevents unresolved research placeholders from becoming black-background videos.
Commons assets still require the downstream live license/integrity gate.
Local assets require a verified file checksum and documented rights review.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

BLOCKED_STATUS = {"RESEARCH_DRAFT_UNAPPROVED", "NOT_VERIFIED", "PENDING", "NOT_SELECTED"}
BAD_NOTES = ("PENDING", "UNVERIFIED", "NO_RENDER", "NOT_SELECTED", "PLACEHOLDER", "FORBIDDEN")
SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")


def reject(reason):
    raise ValueError(f"RENDER_PREFLIGHT_BLOCKED: {reason}")


def check(filename, root=None):
    root = (Path(root) if root else Path.cwd()).resolve()
    path = Path(filename)
    data = json.loads((root / path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        reject("content is not a JSON object")
    required_approvals = {"editorial_status": "APPROVED", "media_rights_status": "VERIFIED", "publishing_status": "READY"}
    for key, expected in required_approvals.items():
        value = data.get(key)
        if not isinstance(value, str) or value.strip().upper() != expected:
            reject(f"approval not proven {key}: expected {expected}")
    media = data.get("media")
    if not isinstance(media, list) or not media:
        reject("no declared visual asset")
    for index, item in enumerate(media, 1):
        if not isinstance(item, dict):
            reject(f"media {index}: not an object")
        for key in ("asset_status", "license_note", "rights_review"):
            value = item.get(key)
            if isinstance(value, str) and (value.upper() in BLOCKED_STATUS or
                                           any(token in value.upper() for token in BAD_NOTES)):
                reject(f"media {index}: unresolved {key}")
        if "commons_title" in item:
            title = item["commons_title"]
            if not isinstance(title, str) or not title.startswith("File:") or len(title[5:].strip()) < 5:
                reject(f"media {index}: invalid Commons title")
            # This only validates the reference shape. audit_commons_licenses.py
            # validates live Commons license metadata after download.
            continue
        if "path" in item:
            rel = item.get("path")
            digest = item.get("sha256")
            if item.get("rights_review") != "PASS" or item.get("visual_review") != "PASS":
                reject(f"media {index}: local asset reviews not approved")
            if not isinstance(rel, str) or not rel.startswith("media/"):
                reject(f"media {index}: local asset must be inside media/")
            target = (root / rel).resolve()
            if not target.is_relative_to(root / "media") or not target.is_file() or not target.stat().st_size:
                reject(f"media {index}: local asset missing or escapes media/")
            if not isinstance(digest, str) or not SHA256.fullmatch(digest):
                reject(f"media {index}: missing SHA256")
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest.lower():
                reject(f"media {index}: SHA256 mismatch")
            continue
        reject(f"media {index}: unresolved non-Commons asset (including Flow)")
    print(f"RENDER_PREFLIGHT=PASS_INPUT_ONLY FILE={filename} RIGHTS_CLEARANCE=NOT_GRANTED")


def main():
    if len(sys.argv) < 2:
        reject("no content files")
    for name in sys.argv[1:]:
        check(name)


if __name__ == "__main__":
    main()
