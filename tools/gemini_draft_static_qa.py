#!/usr/bin/env python3
import json,sys,re,pathlib
draft=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
evidence=json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
errors=[]
for k in ["title","hook","narration","caption","cta"]:
 if not isinstance(draft.get(k),str) or not draft[k].strip(): errors.append("MISSING_"+k.upper())
if not isinstance(draft.get("hashtags"),list) or not draft["hashtags"]: errors.append("INVALID_HASHTAGS")
if draft.get("status")!="UNVERIFIED_DRAFT" or draft.get("review_required") is not True: errors.append("UNVERIFIED_GATES_INVALID")
if draft.get("date")!="2026-10-16" or draft.get("brand")!="dogs": errors.append("IDENTITY_MISMATCH")
if draft.get("sources")!=evidence.get("sources"): errors.append("SOURCE_SET_MISMATCH")
words=len(re.findall(r"\b[\wÀ-ÿ]+\b",draft.get("narration","")))
lo,hi=(180,240) if "dogs"=="history" else (100,150)
if not lo<=words<=hi: errors.append("WORD_COUNT_OUT_OF_RANGE")
print("DRAFT_WORD_COUNT="+str(words))
print("SOURCES_COUNT="+str(len(draft.get("sources",[]))))
print("AUTOMATED_STRUCTURE="+("FAIL" if errors else "PASS"))
for e in errors: print("ISSUE="+e)
print("EDITORIAL_FACTUAL_APPROVAL=PENDING_HUMAN_REVIEW")
print("RIGHTS_CLEARANCE=PENDING")
print("PUBLICATION_ALLOWED=NO")
sys.exit(bool(errors))
