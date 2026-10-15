# Gemini + IndiePost unblock checklist (staging, 2026-10-15)

## Verified
- Gemini model listing preflight PASS. This does not prove a successful generateContent request.
- IndiePost GET /api/v1/accounts preflight PASS, TikTok accounts taldiacomohoy09 and tuperrofelizofficial connected. This does not prove posting permission or scheduling.
- Existing render and premium audio tests PASS on previously dated content.
- Backlog 2026-10-16 through 2026-10-29: 0/42 approved videos per account.
- Production main unchanged. Existing TryPost workflow remains disabled.

## Blocker G1: Gemini input evidence
Workflow gemini-single-draft-manual.yml requires a committed evidence JSON with:
  topic; manual_review_approved=true; >=2 sources each with https url and nonempty facts.
No approved evidence has been established in this workstream. Do not set manual_review_approved=true on model-generated or unverified facts.
Once reviewed evidence is committed, execute ONE gemini-2.5-flash-lite generateContent test with a free-tier project and no paid upgrade; label the output UNVERIFIED_DRAFT; validate fields, length and novelty.
The workflow_dispatch workflow exists only on staging. GitHub may require dispatch workflow registration on the default branch; do not enable it by secretly writing main. If unavailable, arrange an explicitly approved safe trigger on default branch, or request manual local test with approved inputs.

## Blocker I1: IndiePost publishing contract
Only GET /api/v1/accounts was confirmed. Obtain authoritative API documentation for upload, schedule/create, status/read-back, authorization, TikTok account IDs, quotas, public video URL, idempotency and scheduling timezone.
Do not guess endpoints or POST schemas. Do not use TryPost endpoints as IndiePost endpoints. Do not remove Metricool.

## Mandatory release gates
1. Two independently verified factual sources for the scenario (editorial accuracy).
2. Documented media permission or license with source attribution.
3. JSON schema/quality PASS; no duplicate title, narration or already scheduled slot.
4. Actual MP4 probe PASS; visual/audio spot-check PASS.
5. Account handle, Europe/Madrid timestamp and duplicate key locked before a POST.
6. Exactly one staging pilot with explicit real-post permission, followed by provider receipt, id and final TikTok read-back.
7. Only after successful pilot per channel consider 10:00/16:00/19:00 daily schedule.

NO_AUTOMATIC_POST=true
NO_ANTHROPIC_CALLS=true
NO_PRODUCTION_MERGE=true
