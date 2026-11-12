# ingot-auth Changelog

<!-- towncrier release notes start -->

## [0.1.0] - 2026-11-12
### Added
- ingot-auth, an addon of Ingots for the sign-up, the sign-in and the
  sessions of the users of an application, for `ingots` 0.33.1 and later
  0.33 releases. `AuthProject`, the project of the defaults with the
  addon's `AuthSettingsUnit` and its `AuthConfigs`, named `AUTH_*`,
  `AuthLoggingUnit`, the logger `ingot_auth`, and `AuthUnit`, the auth of
  the project, a unit a subdomain: the profiles, the methods, the sign-up,
  the sign-in, the sessions, the access, the metadata, the storage and the
  cache. The core assumes no details: the methods are bound by the
  application, the storage, the cache and the transport plug in from
  `ingot_auth.contrib`, each under its own extra when it needs more than
  the core. `python -m ingot_auth` runs the addon on its own, its storage
  and cache in memory.
- The registries of the tags and the attributes of the profiles,
  `auth.profiles.tags` and `auth.profiles.attrs`: items of explicit ids,
  never reused, and names an operator renames, an attribute with its type;
  the operations to create, list, rename and delete them, and the commands
  `auth profiles tags|attrs` running them.
- The methods of signing up and in, slots of `AuthMethodsUnit`, a
  catalogue in the core, none bound until an application declares its
  slot. A method verifies in steps, each ending with a challenge for the
  client to answer or with the verified subject, an attempt keeping the
  flow in the cache between them, taken once, with a limit of refused
  answers (`AUTH_ATTEMPT_TTL`, `AUTH_ATTEMPT_MAX_FAILURES`). It names the
  kind of the identifier it verifies, and an identity, `(kind, value)`, is
  bound to a profile once, whatever method. The password is of the
  profile, `AuthPassword`, the slot `password` of the methods, kept as its
  hash by scrypt of the standard library. In the catalogue: the nickname
  and the password, `AuthNicknameMethod`, and the email and a code sent to
  it, of two steps, `BaseAuthEmailCodeMethod`, the sending of the code the
  application's hook `_send_code()`. The flows of a method are toggles,
  its configs mixed into those of the application, on by default, and
  permissions, a domain a method, `CAN_SIGN_UP` and `CAN_SIGN_IN`, the
  anonymous caller given the flags of the flows open,
  `auth.methods.get_anonymous_permissions()`. `AuthTestingMethod` of
  `ingot_auth.testing.methods` serves the tests of applications.
- The policies of what a user types, each an operation taking the part of
  its parameters its protocol tells and raising `AuthPolicyViolationError`
  with its name when the value breaks it: the length and the characters,
  by the sets of Unicode, in the core, configured by the `CONFIG` of their
  class, which a subclass replaces; an application writes its own as any
  operation. The policies of a field of a flow are a group of a method,
  its slot `policies_<flow>_<field>`, a `Factories` of ingots of the type
  the method gives, `AuthNicknameSignUpPolicies(AppNicknameLength)`, empty
  until an application gives policies to it in a subclass, mypy refusing
  a policy taking what the group does not give; the password has its own,
  `policies_set` of `AuthPassword`, by any method. A group runs together,
  every policy to its end, and a value breaking some raises
  `AuthMethodInvalidError`, naming the field and every policy broken.
- The sign-up, `auth.sign_up`, `op_start` and `op_answer`: once a method
  verified the subject, the sign-up binds it to a new profile with its
  secret, the hash of a password, and keeps the record of what it happened
  on, the values of the attributes of the session the client gave, checked
  to be the client's, all in one transaction of the storage. It requires
  `CAN_SIGN_UP` of `auth.sign_up` and the `CAN_SIGN_UP` of the method.
- The sign-in, `auth.sign_in`, `op_start` and `op_answer`, as the sign-up
  goes: it finds the profile bound to what the method verified, an
  identifier bound to none refused as a wrong secret, checks the profile
  may sign in by the method, `AuthMethodDeniedError` otherwise, and opens a
  session, `AuthSignedIn` giving its token once and its id. It requires
  `CAN_SIGN_IN` of `auth.sign_in` and the `CAN_SIGN_IN` of the method. Its
  replies are held by the strategy in the slot `timing`, none by default:
  `AuthFloorTiming` holds each, a refusal as a success, to
  `AUTH_SIGN_IN_MIN_DURATION` seconds, so that its time tells nothing of
  who signed up; `AuthNoTiming` holds none.
- The sessions, `auth.sessions`: `open()` opens one for a profile signed in
  and gives its token, 256 random bits the storage keeps the sha256 of,
  and `authenticate(token)` gives its caller, `AuthCaller` with the uid,
  the id of the session and the permissions of the groups of the user,
  from the cache, or from the storage and the access on a miss, kept
  `AUTH_SESSION_CACHE_TTL` seconds. A session lives as the strategy in the
  slot `lifetime` says, none by default: `AuthFixedLifetime`,
  `AUTH_SESSION_TTL` seconds from the sign-in; an expired one is closed,
  kept as the record of the sign-in, and refused,
  `AuthSessionExpiredError`. The registries of the attributes of the
  sessions, each with its type and its source, the transport, the client,
  the provider or the server, and of the presets asking for them, bound
  many to many, with their operations and the commands
  `auth sessions attrs|presets`.
- The access, `auth.access`: the groups of the users, declared in the code
  as slots of `AuthGroupsUnit`, each granting by its hook
  `_get_permissions()`, the addons and the application granting to the
  same group; `signed_in` of the core, `AuthSignedInGroup`, of every
  signed-in user, none stored, granting the `CAN_SIGN_IN` of each method
  open. The memberships, added, removed and listed by the operations of
  `auth.access.members` and the commands `auth access groups|members`, run
  as the root, so that the first administrator is made there; and
  `AuthGroupsGrants`, the permissions of a user from its groups. A change
  of the groups of a user shows on its next request, signed in still: its
  callers are forgotten in the cache, `auth.sessions.forget_callers(uid)`,
  and a caller is cached by the digest of the groups too, so that a deploy
  changing what they grant finds none formed before.
- The metadata for the clients, `auth.metadata`, a part a subdomain: the
  methods with their flows open or closed; `profile`, the tags and the
  attributes of the profiles; `session`, the attributes whose source is the
  client, the presets and their bindings to them, flat lists linked by
  ids.
- The storage and the cache, the facades `AuthStorage` of
  `ingot_auth.storages`, a storage a subdomain, with the transactions of a
  backend over all of them, and `AuthCache` of `ingot_auth.caches`, for the
  attempts, the sessions and their callers, each depending on no other
  part of the auth. In `ingot_auth.contrib`: the storage and the cache in
  memory, `AuthMemoryStorage` and `AuthMemoryCache`, and the storage in
  MongoDB under the extra `pymongo`, `AuthMongoDbStorage`, on a client of
  ingot-pymongo, its transactions taking a replica set. The contracts of
  `ingot_auth.testing.contracts` tell what a backend guarantees, as tests
  its author runs on it.
- The auth over gRPC under the extra `grpcio`, on ingot-grpcio, in
  `ingot_auth.contrib.transports.grpcio`: a service a registry and a
  method, each in a binding of its own, `AuthGrpcMetadataBinding` and
  `AuthGrpcNicknameBinding` for a public server, `AuthGrpcAdminBinding`
  for the administration, the profiles, the sessions and the access, the
  contracts in the tree of the core at the path of their packages,
  `ingot_auth.profiles.tags.v1`, the permissions of each in an enum of
  its contract. A call runs for the caller of the session of its token,
  `authorization: Bearer <token>`, or for the anonymous one, and
  `AuthGrpcErrorsUnit` gives the errors of the auth their statuses.
- The documentation on Read the Docs, a subproject of that of Ingots,
  https://ingots.readthedocs.io/projects/ingot-auth/: the guide, the
  contrib, the caches, the storages and the transports and how an
  application plugs them in, and the Python API.
