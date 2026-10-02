#!/usr/bin/env python3
import json, pathlib, sys

HISTORY=pathlib.Path("content/published_history.json")

def main():
    items=json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
    for name in sys.argv[1:]:
        d=json.loads(pathlib.Path(name).read_text(encoding="utf-8"))
        items=[x for x in items if not (x.get("date")==d.get("date") and x.get("series")==d.get("series"))]
        items.append({
            "date":d.get("date"),
            "series":d.get("series"),
            "title":d.get("title"),
            "topic_family":d.get("topic_family"),
            "format":d.get("format"),
            "hook_pattern":d.get("hook_pattern"),
            "duration_target":d.get("duration_target")
        })
    HISTORY.write_text(json.dumps(items[-730:],ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
