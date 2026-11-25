# CLAUDE.md of `contrib/`

The implementations of the facades of the core, each under its own extra
when it needs more than the core: `storages/<backend>/` (`memory`,
`mongodb`), `caches/<backend>/` (`memory`, `redis` on ingot-redis),
`dispatchers/<backend>/`, `transports/<addon>/` (`grpcio`, `starlette` on
ingot-starlette, no grpcio), `policies/` (a call out, Pwned Passwords).

- A contrib is laid out by the subdomains of the core, `profiles/`,
  `sessions/`, as the core is.
- A contrib gives the class of the slot it fills (`AuthMemoryStorage` for
  `AuthUnit.storage`), no unit or project: the application composes.
- What a backend chooses is changed by subclassing, not a config: a client
  by a hook, the names of its collections by a `ClassVar`; the configs of
  the environment belong to the infrastructure addon.
- A backend runs the contracts of its facade from `testing/contracts/`; a
  new method of a facade gets its contract first, then every backend.
- A transport mixes in the RPCs of `api/` and adds only the transport: the
  servicer of a method of gRPC extends `BaseAuthGrpcMethodServicer`, which
  gives the values of the attributes of the transport by their names, each
  bound to its reader (`ip`, the peer); every reply tells the
  `profile_hash` of the caller.
