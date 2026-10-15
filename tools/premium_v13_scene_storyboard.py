#!/usr/bin/env python3
"""Staging-only narration-to-scenes storyboard. No generative or publishing calls.
Timing is an estimate until a speech aligner is validated; no invented source media.
"""
import argparse
import json
import math
import re
from pathlib import Path

def storyboard(data, duration, max_scenes=16):
    text=str(data.get("narration","")).strip()
    if not text: raise ValueError("missing narration")
    if not (15<=duration<=180): raise ValueError("invalid duration")
    sentences=[s.strip() for s in re.split(r"(?<=[.!?])\s+",text) if s.strip()]
    if not sentences: raise ValueError("no sentences")
    # Keep complete sentences; group contiguous ones into bounded beats.
    target=max(1,min(max_scenes, math.ceil(duration/5)))
    count=min(target,len(sentences))
    groups=[sentences[(i*len(sentences))//count:((i+1)*len(sentences))//count] for i in range(count)]
    weights=[max(1,len(" ".join(g).split())) for g in groups]
    total=sum(weights); cursor=0.0
    media=[m for m in data.get("media",[]) if isinstance(m,dict)]
    scenes=[]
    for i,(group,weight) in enumerate(zip(groups,weights)):
        end=duration if i==count-1 else cursor+duration*weight/total
        selected=media[i%len(media)] if media else None
        scenes.append({"index":i+1,"start_estimate":round(cursor,3),"end_estimate":round(end,3),
                       "narration":" ".join(group),
                       "media_path":selected.get("path") if selected else None,
                       "media_rights_verified":False,
                       "timing_verified":False})
        cursor=end
    return {"mode":"STAGING_READ_ONLY","timing_method":"word_weight_estimate_not_for_final_sync",
            "source_media_verified":False,"editorial_facts_verified":False,
            "publish_authorized":False,"scenes":scenes}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--content",required=True)
    a.add_argument("--duration",required=True,type=float)
    a.add_argument("--out")
    args=a.parse_args()
    data=json.loads(Path(args.content).read_text(encoding="utf-8"))
    result=storyboard(data,args.duration)
    output=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.out:
        path=Path(args.out)
        if path.exists(): raise SystemExit("BLOCKED_OUTPUT_EXISTS")
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(output,encoding="utf-8")
    else:
        print(output,end="")
if __name__=="__main__":
    main()
