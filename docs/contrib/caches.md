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
application running more needs a cache they share, that in Redis.

## In Redis

`AuthRedisCache` of `ingot_auth.contrib.caches.redis`, under the extra
`redis`, on the default client of
[ingot-redis](https://pypi.org/project/ingot-redis/), whose `REDIS_DEFAULT_*`
configs tell the server: the project joins its `RedisProject`.

```python
from ingot_auth.contrib.caches.redis import AuthRedisCache
from ingot_redis import RedisProject


class AppAuthUnit(AuthUnit):
    cache = Slot(AuthRedisCache)


class AppProject(AuthProject, RedisProject):
    auth = Slot(AppAuthUnit)
```

An entry is JSON of plain values, never pickled, as more than the server
may read the cache, under a key of the prefix `ingot_auth`,
`ingot_auth:attempt:<uid>`, `ingot_auth:session:<hash>`,
`ingot_auth:caller:<hash>:<digest>`, which Redis expires at its time; an
attempt is taken by `GETDEL`, so two answers to it never both proceed. The
state of an attempt is of its method, which gives it as plain values by
`dump_state()` and takes it back by `load_state()`: a method of more than
one step of an application overrides their hooks, `_dump_state()` and
`_load_state()`. Another client, another prefix are a matter of a
subclass of a part, its hook `_redis_get_client()` and its `REDIS_PREFIX`.
