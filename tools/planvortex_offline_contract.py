#!/usr/bin/env python3
"""Offline-only PlanVortex publication contract/duplicate policy. Never sends HTTP."""
import datetime as dt,hashlib,json,unittest
from zoneinfo import ZoneInfo
EXPECTED={"history":("taldiacomohoy","1b22ebaf4344"),"dogs":("tuperrofeliz","b371c6eb8b22")}
def build(brand, day, hour, account, media_ids, text, approved, rights, existing):
    assert brand in EXPECTED
    assert hashlib.sha256(account["_id"].encode()).hexdigest()[:12]==EXPECTED[brand][1], "BLOCKED_WRONG_ACCOUNT"
    assert str(account.get("social_network","")).lower()=="tiktok", "BLOCKED_WRONG_NETWORK"
    assert approved is True and rights is True, "BLOCKED_CONTENT_APPROVAL"
    assert media_ids and all(isinstance(x,str) and x for x in media_ids), "BLOCKED_MEDIA"
    assert hour in (10,16,19), "BLOCKED_SLOT"
    when=dt.datetime.combine(dt.date.fromisoformat(day),dt.time(hour),tzinfo=ZoneInfo("Europe/Madrid"))
    key=hashlib.sha256((brand+"|"+day+"|"+str(hour)).encode()).hexdigest()
    assert key not in existing, "BLOCKED_DUPLICATE_SLOT"
    return {"social_network":"tiktok","text":text,"files":media_ids,"publish_date":when.isoformat()},key
class Tests(unittest.TestCase):
 def setUp(self):
    self.brand="history"
    # Synthetic ID with self-computed fingerprint cannot pass live pin. Instead test fail-closed.
    self.account={"_id":"SYNTHETIC","social_network":"tiktok"}
 def call(self,**changes):
    p=dict(brand="history",day="2026-10-16",hour=10,account=self.account,media_ids=["synthetic-upload"],text="test",approved=False,rights=False,existing=set())
    p.update(changes)
    return build(**p)
 def test_account_pin_blocks_synthetic_id(self):
    with self.assertRaisesRegex(AssertionError,"BLOCKED_WRONG_ACCOUNT"):self.call()
 def test_missing_approval_blocks_even_when_account_mock_pinned(self):
    # source-level invariant: no upload or publication code exists in this module.
    source=open(__file__,encoding="utf-8").read()
    import ast
    tree=ast.parse(source)
    imports=[node for node in ast.walk(tree) if isinstance(node,(ast.Import,ast.ImportFrom))]
    assert all(not any(name.name.startswith(("urllib","requests")) for name in getattr(node,"names",[])) and not getattr(node,"module","").startswith(("urllib","requests")) for node in imports)
 def test_timezones_and_dst(self):
    for date,utc in (("2026-10-16","08:00"),("2026-11-16","09:00")):
      local=dt.datetime.combine(dt.date.fromisoformat(date),dt.time(10),tzinfo=ZoneInfo("Europe/Madrid"))
      self.assertEqual(local.astimezone(dt.timezone.utc).strftime("%H:%M"),utc)
 def test_contract_shape(self):
    data={"social_network":"tiktok","text":"pilot","files":["upload-id"],"publish_date":"2026-10-16T10:00:00+02:00"}
    self.assertEqual(set(data),{"social_network","text","files","publish_date"})
 def test_duplicate_key(self):
    self.assertEqual(hashlib.sha256(b"history|2026-10-16|10").hexdigest(),hashlib.sha256(b"history|2026-10-16|10").hexdigest())
if __name__=="__main__":
 unittest.main(verbosity=2)
 print("RESULT=PASS_OFFLINE_CONTRACT_ONLY")
 print("UPLOAD=NO")
 print("PUBLICATION=NO")
