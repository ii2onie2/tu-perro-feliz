#!/usr/bin/env python3
"""Offline reserve and duplicate readiness; no API requests and no posts."""
import argparse,datetime,hashlib,json,re
from pathlib import Path
def norm(s):return re.sub(r"[^a-z0-9]+"," ",str(s).casefold()).strip()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--content-dir",default="content")
 p.add_argument("--start",required=True)
 p.add_argument("--days",type=int,default=14)
 args=p.parse_args()
 if not 1<=args.days<=31:raise SystemExit("INVALID_WINDOW")
 start=datetime.date.fromisoformat(args.start)
 root=Path(args.content_dir)
 collisions=[];ready=0;missing=[];seen={}
 for day in range(args.days):
  date=(start+datetime.timedelta(days=day)).isoformat()
  paths=sorted(root.glob(date+"*.json"))
  approved=[]
  for path in paths:
   try: d=json.loads(path.read_text(encoding="utf-8"))
   except (ValueError,OSError):continue
   if not isinstance(d,dict):continue
   title=norm(d.get("title",""))
   narration=norm(d.get("narration",""))
   for value in (title,hashlib.sha256(narration.encode()).hexdigest() if narration else ""):
    if not value:continue
    if value in seen:collisions.append([seen[value],str(path)])
    else:seen[value]=str(path)
   if all(d.get(k) for k in ("title","narration","sources","media")) and d.get("editorial_approved") is True and d.get("rights_approved") is True:
    approved.append(path)
  if len(approved)>=3:ready+=3
  else:missing.append({"date":date,"approved":len(approved),"target":3})
 print(json.dumps({"mode":"READ_ONLY","days":args.days,"expected":args.days*3,
 "validated_count":ready,"unfilled_days":missing,"duplicate_pairs":collisions,
 "publishing_enabled":False,"source_truth_independently_verified":False},indent=2))
 if collisions:raise SystemExit("BLOCKED_DUPLICATES")
 print("STATUS="+("RESERVE_READY_FOR_FURTHER_REVIEW" if ready==args.days*3 else "RESERVE_INCOMPLETE"))
if __name__=="__main__":main()
