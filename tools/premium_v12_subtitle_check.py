#!/usr/bin/env python3
"""V1.2 subtitle timing and safe-area validator; read only."""
import argparse
import re
from pathlib import Path

TIME=re.compile(r"^(\d\d):(\d\d):(\d\d),(\d{3})$")
def seconds(s):
    m=TIME.match(s.strip())
    if not m: raise ValueError("invalid timestamp")
    h,mn,sec,ms=map(int,m.groups())
    if mn>=60 or sec>=60: raise ValueError("invalid clock")
    return h*3600+mn*60+sec+ms/1000

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--srt",required=True)
    p.add_argument("--duration",type=float,required=True)
    a=p.parse_args()
    if a.duration<=0: raise SystemExit("BLOCKED_DURATION")
    text=Path(a.srt).read_text(encoding="utf-8-sig")
    blocks=[b.strip().splitlines() for b in re.split(r"\n\s*\n",text.strip()) if b.strip()]
    errors=[]
    previous=0.0
    for i,block in enumerate(blocks,1):
        if len(block)<3 or "-->" not in block[1]:
            errors.append("INVALID_BLOCK_"+str(i)); continue
        try:
            start,end=[seconds(x) for x in block[1].split("-->")]
            if not (0<=start<end<=a.duration+0.5):
                errors.append("TIMING_"+str(i))
            if start<previous-0.05: errors.append("OVERLAP_"+str(i))
            previous=end
            caption=" ".join(block[2:]).strip()
            if len(caption)>90: errors.append("LONG_CAPTION_"+str(i))
            if not caption: errors.append("EMPTY_CAPTION_"+str(i))
        except (ValueError,IndexError):
            errors.append("INVALID_TIMESTAMP_"+str(i))
    if not blocks: errors.append("NO_CAPTIONS")
    print("MODE=READ_ONLY")
    print("SUBTITLE_BLOCKS="+str(len(blocks)))
    print("TIMING_FORMAT_CHECK="+("PASS" if not errors else "FAIL"))
    print("VOICE_ALIGNMENT_VERIFIED=NO")
    print("ON_SCREEN_SAFE_AREA_VERIFIED=NO")
    for e in errors: print("ISSUE="+e)
    raise SystemExit(1 if errors else 0)
if __name__=="__main__":
    main()
