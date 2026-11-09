# ingot-auth

[![ci](https://github.com/ak-ingots/ingot-auth/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ak-ingots/ingot-auth/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ak-ingots/ingot-auth/blob/main/LICENSE)

<!-- Links must be absolute: this README also renders on PyPI. -->

The sign-up, the sign-in and the sessions of the users of Ingots
applications. An addon of [Ingots](https://github.com/ak-ingots/ingots).

**Status:** pre-alpha: the registries of the tags and the attributes of the
profiles and of the attributes and the presets of the sessions, with their
metadata for the consumers; stored in memory or in MongoDB, and all of it
over gRPC; the sign-up by pluggable methods in steps, a nickname and a
password, and an email and a code sent to it, in memory so far; the policies of what a user types,
bound to their presets; the groups of the users, declared in the code, and
their members, in memory so far, on the command line and over gRPC.

## For Consumers

### Install

```sh
uv add ingot-auth
```

### Integrate

An application inherits `AuthProject`, the project of the defaults with the
addon's settings, logging and `auth` unit, or takes the classes of the addon
among the bases of its own, as the
[addon guide](https://github.com/ak-ingots/ingots/blob/main/docs/defaults/addon.md)
of Ingots shows.

The methods of signing up and in are slots of the methods of the auth,
named by their slots. The addon comes with a catalogue of them, none bound
until the application declares its slot: a nickname and a password,

```python
from ingot_auth.methods.nickname import AuthNicknameMethod


class AppMethods(AuthMethods):
    nickname = Slot(AuthNicknameMethod)
```

the nickname and the password of a sign-up checked by the presets of the
policies of the method, its slots `preset_sign_up_nickname` and
`preset_sign_up_password`, empty unless the application binds policies to
them in a subclass of the method, the parameters of its hash, scrypt,
changed by subclassing too. An email and a code
sent to it comes too, of two steps, the sending of the code the
application's:

```python
from ingot_auth.methods.email_code import BaseAuthEmailCodeMethod


class AppEmailCodeMethod(BaseAuthEmailCodeMethod):
    @t.override
    async def _send_code(self, email: str, code: str) -> None:
        ...  # by the mail of the application


class AppMethods(AuthMethods):
    email_code = Slot(AppEmailCodeMethod)
```

its email checked on a sign-up by its preset `preset_sign_up_email`.

A method bound binds its configs too: the toggles of its flows, on by
default, which the application mixes into its configs. A toggle closes a
flow in an environment, and the metadata lists the methods with their
flows open or closed:

```python
class AppConfigs(AuthNicknameConfigs, AuthEmailCodeConfigs, AuthConfigs):
    AUTH_SIGN_UP_NICKNAME_ENABLED = BoolConfig(False)  # by invitation only
```

A signed-in user has what its groups grant. The groups are declared in
the code, slots of the groups of the access, each granting by its hook;
the addons grant to a group as the application does, which declares the
class joining them when two of its bases hold the group:

```python
class AppAdminsGroup(ShopAdminsGroup, ArticlesAdminsGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | Permissions(
            AuthMembersPermissions.CAN_ADD | AuthMembersPermissions.CAN_REMOVE
        )


class AppGroups(ShopGroups, ArticlesGroups):
    admins = Slot(AppAdminsGroup)  # joins what the two grant to it
    editors = Slot(EditorsGroup)


class AppAccess(AuthAccess):
    groups = Slot(AppGroups)
```

The storage keeps the members of the groups only, added and removed by the
operations of `auth.access.members`, a group no source has granting
nothing. The command line runs them as the root, so the first
administrator is made there; then an administrator does the rest over
gRPC, the services `Groups` and `Members` of `AuthGrpcAccessBinding`:

```console
$ python -m app auth access groups list
$ python -m app auth access members add admins 0f6c…
```

The storage in MongoDB (extra `pymongo`, `AuthMongoDbStorage`) writes what
belongs together in one transaction, the end of a sign-up for one, and
MongoDB takes transactions on a replica set only: run a replica set, of one
node if that is all there is.

### Configs

Set as environment variables with the prefix of the project
(`APP_AUTH_LOGGING_LEVEL`), in a `--configs-file` or with `--config`.

| Name | Default | Meaning |
|---|---|---|
| `AUTH_LOGGING_LEVEL` | `INFO` | the level of the logger of the addon, `ingot_auth` |
| `AUTH_ATTEMPT_TTL` | `600` | the seconds an attempt of a sign-up waits for an answer |
| `AUTH_ATTEMPT_MAX_FAILURES` | `5` | the answers refused before an attempt is over |

## Development

Requires [uv](https://docs.astral.sh/uv/) and `make`; uv fetches the
interpreters it needs. `make lint` lints the gRPC contract by
[Buf](https://buf.build/docs/cli/), of the version the ecosystem pins in
[ingots-libs](https://github.com/ak-ingots/ingots-libs/blob/main/.github/actions/setup-buf/version):
its `make check` passes its own, alone install that version, or give its
path as `BUF`.

```sh
make                 # the target list
make check           # everything CI runs: lint, test, coverage, wheel-test, doc, cl-check
make format          # black
make doc-serve       # build the documentation and serve it
make all             # build the sdist and the wheel into dist/
```

- Every change users should know about adds a news fragment to `changelog.d/`
  (see [its README](https://github.com/ak-ingots/ingot-auth/blob/main/changelog.d/README.md)).
- A release is a pull request setting the version (`uv version X.Y.Z`) and
  collating the changelog (`make cl-build VERSION=X.Y.Z`), then the tag
  `vX.Y.Z` on `main`: the `release` workflow publishes the tested build to
  TestPyPI, tests it as installed from there, then
  publishes it to PyPI. Run by hand, it rehearses on TestPyPI only.
