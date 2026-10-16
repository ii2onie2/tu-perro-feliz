# PlanVortex publication deduplication — staging design (NOT LIVE)

Current state: account identity read-only PASS; GET /organizations/{org}/publish HTTP 200; local SQLite reservation tests PASS; GitHub concurrency group configured for disabled placeholder and separate safety workflow. Publishing remains disabled.

## Critical limitations

* GitHub concurrency only serializes runs that use the identical concurrency group; it is not a durable reservation database or an idempotency guarantee after retries.
* A SQLite file on an ephemeral GitHub runner does not persist between workflow runs or across repositories.
* Do not use uploaded artifact files or cache as a transactional lock.
* GET publications returning HTTP 200 is not proof that all pages, statuses, dates and per-account associations are understood. No write may occur based on an ambiguous response.
* Publishing request shape was not tested against the provider using a write request.

## Proposed fail-closed flow

1. Compute slot_key from organization/account internal ID + Europe/Madrid local date and slot; compute distinct media-content SHA256 for asset reuse detection.
2. Load the existing PlanVortex publications **for the exact bound TikTok account**, traverse pagination, verify statuses, timezones and all pending/scheduled entries. Fail closed if response schema, status or pagination is unknown.
3. Acquire an **atomic durable reservation in a shared database** keyed by account ID + slot; unique key/transactional compare-and-insert required. Store content digest, GitHub run ID, lease owner, intended UTC and local publish dates, provider post ID and state. Do not claim protection based only on workflow concurrency.
4. Reconcile existing scheduled posts and reservations, then atomically reserve; only then allow an upload if source and media rights and publishing approvals are true.
5. On upload/publish timeouts, mark UNKNOWN and **reconcile from PlanVortex** before retrying; never retry a potentially successful non-idempotent POST blindly.
6. Require separate validation of PlanVortex upload/publish contract, protected release and the real end-to-end test before enabling.

## Current release gates

- STAGING_ONLY=YES
- PLANVORTEX_UPLOAD_ENABLED=NO
- PLANVORTEX_PUBLISH_ENABLED=NO
- DURABLE_CROSS_RUN_RESERVATION=NOT_IMPLEMENTED
- PLANVORTEX_PUBLICATION_LIST_RECONCILIATION=NOT_VERIFIED
- CONTENT_AND_MEDIA_RIGHTS=NOT_APPROVED
