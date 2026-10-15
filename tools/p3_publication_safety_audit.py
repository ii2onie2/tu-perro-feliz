#!/usr/bin/env python3
"""P3 safe launch audit: never posts or calls paid APIs."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
drafts=sorted((ROOT/"content").glob("2026-10-1*.json"))
history=ROOT/"content"/"published_history.json"
publishing=ROOT/".github"/"workflows"/"publish-trypost.yml"
gemini=ROOT/".github"/"workflows"/"gemini-single-draft-manual.yml"
quality=ROOT/"tools"/"premium_v1_quality_gate.py"
results={
  "history_file_exists":history.is_file(),
  "candidate_october_scenarios":len(drafts),
  "manual_gemini_workflow_exists":gemini.is_file(),
  "quality_gate_exists":quality.is_file(),
  "publishing_workflow_is_disabled":publishing.is_file() and "Automatic TryPost publishing is disabled" in publishing.read_text(encoding="utf8"),
  "curated_evidence_files":len(list((ROOT/"evidence"/"approved").glob("*.json"))) if (ROOT/"evidence"/"approved").is_dir() else 0,
  "live_indiepost_schema_verified":False,
  "idempotency_receipt_store_verified":False,
  "all_tiktok_posts_verified":False,
  "video_reserve_validated":0,
  "live_publish_allowed":False,
}
print(json.dumps(results,indent=2))
assert results["publishing_workflow_is_disabled"],"FAIL_CLOSED_PUBLISHING_WORKFLOW_CHANGED"
assert results["manual_gemini_workflow_exists"] and results["quality_gate_exists"]
print("RESULT=PASS_SAFE_PREP_ONLY")
print("NEXT=CURATED_EVIDENCE_AND_INDIEPOST_READONLY_SCHEMA")
