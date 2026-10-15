#!/usr/bin/env python3
"""Offline 14-day schedule inventory. Does not generate, schedule or publish videos."""
import datetime as dt, json, pathlib, argparse
from zoneinfo import ZoneInfo
p=argparse.ArgumentParser();p.add_argument("--start",default="2026-10-16");p.add_argument("--days",type=int,default=14);p.add_argument("--brand",choices=["history","dogs"],required=True);p.add_argument("--pilot",default="pilots/2026-10-16-editorial.json");a=p.parse_args()
assert 1<=a.days<=31
first=dt.date.fromisoformat(a.start)
rows=[];occupied=set()
for i in range(a.days):
 d=first+dt.timedelta(days=i)
 for hour in (10,16,19):
  local=dt.datetime.combine(d,dt.time(hour),tzinfo=ZoneInfo("Europe/Madrid"))
  utc=local.astimezone(dt.timezone.utc)
  key=f"{a.brand}:{d.isoformat()}:{hour:02}"
  assert key not in occupied;occupied.add(key)
  rows.append({"key":key,"local":local.isoformat(),"utc":utc.isoformat(),"state":"NOT_APPROVED_NOT_SCHEDULED"})
pil=pathlib.Path(a.pilot)
if pil.exists():
 data=json.loads(pil.read_text())
 print("PILOT_EXISTS=YES")
 print("PILOT_PUBLISHABLE="+str(data.get("publication_approved") is True and data.get("media_license_approved") is True))
else:print("PILOT_EXISTS=NO")
print("MODE=OFFLINE")
print("EXPECTED_SLOTS="+str(a.days*3))
print("APPROVED_AND_SCHEDULED=0")
print("DAYLIGHT_SAVING_OFFSETS="+",".join(sorted(set(s["local"][-6:] for s in rows))))
print("SAMPLE_FIRST="+json.dumps(rows[0],ensure_ascii=False))
print("SAMPLE_LAST="+json.dumps(rows[-1],ensure_ascii=False))
print("RESULT=RESERVE_NOT_READY")
print("INDIEPOST_API_CALLS=0")
