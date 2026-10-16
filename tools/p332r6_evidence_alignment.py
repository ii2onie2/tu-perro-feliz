#!/usr/bin/env python3
"""P3.32R6: fail-closed alignment of authored items with approved evidence.
Offline only; never generates or publishes content.
"""
import argparse
import json
from pathlib import Path

def fail(code):
    print("BLOCKED_" + code)
    return 1

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--draft", required=True)
    p.add_argument("--dossiers", required=True)
    a = p.parse_args()
    try:
        draft = json.loads(Path(a.draft).read_text(encoding="utf-8"))
        evidence = json.loads(Path(a.dossiers).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return fail("INVALID_INPUT")
    items = draft.get("items")
    dossiers = evidence.get("dossiers")
    if not isinstance(items, list) or not isinstance(dossiers, list) or len(items) != 3 or len(dossiers) != 3:
        return fail("THREE_ITEMS_REQUIRED")
    if not isinstance(draft.get("date"), str) or draft["date"] != evidence.get("date"):
        return fail("DATE_MISMATCH")
    for i, (item, dossier) in enumerate(zip(items, dossiers)):
        if not isinstance(item, dict) or not isinstance(dossier, dict):
            return fail("INVALID_ENTRY")
        if item.get("date") != dossier.get("date") or item.get("slot") != dossier.get("slot"):
            return fail("SLOT_DATE_MISMATCH")
        topic = dossier.get("topic")
        if not isinstance(topic, str) or not topic.strip():
            return fail("MISSING_TOPIC")
        if item.get("evidence_topic") != topic:
            return fail("TOPIC_MISMATCH")
        if dossier.get("evidence_review_approved") is not True or dossier.get("publication_approved") is not False:
            return fail("EVIDENCE_NOT_APPROVED")
        evidence_urls = {s.get("url") for s in dossier.get("sources", []) if isinstance(s, dict)}
        item_sources = item.get("sources")
        if not isinstance(item_sources, list) or not item_sources:
            return fail("MISSING_DRAFT_SOURCES")
        for source in item_sources:
            if not isinstance(source, dict) or source.get("url") not in evidence_urls:
                return fail("UNMATCHED_SOURCE")
    print("P332R6_ALIGNMENT=PASS")
    print("NOTE=STRUCTURAL_ONLY_NOT_FACT_CHECKING")
    print("CONTENT_WRITES=0 MODEL_CALLS=0 PUBLICATIONS=0")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
