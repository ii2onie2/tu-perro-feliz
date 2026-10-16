#!/usr/bin/env python3
"""Validate three independent evidence dossiers without calling an AI or publishing."""
import argparse
import datetime as dt
import json
from pathlib import Path

def fail(reason):
    raise SystemExit("BLOCKED_" + reason)

def normalized_org(s):
    value=str(s.get("organization") or s.get("name") or "").strip().lower()
    if not value: fail("MISSING_SOURCE_ORG")
    aliases={"boe":"boe","unesco":"unesco","akc":"akc","american kennel":"akc","vca":"vca"}
    for token,org in aliases.items():
        if token in value:return org
    return value

def validate(doc,brand):
    date=dt.date.fromisoformat(doc["date"]).isoformat()
    dossiers=doc.get("dossiers")
    if not isinstance(dossiers,list) or len(dossiers)!=3:fail("THREE_DOSSIERS_REQUIRED")
    topics=set()
    for i,d in enumerate(dossiers):
        if d.get("slot")!=["10:00","16:00","19:00"][i]:fail("WRONG_SLOT")
        if d.get("date")!=date:fail("WRONG_DATE")
        topic=str(d.get("topic") or "").strip()
        if not topic or topic.casefold() in topics:fail("DUPLICATE_OR_EMPTY_TOPIC")
        topics.add(topic.casefold())
        sources=d.get("sources")
        if not isinstance(sources,list) or len(sources)<2:fail("INSUFFICIENT_SOURCES")
        orgs=set()
        for s in sources:
            if not isinstance(s,dict) or not str(s.get("url","")).startswith("https://") or not isinstance(s.get("facts"),list) or not s["facts"]:fail("INVALID_SOURCE")
            orgs.add(normalized_org(s))
        if len(orgs)<2:fail("SAME_ORGANIZATION")
        if d.get("evidence_review_approved") is not True:fail("EVIDENCE_NOT_APPROVED")
        if d.get("publication_approved") is not False:fail("PUBLICATION_MUST_BE_DISABLED")
    print("THREE_DOSSIERS=PASS")
    print("INDEPENDENT_SOURCE_ORGANIZATIONS=PASS")
    print("NO_REPEATED_TOPICS=PASS")
    print("MODEL_CALL=NO")
    print("PUBLICATION=NO")
    print("RESULT=PASS_EDITORIAL_EVIDENCE_GATE")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--brand",choices=["history","dogs"],required=True)
    a=p.parse_args()
    validate(json.loads(Path(a.input).read_text(encoding="utf-8")),a.brand)
if __name__=="__main__":main()
