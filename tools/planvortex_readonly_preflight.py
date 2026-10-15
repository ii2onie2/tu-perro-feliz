#!/usr/bin/env python3
"""PlanVortex authenticated GET-only preflight; never publish or upload."""
import json,os,urllib.parse,urllib.request,urllib.error,sys
base="https://api.planvortex.com/v1.0.0"
client=os.getenv("PLANVORTEX_CLIENT_ID","").strip()
secret=os.getenv("PLANVORTEX_CLIENT_SECRET","").strip()
org=os.getenv("PLANVORTEX_ORG_ID","").strip()
if not all((client,secret,org)):
 print("RESULT=BLOCKED_MISSING_PLANVORTEX_SECRETS_OR_ORG_ID")
 sys.exit(0)
if not org.replace("-","").isalnum():
 raise SystemExit("BLOCKED_INVALID_ORG_ID")
form=urllib.parse.urlencode({"grant_type":"client_credentials","client_id":client,"client_secret":secret}).encode()
req=urllib.request.Request(base+"/oauth/token",data=form,headers={"Content-Type":"application/x-www-form-urlencoded"},method="POST")
try:
 with urllib.request.urlopen(req,timeout=20) as r: payload=json.load(r)
 token=payload.get("access_token","")
 if not token: raise ValueError("missing token")
except Exception as e:
 print("RESULT=BLOCKED_AUTH");print("ERROR_TYPE="+type(e).__name__);sys.exit(1)
for name,path in (("ACCOUNTS","accounts"),("LIMITS","limits")):
 try:
  req=urllib.request.Request(base+"/organizations/"+org+"/"+path,headers={"Authorization":"Bearer "+token,"Accept":"application/json"},method="GET")
  with urllib.request.urlopen(req,timeout=20) as r:
   data=json.load(r)
   print(name+"_HTTP="+str(r.status))
   if name=="ACCOUNTS":
    serialized=json.dumps(data,ensure_ascii=False).lower()
    print("TAL_DIA_HANDLE_VISIBLE="+str("taldiacomohoy09" in serialized).upper())
    print("TU_PERRO_HANDLE_VISIBLE="+str("tuperrofelizofficial" in serialized).upper())
   else: print("LIMITS_READ=PASS")
 except Exception as e:
  print(name+"_READ=FAIL");print("ERROR_TYPE="+type(e).__name__);sys.exit(1)
print("MODE=READ_ONLY")
print("NO_UPLOAD_NO_PUBLICATION=YES")
print("RESULT=PASS_READ_ONLY")
