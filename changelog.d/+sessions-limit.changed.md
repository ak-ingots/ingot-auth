The sessions of a profile are limited: `AUTH_SESSIONS_MAX`, 10 by
default, set by the operator, and the strategy in the new slot `limit` of
the sessions, which has none, so that an application declares one:
`AuthEvictOldestLimit` signs out the sessions seen longest ago, `evicted`,
a new action `evict` in the activity log; `AuthRefuseLimit` refuses the
sign-in, `AuthSessionsLimitError`, over gRPC `RESOURCE_EXHAUSTED`,
`SESSIONS_LIMIT`; `AuthNoLimit` keeps any number. An expired session
takes no room. `get_open` of the storage of the sessions gives them in no
order.
