# IndiePost + premium video migration (staging only)

Repository: ii2onie2/tu-perro-feliz
Date: 2026-10-15
Status: PREPARATION_ONLY; NO_PRODUCTION_ACTIVATION

## Target
- TikTok brand: @tuperrofelizofficial
- Timezone: Europe/Madrid (DST-aware)
- Intended schedule: 10:00 / 16:00 / 19:00, Monday-Sunday
- End date: 2030-12-31
- Source of truth: verified TikTok published posts + IndiePost pending queue; compare Metricool legacy queue before cutover.

## Verified existing pipeline
- .github/workflows/render.yml uses FFmpeg, Piper Spanish voice, validates JSON inputs, and renders MP4/captions.
- Scheduled render expects exactly three date-stamped content files; absent input is a hard failure.
- .github/workflows/publish-trypost.yml currently is manual-only and disabled.

## Migration release gates (fail closed)
1. Confirm IndiePost plan, API rate limits, media limits, and TikTok publish/privacy semantics.
2. Provision INDIEPOST_API_KEY in repository secrets via authorized secure GitHub UI; never commit token.
3. Obtain complete IndiePost v1 POST media/posts schema and test against a controlled non-publishing path.
4. Query all queued/published items in IndiePost, TikTok and legacy Metricool for the same identity/date/slot. Any ambiguity => no write.
5. Require exact workspace/platform/user match, explicit schedule offset Europe/Madrid, immutable content hash/idempotency marker.
6. Generate new scripts or missing dated content only with verifiable provenance; never regenerate/overwrite a valid published asset.
7. Preserve existing render.yml until premium media and automated content generation pass offline tests.
8. Paid Google Veo / Flow API is not verified. Only user-provided clips or proven authorized API/fallback pipeline may be used.
9. Controlled one-post end-to-end test, verify TikTok published ID and visibility before enabling recurring automation.
10. Do not push to main or automatically publish unless all guards pass; no force push or deletion of valid content.

## Current known blockers
- IndiePost is not connected as an app to this conversation; the API authentication was tested by the user on their own computer, but the API key is not available to GitHub or the assistant.
- Google Flow free UI is manual; no automated Nano Banana/Veo API credentials verified.
- No TikTok post-state cross-check currently available via connected tools.

No secrets or production automation are changed by this file.
