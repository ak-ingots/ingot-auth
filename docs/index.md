# ingot-auth

The sign-up, the sign-in and the sessions of the users of
[Ingots](https://ingots.readthedocs.io/) applications.

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

## Where to go next

- {doc}`guide/index`: the methods, the sign-in, the access, the sessions
  and the configs.
- {doc}`contrib/index`: the caches, the storages and the transports, and
  how an application plugs them in.
- {doc}`reference/index`: the Python API.
- {doc}`changelog`.

```{toctree}
:hidden:
:caption: Guide

guide/index
```

```{toctree}
:hidden:
:caption: Contrib

contrib/index
```

```{toctree}
:hidden:
:caption: Reference

reference/index
changelog
```
