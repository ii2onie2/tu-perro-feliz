#!/usr/bin/env python3
"""Single-scenario Gemini draft pilot. No publication, no repository writes.
Requires GEMINI_API_KEY and a curated, manually verified evidence JSON.
Evidence format: {"topic":"...", "sources":[{"name":"...", "url":"https://...", "facts":["..."]}]}
Output is a GitHub Actions artifact only, with draft status.
"""
import argparse
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--evidence", required=True)
    p.add_argument("--brand", required=True, choices=["history", "dogs"])
    p.add_argument("--date", required=True)
    p.add_argument("--output", default="draft_scenario.json")
    args = p.parse_args()
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise SystemExit("BLOCKED_NO_API_KEY")
    evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    sources = evidence.get("sources", [])
    if not evidence.get("topic") or not sources:
        raise SystemExit("BLOCKED_NO_EVIDENCE")
    for source in sources:
        if not source.get("name") or not str(source.get("url", "")).startswith("https://") or not source.get("facts"):
            raise SystemExit("BLOCKED_INCOMPLETE_EVIDENCE")
    guide = (
        "Historical event linked to Spain. Historical accuracy and event date must match; "
        "never claim anniversary if source facts do not support it."
        if args.brand == "history" else
        "Safe, practical canine welfare topic. No diagnosis or unsupported veterinary advice."
    )
    instructions = (
        "Write ONE Spanish TikTok narration draft, 180-240 words for history or "
        "100-150 words for dogs, using ONLY the supplied verified facts. "
        "Do not browse, invent facts, citations or media licenses. "
        "Return JSON object with title, hook, narration, caption, cta, "
        "hashtags (array), sources (exactly supplied sources), review_required=true. "
        "No publish-ready status. Context: " + guide +
        "\nDate: " + args.date + "\nEvidence:\n" +
        json.dumps(evidence, ensure_ascii=False)
    )
    body = {
        "contents": [{"parts": [{"text": instructions}]}],
        "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"},
    }
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent",
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        data=json.dumps(body).encode("utf-8"), method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        print("GEMINI_HTTP_STATUS=" + str(exc.code))
        raise SystemExit("BLOCKED_GEMINI_REQUEST")
    parts = payload.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    raw = "".join(part.get("text", "") for part in parts)
    draft = json.loads(raw)
    if not all(draft.get(k) for k in ("title", "hook", "narration", "caption", "cta", "hashtags")):
        raise SystemExit("BLOCKED_INVALID_DRAFT")
    draft["sources"] = sources
    draft["review_required"] = True
    draft["status"] = "UNVERIFIED_DRAFT"
    draft["brand"] = args.brand
    draft["date"] = args.date
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("RESULT=DRAFT_CREATED_REVIEW_REQUIRED")
    print("PUBLICATION_ENABLED=NO")

if __name__ == "__main__":
    main()
