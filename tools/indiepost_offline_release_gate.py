#!/usr/bin/env python3
"""Offline, fail-closed preflight for Gemini -> media -> IndiePost. No network, no writes."""
import argparse, datetime as dt, hashlib, json, pathlib, re
from zoneinfo import ZoneInfo

def validate(data, brand, slot, date):
    issues=[]
    expected="Tal Día Como Hoy" if brand=="history" else "Tu Perro Feliz"
    if data.get("series")!=expected: issues.append("BRAND_MISMATCH")
    if data.get("date")!=date: issues.append("DATE_MISMATCH")
    if data.get("publication_approved") is not True: issues.append("PUBLICATION_NOT_APPROVED")
    if data.get("media_license_approved") is not True: issues.append("MEDIA_RIGHTS_NOT_APPROVED")
    if data.get("status")!="PUBLISH_APPROVED": issues.append("NOT_PUBLISH_APPROVED")
    if len(data.get("media", []))<1: issues.append("NO_CLEARED_MEDIA")
    if len(data.get("sources",[]))<2: issues.append("INSUFFICIENT_SOURCES")
    if not data.get("narration","").strip(): issues.append("NO_NARRATION")
    words=len(re.findall(r"\b\w+\b",data.get("narration","")))
    low,high=(180,240) if brand=="history" else (100,150)
    if not low<=words<=high: issues.append("WORDS_OUT_OF_RANGE")
    if slot not in (10,16,19): issues.append("INVALID_SLOT")
    try:
        moment=dt.datetime.combine(dt.date.fromisoformat(date),dt.time(slot,0),tzinfo=ZoneInfo("Europe/Madrid"))
        when_utc=moment.astimezone(dt.timezone.utc).isoformat().replace("+00:00","Z")
    except ValueError: issues.append("INVALID_DATE"); when_utc=""
    # Stable across retries; never log secrets, never post.
    identity=f"{brand}|{date}|{slot}|{hashlib.sha256(data.get('narration','').encode()).hexdigest()}"
    token=hashlib.sha256(identity.encode()).hexdigest()[:24]
    return issues,when_utc,token

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--content",required=True)
    ap.add_argument("--brand",choices=("history","dogs"),required=True)
    ap.add_argument("--slot",type=int,default=10)
    ap.add_argument("--date",required=True)
    args=ap.parse_args()
    data=json.loads(pathlib.Path(args.content).read_text(encoding="utf-8"))
    issues,utc,key=validate(data,args.brand,args.slot,args.date)
    print("MODE=OFFLINE_READ_ONLY")
    print("TARGET_UTC="+utc)
    print("DUPLICATE_KEY="+key)
    print("LIVE_PUBLISH=NO")
    print("INDIEPOST_API_WRITE=NO")
    print("RESULT="+("BLOCKED" if issues else "READY_FOR_SEPARATE_PROVIDER_CONTRACT_REVIEW"))
    for issue in issues: print("GATE="+issue)
    if not issues: print("NOTE=No account or provider schedule check has been performed")
if __name__=="__main__":main()
