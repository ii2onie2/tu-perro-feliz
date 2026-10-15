#!/usr/bin/env python3
"""Premium V1 quality gate. Read-only; no upload or publication.
Checks source declarations and (optionally) real MP4 technical properties.
A PASS is technical only, never editorial fact-check or media licensing approval.
"""
import argparse
import json
import subprocess
from pathlib import Path

def probe(path):
    p=subprocess.run(["ffprobe","-v","error","-show_streams",
                      "-show_format","-of","json",str(path)],
                     capture_output=True,text=True,timeout=30)
    if p.returncode: raise ValueError("ffprobe_failed")
    return json.loads(p.stdout)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--content",required=True)
    a.add_argument("--video")
    a.add_argument("--brand",choices=("history","dogs"),required=True)
    q=a.parse_args()
    issues=[]
    d=json.loads(Path(q.content).read_text(encoding="utf-8"))
    for name in ("title","hook","narration","caption","cta","sources","media","hashtags"):
        if not d.get(name): issues.append("missing_"+name)
    min_words=180 if q.brand=="history" else 65
    if len(str(d.get("narration","")).split())<min_words:
        issues.append("narration_too_short")
    for s in d.get("sources",[]):
        if not isinstance(s,dict) or not s.get("name") or not str(s.get("url","")).startswith("https://"):
            issues.append("invalid_source_reference")
    if q.video:
        path=Path(q.video)
        if not path.is_file() or not path.stat().st_size:
            issues.append("video_missing")
        else:
            try:
                meta=probe(path)
                streams=meta.get("streams",[])
                videos=[x for x in streams if x.get("codec_type")=="video"]
                audios=[x for x in streams if x.get("codec_type")=="audio"]
                duration=float(meta.get("format",{}).get("duration",0))
                if not videos: issues.append("video_stream_missing")
                if not audios: issues.append("audio_stream_missing")
                if videos and (int(videos[0].get("width",0))!=1080 or
                               int(videos[0].get("height",0))!=1920):
                    issues.append("wrong_resolution")
                if duration<15 or duration>180:
                    issues.append("duration_out_of_range")
                print("VIDEO_DURATION_SECONDS="+str(round(duration,2)))
            except (ValueError,OSError,subprocess.TimeoutExpired):
                issues.append("video_probe_error")
    else:
        print("VIDEO_NOT_PROVIDED=YES")
    print("MODE=READ_ONLY")
    print("CONTENT="+q.content)
    print("QUALITY_GATE="+("PASS_TECHNICAL_ONLY" if not issues else "FAIL"))
    for issue in sorted(set(issues)): print("ISSUE="+issue)
    print("SOURCE_TRUTH_VERIFIED=NO")
    print("MEDIA_LICENSES_VERIFIED=NO")
    print("PUBLISHING_ENABLED=NO")
    raise SystemExit(1 if issues else 0)

if __name__=="__main__":
    main()
