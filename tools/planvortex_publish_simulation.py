#!/usr/bin/env python3
"""Offline PlanVortex publish simulation. NO HTTP requests. Fail closed."""
import argparse,datetime as dt,hashlib,json,pathlib,re,sys
from zoneinfo import ZoneInfo
p=argparse.ArgumentParser()
p.add_argument("--content",required=True);p.add_argument("--brand",choices=("history","dogs"),required=True)
p.add_argument("--date",required=True);p.add_argument("--slot",type=int,required=True)
p.add_argument("--mp4",required=True)
a=p.parse_args()
d=json.loads(pathlib.Path(a.content).read_text(encoding="utf-8"))
expected={"history":"Tal Día Como Hoy","dogs":"Tu Perro Feliz"}[a.brand]
handle={"history":"taldiacomohoy","dogs":"tuperrofeliz"}[a.brand]
issues=[]
if d.get("series")!=expected or d.get("date")!=a.date:issues.append("CONTENT_IDENTITY")
if d.get("publication_approved") is not True or d.get("status")!="PUBLISH_APPROVED":issues.append("PUBLICATION_NOT_APPROVED")
if d.get("media_license_approved") is not True or not d.get("media"):issues.append("MEDIA_RIGHTS_NOT_APPROVED")
if not pathlib.Path(a.mp4).is_file():issues.append("MP4_MISSING")
if a.slot not in (10,16,19):issues.append("SLOT_INVALID")
try:
 local=dt.datetime.combine(dt.date.fromisoformat(a.date),dt.time(a.slot),tzinfo=ZoneInfo("Europe/Madrid"))
 when=local.astimezone(dt.timezone.utc).isoformat()
except ValueError:issues.append("DATE_INVALID");when=""
digest=hashlib.sha256((a.brand+"|"+a.date+"|"+str(a.slot)+"|"+d.get("narration","")).encode()).hexdigest()[:24]
print("MODE=OFFLINE_NO_HTTP")
print("EXPECTED_TIKTOK_HANDLE="+handle)
print("PROVIDER_ACCOUNT_ID_FROM_LIVE_API=NOT_EMBEDDED")
print("SCHEDULE_UTC="+when)
print("IDEMPOTENCY_FINGERPRINT="+digest)
for x in issues:print("BLOCKER="+x)
print("RESULT="+("BLOCKED" if issues else "PREFLIGHT_ONLY_REQUIRES_API_CONTRACT"))
print("UPLOAD=NO")
print("POST=NO")
# This script is a negative test; never treats a passed static gate as publishing authorization.
sys.exit(0 if issues else 2)
