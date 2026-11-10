The sessions: `auth.sessions.open()` opens one for a profile signed in and
gives its token, 256 random bits the storage keeps the sha256 of, and
`auth.sessions.authenticate(token)` gives its caller, `AuthCaller` with the
uid, the id of the session and the permissions of the groups of the user,
from the cache, `cache.sessions` and `cache.callers`, or from the storage
and the access on a miss, kept `AUTH_SESSION_CACHE_TTL` seconds. A session
lives as the strategy in the slot `lifetime` says, none by default:
`AuthFixedLifetime`, `AUTH_SESSION_TTL` seconds from the sign-in; an expired
one is closed, kept as the record of the sign-in, and refused,
`AuthSessionExpiredError`. The storage keeps them in memory and in MongoDB,
the cache in memory, each with its contract.
