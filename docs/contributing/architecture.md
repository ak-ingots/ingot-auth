# Architecture

A map of `ingot_auth` for its contributors: where each part lives and what
it leans on. What a consumer writes is in the {doc}`guide <../guide/index>`.

## The project and its units

- `AuthProject` (`project.py`) extends the `MailProject` of ingot-mail,
  whose mailer sends the mail of the methods. It takes:
  - `AuthSettingsUnit` (`settings.py`) with its `AuthConfigs`, named
    `AUTH_*`;
  - `AuthLoggingUnit` (`logging.py`), the logger `ingot_auth`;
  - `AuthOperationsUnit` (`operations/`), whose `AuthCallersProvider` gives
    the anonymous caller what `auth.grp_anonymous` grants;
  - `AuthUnit` (`auth.py`), the auth of the project, holding the units below.
- `python -m ingot_auth` runs the addon on its own, the prefix `INGOT`, the
  storage in memory.

## The domains

- `profiles/`: the registries `tags/` and `attrs/`; the values of a profile
  an operator sets, the whole set each time.
- `sessions/`: the registries `attrs/`, each attribute with its source, and
  `presets/`, bound to the attributes many to many, all on the shared
  `registry/`. A session is kept by the hash of its token. Strategies in
  slots, none by default:
  - `lifetime`: sliding, fixed or both; the time seen written once an
    interval;
  - `deriver`: the values of the attributes of the source `derived`;
  - `limit`: over `AUTH_SESSIONS_MAX` a sign-in evicts or is refused.

  A user lists and revokes its own by the flags `auth.grp_signed_in`
  grants; a closed session is kept, the record of the sign-ins an operator
  reads. `authenticate()` turns a token into an `AuthCaller`; the session
  and the caller are cached apart, the caller by the digest of the groups
  too, forgotten by `forget_callers()` on a change of the memberships or of
  the values of the profile. A caller carries `profile_hash`, which the
  transports tell in every reply.
- `access/`: `groups/`, entities in slots `grp_*` of the units of their
  domains (`AuthGroupsOwner`), found by a walk from the project down the
  owners by `AuthGroupsUnit`, each named by its full name
  (`auth.profiles.grp_managers`), granting by a hook; `members/`, the
  memberships in the storage; `AuthGroupsGrants`, the permissions of a user
  from its groups. Of the core: `auth.grp_signed_in`, every signed-in user,
  none stored; `auth.grp_anonymous`, every caller that tells no one.
- `activities/`: the activity log of ADR 0015; a change of state is recorded
  by its operation in its transaction by `record()`; the strategy of a
  failure in the slot `failure`, strict or swallow, none by default; read by
  `auth.activities.grp_auditors`.
- `metadata/`: what the clients of a subdomain need to know, of the sessions
  what is the client's.

## The methods and the flows

- `methods/`: the methods of signing up and in, units in slots of
  `AuthMethodsUnit`, a subpackage a method (`nickname/`, `email_code/`),
  none bound until an application declares its slot.
  - A flow goes in steps kept by attempts; the state of a step is plain
    values by `_dump_state()`/`_load_state()`, for a cache out of the
    process.
  - A method names the kind of the identifier it verifies
    (`IDENTIFIER_KIND`); an identity `(kind, value)` is bound to one profile
    whatever the method.
  - Its permissions: a domain a method, a flag a flow by a hook
    (`_get_<flow>_permissions`), given by the toggles.
  - Its policies: slots `policies_<flow>_<field>`, each a `Factories` of
    ingots typed by its parameters, run all together (`run_all_in_group`).
  - A method of the catalogue is whole, with a plain default for what it
    sends, so that an application plugs only the backends.
- `methods/password/`: the password of the profile, the slot `password` of
  the methods, not a method. Its hash is the secret of the uid
  (`storages/profiles/secrets.py`). `policies_set` checks a new one, the
  length of OWASP by default (`AuthPasswordLengthPolicy`); `AuthPwnedPolicy`
  of `contrib/policies/` refuses a leaked one. `op_change` changes it, the old
  one given, the other sessions closed, then publishes `ev_changed`.
- `policies/`: rules a value is checked against, each an operation taking a
  part of its parameters by a protocol, raising `AuthPolicyViolationError`
  with its name, configured by the `CONFIG` of its class.
- `sign_up/`, `sign_in/`: the flows over `methods/operations.py`. The
  sign-up opens by its toggle, `AUTH_SIGN_UP_ENABLED`; the sign-in opens a
  session, its replies held by the strategy in its slot `timing`, none by
  default. `sign_out/` closes the session of the caller.

## The events

A domain publishes its events by slots `ev_*`, a `Factories` of
subscribers, through `project.events` of ingots, after the change: the
transaction of the storage holds them till it commits and drops them on a
rollback. The mail of the core is the default subscriber.

## The backends

The core holds the facades, `contrib/` their implementations:

- `storages/`: the interfaces a backend implements, what they keep and
  raise, depending on no other part of the auth, laid out by the subdomains;
  `AuthStorage` with the transactions of a backend over all its storages.
- `caches/`: the same for what lives minutes, the attempts, the sessions and
  their callers; `AuthCache` the facade, depending on the storages alone.
- `dispatchers.py`: operations run in the background, `BaseAuthDispatcher`
  the facade; the mail of a method is a `Mail` of ingot-mail, sent by an
  operation of the dispatcher by the mailer of the project.
- `contrib/`: `storages/<backend>/` (`memory`, `mongodb`),
  `caches/<backend>/` (`memory`, `redis`), `dispatchers/<backend>/`,
  `transports/<addon>/` (`grpcio`, `starlette`), `policies/`.

## The API

`api/` holds the contract of gRPC and the business layer of the transports,
protobuf alone (ADRs 0009, 0011, 0013):

- a file per service at the path of its package, the tree that of the
  subdomains of the core: `api/profiles/tags/v1/tags.proto` for
  `ingot_auth.api.profiles.tags.v1`;
- the RPCs of a service as mixins in the `rpcs.py` next to its `v1/`
  (`rpc_*`, a call told by `BaseAuthRpcContext`), all exported by
  `ingot_auth.api`;
- the statuses of the errors in `api/errors.py`;
- what a step asks for, `Challenge`, in `api/methods/v1/`; the results and
  the answers of the flows in `api/sign_up/v1/`, `api/sign_in/v1/`; the
  values of the attributes, `AttrValue`, in `api/attrs/v1/`.

`contrib/transports/grpcio/` mixes the RPCs into its servicers,
`contrib/transports/starlette/` into the endpoints ingot-starlette
transcodes to JSON, no grpcio.

## Tests and examples

- `testing/contracts/`: the guarantees of the addon as tests a consumer runs
  (ADR 0005).
- `examples/game`, `examples/web`: the stacks of the extras `game` and
  `web`, run by their scenarios; `perf/game` loads the game at the cut of a
  release.
