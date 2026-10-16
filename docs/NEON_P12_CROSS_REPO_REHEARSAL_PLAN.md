# Cross-repository Neon P1.2 coordination test — preparation only
Status: NOT EXECUTED. No permanent DB writes, no PlanVortex calls, no TikTok publishing.

## Verified independent prerequisites
- Both repositories: restricted Neon credential readonly audit PASS.
- Both repositories: concurrent two-session local rehearsal PASS with both ROLLBACK and zero test rows.
- Real cross-repository overlapping executions NOT YET TESTED.

## Proposed synchronized protocol
1. Assign one unique test-id and SAME synthetic organization/account/date/hour to both repository jobs. Never use a real connected account ID.
2. Use an external synchronized start signal/barrier with bounded timeouts. GitHub job starts alone do not guarantee overlap.
3. Repo A obtains INSERT inside explicit transaction and holds it.
4. Repo B attempts an INSERT for same unique (organization_id,account_id,local_date,slot_hour), with lock_timeout and no commit.
5. Assert Repo B is blocked by uniqueness (lock timeout or unique violation), not granted a second reservation.
6. Both workers MUST perform ROLLBACK in finally, including failure and cancellation scenarios.
7. Independently SELECT COUNT(*) for test keys; expect 0.
8. Fail closed on barrier, auth, network, timeout, unexpected insert, or postrollback residue.

## Limitation
Do not claim cross-repo PASS until a synchronized run has actually completed with both GitHub evidence records.
No production publishing and no modification to main.
