#!/usr/bin/env python3
"""Build auditable, unapproved research packets. Never manufacture evidence."""
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
    sources = {}
    provider_stats = {}
    for provider in candidates.get("providers", []):
        items = provider.get("items", [])
        provider_stats[provider.get("name", "unknown")] = {"status": provider.get("status"), "items": len(items)}
        for item in items:
            url = item.get("url", "")
            if isinstance(url, str) and url.startswith("https://") and urlparse(url).hostname:
                sources[url] = {"url": url, "title": str(item.get("title") or "")[:240],
                                "organization": urlparse(url).hostname, "facts": [],
                                "source_verified": False}
    dossiers, seen, rejections = [], set(), []
    ideas = model.get("ideas", [])
    if not isinstance(ideas, list):
        raise ValueError("INVALID_IDEAS")
    for index, idea in enumerate(ideas):
        if len(dossiers) >= 3:
            break
        if not isinstance(idea, dict):
            rejections.append({"index": index, "reason": "INVALID_IDEA"})
            continue
        topic = str(idea.get("title") or "").strip()
        url = str(idea.get("source_url") or "")
        if not topic:
            reason = "EMPTY_TOPIC"
        elif topic.casefold() in seen:
            reason = "DUPLICATE_TOPIC"
        elif url not in sources:
            reason = "SOURCE_URL_NOT_IN_COLLECTED_CANDIDATES"
        else:
            reason = None
        if reason:
            rejections.append({"index": index, "reason": reason})
            continue
        seen.add(topic.casefold())
        dossiers.append({"slot": SLOTS[len(dossiers)], "date": day, "topic": topic,
                         "sources": [sources[url]], "verification_needed": True,
                         "evidence_review_approved": False, "publication_approved": False,
                         "missing": ["second_independent_source", "verified_facts", "editorial_approval"]})
    return {"date": day, "brand": brand, "status": "RESEARCH_DRAFT_NOT_APPROVED",
            "model_status": model.get("status"), "provider_stats": provider_stats,
            "model_idea_count": len(ideas), "rejections": rejections,
            "evidence_review_approved": False, "publication_approved": False,
            "dossiers": dossiers, "ready_for_evidence_gate": False,
            "missing_slots": list(SLOTS[len(dossiers):])}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", default="out/editorial-discovery")
    args = p.parse_args()
    folder = Path(args.input_dir)
    candidates = json.loads((folder / "candidates.json").read_text(encoding="utf-8"))
    model = json.loads((folder / "gemini-ideas.json").read_text(encoding="utf-8"))
    result = build(candidates, model)
    (folder / "editorial-research-dossiers.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("MODEL_IDEAS=" + str(result["model_idea_count"]))
    print("RESEARCH_DOSSIERS=" + str(len(result["dossiers"])))
    print("REJECTED_IDEAS=" + str(len(result["rejections"])))
    for item in result["rejections"]:
        print("REJECTED_IDEA=" + str(item["index"]) + ":" + item["reason"])
    for name, stat in result["provider_stats"].items():
        print("SOURCE_PROVIDER=" + name + ":" + str(stat["status"]) + ":" + str(stat["items"]))
    print("EDITORIAL_APPROVAL=NO PUBLICATION=NO")
    if not result["dossiers"]:
        raise SystemExit("BLOCKED_ZERO_RESEARCH_DOSSIERS")
    print("RESEARCH_PACKET=GENERATED_NOT_APPROVED")

if __name__ == "__main__":
    main()
