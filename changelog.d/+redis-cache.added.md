The cache in Redis, `AuthRedisCache` of `ingot_auth.contrib.caches.redis`,
under the extra `redis`, on the default client of
[ingot-redis](https://pypi.org/project/ingot-redis/): for a project of more
than one process. It keeps JSON of plain values under keys of the prefix
`ingot_auth`, expiring at their times, an attempt taken by `GETDEL`. A
method gives the state of its step as plain values, `dump_state()` and
`load_state()` of `BaseAuthMethod`, by the hooks `_dump_state()` and
`_load_state()`, which a method of more than one step overrides, as
`AuthEmailCodeMethod` and `AuthTestingMethod` do.
