#!/usr/bin/env python3
"""Strict PlanVortex list reconciliation policy, offline only, fail closed."""
import unittest
def reconcile(body, account_id, pagination_verified=False):
    if not isinstance(body,dict) or set(body)!={"publications","total"}:
        raise ValueError("BLOCKED_UNKNOWN_RESPONSE_SCHEMA")
    rows=body["publications"]; total=body["total"]
    if not isinstance(rows,list) or type(total) is not int or total<0:
        raise ValueError("BLOCKED_INVALID_LIST_OR_TOTAL")
    if total != len(rows): raise ValueError("BLOCKED_PAGINATION_INCOMPLETE")
    if not pagination_verified: raise ValueError("BLOCKED_PAGINATION_UNVERIFIED")
    if not account_id: raise ValueError("BLOCKED_ACCOUNT_UNKNOWN")
    for row in rows:
        if not isinstance(row,dict) or row.get("account_id")!=account_id:
            raise ValueError("BLOCKED_ACCOUNT_OR_ROW_SCHEMA_UNVERIFIED")
    return True
class Tests(unittest.TestCase):
    def test_empty_response_must_remain_blocked_without_pagination_proof(self):
        with self.assertRaisesRegex(ValueError,"PAGINATION_UNVERIFIED"):
            reconcile({"publications":[],"total":0},"synthetic")
    def test_partial_list_blocked(self):
        with self.assertRaisesRegex(ValueError,"PAGINATION_INCOMPLETE"):
            reconcile({"publications":[],"total":1},"synthetic")
    def test_foreign_account_blocked(self):
        with self.assertRaisesRegex(ValueError,"ACCOUNT_OR_ROW_SCHEMA_UNVERIFIED"):
            reconcile({"publications":[{"account_id":"other"}],"total":1},"synthetic",True)
    def test_verified_empty_synthetic_list_only(self):
        self.assertTrue(reconcile({"publications":[],"total":0},"synthetic",True))
if __name__=="__main__":
    result=unittest.main(exit=False,verbosity=2)
    if not result.result.wasSuccessful():raise SystemExit(1)
    print("RESULT=PASS_FAIL_CLOSED_RECONCILIATION_TESTS")
    print("LIVE_PAGINATION_VERIFIED=NO")
    print("LIVE_ACCOUNT_POST_MATCH_VERIFIED=NO")
    print("UPLOAD=NO")
    print("PUBLICATION=NO")
