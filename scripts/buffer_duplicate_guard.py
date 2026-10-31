import argparse,hashlib,json,pathlib,sys
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""): h.update(chunk)
 return h.hexdigest()
def cap(p): return hashlib.sha256(" ".join(p.read_text(encoding="utf-8").casefold().split()).encode()).hexdigest()
def check(day,root,ledger):
 if day<"2026-11-01": raise ValueError("historical date")
 v=root/(day+".mp4");c=root/(day+".caption.txt");s=root/(day+".sources.json")
 if not all(x.is_file() and x.stat().st_size for x in (v,c,s)): raise ValueError("incomplete package")
 json.loads(s.read_text(encoding="utf-8"))
 vh,ch=sha(v),cap(c)
 if any(sha(x)==vh for x in root.glob("*.mp4") if x!=v): raise ValueError("duplicate video bytes")
 if any(cap(x)==ch for x in root.glob("*.caption.txt") if x!=c): raise ValueError("duplicate caption")
 data=json.loads(ledger.read_text(encoding="utf-8"))
 if data.get("schema_version")!=1 or not isinstance(data.get("known_publications"),list): raise ValueError("bad ledger")
 if any(e.get("video_sha256")==vh or e.get("caption_sha256")==ch for e in data["known_publications"]): raise ValueError("ledger duplicate")
 print("DUPLICATE_GUARD=PASS","VIDEO_SHA256="+vh,"CAPTION_SHA256="+ch)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--date",required=True);a=p.parse_args()
 try: check(a.date,pathlib.Path("videos"),pathlib.Path("editorial/publication_evidence.json"))
 except (ValueError,OSError) as e: print("DUPLICATE_GUARD=BLOCKED",e,file=sys.stderr);sys.exit(1)
