# Storages

The storage keeps what lives years: the profiles, their identities and
secrets, the registries of the tags and the attributes, the sessions, open
and closed, the records of the sign-ups and the memberships of the groups.
`AuthStorage` is the facade, with the transactions of a backend over all
its storages: what belongs together, the end of a sign-up, is written in
one.

## In memory

`AuthMemoryStorage` of `ingot_auth.contrib.storages.memory`, with no extra,
for the tests and the addon run on its own: what it stores is gone with the
project.

```python
from ingot_auth.contrib.storages.memory import AuthMemoryStorage


class AppAuthUnit(AuthUnit):
    storage = Slot(AuthMemoryStorage)
```

## MongoDB

`AuthMongoDbStorage` of `ingot_auth.contrib.storages.mongodb`, with the
extra `pymongo`, on a client of
[ingot-pymongo](https://github.com/ak-ingots/ingot-pymongo): the project
joins `MongoDbProject`, its settings and logging joined with those of the
auth.

```sh
uv add 'ingot-auth[pymongo]'
```

```python
from ingot_pymongo import MongoDbProject
from ingot_pymongo.logging import MongoDbLoggingUnit
from ingot_pymongo.settings import MongoDbSettingsUnit
from ingot_pymongo.settings.configs import MongoDbConfigs

from ingot_auth.contrib.storages.mongodb import AuthMongoDbStorage


class AppConfigs(AuthConfigs, MongoDbConfigs):
    pass


class AppSettingsUnit(AuthSettingsUnit, MongoDbSettingsUnit):
    configs = Slot(AppConfigs)


class AppLoggingUnit(AuthLoggingUnit, MongoDbLoggingUnit):
    project: "AppProject"  # of both, for mypy


class AppAuthUnit(AuthUnit):
    storage = Slot(AuthMongoDbStorage)
    cache = Slot(AuthMemoryCache)


class AppProject(AuthProject, MongoDbProject):
    settings = Slot(AppSettingsUnit)
    logging = Slot(AppLoggingUnit)
    auth = Slot(AppAuthUnit)
```

The storage takes the client `default` of ingot-pymongo, configured by
`MONGODB_DEFAULT_*`, the database `ingot_auth`, a collection a storage,
created with its indexes on its first use. A subclass changes what it
chooses, not a config: the client by the hook `_get_client()` of the
storage and `_mongodb_get_client()` of each collection, the names by
`MONGODB_DATABASE` and `MONGODB_COLLECTION`.

MongoDB takes transactions on a replica set only: run a replica set, of
one node if that is all there is. A transaction may fail on a conflict with
another, with the label `TransientTransactionError`: retrying it is the
caller's.
