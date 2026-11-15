The sessions of a user's own: `auth.sessions.op_list_own`, its open
sessions, each with its public id, the values of its attributes, the times
it opened and was seen at, the current one marked; `op_revoke_own`, closing
one, `REVOKED`, a session of another, closed or unknown not found,
`AuthOwnSessionNotFoundError`; `op_revoke_others`, closing all but the
current one and telling how many. The flags `CAN_LIST_OWN` and
`CAN_REVOKE_OWN` of `auth.sessions`, `AuthSessionsPermissions`, which
`auth.grp_signed_in` grants. Over gRPC, the service `Sessions` of
`ingot_auth.sessions.v1`, in `AuthGrpcSessionsBinding`, an own session not
found `NOT_FOUND`, `OWN_SESSION_NOT_FOUND`.
