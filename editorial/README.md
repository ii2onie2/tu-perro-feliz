# Daily editorial approval queue

This directory holds date-specific Spanish editorial JSON packages that have been reviewed and approved for Tu Perro Feliz.

## Workflow
1. Prepare a new file at `editorial/approved/YYYY-MM-DD.json` using the existing `content/2026-10-25.json` structure.
2. Verify all factual claims against the cited sources; ensure media provenance, license and attribution are accurate. Do not invent sources, URLs or media.
3. Use the same date in the file name and `date` field. Check originality and avoid recycling previously published topics.
4. Run `python scripts/stage_daily_content.py --date YYYY-MM-DD --dry-run` to check readiness.
5. For local staging only, run without `--dry-run` and review the result with `python scripts/validate_content.py content/YYYY-MM-DD.json`.
6. Submit the validated content file for review before merging to main.

## Current operating state
- No approved queue entries exist yet; missing dates must fail closed.
- The manual GitHub Actions preflight is read-only.
- No scheduled content generator, autonomous factual research, repository writes, Buffer drafts or TikTok publication are enabled by this queue.
- Do not backfill missing days with old content or treat a draft as reviewed merely because it passes schema checks.
