#!/usr/bin/env python3
"""Offline gate for manually downloaded Google Flow visual assets."""
import argparse
import hashlib
import json
from pathlib import Path

def validate(asset: Path, manifest: Path) -> dict:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("source_tool") != "Google Flow / Nano Banana 2.1":
        raise ValueError("unexpected source tool")
    if data.get("rights_review") != "PASS":
        raise ValueError("rights review not approved")
    if data.get("visual_review") != "PASS":
        raise ValueError("visual review not approved")
    if data.get("asset_status") != "IMPORTED":
        raise ValueError("asset not imported")
    if asset.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise ValueError("unsupported image format")
    if not asset.is_file() or asset.stat().st_size == 0:
        raise ValueError("image missing or empty")
    actual = hashlib.sha256(asset.read_bytes()).hexdigest()
    if actual != data.get("sha256"):
        raise ValueError("SHA256 mismatch")
    return {"status": "PASS", "sha256": actual, "bytes": asset.stat().st_size}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--asset", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(validate(args.asset, args.manifest)))
