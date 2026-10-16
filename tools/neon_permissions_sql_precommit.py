#!/usr/bin/env python3
"""Neon precommit READ-ONLY privilege and SQL inventory inspection. No DDL."""
import hashlib,os,pathlib,sys
import psycopg
from psycopg.conninfo import conninfo_to_dict
path=pathlib.Path("sql/neon_reservation_schema_v1.sql")
sql=path.read_bytes()
sha=hashlib.sha256(sql).hexdigest()
print("DDL_SHA256="+sha)
assert sql.startswith(b"-- TikTok autopilot reservation ledger, PROPOSAL ONLY.")
assert b"UNIQUE (organization_id, account_id, local_date, slot_hour)" in sql
assert b"provider_publication_id text UNIQUE" in sql
assert b"BEGIN;" in sql and sql.rstrip().endswith(b"COMMIT;")
dsn=os.getenv("NEON_DATABASE_URL","")
if not dsn:raise SystemExit("BLOCKED_DSN_MISSING")
if conninfo_to_dict(dsn).get("sslmode") not in ("require","verify-full","verify-ca"):raise SystemExit("BLOCKED_SSL")
try:
 with psycopg.connect(dsn,connect_timeout=15,options="-c default_transaction_read_only=on") as conn:
  conn.read_only=True
  with conn.cursor() as c:
   c.execute("""SELECT current_setting('transaction_read_only'),
      current_user, current_database(),
      rolsuper, rolcreatedb, rolcreaterole, rolreplication, rolbypassrls
      FROM pg_roles WHERE rolname=current_user""")
   row=c.fetchone()
   if not row or row[0]!="on":raise RuntimeError("NOT_READ_ONLY")
   _,role,database,*flags=row
   print("ROLE_FLAGS="+",".join(["rolsuper","rolcreatedb","rolcreaterole","rolreplication","rolbypassrls"][i]+"="+str(x).upper() for i,x in enumerate(flags)))
   c.execute("""SELECT has_database_privilege(current_user,current_database(),'CREATE'),
      has_schema_privilege(current_user,'public','CREATE'),
      to_regnamespace('tiktok_autopilot') IS NOT NULL,
      to_regclass('tiktok_autopilot.publication_reservations') IS NOT NULL""")
   dbcreate,pubcreate,schema_exists,table_exists=c.fetchone()
   print("ROLE_CAN_CREATE_IN_DB="+str(dbcreate).upper())
   print("ROLE_CAN_CREATE_IN_PUBLIC="+str(pubcreate).upper())
   print("NAMESPACE_EXISTS="+str(schema_exists).upper())
   print("TABLE_EXISTS="+str(table_exists).upper())
   if table_exists:raise RuntimeError("TABLE_ALREADY_EXISTS")
   print("NEON_READ_ONLY_CHECK=PASS")
   print("ROLE_LEAST_PRIVILEGE_VERIFIED="+("YES" if not any(flags) and not dbcreate and not pubcreate else "NO"))
   print("PERMANENT_MIGRATION=NOT_AUTHORIZED")
   print("DATABASE_WRITE=NO")
   print("RESULT=PASS_PRECOMMIT_INSPECTION")
except Exception as e:
 print("RESULT=BLOCKED_PRECOMMIT_INSPECTION")
 print("ERROR_CLASS="+type(e).__name__)
 sys.exit(1)
