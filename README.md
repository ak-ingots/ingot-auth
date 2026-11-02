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
bound to their presets.

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
named by their slots: a nickname and a password comes with the addon,

```python
from ingot_auth.contrib.methods.password import AuthPasswordMethod


class AppMethods(AuthMethods):
    password = Slot(AuthPasswordMethod)
```

the nickname and the password of a sign-up checked by the presets of the
policies `preset_sign_up_nickname` and `preset_sign_up_password`, empty
unless the application binds policies to them in its `AuthPolicies`, the
parameters of its hash, scrypt, changed by subclassing. An email and a code
sent to it comes too, of two steps, the sending of the code the
application's:

```python
from ingot_auth.contrib.methods.email import BaseAuthEmailMethod


class AppEmailMethod(BaseAuthEmailMethod):
    @t.override
    async def _send_code(self, email: str, code: str) -> None:
        ...  # by the mail of the application


class AppMethods(AuthMethods):
    email = Slot(AppEmailMethod)
```

its email checked on a sign-up by the preset `preset_sign_up_email`.

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
interpreters it needs.

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
