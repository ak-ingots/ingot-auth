The server acting by itself is the caller `auth.system`, given by
`AuthCallersProvider.get_auth_system()` what the new group `auth.grp_system`
grants, keeping no members; `AUTH_SYSTEM` of `ingot_auth.activities` is
gone. The records of the activity log written before tell `system`.
