# PlanVortex Shared Reservation Store — Design Gate (No production writes)

## Decision
Use a durable transactional store with a UNIQUE constraint for (organization_id, account_id, local_date, slot_hour). A GitHub Actions concurrency group serializes cooperating jobs but does not persist reservations and cannot substitute for a transaction.

## Required table
- reservation_key: SHA256(org|account|local_date|slot_hour), PRIMARY KEY
- organization_id and provider_account_id (access controlled)
- local_date, slot_hour (10/16/19), scheduled_utc, timezone (Europe/Madrid)
- content_sha256, asset_sha256, github_run_id
- state: RESERVED, SUBMITTED, CONFIRMED, UNKNOWN, CANCELLED
- provider_publication_id nullable, created_at, updated_at
- UNIQUE(organization_id, provider_account_id, local_date, slot_hour)
- Separate provider publication identifier uniqueness when present

## Fail-closed decision
1. Fetch verified TikTok account; pin to known live fingerprint.
2. Read all PlanVortex pages and verify every publication account mapping and status. If pagination cannot be established, STOP.
3. Begin durable transaction; atomically reserve the key (compare-and-insert) or reject duplicate.
4. Require approval, media-rights proof, MP4 readiness, write-contract validation and an explicitly approved release switch.
5. Never blindly repeat publish after timeout: mark UNKNOWN and reconcile remote state before retry.
6. Explicitly verify scheduled post exists and record provider ID before marking CONFIRMED.

## Current gates
LIVE_LIST_PAGINATION=UNVERIFIED (total=0 from both accounts on 2026-10-16)
DURABLE_STORE_SELECTED=NO
DURABLE_STORE_DEPLOYED=NO
LIVE_PUBLISH=DISABLED
API_WRITE=NO
MAIN_BRANCH=UNCHANGED

## Environment choice
A shared PostgreSQL or hosted transactional DB can satisfy atomic uniqueness if both repositories have scoped access. Do NOT assume current VPS/Veritas DB may be reused; no database access, provisioning, or writes are authorized as part of this design.
