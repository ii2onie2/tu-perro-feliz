# P3.2 verification — 2026-10-15

Scope: read-only verification of existing GitHub workflow and staging scripts. No VPS, no TikTok publishing, no edits to main.

## Confirmed
- IndiePost account preflight previously succeeded via GitHub Actions (HTTP 200, both TikTok accounts connected).
- Scheduled render jobs on main failed because dated input files are absent.
- render.yml runs on any push touching scripts/**, including staging branches, and its publishing step commits artifacts and executes git pull --rebase origin main; isolate staging tests before continuing.
- scripts/p3_2_prepare_daily_content.py is a draft JSON packager only; no model API, research, fact-checking or autonomous editorial generation.
- scripts/p3_2_daily_preflight.py checks existence and required fields, not historical accuracy or platform queue state.
- Existing validator requires at least 65 words; staging preparer matches this minimum but does not enforce all validator-specific checks.
- No confirmed IndiePost post-creation schema, TikTok privacy settings, production queue reconciliation, or full idempotency guarantees.

## Required bounded gates
1. Separate test-only workflow from render.yml and prevent unintended production repository writes.
2. Align preparer with complete validator rules (including historical/canine subject review and provenance).
3. Prove six dated daily JSON outputs can be produced with real verified evidence; no invented facts.
4. Verify render to MP4 on a no-write staging path.
5. Verify IndiePost API creation semantics and live-state anti-duplicate check before any posting.
6. Authorize a bounded pilot publication after tests; only then activate recurring slots.

RESULT=BLOCKED_PENDING_IMPLEMENTATION_AND_VALIDATION
