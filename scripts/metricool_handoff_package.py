#!/usr/bin/env python3
"""P3.17 prepare a verifiable MP4 handoff, without uploading or scheduling."""
import argparse
import hashlib
import json
import pathlib
import re
import sys

def prepare(video, caption, sources, credits, day, slot, public_url=None):
    errors = []
    if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", day):
        errors.append("invalid editorial date")
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", slot):
        errors.append("invalid slot")
    for label, path in (("video",video),("caption",caption),("sources",sources),("credits",credits)):
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty {label}")
    if errors:
        return {"status":"BLOCKED","errors":errors,"uploaded":False,"scheduled":False}
    if video.suffix.lower() != ".mp4":
        return {"status":"BLOCKED","errors":["video is not MP4"],"uploaded":False,"scheduled":False}
    try:
        source_data=json.loads(sources.read_text(encoding="utf-8"))
        credit_data=json.loads(credits.read_text(encoding="utf-8"))
        caption_text=caption.read_text(encoding="utf-8").strip()
    except (ValueError,UnicodeError,OSError) as exc:
        return {"status":"BLOCKED","errors":[str(exc)],"uploaded":False,"scheduled":False}
    if not caption_text or not source_data or not credit_data:
        return {"status":"BLOCKED","errors":["caption/sources/credits missing"],"uploaded":False,"scheduled":False}
    digest=hashlib.file_digest(video.open("rb"),"sha256").hexdigest()
    manifest={"brand_id":"7173924","account":"tuperrofelizofficial",
              "editorial_date":day,"slot":slot,"video_sha256":digest,
              "caption":caption_text,"sources":source_data,"credits":credit_data}
    if public_url:
        manifest["video_url"]=public_url
    return {"status":"HANDOFF_READY_NO_UPLOAD","manifest":manifest,
            "uploaded":False,"scheduled":False,
            "requires":"Authorized media hosting and a verified public HTTPS URL before Metricool dry-run"}

def main():
    ap=argparse.ArgumentParser()
    for x in ("video","caption","sources","credits","date","slot"):
        ap.add_argument("--"+x,required=True)
    ap.add_argument("--video-url")
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    result=prepare(*(pathlib.Path(getattr(a,x)) for x in ("video","caption","sources","credits")),a.date,a.slot,a.video_url)
    pathlib.Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(result["status"])
    return 0 if result["status"]=="HANDOFF_READY_NO_UPLOAD" else 2
if __name__=="__main__":
    sys.exit(main())
