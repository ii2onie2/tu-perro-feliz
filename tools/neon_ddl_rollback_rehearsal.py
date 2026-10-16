#!/usr/bin/env python3
"""Neon PostgreSQL transactional DDL rehearsal: always ROLLBACK; no permanent schema."""
import os,sys
import psycopg
from psycopg.conninfo import conninfo_to_dict
from pathlib import Path
dsn=os.getenv("NEON_DATABASE_URL","")
if not dsn:raise SystemExit("BLOCKED_DSN_MISSING")
if conninfo_to_dict(dsn).get("sslmode") not in ("require","verify-full","verify-ca"):raise SystemExit("BLOCKED_SSL")
sql=Path("sql/neon_reservation_schema_v1.sql").read_text()
if not sql.startswith("-- TikTok autopilot reservation ledger, PROPOSAL ONLY."):raise SystemExit("BLOCKED_UNKNOWN_SQL")
# Strip BEGIN/COMMIT so transaction is controlled by this program only.
sql=sql.replace("\nBEGIN;\n","\n",1)
if not sql.rstrip().endswith("COMMIT;"):raise SystemExit("BLOCKED_SQL_BOUNDARY")
sql=sql.rstrip()[:-len("COMMIT;")]
conn=None
try:
 conn=psycopg.connect(dsn,connect_timeout=15,autocommit=False)
 with conn.cursor() as cur:
  cur.execute("SET LOCAL statement_timeout = '10s'")
  cur.execute(sql)
  cur.execute("SELECT to_regclass('tiktok_autopilot.publication_reservations') IS NOT NULL")
  if not cur.fetchone()[0]:raise RuntimeError("REHEARSAL_TABLE_NOT_VISIBLE")
 print("DDL_REHEARSAL=PASS")
except Exception as e:
 print("DDL_REHEARSAL=FAIL")
 print("ERROR_CLASS="+type(e).__name__)
 sys.exit(1)
finally:
 if conn is not None:
  conn.rollback()
  conn.close()
print("TRANSACTION=ROLLBACK")
print("PERMANENT_SCHEMA_CREATED=NO")
print("RESULT=PASS_DDL_REHEARSAL_ONLY")
