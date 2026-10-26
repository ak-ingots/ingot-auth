# ingot-auth

[![ci](https://github.com/ak-ingots/ingot-auth/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ak-ingots/ingot-auth/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ak-ingots/ingot-auth/blob/main/LICENSE)

<!-- Links must be absolute: this README also renders on PyPI. -->

The sign-up, the sign-in and the sessions of the users of Ingots
applications. An addon of [Ingots](https://github.com/ak-ingots/ingots).

**Status:** pre-alpha, on ingots 0.32: the skeleton of the addon, its
project, settings, logging and an empty `auth` unit.

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

### Configs

Set as environment variables with the prefix of the project
(`APP_AUTH_LOGGING_LEVEL`), in a `--configs-file` or with `--config`.

| Name | Default | Meaning |
|---|---|---|
| `AUTH_LOGGING_LEVEL` | `INFO` | the level of the logger of the addon, `ingot_auth` |

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
  TestPyPI, tests it as installed from there (`make index-test`), then
  publishes it to PyPI. Run by hand, it rehearses on TestPyPI only.
