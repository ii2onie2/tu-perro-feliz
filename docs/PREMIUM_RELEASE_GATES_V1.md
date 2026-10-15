# Premium pilot release gates — staging only
- Storyboard V1.4: synthetic-manifest-only tests PASS, not a real rendered MP4 comparison.
- Before media comparison: use a real licensed image and a real existing narration; compare original and modified MP4 for synchronization, sound and clipping.
- Gemini: requires at least two documented source references with verified facts; the manual single-draft workflow does nothing until explicitly dispatched. Generated output status remains UNVERIFIED_DRAFT and requires editorial review.
- Publishing: TryPost placeholder is disabled; IndiePost publication schema, rate limits, account identity, idempotency key and scheduling semantics are not verified. NO LIVE POST.
- Reserve: target 42 per account, no prepopulation from unverified scripts. Never declare existing old assets to be a validated 14-day reserve.
- No writes to main, no production enablement, no paid Anthropic calls.
NEXT_ALLOWED=EVIDENCE_REVIEW_AND_REAL_MP4_COMPARISON
