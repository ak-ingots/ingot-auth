An admin, or a job of a schedule as `auth.system`, sweeps the expired
sessions: `auth.sessions.op_sweep`, the flag `CAN_SWEEP` of `auth.sessions`
granted by `auth.sessions.grp_admins` and `auth.grp_system`,
`auth sessions sweep` on the command line, `SweepSessions` of the service
`Sessions` over gRPC. A storage of the sessions implements
`get_all_open(after, limit)`, the open ones in pages.
