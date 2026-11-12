# Contrib

The core of the addon holds the facades: `AuthStorage` of
`ingot_auth.storages`, `AuthCache` of `ingot_auth.caches`, and the
operations a transport runs. What implements them is in
`ingot_auth.contrib`, each under its own extra when it needs more than the
core. A contrib gives the class of the slot it fills, `AuthMemoryStorage`
for the slot `storage` of the auth, no unit or project: the application
composes, and joins the project of the addon a backend is written against,
`MongoDbProject` of ingot-pymongo, `GrpcProject` of ingot-grpcio.

| Contrib | Extra | What it gives |
|---|---|---|
| {doc}`caches` | | the cache in memory |
| {doc}`storages` | `pymongo` | the storage in memory; in MongoDB |
| {doc}`transports` | `grpcio` | the services of gRPC |

The auth has no storage or cache by default: an application declares both.

## A backend of its own

A backend of an application implements the interfaces of
`ingot_auth.storages` or `ingot_auth.caches`, the hooks of each, and runs
the contracts of `ingot_auth.testing.contracts` against itself: a test case
a contract, `AuthSessionsStorageContract`, `AuthCallersCacheContract`,
giving the project to run on by `create_project()`, its storage and cache
empty:

```python
class AppSessionsStorageTestCase(
    AuthSessionsStorageContract, unittest.IsolatedAsyncioTestCase
):
    @t.override
    async def create_project(self) -> AuthProject:
        return AppProject()
```

```{toctree}
:maxdepth: 2

caches
storages
transports
```
