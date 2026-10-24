# P3.14 — TikTok/Metricool pilot release gate (NOT authorization)

## Verified 2026-10-24
- PR #12 is draft and not merged.
- JSON resolver, synthetic MP4 and full Piper/Wikimedia render tests succeeded on 93bae923.
- Metricool brand 7173924 is connected to TikTok account tuperrofelizofficial, timezone Europe/Paris.
- No scheduled posts found for 2026-10-24 through 2026-11-07.
- The render workflow only writes rendered MP4s and metadata to GitHub with an explicitly gated manual write job. This is NOT TikTok publishing.
- The CI integration test renders a historical fixture from 2026-10-09 and does NOT establish fresh editorial readiness.

## Fail-closed bridge contract
1. Input: fresh validated editorial JSON for the target calendar day; never silently reuse historical content.
2. Output: real nonempty MP4, caption, sources, media credits and QC metadata from a successful render run.
3. Verify account: Metricool brand 7173924 and network TikTok; fail if the account differs.
4. Supply a reachable, authorized video URL to Metricool. A GitHub Actions temporary artifact URL or a GitHub repository path is NOT assumed to be a publicly usable media URL.
5. Before scheduling, read current Metricool planned posts for the target slot and inspect any available publication history. Block if same content/slot is present or history cannot be checked adequately.
6. Use a deterministic key from channel + editorial date + slot + content digest; persist evidence of attempts and provider responses before retry. Unknown outcome means STOP, not automatic retry.
7. Initially schedule no more than one video per calendar day; require explicit release authorization. Prefer manual confirmation for the first actual TikTok publication.
8. Verify actual publication in the TikTok/Metricool result, not merely GitHub CI PASS or scheduling success.
9. No tokens or credentials in repository files, CI logs or generated artifacts.
10. Rollback: disable the publishing path and leave the rendering pipeline read-only. Never delete historical posts automatically.

## Unresolved before production
- No proven end-to-end transfer from GitHub-produced MP4 to a Metricool-accessible media URL.
- No implemented idempotent Metricool scheduling connector in the repository.
- No proven real TikTok publish/verification loop.
- Production merger and first scheduled post require separate explicit user authorization.

## Release gate
DO NOT MERGE PR #12 or schedule/publish any TikTok post based on this document alone.
