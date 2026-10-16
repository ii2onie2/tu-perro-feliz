#!/usr/bin/env python3
"""Privacy-preserving inspection of PlanVortex publication list. GET only, fail closed."""
import hashlib,json,os,sys,urllib.parse,urllib.request
brand=os.getenv("BRAND","")
expected={"history":("taldiacomohoy","1b22ebaf4344"),"dogs":("tuperrofeliz","b371c6eb8b22")}
if brand not in expected:raise SystemExit("BLOCKED_BRAND")
cid=os.getenv("PLANVORTEX_CLIENT_ID","");sec=os.getenv("PLANVORTEX_CLIENT_SECRET","");org=os.getenv("PLANVORTEX_ORG_ID","")
if not all((cid,sec,org)):raise SystemExit("BLOCKED_CONFIG")
base="https://api.planvortex.com/v1.0.0"
form=urllib.parse.urlencode({"grant_type":"client_credentials","client_id":cid,"client_secret":sec}).encode()
req=urllib.request.Request(base+"/oauth/token",data=form,headers={"Content-Type":"application/x-www-form-urlencoded"},method="POST")
with urllib.request.urlopen(req,timeout=20) as r:token=json.load(r).get("access_token")
if not token:raise SystemExit("BLOCKED_AUTH")
root="/organizations/"+urllib.parse.quote(org,safe="")
def fetch(path):
 req=urllib.request.Request(base+path,headers={"Authorization":"Bearer "+token,"Accept":"application/json"},method="GET")
 with urllib.request.urlopen(req,timeout=20) as r:return json.load(r),r.status
accounts,_=fetch(root+"/accounts")
items=accounts if isinstance(accounts,list) else accounts.get("data",accounts.get("accounts",[]))
if isinstance(items,dict):items=items.get("data",items.get("items",[]))
if not isinstance(items,list):raise SystemExit("BLOCKED_ACCOUNT_SCHEMA")
matches=[]
for a in items:
 if not isinstance(a,dict):continue
 names=[str(a.get(k,"")).lower().lstrip("@") for k in ("username","handle","name","account_name","social_username")]
 network=str(a.get("social_network",a.get("network",a.get("provider","")))).lower()
 if expected[brand][0] in names and "tiktok" in network:matches.append(a)
if len(matches)!=1:raise SystemExit("BLOCKED_ACCOUNT_MATCH")
ident=str(matches[0].get("_id",matches[0].get("id","")))
if hashlib.sha256(ident.encode()).hexdigest()[:12]!=expected[brand][1]:raise SystemExit("BLOCKED_ACCOUNT_FINGERPRINT")
data,status=fetch(root+"/publish")
print("PUBLICATIONS_HTTP="+str(status))
print("RESPONSE_KIND="+type(data).__name__)
if isinstance(data,dict):
 print("TOP_LEVEL_KEYS="+",".join(sorted(data.keys())))
 for k,v in sorted(data.items()):
  if isinstance(v,list):
   print("LIST_FIELD="+k);print("LIST_LENGTH="+str(len(v)))
   if v and isinstance(v[0],dict):print("ITEM_FIELD_NAMES="+",".join(sorted(v[0].keys())))
  elif isinstance(v,dict):print("OBJECT_FIELD="+k+"_KEYS="+",".join(sorted(v.keys())))
  else:print("SCALAR_FIELD="+k+"_TYPE="+type(v).__name__)
elif isinstance(data,list):
 print("LIST_LENGTH="+str(len(data)))
 if data and isinstance(data[0],dict):print("ITEM_FIELD_NAMES="+",".join(sorted(data[0].keys())))
print("PAGINATION_COMPLETE=UNVERIFIED")
print("ACCOUNT_POST_MATCH=UNVERIFIED")
print("NO_IDENTIFIERS_OR_POST_CONTENT_LOGGED=YES")
print("NO_UPLOAD=YES")
print("NO_PUBLICATION=YES")
print("RESULT=PASS_SCHEMA_INSPECTION_ONLY")
