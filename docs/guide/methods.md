# Methods

The methods of signing up and in are slots of the methods of the auth,
named by their slots. The addon comes with a catalogue of them, none bound
until the application declares its slot: a nickname and a password,

```python
from ingot_auth.methods.nickname import AuthNicknameMethod


class AppMethods(AuthMethodsUnit):
    nickname = Slot(AuthNicknameMethod)
```

## Policies

The nickname of a sign-up is checked by the group of the policies of the
method, its slot `policies_sign_up_nickname`, the password by that of the
password, which is of the profile, one whatever identifier it signs in by:
`policies_set` of `AuthPassword`, the slot `password` of the methods. Both
are empty unless the application gives policies to them in a subclass, each
an operation, run together, so that a client learns every policy broken at
once; the parameters of the hash of the password, scrypt, are changed by
subclassing too:

```python
class AppPasswordLength(AuthLengthPolicy):
    CONFIG = AuthLengthConfig(min=12)


class AppPassword(AuthPassword):
    # a new password, by any method
    policies_set = AuthPasswordSetPolicies(AppPasswordLength)


class AppMethods(AuthMethodsUnit):
    nickname = Slot(AuthNicknameMethod)
    password = Slot(AppPassword)
```

## Identifiers

An identifier is bound to a profile once, whatever method verifies it: a
method names the kind of its identifier, `nickname`, `email`. An email and
a code sent to it comes too, of two steps, the sending of the code the
application's:

```python
from ingot_auth.methods.email_code import BaseAuthEmailCodeMethod


class AppEmailCodeMethod(BaseAuthEmailCodeMethod):
    @t.override
    async def _send_code(self, email: str, code: str) -> None:
        ...  # by the mail of the application


class AppMethods(AuthMethodsUnit):
    email_code = Slot(AppEmailCodeMethod)
```

its email checked on a sign-up by its group `policies_sign_up_email`.

## Toggles and permissions

A method bound binds its configs too: the toggles of its flows, on by
default, which the application mixes into its configs. A toggle closes a
flow in an environment, and the metadata lists the methods with their
flows open or closed:

```python
class AppConfigs(AuthNicknameConfigs, AuthEmailCodeConfigs, AuthConfigs):
    AUTH_SIGN_UP_NICKNAME_ENABLED = BoolConfig(False)  # by invitation only
```

The flows of a method are permissions too, a domain a method,
`AuthNicknamePermissions` of `auth.methods.nickname`, a flag a flow: a
sign-up by a method needs its `CAN_SIGN_UP` besides the `CAN_SIGN_UP` of
the sign-up, and the toggles give the anonymous caller the flags of the
flows open, so that a flow closed is refused as any operation the caller
may not run:

```python
anonymous = Caller(
    uid="anonymous",
    permissions=Permissions(
        AuthSignUpPermissions.CAN_SIGN_UP, AuthSignInPermissions.CAN_SIGN_IN
    )
    | project.auth.methods.get_anonymous_permissions(),
)
```
