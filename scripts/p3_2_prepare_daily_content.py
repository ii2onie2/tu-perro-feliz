#!/usr/bin/env python3
"""P3.2 draft-to-dated-JSON generator; offline, safe by default.

Input: JSON file containing {"date":"YYYY-MM-DD","items":[three authored,
source-checked content objects]}. No model/network call; no invented facts.
Dry run validates only; --write outputs three files using exclusive creation.
"""
import argparse
import datetime as dt
import json
from pathlib import Path

SUFFIXES=["","-educacion","-sabias"]
SERIES=["Tu perro feliz","Buenos modales","¿Sabías esto de tu perro?"]
SLOTS=["10:00","16:00","19:00"]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--content-dir",default="content")
    p.add_argument("--write",action="store_true")
    a=p.parse_args()
    src=Path(a.input)
    doc=json.loads(src.read_text(encoding="utf-8"))
    date=dt.date.fromisoformat(doc["date"]).isoformat()
    items=doc.get("items")
    if not isinstance(items,list) or len(items)!=3:
        raise SystemExit("BLOCKED: exactly three authored items required")
    paths=[]
    for i,item in enumerate(items):
        if not isinstance(item,dict):
            raise SystemExit("BLOCKED: invalid item")
        expected={"series":SERIES[i],"date":date,"slot":SLOTS[i]}
        for k,v in expected.items():
            if item.get(k)!=v:
                raise SystemExit("BLOCKED: item %s %s mismatch"%(i,k))
        for field in ("title","hook","narration","caption","cta","hashtags","sources","media"):
            if not item.get(field):
                raise SystemExit("BLOCKED: item %s missing %s"%(i,field))
        if len(item["narration"].split())<65:
            raise SystemExit("BLOCKED: narration too short")
        if not isinstance(item["sources"], list) or not all(isinstance(source,dict) and source.get("name") and str(source.get("url","")).startswith("https://") for source in item["sources"]):
            raise SystemExit("BLOCKED: source URLs invalid")
        paths.append((Path(a.content_dir)/(date+SUFFIXES[i]+".json"),item))
    if len({x["title"].casefold().strip() for _,x in paths})!=3:
        raise SystemExit("BLOCKED: duplicate titles")
    for path,_ in paths:
        if path.exists():
            raise SystemExit("BLOCKED: existing file "+str(path))
    print("MODE="+("WRITE_NEW_ONLY" if a.write else "DRY_RUN"))
    for path,_ in paths:
        print("READY="+str(path))
    if not a.write:
        print("RESULT=PASS_DRAFT_ONLY")
        return
    # Exclusively create three files. Remove only files created in this run on failure.
    created=[]
    try:
        for path,item in paths:
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open("x",encoding="utf-8") as f:
                created.append(path)
                json.dump(item,f,ensure_ascii=False,indent=2)
                f.write("\\n")
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    print("RESULT=CREATED_UNPUBLISHED_JSON")

if __name__=="__main__":
    main()
