The interfaces of the caches are in `ingot_auth.caches`, as those of the
storages are in `ingot_auth.storages`: `AuthCache`, the caches of the
attempts, of the sessions and of their callers, and what they keep and raise
of their own, `AuthAttempt`, `AuthCaller` and `AuthAttemptNotFoundError`, no
more an `AuthMethodError`. The methods and the sessions no more export them:
`from ingot_auth.caches import AuthCaller` in place of
`from ingot_auth.sessions import AuthCaller`.
