-- PROPOSAL ONLY. Requires separate explicit DB-write authorization.
-- Create a dedicated Neon login role using Neon Console, with a unique strong password.
-- NEVER paste a password or connection string into source, Actions logs or chat.
-- Replace tiktok_autopilot_login with the actual dedicated login role name after validation.
BEGIN;
GRANT tiktok_reservation_rw TO tiktok_autopilot_login;
COMMIT;
-- Do not grant CREATE, DELETE, TRUNCATE, elevated admin privileges or access to other schemas.
