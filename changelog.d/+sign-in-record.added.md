The record of the sign-ins: a closed session keeps who closed it,
`closed_by` of `AuthSessionRecord`, the uid of the caller, none when it
expired; `storage.sessions.get_all()` gives the sessions of a profile, open
and closed. An operator reads them, `auth.sessions.op_list`, those open or
all of them, `AuthSessionInfo` with no token nor its hash, by the flag
`CAN_LIST` of `auth.sessions`, which `auth.sessions.grp_admins` grants; on
the command line `auth sessions list <uid> --closed`, over gRPC
`ListSessions` of the service `Sessions`, which `AuthGrpcAdminBinding`
serves too, the reason of a closed one a `CloseReason`.
