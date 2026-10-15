#!/usr/bin/env python3
"""Read-only premium scene planner -> FFmpeg concat manifest.
The manifest lists EXISTING verified-on-disk frames only; it never downloads, generates,
publishes, or changes source footage. Word-weight timing is approximate.
"""
import argparse,json,math
from pathlib import Path
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--storyboard",required=True);p.add_argument("--media-root",default=".")
 p.add_argument("--output",required=True);a=p.parse_args()
 j=json.loads(Path(a.storyboard).read_text(encoding="utf-8"))
 if j.get("publish_authorized") is not False:raise SystemExit("BLOCKED_UNSAFE_STORYBOARD")
 scenes=j.get("scenes",[]);root=Path(a.media_root).resolve();lines=["ffconcat version 1.0"]
 if not scenes:raise SystemExit("BLOCKED_EMPTY_STORYBOARD")
 for s in scenes:
  item=s.get("media_path")
  if not item:raise SystemExit("BLOCKED_MISSING_MEDIA")
  target=(root/item).resolve()
  if not target.is_relative_to(root) or not target.is_file():raise SystemExit("BLOCKED_MISSING_OR_OUTSIDE_MEDIA")
  if target.suffix.lower() not in (".jpg",".jpeg",".png",".webp"):raise SystemExit("BLOCKED_UNSUPPORTED_MEDIA")
  seconds=float(s["end_estimate"])-float(s["start_estimate"])
  if not math.isfinite(seconds) or seconds<=0:raise SystemExit("BLOCKED_BAD_DURATION")
  # FFconcat quoting for an absolute filename. The caller must explicitly opt into FFmpeg execution.
  quoted=str(target).replace("'","'\\''")
  lines.extend(["file '"+quoted+"'","duration "+format(seconds,".3f")])
 # ffconcat still-image durations need the last image repeated.
 lines.append(lines[-2])
 out=Path(a.output)
 if out.exists():raise SystemExit("BLOCKED_OUTPUT_EXISTS")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text("\n".join(lines)+"\n",encoding="utf-8")
 print("RESULT=MANIFEST_ONLY_NO_RENDER")
 print("TIMING_VERIFIED=NO")
 print("MEDIA_LICENSES_VERIFIED=NO")
 print("PUBLISHING_ENABLED=NO")
if __name__=="__main__":main()
