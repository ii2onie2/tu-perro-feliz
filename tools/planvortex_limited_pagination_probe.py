#!/usr/bin/env python3
"""GET-only PlanVortex pagination probe; empty datasets cannot prove nonempty pagination."""
import json,os,urllib.parse,urllib.request,hashlib
brand=os.getenv("BRAND")
expected={"history":("taldiacomohoy","1b22ebaf4344"),"dogs":("tuperrofeliz","b371c6eb8b22")}
if brand not in expected:raise SystemExit("BLOCKED_BRAND")
client=os.getenv("PLANVORTEX_CLIENT_ID");secret=os.getenv("PLANVORTEX_CLIENT_SECRET");org=os.getenv("PLANVORTEX_ORG_ID")
if not all((client,secret,org)):raise SystemExit("BLOCKED_CONFIG")
base="https://api.planvortex.com/v1.0.0"
form=urllib.parse.urlencode({"grant_type":"client_credentials","client_id":client,"client_secret":secret}).encode()
req=urllib.request.Request(base+"/oauth/token",data=form,headers={"Content-Type":"application/x-www-form-urlencoded"},method="POST")
with urllib.request.urlopen(req,timeout=20) as r:token=json.load(r).get("access_token")
if not token:raise SystemExit("BLOCKED_AUTH")
root="/organizations/"+urllib.parse.quote(org,safe="")
def get(path):
 req=urllib.request.Request(base+path,headers={"Authorization":"Bearer "+token,"Accept":"application/json"},method="GET")
 with urllib.request.urlopen(req,timeout=20) as r:return json.load(r),r.status
accounts,_=get(root+"/accounts")
items=accounts if isinstance(accounts,list) else accounts.get("data",accounts.get("accounts",[]))
if isinstance(items,dict):items=items.get("data",items.get("items",[]))
matches=[]
for a in items:
 if not isinstance(a,dict):continue
 names=[str(a.get(k,"")).lower().lstrip("@") for k in ("username","handle","name","account_name","social_username")]
 network=str(a.get("social_network",a.get("network",a.get("provider","")))).lower()
 if expected[brand][0] in names and "tiktok" in network:matches.append(a)
if len(matches)!=1:raise SystemExit("BLOCKED_ACCOUNT_IDENTITY")
ident=str(matches[0].get("_id",matches[0].get("id","")))
if hashlib.sha256(ident.encode()).hexdigest()[:12]!=expected[brand][1]:raise SystemExit("BLOCKED_ACCOUNT_CHANGED")
totals=[];pages=[]
for offset in (0,1):
 qs=urllib.parse.urlencode({"limit":1,"offset":offset})
 body,status=get(root+"/publish?"+qs)
 if status!=200 or not isinstance(body,dict) or set(body)!={"publications","total"}:raise SystemExit("BLOCKED_PAGINATION_SCHEMA")
 if not isinstance(body["publications"],list) or type(body["total"]) is not int:raise SystemExit("BLOCKED_PAGINATION_VALUES")
 totals.append(body["total"]);pages.append(len(body["publications"]))
 print("OFFSET_"+str(offset)+"_HTTP=200")
 print("OFFSET_"+str(offset)+"_COUNT="+str(pages[-1]))
print("TOTAL_CONSISTENT="+str(totals[0]==totals[1]).upper())
print("TOTAL_VALUE="+str(totals[0]))
if totals[0]!=totals[1] or totals[0]<0:raise SystemExit("BLOCKED_INCONSISTENT_TOTAL")
print("NONEMPTY_PAGINATION_PROVEN="+str(totals[0]>1 and pages==[1,1]).upper())
print("FULL_ACCOUNT_RECONCILIATION=NOT_PROVEN")
print("NO_UPLOAD=YES")
print("NO_PUBLICATION=YES")
print("RESULT=PASS_LIMITED_READONLY_PAGINATION_PROBE")
