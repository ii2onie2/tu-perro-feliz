# Claude Code supervised integration — P4 preflight
Status: PREPARED_NOT_ENABLED
Date: 2026-10-15

## Verified repository facts
- Public GitHub repository, default branch: main.
- Staging branch: integration/indiepost-premium-audit-20261015.
- Existing render workflow writes MP4 commits in main; staging modifications must never affect main.
- Gemini and IndiePost API GET/list model preflights have succeeded; posting is not operational.
- Quality/backlog audits run, but 14-day reserve is empty.

## Official Claude Code requirements still to verify with the owner
1. Install official GitHub Claude app in **these two repositories only**: https://github.com/apps/claude
2. Choose supported Anthropic authentication (API key in secret ANTHROPIC_API_KEY, or authorized OAuth token as documented).
3. Check Anthropic account billing, limits, and actual available subscription entitlements.
4. Configure GitHub Actions permissions minimally and required branch protection.
5. Confirm published Claude Code action version; pin a release or SHA after verification.

## Guardrails for pilot
- Manual trigger only; do not schedule.
- No unrestricted issue/PR comment triggers before abuse review.
- No push to main, no merge, no force push, no deployment, no secrets disclosure.
- No TikTok post creation, IndiePost changes, or Metricool changes.
- No VPS/Veritas access.
- First pilot: read-only repo diagnosis with **contents: read**, output in Actions logs/artifact only.
- Timeouts and max-turn limits; prefer tool restrictions and never expose full model output.
- All billable executions require explicit budget confirmation.
- Only after budget approval and pilot PASS, test issue/PR review; permit draft PR changes only in a separately approved step.

## Financial boundary
- Public GitHub standard hosted runner minutes: currently free under GitHub billing policy.
- Anthropic model/tool tokens may be charged or consume entitlement; no zero-cost guarantee.
- Cost upper bound cannot be established by max-turns alone; provider-side limits needed.
- Gemini free-tier billing separate from Claude Code.

NEXT_ALLOWED=OWNER_SELECTS_ANTHROPIC_AUTH_AND_COST_LIMIT
CLAUDE_EXECUTIONS=0
