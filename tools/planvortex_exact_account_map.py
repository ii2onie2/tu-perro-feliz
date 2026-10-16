#!/usr/bin/env python3
"""PlanVortex GET-only exact TikTok account map. Never uploads or publishes."""
import json,os,sys,urllib.request,urllib.parse,hashlib
base="https://api.planvortex.com/v1.0.0"
cid=os.environ.get("PLANVORTEX_CLIENT_ID","")
secret=os.environ.get("PLANVORTEX_CLIENT_SECRET","")
org=os.environ.get("PLANVORTEX_ORG_ID","")
brand=os.environ.get("BRAND","")
if not all((cid,secret,org)) or brand not in ("history","dogs"): raise SystemExit("BLOCKED_CONFIG")
form=urllib.parse.urlencode({"grant_type":"client_credentials","client_id":cid,"client_secret":secret}).encode()
req=urllib.request.Request(base+"/oauth/token",data=form,method="POST",headers={"Content-Type":"application/x-www-form-urlencoded"})
with urllib.request.urlopen(req,timeout=20) as r: token=json.load(r).get("access_token")
if not token: raise SystemExit("BLOCKED_TOKEN")
req=urllib.request.Request(base+"/organizations/"+urllib.parse.quote(org,safe="")+"/accounts",headers={"Authorization":"Bearer "+token})
with urllib.request.urlopen(req,timeout=20) as r: body=json.load(r)
items=body if isinstance(body,list) else body.get("data",body.get("accounts",[]))
if isinstance(items,dict): items=items.get("data",items.get("items",[]))
if not isinstance(items,list): raise SystemExit("BLOCKED_ACCOUNTS_SCHEMA")
target="taldiacomohoy" if brand=="history" else "tuperrofeliz"
matches=[]
for a in items:
 if not isinstance(a,dict): continue
 names=[str(a.get(k,"")).lstrip("@").lower() for k in ("username","handle","name","account_name","social_username")]
 social=str(a.get("social_network",a.get("network",a.get("provider","")))).lower()
 if target in names and "tiktok" in social: matches.append(a)
print("MODE=READ_ONLY")
print("EXPECTED_HANDLE="+target)
print("MATCHES="+str(len(matches)))
if len(matches)!=1: raise SystemExit("BLOCKED_NOT_EXACTLY_ONE_TIKTOK_ACCOUNT")
account_id=str(matches[0].get("_id",matches[0].get("id","")))
if not account_id: raise SystemExit("BLOCKED_MISSING_PROVIDER_ACCOUNT_ID")
print("ACCOUNT_ID_FINGERPRINT="+hashlib.sha256(account_id.encode()).hexdigest()[:12])
print("ACCOUNT_ID_NOT_PRINTED=YES")
print("UPLOAD=NO")
print("PUBLICATION=NO")
print("RESULT=PASS_READ_ONLY_ACCOUNT_MAPPING")
