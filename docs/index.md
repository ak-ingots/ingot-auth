# ingot-auth

The sign-up, the sign-in and the sessions of the users of
[Ingots](https://ingots.readthedocs.io/) applications.

**Status:** pre-alpha: the registries of the tags and the attributes of the
profiles and of the attributes and the presets of the sessions, with their
metadata for the consumers, all of it over gRPC; the sign-up and the
sign-in by pluggable methods in steps, a nickname and a password, over gRPC
too, and an email and a code sent to it; the policies of what a user types,
operations run together in groups; the groups of the users, declared in the
code, and their members, on the command line and over gRPC; the sessions a
sign-in opens, a token turned into a caller; all of it stored in memory or
in MongoDB.

```sh
uv add ingot-auth
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
