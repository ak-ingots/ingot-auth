# ingot-auth Changelog

<!-- towncrier release notes start -->

## [0.2.0] - 2026-11-15
### Added
- The dispatcher of the auth, the slot `dispatcher` of `AuthUnit`,
  `BaseAuthDispatcher` of `ingot_auth.dispatchers`, running operations of the
  auth in the background, so that a step replies at once:
  `dispatch(factory, parameters, metadata)` returns before the operation
  ends. In the process, `AuthMemoryDispatcher` of
  `ingot_auth.contrib.dispatchers.memory`: an operation run by `run_safe()`
  of the runner in a task of asyncio, a failure logged, `join()` waiting for
  them. An application declares it in the slot, as the storage and the
  cache.
- The group of every caller that tells no one, `auth.grp_anonymous`,
  `AuthAnonymousGroup`, in the slot `grp_anonymous` of `AuthUnit`, none
  stored, as `auth.grp_signed_in` is of every signed-in user: it grants what
  anyone may of the auth, as its units tell it, the flags of the sign-up and
  of the sign-in, those of the methods their toggles open, and the reading
  of the metadata, `auth.metadata.get_anonymous_permissions()`; an
  application grants anyone more, or less, by its own class in the slot.
  `AuthProject` takes `AuthOperationsUnit`, whose `AuthCallersProvider`
  gives the anonymous caller of the project,
  `operations.callers.get_anonymous()`, what the group grants. A signed-in
  user is not a member: it has what its groups grant alone. A membership of
  `auth.grp_anonymous` is refused as one of `auth.grp_signed_in`, the message of
  both `the group '<name>' keeps no members`.
- The groups of the work of the registries of the core: in the profiles,
  `auth.profiles.grp_consumers`, reading the tags and the attributes, and
  `auth.profiles.grp_managers`, keeping them; in the sessions,
  `auth.sessions.grp_consumers`, reading the attributes and the presets,
  `auth.sessions.grp_managers`, keeping them but the bindings, and
  `auth.sessions.grp_admins`, binding too.
- The mailer of the auth, the slot `mailer` of `AuthUnit`, `BaseAuthMailer`
  of `ingot_auth.mailers`, delivering an `AuthMail`, its address, subject
  and text, the address and the text out of its `repr`. In memory,
  `AuthMemoryMailer` of `ingot_auth.contrib.mailers.memory`, delivering
  nothing and keeping the mail, `get_sent()`, for the tests and the addon
  run on its own. `AuthMailerContract` tells what a backend guarantees, the
  mail delivered as sent, read back by `get_delivered()` of its test case.
  An application declares the mailer in the slot, as the storage and the
  cache.
- The method of an email and a code over gRPC: the service `EmailCode` of
  `ingot_auth.methods.email_code.v1`, `StartSignUp` and `StartSignIn`, in
  `AuthGrpcEmailCodeBinding`, and the answers of the flows, whatever the
  method, `SignUp.AnswerSignUp` and `SignIn.AnswerSignIn`, in
  `AuthGrpcFlowsBinding`, the attempt and the code. The results of the flows
  tell what a step asks for, `challenge`, a `Challenge` of
  `ingot_auth.methods.v1` by the kind of its answer, `code` of its `length`.
  An attempt gone, expired or over is `NOT_FOUND`, the reason
  `ATTEMPT_NOT_FOUND`. The servicers of the flows, open to anyone, run
  for the anonymous caller of the project whatever a call bears.
- The sliding lifetimes of the sessions: `AuthSlidingLifetime`, a session
  living while used and expiring idle `AUTH_SESSION_IDLE_TTL` seconds, an
  hour by default, `EXPIRED_IDLE`, and `AuthSlidingFixedLifetime`, sliding
  and fixed, expiring by whichever comes first, as NIST SP 800-63B-4 and
  OWASP ask for an overall timeout always. A sliding lifetime writes the
  time a session is seen at, `seen_at` of `AuthSessionRecord`, by
  `storage.sessions.touch()`, at most once per
  `AUTH_SESSION_TOUCH_INTERVAL` seconds, five minutes by default; a
  strategy tells it by `is_touch_due()`. A cached session past its
  lifetime is found again in the storage before it closes, as another
  process may have seen it since. The sessions of MongoDB opened by 0.1.0
  are seen at their sign-in.
- The toggle of the sign-up, `AUTH_SIGN_UP_ENABLED`, on by default: off, no
  one signs up by any method, and the metadata lists the sign-up of each
  method closed. The flags the flows give the anonymous caller come from
  their units, `auth.sign_up.get_anonymous_permissions()` and
  `auth.sign_in.get_anonymous_permissions()`, as those of the methods do.
- The values of the attributes of the session of the source `transport`,
  the IP: the starts of the flows take them by the names of their
  attributes, `transport_attr_values` of `AuthStartSignUpParameters` and
  `AuthStartSignInParameters`, which the transport alone sets, and keep
  those the registry has of the transport, under their ids, with the
  values of the client, in the record of the sign-up and in the session;
  a value of no attribute is dropped, one of an attribute of another source
  or type too, with a warning. Over gRPC, the servicers of the methods
  extend `BaseAuthGrpcMethodServicer`, whose hook
  `_get_transport_attr_values()` binds each name to the function reading it
  from the call: `ip` to the IP of the peer, which an application behind a
  proxy binds to the header of its proxy.

### Changed
- Moved on to ingots 0.34, ingot-grpcio 0.13 and ingot-pymongo 0.14. The
  flags of the permissions take no `domain=` now: each enum is bound by the
  slot `permissions` of its unit, a `PermissionsSlot`, the unit an
  `OperationsOwner`, its domain the full name of the unit, the same names as
  before, `auth.profiles.tags`, `auth.methods.nickname`. The operations
  declare no constant `PERMISSIONS`: each builds its permissions by its hook
  `_get_permissions()`, through the permissions of its unit, its parent; a
  method builds its flags so in its `_get_<flow>_permissions()`,
  `self.permissions(self.permissions.flags.CAN_SIGN_UP)`. The storages, the
  caches, the dispatcher and the mailer in memory take no project in their
  `__init__`.
- The groups are in the units of their domains, as the commands are: a group
  is a slot `grp_*` of a unit extending `AuthGroupsOwner`, found by
  `AuthGroupsUnit` from the project down the owners alone, `get_names()`
  giving them. The name of a group is its full name, where it is,
  `shop.grp_buyers`, as the domain of the permissions of a unit is its full
  name; a class in no slot is a mixin of what it grants. A group in a slot of
  `AuthGroupsUnit`, which holds none now, is refused with its class: an
  application moves its groups to a unit of its own, and its memberships to
  their new names. The groups of the core: `auth.grp_anonymous`, of every
  caller that tells no one, and `auth.grp_signed_in`, of every signed-in
  user, `signed_in` before, in the slots of `AuthUnit`; neither keeps
  members, so none stored moves.
- The method of an email and a code is whole: `AuthEmailCodeMethod`, no
  more `BaseAuthEmailCodeMethod`, which an application declared with its
  own `_send_code()`. It builds its mail, a plain text in English, by
  `_build_code_mail()` and `_build_denial_mail()`, which a subclass
  overrides to change it, and sends it by the mailer of the auth in the
  background, `AuthSendCodeOperation` and `AuthSendDenialOperation` in its
  slots `op_send_code` and `op_send_denial`, run by the dispatcher of the
  auth, so that a start replies at once, for an email bound and one not
  alike: an application taking the method declares the dispatcher and the
  mailer of its auth. A sign-in by email checks at its start that the
  profile may sign in by the method: one that may not is asked for a code
  all the same, none sent, and its email gets the word that the way is
  closed.
- The servicers of the auth run their operations by `run_operation()` of
  ingot-grpcio 0.12.1, which the extra `grpcio` now requires, on ingots
  0.33.2, for the caller of the hook `_get_caller()`: those open to anyone,
  the metadata, the starts of the methods, the answers of the flows, extend
  `GrpcServicer` alone and run for the anonymous caller of the project
  whatever a call bears; the others extend `BaseAuthGrpcServicer`, for the
  caller of the token, the anonymous one with none. `_get_anonymous_caller()`
  is gone: a subclass overrides `_get_caller()`, an application closes the
  metadata by its group `auth.grp_anonymous`.
- What a step asks for is described by the kind of its answer, not by the
  method: `AuthCodeChallenge(length)` of `ingot_auth.methods`, a code sent by
  mail, an SMS, an app, in place of `AuthEmailCodeChallenge` of the method of
  the email.

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
