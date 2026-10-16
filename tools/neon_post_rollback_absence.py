#!/usr/bin/env python3
"""Independent read-only Neon post-rollback check; no DDL."""
import os,sys,psycopg
url=os.getenv("NEON_DATABASE_URL","")
if not url:raise SystemExit("BLOCKED_MISSING_DSN")
try:
 with psycopg.connect(url,connect_timeout=15,options="-c default_transaction_read_only=on") as conn:
  conn.read_only=True
  with conn.cursor() as cur:
   cur.execute("SELECT to_regclass('tiktok_autopilot.publication_reservations')")
   result=cur.fetchone()[0]
   cur.execute("SELECT current_setting('transaction_read_only')")
   if cur.fetchone()[0]!="on":raise RuntimeError("NOT_READ_ONLY")
 if result is not None:raise RuntimeError("TABLE_EXISTS_ABORT")
 print("READ_ONLY=YES")
 print("RESERVATION_TABLE=ABSENT")
 print("RESULT=PASS_POST_ROLLBACK_ABSENCE")
except Exception as e:
 print("RESULT=BLOCKED_POST_ROLLBACK")
 print("ERROR_CLASS="+type(e).__name__)
 sys.exit(1)
