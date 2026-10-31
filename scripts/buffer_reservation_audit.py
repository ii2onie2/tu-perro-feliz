#!/usr/bin/env python3
"""Read-only Buffer reservation audit. Never retries uncertain API calls."""
import argparse,json,pathlib,re,sys
STATES={"RESERVED","QUEUED","FAILED_UNCERTAIN","PUBLISHED_CONFIRMED"}
def audit(reservation,receipt):
 lines=reservation.read_text(encoding="utf-8").splitlines()
 fields=dict(line.split("=",1) for line in lines if "=" in line)
 if fields.get("RESERVED")!=reservation.name or not fields.get("CHANNEL"):
  raise ValueError("invalid reservation")
 if not receipt.is_file():
  return "FAILED_UNCERTAIN","missing receipt; query Buffer manually, do not retry"
 data=json.loads(receipt.read_text(encoding="utf-8"))
 state=data.get("state")
 if state not in STATES: raise ValueError("invalid receipt state")
 if data.get("date")!=reservation.name or data.get("channel")!=fields["CHANNEL"]:
  raise ValueError("receipt does not match reservation")
 if state in ("QUEUED","PUBLISHED_CONFIRMED") and not data.get("buffer_post_id"):
  raise ValueError("success state without Buffer post ID")
 if state=="PUBLISHED_CONFIRMED" and not data.get("tiktok_post_id"):
  raise ValueError("TikTok confirmation without TikTok post ID")
 return state,"read-only audit"
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--reservations",type=pathlib.Path,default=pathlib.Path(".buffer-queue-reservations"))
 p.add_argument("--receipts",type=pathlib.Path,default=pathlib.Path(".buffer-queue-receipts"))
 a=p.parse_args()
 blocked=0
 for r in sorted(a.reservations.glob("????-??-??")):
  try:
   state,note=audit(r,a.receipts/(r.name+".json"))
   print(r.name,state,note)
   if state in ("RESERVED","FAILED_UNCERTAIN"): blocked+=1
  except (ValueError,OSError,json.JSONDecodeError) as e:
   print(r.name,"FAILED_UNCERTAIN",str(e));blocked+=1
 print("UNCERTAIN_RESERVATIONS="+str(blocked))
 if blocked: sys.exit(2)
if __name__=="__main__": main()
