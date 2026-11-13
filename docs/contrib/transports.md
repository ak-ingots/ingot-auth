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

| Binding | Services |
|---|---|
| `AuthGrpcMetadataBinding` | `Metadata` of `ingot_auth.metadata.v1` |
| `AuthGrpcNicknameBinding` | `Nickname` of `ingot_auth.methods.nickname.v1`: `SignUp`, `SignIn` |
| `AuthGrpcEmailCodeBinding` | `EmailCode` of `ingot_auth.methods.email_code.v1`: `StartSignUp`, `StartSignIn` |
| `AuthGrpcFlowsBinding` | `SignUp` of `ingot_auth.sign_up.v1` and `SignIn` of `ingot_auth.sign_in.v1`: `AnswerSignUp`, `AnswerSignIn`, the answers of a method of more steps; `AuthGrpcSignUpBinding`, `AuthGrpcSignInBinding` apart |
| `AuthGrpcProfilesBinding` | `Tags` and `Attrs` of `ingot_auth.profiles.*.v1`; `AuthGrpcTagsBinding`, `AuthGrpcAttrsBinding` apart |
| `AuthGrpcSessionsBinding` | `Attrs` and `Presets` of `ingot_auth.sessions.*.v1`; `AuthGrpcSessionAttrsBinding`, `AuthGrpcSessionPresetsBinding` apart |
| `AuthGrpcAccessBinding` | `Groups` and `Members` of `ingot_auth.access.*.v1`; `AuthGrpcGroupsBinding`, `AuthGrpcMembersBinding` apart |
| `AuthGrpcAdminBinding` | those of the profiles, the sessions and the access |

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
of `ingot_auth.sessions.attrs.v1`. Its start gives the result of the flow:
its end, the profile signed up or the session signed in, or what it asks
for, `Challenge` of `ingot_auth.methods.v1`, the attempt to answer to and
the kind of the answer, `code` of its `length` for a code sent by mail. The
client answers by the service of the flow, whatever the method, as the
attempt knows whose challenge it is:

```python
challenge = (
    await email_code.StartSignIn(StartSignInRequest(email="alice@example.com"))
).result.challenge
answer = AnswerSignInRequest(attempt_id=challenge.attempt_id, code="123456")
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
await members.ListMembers(ListMembersRequest(group="admins"), metadata=auth)
```

The anonymous caller is that of the project,
`operations.callers.get_anonymous()`, with what the group `grp_anonymous`
grants ({doc}`../guide/access`). A servicer runs its
operation by `run_operation()` of ingot-grpcio, for the caller of its hook
`_get_caller()`: the servicers open to anyone extend `GrpcServicer` alone,
running for the anonymous caller whatever a call bears, the others
`BaseAuthGrpcServicer`, for the caller of the token. A subclass overrides
the hook to tell the caller otherwise.
