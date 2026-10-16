#!/usr/bin/env python3
"""Neon read-only connection preflight. Never print DSN, host or credentials."""
import hashlib,os,sys
url=os.environ.get("NEON_DATABASE_URL","")
if not url: raise SystemExit("RESULT=BLOCKED_MISSING_NEON_DATABASE_URL")
if not url.startswith(("postgresql://","postgres://")):raise SystemExit("RESULT=BLOCKED_BAD_DSN_SCHEME")
try:
 import psycopg
 from psycopg.conninfo import conninfo_to_dict
 details=conninfo_to_dict(url)
 if details.get("sslmode") not in ("require","verify-full","verify-ca"):raise ValueError("SSL_REQUIRED")
 with psycopg.connect(url,connect_timeout=15,options="-c default_transaction_read_only=on") as conn:
  conn.read_only=True
  with conn.cursor() as cur:
   cur.execute("SELECT current_database(), current_user, current_setting('transaction_read_only'), current_setting('server_version_num')")
   database,user,readonly,version=cur.fetchone()
   if readonly!="on":raise ValueError("NOT_READ_ONLY")
   identity=hashlib.sha256((database+"|"+user+"|"+details.get("host","")).encode()).hexdigest()[:16]
   print("NEON_CONNECTION=PASS")
   print("READ_ONLY=YES")
   print("DB_ROLE_HOST_FINGERPRINT="+identity)
   print("POSTGRES_MAJOR="+str(int(version)//10000))
   print("SCHEMA_WRITE=NO")
   print("RESULT=PASS_READ_ONLY_NEON_PREFLIGHT")
except Exception as e:
 print("RESULT=BLOCKED_NEON_PREFLIGHT")
 print("ERROR_CLASS="+type(e).__name__)
 sys.exit(1)
