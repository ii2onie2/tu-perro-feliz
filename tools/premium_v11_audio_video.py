#!/usr/bin/env python3
"""Staging-only premium V1.1/V1.4 audio-video postprocessor.
No publishing, no source media edits. Requires ffmpeg and ffprobe.
Creates an independent output, never overwrites the input.
"""
import argparse
import json
import subprocess
from pathlib import Path

def run(args, timeout=240):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=timeout)

def probe(path):
    return json.loads(run(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(path)],30).stdout)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--report",required=True)
    ap.add_argument("--subtitle")
    ap.add_argument("--execute", action="store_true",help="Explicit opt-in; default dry-run")
    args=ap.parse_args()
    src=Path(args.input).resolve()
    dst=Path(args.output).resolve()
    rpt=Path(args.report).resolve()
    if src==dst: raise SystemExit("BLOCKED_OVERWRITE")
    if not src.is_file() or src.stat().st_size==0: raise SystemExit("BLOCKED_INPUT_MISSING")
    meta=probe(src)
    vs=[s for s in meta.get("streams",[]) if s.get("codec_type")=="video"]
    aus=[s for s in meta.get("streams",[]) if s.get("codec_type")=="audio"]
    if not vs or not aus: raise SystemExit("BLOCKED_MISSING_AV")
    if (int(vs[0].get("width",0)),int(vs[0].get("height",0)))!=(1080,1920):
        raise SystemExit("BLOCKED_WRONG_RESOLUTION")
    duration=float(meta.get("format",{}).get("duration",0))
    if not 15 <= duration <= 180: raise SystemExit("BLOCKED_DURATION")
    if args.subtitle:
        sub=Path(args.subtitle)
        if not sub.is_file() or not sub.read_text(encoding="utf-8").strip():
            raise SystemExit("BLOCKED_SUBTITLE_MISSING")
    report={"mode":"EXECUTE" if args.execute else "DRY_RUN",
            "duration_seconds":round(duration,3),
            "resolution":"1080x1920","audio_present":True,
            "subtitle_file_checked":bool(args.subtitle),
            "subtitle_alignment_verified":False,
            "visual_quality_verified":False,
            "source_rights_verified":False,
            "publication_enabled":False}
    if args.execute:
        if dst.exists(): raise SystemExit("BLOCKED_OUTPUT_EXISTS")
        dst.parent.mkdir(parents=True,exist_ok=True)
        # Keep video stream intact: this step only normalizes finished audio.
        command=["ffmpeg","-hide_banner","-nostdin","-v","error","-i",str(src),
                 "-map","0:v:0","-map","0:a:0","-c:v","copy",
                 "-af","highpass=f=75,acompressor=threshold=0.13:ratio=2:attack=20:release=180,loudnorm=I=-16:TP=-1.5:LRA=11",
                 "-c:a","aac","-b:a","192k","-movflags","+faststart",str(dst)]
        run(command,240)
        post=probe(dst)
        if not any(s.get("codec_type")=="audio" for s in post["streams"]):
            raise SystemExit("BLOCKED_NO_OUTPUT_AUDIO")
        report["result"]="AUDIO_POSTPROCESSED_NEEDS_LISTENING_REVIEW"
    else:
        report["result"]="PASS_PREFLIGHT_NO_RENDER"
    if rpt.exists(): raise SystemExit("BLOCKED_REPORT_EXISTS")
    rpt.parent.mkdir(parents=True,exist_ok=True)
    rpt.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("RESULT="+report["result"])

if __name__=="__main__":
    main()
