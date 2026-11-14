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
a code sent to it comes too, of two steps, `AuthEmailCodeMethod`, whole as
every method of the catalogue is: the application declares it and plugs a
mailer into its auth ({doc}`../contrib/mailers`), nothing more.

```python
from ingot_auth.methods.email_code import AuthEmailCodeMethod


class AppMethods(AuthMethodsUnit):
    email_code = Slot(AuthEmailCodeMethod)
```

Its email is checked on a sign-up by its group `policies_sign_up_email`.
A start replies at once and the mail goes in the background, its
operations run by the dispatcher of the auth
({doc}`../contrib/dispatchers`): an email bound and one not bound reply in
the same time, and the client shows the form of the code without waiting
for the mail. A sign-in sends nothing to an email bound to no profile,
asking for the code all the same, no code then good; to the email of a
profile that may not sign in by the method, it sends the word that the way
is closed in place of the code, so that who owns the email learns it and
who does not learns nothing.

The mail is a plain text in English. A subclass changes it, its words,
its language, a template, by the hooks that build it:

```python
class AppEmailCodeMethod(AuthEmailCodeMethod):
    @t.override
    def _build_code_mail(self, email: str, code: str) -> AuthMail:
        return AuthMail(to=email, subject="Votre code", text=f"Code : {code}")
```

## Toggles and permissions

A method bound binds its configs too: the toggles of its flows, on by
default, which the application mixes into its configs. A toggle closes a
flow in an environment, and the metadata lists the methods with their
flows open or closed:

```python
class AppConfigs(AuthNicknameConfigs, AuthEmailCodeConfigs, AuthConfigs):
    AUTH_SIGN_UP_NICKNAME_ENABLED = BoolConfig(False)  # by invitation only
```

The sign-up has a toggle of its own, `AUTH_SIGN_UP_ENABLED`, on by
default, of every method: off, it closes the sign-up of each method too,
and the metadata lists them closed. The sign-in has none: what limits it
comes later, as a strategy.

The flows of a method are permissions too, a domain a method,
`AuthNicknamePermissions` of `auth.methods.nickname`, a flag a flow: a
sign-up by a method needs its `CAN_SIGN_UP` besides the `CAN_SIGN_UP` of
the sign-up, and the toggles give the anonymous caller the flags of the
flows open, so that a flow closed is refused as any operation the caller
may not run. The anonymous caller is that of the project, of its
`operations.callers`, `AuthCallersProvider` of `AuthProject`, with what the
group `grp_anonymous` of the access grants ({doc}`access`): what the units of
the auth give anyone, the flags of the flows and of the methods open and
the reading of the metadata. A transport runs what is open to anyone for
it:

```python
anonymous = project.operations.callers.get_anonymous()
```

An application grants anyone more, or less, in its own group, `super()`
first: the metadata closed, for one,

```python
class AppAnonymousGroup(AuthAnonymousGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        metadata = self.project.auth.metadata.permissions
        return super()._get_permissions() - metadata(metadata.flags.CAN_READ)


class AppGroupsUnit(AuthGroupsUnit):
    grp_anonymous = Slot(AppAnonymousGroup)
```
