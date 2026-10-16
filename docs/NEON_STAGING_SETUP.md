# Neon reservation ledger — staging only

The SQL file `sql/neon_reservation_schema_v1.sql` is a **draft**, not an executed migration.

- PostgreSQL UNIQUE constraint provides atomic duplicate prevention across both repos only once both use this shared database.
- Do not run schema migrations yet; first validate Neon connection with a read-only test and agree on migration authorization.
- Add `NEON_DATABASE_URL` separately as a GitHub Actions secret in each repo. Never paste the connection string into chat or logs.
- Prefer a dedicated least-privilege database role over a project owner credential.
- An ephemeral GitHub runner-local SQLite file is not the shared ledger.
- A reservation cannot authorize TikTok publication: editorial/media rights, PlanVortex list reconciliation and publishing API validation remain distinct release gates.
- Do not repurpose Veritas VPS or database.
