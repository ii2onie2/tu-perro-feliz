#!/usr/bin/env python3
"""Offline persistent dedup proof; SQLite state is shared ONLY within one runner workspace.
Not a cross-run or cross-host production lock. No network and no publication."""
import concurrent.futures,hashlib,os,sqlite3,tempfile,unittest
def reserve(db_path,channel,day,slot):
    key=hashlib.sha256(f"{channel}|{day}|{slot}".encode()).hexdigest()
    with sqlite3.connect(db_path,timeout=15) as db:
        db.execute("INSERT OR IGNORE INTO reservations (slot_key) VALUES (?)",(key,))
        return db.execute("SELECT changes()").fetchone()[0]==1
class Tests(unittest.TestCase):
    def test_persists_after_reopening_and_blocks_racers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=os.path.join(tmp,"persistent.sqlite3")
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE reservations (slot_key TEXT PRIMARY KEY)")
            with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
                results=list(pool.map(lambda n: reserve(path,"history","2026-10-16",10),range(24)))
            self.assertEqual(sum(results),1)
            self.assertFalse(reserve(path,"history","2026-10-16",10))
            self.assertTrue(reserve(path,"history","2026-10-16",16))
            self.assertTrue(reserve(path,"dogs","2026-10-16",10))
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM reservations").fetchone()[0],3)
if __name__=="__main__":
    outcome=unittest.main(exit=False,verbosity=2)
    if not outcome.result.wasSuccessful():raise SystemExit(1)
    print("RESULT=PASS_LOCAL_PERSISTENCE_ONLY")
    print("CROSS_RUN_ATOMIC_LOCK=NOT_IMPLEMENTED")
    print("PLANVORTEX_EXISTING_POST_COMPARISON=NOT_IMPLEMENTED")
    print("UPLOAD=NO")
    print("PUBLICATION=NO")
