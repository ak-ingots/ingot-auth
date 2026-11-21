# ingot-auth

[![ci](https://github.com/ak-ingots/ingot-auth/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ak-ingots/ingot-auth/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ak-ingots/ingot-auth/blob/main/LICENSE)
[![Documentation Status](https://app.readthedocs.org/projects/ingot-auth/badge/?version=latest)](https://ingots.readthedocs.io/projects/ingot-auth/en/latest/)

<!-- Links must be absolute: this README also renders on PyPI. -->

The sign-up, the sign-in and the sessions of the users of Ingots
applications. An addon of [Ingots](https://github.com/ak-ingots/ingots).

**Status:** pre-alpha: the registries of the tags and the attributes of the
profiles and of the attributes and the presets of the sessions, with their
metadata for the consumers, all of it over gRPC, the metadata, the method
of a nickname and the sign-out over HTTP too, the JSON of the same contract
transcoded on ingot-starlette, no grpcio; the sign-up and the
sign-in by pluggable methods in steps, a nickname and a password, an email
and a code sent to it in the background by the mailer of ingot-mail,
SMTP among them, over gRPC too; the
policies of what a user types,
operations run together in groups; the groups of the users, declared in the
code, and their members, on the command line and over gRPC; the sessions a
sign-in opens, a token turned into a caller, revoked all at once by an
operator, the expired ones swept by a job; the activity log of every
change of state, read by the auditors; all of it stored in memory or in
MongoDB, cached in memory or in Redis.

## For Consumers

```sh
uv add ingot-auth
```

The stack of a kind of application comes as one extra: `game`, the
transport by gRPC, the storage in MongoDB, the cache in Redis and the mail
by SMTP, as the backend of the
[game](https://github.com/ak-ingots/ingot-auth/tree/main/examples/game)
composes them, run by its scenarios on each change.

```sh
uv add 'ingot-auth[game]'
```

The [documentation](https://ingots.readthedocs.io/projects/ingot-auth/en/latest/)
has the guide, the contrib, the caches, the storages and the transports an
application plugs in, and the Python API.

## Development

Requires [uv](https://docs.astral.sh/uv/) and `make`; uv fetches the
interpreters it needs. `make lint` lints the gRPC contract by
[Buf](https://buf.build/docs/cli/), of the version the ecosystem pins in
[ingots-libs](https://github.com/ak-ingots/ingots-libs/blob/main/.github/actions/setup-buf/version):
cloned inside ingots-libs, as `make clone` there does, it takes that one,
fetched on the first use; alone, install that version on the `PATH`, or give
its path as `BUF`.

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
