-- Run separately AFTER an authorized commit; READ ONLY.
BEGIN READ ONLY;
SELECT r.rolname,r.rolcanlogin,r.rolsuper,r.rolcreatedb,r.rolcreaterole,
 r.rolreplication,r.rolbypassrls,
 pg_has_role(r.rolname,'tiktok_reservation_rw','MEMBER') AS member_of_rw,
 pg_has_role(r.rolname,'neon_superuser','MEMBER') AS member_of_elevated,
 has_table_privilege(r.rolname,'tiktok_autopilot.publication_reservations','SELECT') AS can_select,
 has_table_privilege(r.rolname,'tiktok_autopilot.publication_reservations','INSERT') AS can_insert,
 has_table_privilege(r.rolname,'tiktok_autopilot.publication_reservations','UPDATE') AS can_update,
 has_table_privilege(r.rolname,'tiktok_autopilot.publication_reservations','DELETE') AS can_delete,
 has_table_privilege(r.rolname,'tiktok_autopilot.publication_reservations','TRUNCATE') AS can_truncate,
 has_schema_privilege(r.rolname,'tiktok_autopilot','CREATE') AS schema_create,
 has_database_privilege(r.rolname,current_database(),'CREATE') AS database_create
FROM pg_roles r WHERE r.rolname='tiktok_publisher_limited';
ROLLBACK;
