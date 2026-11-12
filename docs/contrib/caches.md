# Caches

The cache keeps what lives minutes, not years: the attempts of a sign-up,
a sign-in waiting for an answer, the open sessions a request finds before
the storage, and their callers. `AuthCache` is the facade, its slots
`attempts`, `sessions` and `callers` each abstract; a backend fills them
all.

## In memory

`AuthMemoryCache` of `ingot_auth.contrib.caches.memory`, with no extra:

```python
from ingot_auth.contrib.caches.memory import AuthMemoryCache


class AppAuthUnit(AuthUnit):
    cache = Slot(AuthMemoryCache)
```

An entry lives until the time it was put with, `AUTH_ATTEMPT_TTL` for an
attempt and `AUTH_SESSION_CACHE_TTL` for a session and its caller, and is
forgotten when it is got past it. A cache in memory is of one process: an
application running more needs a cache they share, which the addon does
not have yet.
