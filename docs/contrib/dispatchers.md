# Dispatchers

The dispatcher runs operations of the auth in the background, so that a
step replies at once: the mail of the code of a sign-up or a sign-in by
email, and the word of a sign-in closed. `BaseAuthDispatcher` of
`ingot_auth.dispatchers` is the facade, the slot `dispatcher` of the auth:
`dispatch(factory, parameters, metadata)` runs an operation as the runner
does, for the caller of the metadata, and returns before it ends. The
method of the email sends its mail so: `AuthSendCodeOperation` and
`AuthSendDenialOperation`, in its slots `op_send_code` and
`op_send_denial`, build the mail by the hooks of the method and hand it to
the mailer ({doc}`mailers`); their parameters keep the email and the code
out of their `repr`, as the runner logs them.

## In the process

`AuthMemoryDispatcher` of `ingot_auth.contrib.dispatchers.memory`, with no
extra: an operation runs by `run_safe()` of the runner in a task of
asyncio, held until it ends; a failure is logged by the runner, at
`WARNING`, and fails nothing else, the attempt staying.

```python
from ingot_auth.contrib.dispatchers.memory import AuthMemoryDispatcher


class AppAuthUnit(AuthUnit):
    dispatcher = Slot(AuthMemoryDispatcher)
```

An operation is lost if the process stops before it ends: the user starts
the flow again. `join()` waits for the operations dispatched so far to end,
and for those they dispatch: for a shutdown, a test.

A dispatcher on a queue, a backend of its own, serializes the path of the
factory, the parameters and the metadata for a worker that runs the same
operation. A code then goes through the queue: keep it there a short time,
the TTL of the attempt at most, or encrypt it.
