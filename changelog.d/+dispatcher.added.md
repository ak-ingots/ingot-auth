The dispatcher of the auth, the slot `dispatcher` of `AuthUnit`,
`BaseAuthDispatcher` of `ingot_auth.dispatchers`, running operations of the
auth in the background, so that a step replies at once:
`dispatch(factory, parameters, metadata)` returns before the operation
ends. In the process, `AuthMemoryDispatcher` of
`ingot_auth.contrib.dispatchers.memory`: an operation run by `run_safe()`
of the runner in a task of asyncio, a failure logged, `join()` waiting for
them. An application declares it in the slot, as the storage and the
cache.
