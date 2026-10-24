#!/usr/bin/env python3
"""P3.16 Metricool payload dry-run. No network calls or scheduling."""
import argparse
import json
import pathlib
import sys
from metricool_transfer_preflight import check

def build(manifest, scheduled_snapshot):
    gate = check(manifest, scheduled_snapshot)
    if gate["status"] != "PREFLIGHT_PASS_NO_TRANSFER":
        return {"status": "BLOCKED", "errors": gate["errors"], "network_calls": 0, "posts_created": 0}
    # Never embed credentials, and never send a request.
    info = {
        "providers": [{"network": "tiktok"}],
        "media": [manifest["video_url"]],
        "text": manifest["caption"],
        "autoPublish": False,
        "draft": True,
        "tiktokData": {
            "title": manifest["caption"][:90],
            "privacyOption": "SELF_ONLY",
            "disableComment": True,
            "disableDuet": True,
            "disableStitch": True,
            "isAigc": True,
        },
        "publicationDate": {
            "dateTime": manifest["editorial_date"] + "T" + manifest["slot"] + ":00",
            "timezone": "Europe/Paris",
        },
    }
    return {
        "status": "DRY_RUN_READY_NOT_SENT",
        "brand_id": "7173924",
        "account": "tuperrofelizofficial",
        "idempotency_key": gate["idempotency_key"],
        "payload": info,
        "network_calls": 0,
        "posts_created": 0,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--planned", required=True)
    a = p.parse_args()
    try:
        manifest = json.loads(pathlib.Path(a.manifest).read_text(encoding="utf-8"))
        planned = json.loads(pathlib.Path(a.planned).read_text(encoding="utf-8"))
        result = build(manifest, planned)
    except (OSError, ValueError, KeyError, TypeError) as e:
        result = {"status": "BLOCKED", "errors": [str(e)], "network_calls": 0, "posts_created": 0}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "DRY_RUN_READY_NOT_SENT" else 2

if __name__ == "__main__":
    sys.exit(main())
