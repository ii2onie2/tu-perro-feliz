-- PROPOSAL ONLY / NOT AUTHORIZED FOR EXECUTION
-- Neon production: single-transaction, fail-closed role creation.
-- Run only after a separate explicit permanent-migration authorization.
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';

DO $guard$
BEGIN
 IF current_database() <> 'neondb' THEN
  RAISE EXCEPTION 'BLOCKED: database mismatch';
 END IF;
 IF current_user <> 'neondb_owner' THEN
  RAISE EXCEPTION 'BLOCKED: unexpected migration identity';
 END IF;
 IF to_regclass('tiktok_autopilot.publication_reservations') IS NULL THEN
  RAISE EXCEPTION 'BLOCKED: reservation ledger absent';
 END IF;
 IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='tiktok_reservation_rw' AND NOT rolcanlogin) THEN
  RAISE EXCEPTION 'BLOCKED: expected NOLOGIN grant role absent';
 END IF;
 IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='tiktok_publisher_limited') THEN
  RAISE EXCEPTION 'BLOCKED: target role already exists';
 END IF;
 IF NOT (
   has_schema_privilege('tiktok_reservation_rw','tiktok_autopilot','USAGE')
   AND has_table_privilege('tiktok_reservation_rw','tiktok_autopilot.publication_reservations','SELECT')
   AND has_table_privilege('tiktok_reservation_rw','tiktok_autopilot.publication_reservations','INSERT')
   AND has_table_privilege('tiktok_reservation_rw','tiktok_autopilot.publication_reservations','UPDATE')
   AND NOT has_table_privilege('tiktok_reservation_rw','tiktok_autopilot.publication_reservations','DELETE')
 ) THEN
  RAISE EXCEPTION 'BLOCKED: group role privileges unexpected';
 END IF;
END
$guard$;

CREATE ROLE tiktok_publisher_limited
 LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS
 NOINHERIT;

GRANT tiktok_reservation_rw TO tiktok_publisher_limited
 WITH INHERIT TRUE, SET FALSE, ADMIN FALSE;

DO $verify$
DECLARE
 role_flags record;
BEGIN
 SELECT rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,
        rolpassword IS NULL AS password_absent
 INTO role_flags FROM pg_authid WHERE rolname='tiktok_publisher_limited';
 IF NOT FOUND OR role_flags.rolcanlogin IS DISTINCT FROM TRUE
    OR role_flags.rolsuper IS DISTINCT FROM FALSE
    OR role_flags.rolcreatedb IS DISTINCT FROM FALSE
    OR role_flags.rolcreaterole IS DISTINCT FROM FALSE
    OR role_flags.rolreplication IS DISTINCT FROM FALSE
    OR role_flags.rolbypassrls IS DISTINCT FROM FALSE
    OR role_flags.password_absent IS DISTINCT FROM TRUE THEN
  RAISE EXCEPTION 'BLOCKED: role attributes or password state';
 END IF;
 IF pg_has_role('tiktok_publisher_limited','neon_superuser','MEMBER')
    OR NOT pg_has_role('tiktok_publisher_limited','tiktok_reservation_rw','MEMBER') THEN
  RAISE EXCEPTION 'BLOCKED: membership';
 END IF;
 IF NOT (has_schema_privilege('tiktok_publisher_limited','tiktok_autopilot','USAGE')
   AND has_table_privilege('tiktok_publisher_limited','tiktok_autopilot.publication_reservations','SELECT')
   AND has_table_privilege('tiktok_publisher_limited','tiktok_autopilot.publication_reservations','INSERT')
   AND has_table_privilege('tiktok_publisher_limited','tiktok_autopilot.publication_reservations','UPDATE'))
    OR has_table_privilege('tiktok_publisher_limited','tiktok_autopilot.publication_reservations','DELETE')
    OR has_table_privilege('tiktok_publisher_limited','tiktok_autopilot.publication_reservations','TRUNCATE')
    OR has_schema_privilege('tiktok_publisher_limited','tiktok_autopilot','CREATE')
    OR has_database_privilege('tiktok_publisher_limited',current_database(),'CREATE') THEN
  RAISE EXCEPTION 'BLOCKED: effective permission mismatch';
 END IF;
END
$verify$;

COMMIT;
