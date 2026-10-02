#!/usr/bin/env python3
import json, pathlib, sys

HISTORY=pathlib.Path("content/published_history.json")
FORMATS=[
    "step_by_step","three_mistakes","before_after","myth_vs_fact",
    "body_language","do_this_not_that","checklist","mini_lesson",
    "problem_solution","three_facts"
]

def main():
    p=pathlib.Path(sys.argv[1])
    d=json.loads(p.read_text(encoding="utf-8"))
    history=json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
    used={x.get("format") for x in history[-9:]}
    title=(d.get("title") or "").lower()
    explicit=d.get("format")
    if explicit in FORMATS:
        fmt=explicit
    elif any(k in title for k in ["error","errores","nunca"]):
        fmt="three_mistakes"
    elif any(k in title for k in ["señal","lenguaje","cola","orejas"]):
        fmt="body_language"
    elif any(k in title for k in ["mito","verdad"]):
        fmt="myth_vs_fact"
    elif any(k in title for k in ["paso","enseñar","aprende"]):
        fmt="step_by_step"
    else:
        fmt="problem_solution"
    if not explicit and fmt in used:
        fmt=next((x for x in FORMATS if x not in used),fmt)
    d["format"]=fmt
    d["hook_pattern"]=d.get("hook_pattern","problem_first")
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"FORMAT={fmt}")

if __name__=="__main__":
    main()
