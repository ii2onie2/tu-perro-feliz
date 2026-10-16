# Neon V1 — bounded rollout order (PREPARATION ONLY)

## Immutable inputs
Ledger: sql/neon_reservation_schema_v1.sql
Role grants: sql/neon_role_grants_v1_proposal.sql

## Ordered preflight and migration proposal
0. Re-check Neon project, database, connection identity, role powers and absence of ledger and group role. Capture baseline and SQL SHA256.
1. Explicitly authorize a narrowly bounded migration and credentials plan.
2. Apply ledger DDL as a single transaction; validate constraints before COMMIT. Do not run from both repositories.
3. Create NOLOGIN group role in a separate controlled migration, AFTER the ledger table exists; apply USAGE/SELECT/INSERT/UPDATE grants.
4. Provision an individual LOGIN role with strong rotated credentials and membership in group role; do not embed credentials in SQL or logs. Switch both CI secrets away from neondb_owner.
5. Inspect actual effective permissions for application login; should have no DB/schema CREATE, no role admin, no DELETE/TRUNCATE.
6. Rehearse atomic duplicate reservations from both repositories with ROLLBACK and verify zero persisted test rows.
7. Keep write publishing blocked until provider pagination/identity reconciliation and editorial/media rights pass.

## Rollback policy
Before COMMIT any failing transaction must ROLLBACK.
After COMMIT do not drop schema/tables blindly: inspect data/dependencies and back up before separately authorized remediation.

## Stop gates
ROLE_AND_TABLE_CREATION=NOT_AUTHORIZED
NEON_WRITES=NONE
PUBLISHING=DISABLED
