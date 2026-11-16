An operator revokes every open session of a profile:
`auth.sessions.op_revoke_all`, `AuthRevokeAllSessionsParameters`, the flag
`CAN_REVOKE` of `auth.sessions` granted by `auth.sessions.grp_admins`,
`auth sessions revoke-all <profile_uid>` on the command line,
`RevokeSessions` of the service `Sessions` over gRPC.
