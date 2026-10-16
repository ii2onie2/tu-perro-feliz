-- PROPOSAL ONLY: run manually under a separately authorized migration.
-- The privileged admin creates a NOLOGIN group role; application login credentials
-- must be provisioned separately and never stored in GitHub source.
BEGIN;
CREATE ROLE tiktok_reservation_rw NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
-- The schema and table must already exist. Do not run this before ledger migration.
GRANT USAGE ON SCHEMA tiktok_autopilot TO tiktok_reservation_rw;
GRANT SELECT, INSERT, UPDATE ON TABLE tiktok_autopilot.publication_reservations TO tiktok_reservation_rw;
-- No DELETE, TRUNCATE, CREATE ON SCHEMA, database CREATE or role admin grants.
COMMIT;
