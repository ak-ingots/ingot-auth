# Transports

A transport turns the calls of the clients into the operations of the auth,
for the caller of the session of their token.

## gRPC

`ingot_auth.contrib.transports.grpcio`, with the extra `grpcio`, on
[ingot-grpcio](https://github.com/ak-ingots/ingot-grpcio): the project joins
`GrpcProject`.

```sh
uv add 'ingot-auth[grpcio]'
```

A service a registry and a method, each in a binding of its own, so that a
server serves the ones it should: a public server the metadata and the
methods the application takes, an internal one the administration too.

The contract is the API of the addon, `ingot_auth.api`: its services in
`ingot_auth.api.<path>.v1`. A binding binds its service under its old name
too, `ingot_auth.<path>.v1`, deprecated, so that a server serves both while
its clients move on: the attribute of the old name, `auth_metadata`, and
that of the API, `auth_metadata_temp`, its servicer `AuthGrpcMetadataServicerTemp`.
A client moves on to the stubs of the attributes `*_temp` and the messages
of `ingot_auth.api.<path>.v1`; in a coming release the attributes of the
old names take the services of the API, and `*_temp` goes.

| Binding | Services |
|---|---|
| `AuthGrpcMetadataBinding` | `Metadata` of `ingot_auth.metadata.v1` |
| `AuthGrpcNicknameBinding` | `Nickname` of `ingot_auth.methods.nickname.v1`: `SignUp`, `SignIn` |
| `AuthGrpcEmailCodeBinding` | `EmailCode` of `ingot_auth.methods.email_code.v1`: `StartSignUp`, `StartSignIn` |
| `AuthGrpcFlowsBinding` | `SignUp` of `ingot_auth.sign_up.v1` and `SignIn` of `ingot_auth.sign_in.v1`: `AnswerSignUp`, `AnswerSignIn`, the answers of a method of more steps; `SignOut` of `ingot_auth.sign_out.v1`, the sign-out of the caller of the token, open to any; `AuthGrpcSignUpBinding`, `AuthGrpcSignInBinding`, `AuthGrpcSignOutBinding` apart |
| `AuthGrpcProfilesBinding` | `Profiles` of `ingot_auth.profiles.v1`: `GetOwnProfile`, the profile of the caller; `SetProfileTags`, `SetProfileAttrValues`, the values of a profile |
| `AuthGrpcProfileRegistriesBinding` | `Tags` and `Attrs` of `ingot_auth.profiles.*.v1`; `AuthGrpcTagsBinding`, `AuthGrpcAttrsBinding` apart |
| `AuthGrpcSessionsBinding` | `Sessions` of `ingot_auth.sessions.v1`: `ListOwnSessions`, `RevokeOwnSession`, `RevokeOtherSessions`, the sessions of the caller's own; `ListSessions`, those of a profile, the record of its sign-ins; `RevokeSessions`, every open one of a profile; `SweepSessions`, the expired ones |
| `AuthGrpcSessionRegistriesBinding` | `Attrs` and `Presets` of `ingot_auth.sessions.*.v1`; `AuthGrpcSessionAttrsBinding`, `AuthGrpcSessionPresetsBinding` apart |
| `AuthGrpcAccessBinding` | `Groups` and `Members` of `ingot_auth.access.*.v1`; `AuthGrpcGroupsBinding`, `AuthGrpcMembersBinding` apart |
| `AuthGrpcActivitiesBinding` | `Activities` of `ingot_auth.activities.v1`: `ListActivities`, the activity log, for the auditors |
| `AuthGrpcAdminBinding` | those of the profiles and of the sessions, their registries and their services, the access and the activity log |

The errors unit of the gRPC takes `AuthGrpcErrorsUnit` as a base, the statuses of the errors of the
auth. The public server is the default one here; an internal one, serving
`AuthGrpcAdminBinding`, extends `BaseGrpcServer` with configs of its own,
as ingot-grpcio tells:

```python
from ingot_grpcio import GrpcProject
from ingot_grpcio.grpc import GrpcUnit
from ingot_grpcio.grpc.servers import DefaultGrpcServer, GrpcServersUnit

from ingot_auth.contrib.transports.grpcio import (
    AuthGrpcEmailCodeBinding,
    AuthGrpcErrorsUnit,
    AuthGrpcFlowsBinding,
    AuthGrpcMetadataBinding,
    AuthGrpcNicknameBinding,
)


class AppGrpcServer(
    AuthGrpcMetadataBinding,
    AuthGrpcNicknameBinding,
    AuthGrpcEmailCodeBinding,
    AuthGrpcFlowsBinding,  # the answers of the code
    DefaultGrpcServer,
):
    pass


class AppGrpcServersUnit(GrpcServersUnit):
    default = Slot(AppGrpcServer)


class AppGrpcUnit(GrpcUnit):
    errors = Slot(AuthGrpcErrorsUnit)
    servers = Slot(AppGrpcServersUnit)


class AppProject(AuthProject, GrpcProject):
    # joined with those of the auth, as for MongoDB
    settings = Slot(AppSettingsUnit)
    logging = Slot(AppLoggingUnit)
    grpc = Slot(AppGrpcUnit)
    auth = Slot(AppAuthUnit)
```

A method of the sign-up and the sign-in runs for the anonymous caller,
given the flags of the flows and of the methods open by their toggles,
`AUTH_SIGN_UP_ENABLED` closing the sign-up of every method, with
the values of the attributes of the session the client gives, `AttrValue`
of `ingot_auth.attrs.v1`. Its start gives the result of the flow:
its end, the profile signed up or the session signed in, or what it asks
for, `Challenge` of `ingot_auth.methods.v1`, the attempt to answer to and
the kind of the answer, `code` of its `length` for a code sent by mail. The
client answers by the service of the flow, whatever the method, as the
attempt knows whose challenge it is:

```python
challenge = (
    await email_code.StartSignIn(StartSignInRequest(email="alice@example.com"))
).result.challenge
answer = AnswerSignInRequest(attempt_uid=challenge.attempt_uid, code="123456")
token = (await sign_in.AnswerSignIn(answer)).result.signed_in.token
```

A wrong password, a wrong code or no such nickname is `UNAUTHENTICATED`, a
nickname taken `ALREADY_EXISTS`, a policy broken `INVALID_ARGUMENT`, a flow
closed `PERMISSION_DENIED`, an attempt gone, expired or over `NOT_FOUND`,
the client starting again.

### The token

The client sends the token of the sign-in with each call,
`authorization: Bearer <token>`, and the call runs for the caller of its
session, with the permissions its groups grant; a call with no token runs
for the anonymous one, and a token of no open session, or of one expired, is
`UNAUTHENTICATED`, the client signing in again. The metadata, the methods
and the answers of the flows run for the anonymous one, signed in or not:

```python
auth = [("authorization", f"Bearer {token}")]
await members.ListMembers(ListMembersRequest(group="app.grp_admins"), metadata=auth)
```

The anonymous caller is that of the project,
`operations.callers.get_anonymous()`, with what the group `auth.grp_anonymous`
grants ({doc}`../guide/access`). A servicer runs its
operation by `run_operation()` of ingot-grpcio, for the caller of its hook
`_get_caller()`: the servicers open to anyone extend `GrpcServicer` alone,
running for the anonymous caller whatever a call bears, the others
`BaseAuthGrpcServicer`, for the caller of the token. A subclass overrides
the hook to tell the caller otherwise.

### The attributes of the transport

The start of a flow gives the values of the attributes of the session of
the transport, by their names, as the registry keeps them
({doc}`../guide/sessions`): a servicer of a method,
`BaseAuthGrpcMethodServicer`, binds each name to the function reading its
value from the call in its hook `_get_transport_attr_values()`, `ip` to the
IP of the peer here, `None` for a call without one. Behind a proxy the
peer is the proxy: an application binds `ip` to a reader of the header the
proxy sets, trusted from its proxy alone, and binds others the same way,
in a mixin of its own mixed into each servicer of a method it serves:

```python
class AppTransportAttrs(BaseAuthGrpcMethodServicer):
    @t.override
    def _get_transport_attr_values(
        self, context: Context
    ) -> dict[str, AuthAttrValue | None]:
        return super()._get_transport_attr_values(context) | {
            "ip": get_forwarded_ip(context),
        }


class AppNicknameServicer(AppTransportAttrs, AuthGrpcNicknameServicer):
    pass


class AppNicknameBinding(AuthGrpcNicknameBinding):
    auth_methods_nickname = GrpcService(NicknameStub, AppNicknameServicer)
```

## HTTP

`ingot_auth.contrib.transports.starlette`, with the extra `starlette`, on
[ingot-starlette](https://github.com/ak-ingots/ingot-starlette): the project
joins `StarletteProject`, no grpcio. Its endpoints are the services of the
contract, the same RPCs gRPC serves, transcoded to JSON by the annotations
`google.api.http` of their methods (AIP-127): the request and the reply are
the canonical JSON of proto3 of their messages, the fields of their names.

```sh
uv add 'ingot-auth[starlette]'
```

| Endpoint | Routes |
|---|---|
| `AuthStarletteMetadataEndpoint` | `GET /v1/metadata` |
| `AuthStarletteNicknameEndpoint` | `POST /v1/methods/nickname:signUp`, `POST /v1/methods/nickname:signIn` |
| `AuthStarletteEmailCodeEndpoint` | `POST /v1/methods/emailCode:startSignUp`, `POST /v1/methods/emailCode:startSignIn` |
| `AuthStarletteSignUpEndpoint` | `POST /v1/signUp:answer`, the answer of a method of more steps |
| `AuthStarletteSignInEndpoint` | `POST /v1/signIn:answer` |
| `AuthStarletteSignOutEndpoint` | `POST /v1/session:signOut` |
| `AuthStarletteOwnSessionsEndpoint` | `GET /v1/ownSessions`, `POST /v1/ownSessions/{session_uid}:revoke`, `POST /v1/ownSessions:revokeOthers`, the sessions of the caller's own |
| `AuthStarletteOwnProfileEndpoint` | `GET /v1/ownProfile`, the profile of the caller, its values, its permissions and its hash |

The administration, the registries, the sessions and the values of the
profiles of an operator, the access and the activity log, is served over
gRPC alone for now.

An application mounts those it serves in the subtree of its API, of JSON
alone, with the middleware telling the hash of the profile of the caller,
and takes `AuthStarletteErrorsUnit` as the base of its errors unit:

```python
from ingot_starlette import StarletteProject
from ingot_starlette.starlette import StarletteApiUnit, StarletteEndpoint, StarletteUnit

from ingot_auth.contrib.transports.starlette import (
    AuthStarletteEmailCodeEndpoint,
    AuthStarletteErrorsUnit,
    AuthStarletteMetadataEndpoint,
    AuthStarletteOwnProfileEndpoint,
    AuthStarletteOwnSessionsEndpoint,
    AuthStarletteProfileHashMiddleware,
    AuthStarletteSignInEndpoint,
    AuthStarletteSignOutEndpoint,
    AuthStarletteSignUpEndpoint,
)


class AppAuthEndpoint(StarletteEndpoint, Unit):
    metadata = Slot(AuthStarletteMetadataEndpoint)
    email_code = Slot(AuthStarletteEmailCodeEndpoint)
    sign_up = Slot(AuthStarletteSignUpEndpoint)  # the answers of the code
    sign_in = Slot(AuthStarletteSignInEndpoint)
    sign_out = Slot(AuthStarletteSignOutEndpoint)
    own_sessions = Slot(AuthStarletteOwnSessionsEndpoint)
    own_profile = Slot(AuthStarletteOwnProfileEndpoint)

    @t.override
    def _iter_routes(self):
        for endpoint in (
            self.metadata,
            self.email_code,
            self.sign_up,
            self.sign_in,
            self.sign_out,
            self.own_sessions,
            self.own_profile,
        ):
            yield from endpoint.get_routes()


class AppApiUnit(StarletteApiUnit):
    auth = Slot(AppAuthEndpoint)

    @t.override
    def _iter_routes(self):
        yield Mount("/auth", routes=self.auth.get_routes())

    @t.override
    def _iter_middleware(self):
        yield Middleware(AuthStarletteProfileHashMiddleware)


class AppStarletteUnit(StarletteUnit):
    errors = Slot(AuthStarletteErrorsUnit)
    api = Slot(AppApiUnit)


class AppProject(AuthProject, StarletteProject):
    # joined with those of the auth, as for gRPC
    settings = Slot(AppSettingsUnit)
    logging = Slot(AppLoggingUnit)
    starlette = Slot(AppStarletteUnit)
    auth = Slot(AppAuthUnit)
```

A sign-in, then a request of the caller, its token in `Authorization`:

```text
POST /api/auth/v1/methods/nickname:signIn
{"nickname": "alice", "password": "..."}
→ 200 {"result": {"signed_in": {"session_uid": "...", "token": "..."}}}

POST /api/auth/v1/session:signOut
Authorization: Bearer <token>
→ 200 {}   ingot-auth-user-profile-hash: ...
```

The caller is told as over gRPC: the metadata and the methods run for the
anonymous one, whatever a request bears; the sign-out for the caller of the
token, the anonymous one of a token closed, expired or unknown; the
others, `BaseAuthStarletteEndpoint` with an RPC of the signed-in, for the
caller of the token. A failure is a problem of RFC 9457,
`application/problem+json`, of the status of HTTP of the code of gRPC
(AIP-193), with the reason, the domain and the metadata of the `ErrorInfo`
gRPC tells: a wrong password is 401, the reason `METHOD_REFUSED`; a
nickname taken 409, `IDENTITY_CONFLICT`, the metadata `{"kind":
"nickname"}`; a request not of its message 400. A response to a caller
signed in tells the hash of its profile in the header
`ingot-auth-user-profile-hash`, by the middleware.

The attributes of the transport are read as over gRPC, by the hook
`_get_transport_attr_values()` of `BaseAuthStarletteEndpoint`: `ip` the
client of the connection; behind a proxy, `uvicorn --proxy-headers` tells
the forwarded one, or a subclass reads the header of the proxy.
