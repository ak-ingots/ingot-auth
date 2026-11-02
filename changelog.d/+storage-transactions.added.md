The transactions of the storage, over all the storages of a backend:
`begin()`, `commit()`, `rollback()` and `transaction()` of `AuthStorage`,
the transaction of the current context, a task of asyncio, which the
storages of the backend reach with `get_transaction()`. In memory, a copy
put back on a rollback; in MongoDB, a transaction of a session of the
client, which takes a replica set. The end of a sign-up is one
transaction: a sign-up failing midway leaves nothing. The README lists
the configs of the attempts, `AUTH_ATTEMPT_TTL` and
`AUTH_ATTEMPT_MAX_FAILURES`.
