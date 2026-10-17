#!/usr/bin/env python3
"""Build unapproved editorial evidence research packets from source candidates."""
import argparse
import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlparse

SLOTS = ("10:00", "16:00", "19:00")

def build(candidates, model):
    day = dt.date.fromisoformat(candidates["date"]).isoformat()
    brand = candidates["brand"]
    if brand not in ("history", "dogs") or model.get("brand") != brand or model.get("date") != day:
        raise ValueError("MISMATCHED_BRAND_OR_DATE")
    providers = candidates.get("providers", [])
    sources = {}
    for provider in providers:
        for item in provider.get("items", []):
            url = item.get("url", "")
            if isinstance(url, str) and url.startswith("https://") and urlparse(url).hostname:
                sources[url] = {"url": url, "title": str(item.get("title", ""))[:240],
                                "organization": urlparse(url).hostname, "facts": [],
                                "source_verified": False}
    dossiers = []
    seen = set()
    for idea in model.get("ideas", []):
        if len(dossiers) >= 3:
            break
        topic = str(idea.get("title", "")).strip()
        url = str(idea.get("source_url", ""))
        if not topic or topic.casefold() in seen or url not in sources:
            continue
        seen.add(topic.casefold())
        dossiers.append({"slot": SLOTS[len(dossiers)], "date": day, "topic": topic,
                         "sources": [sources[url]], "verification_needed": True,
                         "evidence_review_approved": False, "publication_approved": False,
                         "missing": ["second_independent_source", "verified_facts", "editorial_approval"]})
    return {"date": day, "brand": brand, "status": "RESEARCH_DRAFT_NOT_APPROVED",
            "evidence_review_approved": False, "publication_approved": False,
            "dossiers": dossiers, "ready_for_evidence_gate": False,
            "missing_slots": list(SLOTS[len(dossiers):])}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="out/editorial-discovery")
    args = parser.parse_args()
    folder = Path(args.input_dir)
    candidates = json.loads((folder / "candidates.json").read_text(encoding="utf-8"))
    model = json.loads((folder / "gemini-ideas.json").read_text(encoding="utf-8"))
    result = build(candidates, model)
    target = folder / "editorial-research-dossiers.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("RESEARCH_DOSSIERS=" + str(len(result["dossiers"])))
    print("EDITORIAL_APPROVAL=NO PUBLICATION=NO")
    print("RESEARCH_PACKET=GENERATED_NOT_APPROVED")

if __name__ == "__main__":
    main()
