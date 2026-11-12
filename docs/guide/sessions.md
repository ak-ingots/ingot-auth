# Sessions

A session lives as the strategy of its lifetime says, which the
application declares, as the sessions have none: `AuthFixedLifetime` for
one, `AUTH_SESSION_TTL` seconds from the sign-in:

```python
class AppSessionsUnit(AuthSessionsUnit):
    lifetime = Slot(AuthFixedLifetime)
```

## Callers

A request brings the token of its session, and
`auth.sessions.authenticate(token)` gives its caller, with the uid of the
profile and the permissions of its groups, from the cache. A member added
to a group or removed has it on its next request, signed in still: the
operations of the members forget its callers. A deploy changing what the
groups grant finds none of the callers formed before. A change made past
the operations, by hand in the database, shows past
`AUTH_SESSION_CACHE_TTL`.
