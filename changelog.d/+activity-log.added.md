The activity log, by ADR 0015 of the ecosystem: `auth.activities`,
`AuthActivitiesUnit`, `record()` writing a record a change of state of an
entity in the transaction of the change, `AuthActivityRecord`: the actor,
`who` and `session_uid`, the action, `AuthActivityAction`, the type of the
entity, the full name of its unit, its id, an optional context, a
dataclass extending `AuthActivityContext` kept as a map of its attributes,
the uid of the run and the time. A failure to write it is for the strategy
in the slot `failure`, `AuthStrictActivityFailure`, failing the change, or
`AuthSwallowActivityFailure`, logging it. The auditors,
`auth.activities.grp_auditors`, read it by the flag `CAN_READ` of
`auth.activities`, `op_list`, `auth activities list` on the command line,
`ListActivities` of the service `Activities` over gRPC. The storage
`storage.activities`, `BaseAuthActivitiesStorage`, in memory and in MongoDB,
with its contract. The registries record their items created, renamed and
deleted, an attribute created with its name and type.
