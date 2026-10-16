#!/usr/bin/env python3
"""Offline concurrency rehearsal using SQLite unique reservations, no PlanVortex calls."""
import concurrent.futures,sqlite3,tempfile,os,hashlib,unittest
def reserve(path,key):
 db=sqlite3.connect(path,timeout=10,isolation_level=None)
 try:
  db.execute("PRAGMA busy_timeout=10000")
  db.execute("INSERT INTO reservations(slot_key) VALUES (?)",(key,))
  return True
 except sqlite3.IntegrityError: return False
 finally: db.close()
class Check(unittest.TestCase):
 def test_24_racing_workers_one_reservation(self):
  with tempfile.TemporaryDirectory() as t:
   path=os.path.join(t,"reservations.sqlite")
   db=sqlite3.connect(path);db.execute("CREATE TABLE reservations(slot_key TEXT PRIMARY KEY)");db.commit();db.close()
   key=hashlib.sha256(b"history|2026-10-16|10").hexdigest()
   with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
    results=list(pool.map(lambda _:reserve(path,key),range(24)))
   self.assertEqual(sum(results),1)
   db=sqlite3.connect(path);count=db.execute("SELECT count(*) FROM reservations").fetchone()[0];db.close()
   self.assertEqual(count,1)
if __name__=="__main__":
 result=unittest.main(exit=False,verbosity=2)
 if not result.result.wasSuccessful():raise SystemExit(1)
 print("RESULT=PASS_SQLITE_CONCURRENCY_REHEARSAL")
 print("PRODUCTION_LOCK_IMPLEMENTED=NO")
 print("UPLOAD=NO")
 print("PUBLICATION=NO")
