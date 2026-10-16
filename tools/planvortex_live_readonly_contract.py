#!/usr/bin/env python3
"""PlanVortex live GET-only contract test: no upload, no publication, no secret logs."""
import json,os,sys,urllib.request,urllib.parse,urllib.error,hashlib
base="https://api.planvortex.com/v1.0.0"
brand=os.getenv("BRAND","")
target={"history":"taldiacomohoy","dogs":"tuperrofeliz"}.get(brand)
cid=os.getenv("PLANVORTEX_CLIENT_ID","")
sec=os.getenv("PLANVORTEX_CLIENT_SECRET","")
org=os.getenv("PLANVORTEX_ORG_ID","")
if not target or not all((cid,sec,org)): raise SystemExit("BLOCKED_CONFIG")
def get(path,token):
 req=urllib.request.Request(base+path,headers={"Authorization":"Bearer "+token,"Accept":"application/json"},method="GET")
 with urllib.request.urlopen(req,timeout=20) as r: return json.load(r),r.status
form=urllib.parse.urlencode({"grant_type":"client_credentials","client_id":cid,"client_secret":sec}).encode()
req=urllib.request.Request(base+"/oauth/token",data=form,headers={"Content-Type":"application/x-www-form-urlencoded"},method="POST")
with urllib.request.urlopen(req,timeout=20) as r: token=json.load(r).get("access_token")
if not token: raise SystemExit("BLOCKED_TOKEN")
root="/organizations/"+urllib.parse.quote(org,safe="")
body,status=get(root+"/accounts",token)
items=body if isinstance(body,list) else body.get("data",body.get("accounts",[]))
if isinstance(items,dict):items=items.get("data",items.get("items",[]))
if not isinstance(items,list):raise SystemExit("BLOCKED_ACCOUNTS_SCHEMA")
matches=[]
for x in items:
 if not isinstance(x,dict):continue
 names=[str(x.get(k,"")).lower().lstrip("@") for k in ("username","handle","name","account_name","social_username")]
 network=str(x.get("social_network",x.get("network",x.get("provider","")))).lower()
 if target in names and "tiktok" in network:matches.append(x)
print("ACCOUNTS_HTTP="+str(status))
print("ACCOUNT_MATCH_COUNT="+str(len(matches)))
if len(matches)!=1:raise SystemExit("BLOCKED_ACCOUNT_AMBIGUITY")
ident=str(matches[0].get("_id",matches[0].get("id","")))
if not ident:raise SystemExit("BLOCKED_ACCOUNT_ID_MISSING")
fingerprint=hashlib.sha256(ident.encode()).hexdigest()[:12]
expected_fingerprint={"history":"1b22ebaf4344","dogs":"b371c6eb8b22"}[brand]
print("ACCOUNT_ID_FINGERPRINT="+fingerprint)
if fingerprint!=expected_fingerprint:raise SystemExit("BLOCKED_ACCOUNT_FINGERPRINT_CHANGED")
print("ACCOUNT_BINDING=VERIFIED_LIVE_BY_FINGERPRINT")
secret_account=os.getenv("PLANVORTEX_ACCOUNT_ID","")
if secret_account and secret_account!=ident:raise SystemExit("BLOCKED_ACCOUNT_ID_MISMATCH")
print("ACCOUNT_SECRET_STATUS="+("MATCH" if secret_account else "NOT_CONFIGURED"))
for name,path in (("LIMITS","/limits"),("PUBLICATIONS","/publish")):
 try:
  val,code=get(root+path,token)
  print(name+"_HTTP="+str(code))
  print(name+"_SCHEMA="+type(val).__name__)
 except urllib.error.HTTPError as e:
  print(name+"_HTTP="+str(e.code))
  raise SystemExit("BLOCKED_"+name+"_READ")
print("PUBLISH_CONTRACT=DOCUMENTATION_ONLY_NOT_EXECUTED")
print("NO_UPLOAD=YES")
print("NO_PUBLICATION=YES")
print("RESULT=PASS_READ_ONLY_CONTRACT")
