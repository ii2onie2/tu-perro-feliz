# Neon least-privilege login — approval gate

Current verified state: table tiktok_autopilot.publication_reservations and NOLOGIN group tiktok_reservation_rw exist. Production publishing is OFF.

## Next operations (NOT EXECUTED)
1. Via Neon Console, provision a **separate LOGIN credential** for TikTok autopilot; save credentials only in secure storage. Check Neon-generated role privileges before proceeding.
2. Review and authorize the one-line group membership grant in sql/neon_login_membership_proposal.sql, using the exact verified role name.
3. Verify effective LOGIN permissions: schema USAGE and table SELECT/INSERT/UPDATE only, no DELETE, no schema CREATE, no database CREATE, no admin role privileges. Test with read-only catalog queries.
4. Only after that, replace the two GitHub NEON_DATABASE_URL secrets with the least-privilege login's secure connection string. Never paste it in chat.
5. Verify both read-only connections again before testing transactional reservations.

## Current stop gates
LOGIN_ROLE_CREATED=NO
GRANT_EXECUTED=NO
NEON_SECRETS_CHANGED=NO
PUBLISHING_ENABLED=NO
