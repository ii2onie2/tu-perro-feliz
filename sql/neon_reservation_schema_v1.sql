-- TikTok autopilot reservation ledger, PROPOSAL ONLY. Do not run until reviewed.
BEGIN;
CREATE SCHEMA IF NOT EXISTS tiktok_autopilot;
CREATE TABLE IF NOT EXISTS tiktok_autopilot.publication_reservations (
  reservation_key text PRIMARY KEY,
  channel text NOT NULL CHECK (channel IN ('history','dogs')),
  organization_id text NOT NULL,
  account_id text NOT NULL,
  local_date date NOT NULL,
  slot_hour smallint NOT NULL CHECK (slot_hour IN (10,16,19)),
  timezone text NOT NULL DEFAULT 'Europe/Madrid' CHECK (timezone='Europe/Madrid'),
  scheduled_at_utc timestamptz NOT NULL,
  content_sha256 char(64) NOT NULL,
  media_sha256 char(64) NOT NULL,
  github_run_id bigint,
  state text NOT NULL DEFAULT 'RESERVED' CHECK (state IN ('RESERVED','SUBMITTED','CONFIRMED','UNKNOWN','CANCELLED')),
  provider_publication_id text UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, account_id, local_date, slot_hour)
);
COMMIT;
