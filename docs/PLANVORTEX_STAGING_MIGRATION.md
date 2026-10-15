# PlanVortex transition — STAGING ONLY

Decision: PlanVortex is preferred candidate. This file does NOT authorize activation or public posting.

Official vendor URLs:
- https://planvortex.com/pricing
- https://planvortex.com/en/developers
- https://planvortex.com/documentation
- Base URL advertised: https://api.planvortex.com/v1.0.0

Verified published Free claims (2026-10-15):
- EUR 0, 3 connected social accounts, unlimited posts, 1 GB shared storage, 1 app for API, rate limits differ by plan.
- These are vendor claims, not yet verified for the user's account.
- Confirm TikTok account compatibility, direct video scheduling, video upload size/retention, permission scopes and API authentication before any write.

Published API endpoints (authentication and schemas must be confirmed with official OpenAPI):
- GET /organizations/{id_organization}/accounts
- POST /organizations/{id_organization}/uploads
- POST /organizations/{id_organization}/accounts/{id_account}/publish
- GET /organizations/{id_organization}/publish
- GET /organizations/{id_organization}/limits

Migration rollout:
1. Keep Metricool/IndiePost untouched while evaluating PlanVortex.
2. Create a PlanVortex Free account and one API app (manual user action). Never request credentials in chat.
3. Connect only the two TikTok accounts using vendor OAuth, keeping current publisher active.
4. Put OAuth client ID/secret in GitHub Actions secrets, not tracked files.
5. Verify authenticated GET accounts and limits, log IDs masked where practical.
6. Verify official upload/publish schema, scheduled local times Europe/Madrid / conversion to UTC, and TikTok video support.
7. Run offline dry run with a verified media-rights and editorial safety gate, no POST.
8. Explicitly approve first PUBLIC pilot and check actual TikTok publication, duplication, provider receipt and status.
9. Only then disable old scheduler and enable PlanVortex. Never allow two active automatic schedulers for same slot.
10. Free-tier storage budget must be quantified: 84 MP4s may exceed 1 GB; schedule with bounded rolling uploads and deletion only after final posting and proof. Do not assume storage is unlimited.

Current: NO_PLANVORTEX_CREDENTIALS; NO_CONNECTED_ACCOUNTS_CONFIRMED; NO_PLANVORTEX_POST; NO_MAIN_CHANGES; NO_PAID_PLAN.
