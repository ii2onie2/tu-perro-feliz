#!/usr/bin/env python3
"""Static-only role grant policy tests; never connects to Neon."""
import pathlib,re,unittest
s=pathlib.Path("sql/neon_role_grants_v1_proposal.sql").read_text()
class RolePolicy(unittest.TestCase):
 def test_no_login_admin_flags(self):
  for token in ("NOLOGIN","NOSUPERUSER","NOCREATEDB","NOCREATEROLE","NOREPLICATION"):
   self.assertIn(token,s)
 def test_grant_scope(self):
  self.assertRegex(s,r"GRANT USAGE ON SCHEMA tiktok_autopilot TO tiktok_reservation_rw")
  self.assertRegex(s,r"GRANT SELECT, INSERT, UPDATE ON TABLE tiktok_autopilot.publication_reservations TO tiktok_reservation_rw")
 def test_no_destructive_statement(self):
  statements=[line.strip().upper() for line in s.splitlines() if line.strip() and not line.lstrip().startswith("--")]
  forbidden=("DROP ","REVOKE ","TRUNCATE ","DELETE ","ALTER SYSTEM","GRANT ALL","GRANT CREATE")
  self.assertFalse(any(any(line.startswith(t) for t in forbidden) for line in statements))
 def test_explicit_proposal(self):
  self.assertIn("PROPOSAL ONLY",s)
if __name__=="__main__":
 result=unittest.main(exit=False,verbosity=2)
 if not result.result.wasSuccessful():raise SystemExit(1)
 print("RESULT=PASS_ROLE_SQL_STATIC_ONLY")
 print("NEON_CONNECTION=NO")
 print("DATABASE_WRITE=NO")
