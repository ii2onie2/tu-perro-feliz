#!/usr/bin/env python3
"""Offline audit: 14-day coverage, duplicate titles, and content quality.
READ ONLY, no API calls, no publication or repository changes.
Exit 0 for a completed audit; report BLOCKED gaps separately.
"""
import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo

SUFFIXES = {
    "history": ("", "-detalle", "-sabias"),
    "dogs": ("", "-educacion", "-sabias"),
}
SLOTS = ("10:00", "16:00", "19:00")
MIN_WORDS = {"history": 180, "dogs": 65}

def normalize(value):
    return re.sub(r"\s+", " ", str(value).casefold()).strip()

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--brand", choices=SUFFIXES, required=True)
    cli.add_argument("--content-dir", default="content")
    cli.add_argument("--days", type=int, default=14)
    cli.add_argument("--start-date")
    args = cli.parse_args()
    if not 1 <= args.days <= 31:
        cli.error("days must be 1..31")
    start = (dt.date.fromisoformat(args.start_date) if args.start_date
             else dt.datetime.now(ZoneInfo("Europe/Madrid")).date())
    root = Path(args.content_dir)
    issues, titles, bodies = [], set(), set()
    coverage = 0
    # Include existing JSON & history to detect repeats outside the forecast window.
    history = root / "published_history.json"
    historical_titles = set()
    if history.is_file():
        try:
            records = json.loads(history.read_text(encoding="utf-8"))
            historical_titles = {normalize(x.get("title", "")) for x in records
                                 if isinstance(x, dict) and x.get("title")}
        except (ValueError, OSError):
            issues.append("UNREADABLE_HISTORY")
    for offset in range(args.days):
        date = (start + dt.timedelta(days=offset)).isoformat()
        for suffix, slot in zip(SUFFIXES[args.brand], SLOTS):
            path = root / (date + suffix + ".json")
            if not path.is_file():
                issues.append("MISSING:" + str(path))
                continue
            try:
                item = json.loads(path.read_text(encoding="utf-8"))
                if item.get("date") != date or item.get("slot") != slot:
                    issues.append("DATE_SLOT_MISMATCH:" + str(path))
                    continue
                if not all(item.get(f) for f in (
                    "series", "title", "hook", "narration", "caption",
                    "cta", "hashtags", "sources", "media"
                )):
                    issues.append("MISSING_FIELDS:" + str(path))
                    continue
                if len(str(item["narration"]).split()) < MIN_WORDS[args.brand]:
                    issues.append("SHORT_NARRATION:" + str(path))
                    continue
                if not all(isinstance(s, dict) and s.get("name") and
                           str(s.get("url", "")).startswith("https://")
                           for s in item["sources"]):
                    issues.append("INVALID_SOURCES:" + str(path))
                    continue
                title = normalize(item["title"])
                digest = hashlib.sha256(normalize(item["narration"]).encode()).hexdigest()
                if title in titles or digest in bodies:
                    issues.append("DUPLICATE_IN_WINDOW:" + str(path))
                    continue
                # Historical log is not proof of actual TikTok publication; it is
                # nevertheless a strict replay guard for content.
                if title in historical_titles:
                    issues.append("REPLAY_RISK_HISTORY:" + str(path))
                    continue
                titles.add(title)
                bodies.add(digest)
                coverage += 1
            except (OSError, ValueError, TypeError):
                issues.append("INVALID_JSON:" + str(path))
    expected = args.days * len(SLOTS)
    print("MODE=READ_ONLY")
    print("BRAND=" + args.brand)
    print("START_DATE=" + start.isoformat())
    print("EXPECTED=" + str(expected))
    print("VALID=" + str(coverage))
    print("GAPS=" + str(len(issues)))
    for issue in issues:
        print("ISSUE=" + issue)
    print("RESULT=" + ("PASS_COVERAGE" if coverage == expected else "BLOCKED_COVERAGE"))
    print("PUBLISHING=DISABLED")

if __name__ == "__main__":
    main()
