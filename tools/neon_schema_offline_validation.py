#!/usr/bin/env python3
"""Offline SQL shape checks; does not connect to Neon or execute SQL."""
import pathlib,re,unittest
sql=pathlib.Path("sql/neon_reservation_schema_v1.sql").read_text()
class Tests(unittest.TestCase):
 def test_transaction(self):
  self.assertRegex(sql,r"(?im)^BEGIN;$")
  self.assertRegex(sql,r"(?im)^COMMIT;$")
 def test_atomic_uniqueness(self):
  self.assertIn("reservation_key text PRIMARY KEY",sql)
  self.assertIn("UNIQUE (organization_id, account_id, local_date, slot_hour)",sql)
  self.assertIn("provider_publication_id text UNIQUE",sql)
 def test_account_slot_and_states(self):
  for word in ("CHECK (channel IN ('history','dogs'))","CHECK (slot_hour IN (10,16,19))","Europe/Madrid","'UNKNOWN'","'CONFIRMED'"):
   self.assertIn(word,sql)
 def test_no_destructive_sql(self):
  for word in ("DROP TABLE","TRUNCATE","DELETE FROM","ALTER TABLE"):
   self.assertNotIn(word,sql.upper())
 def test_explicit_nonproduction(self):
  self.assertTrue(sql.startswith("-- TikTok autopilot reservation ledger, PROPOSAL ONLY."))
if __name__=="__main__":
 result=unittest.main(exit=False,verbosity=2)
 if not result.result.wasSuccessful():raise SystemExit(1)
 print("RESULT=PASS_OFFLINE_SQL_SHAPE")
 print("NEON_CONNECT=NO")
 print("DATABASE_WRITE=NO")
 print("MIGRATION_EXECUTED=NO")
