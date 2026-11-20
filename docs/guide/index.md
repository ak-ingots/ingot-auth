# Guide

An application inherits `AuthProject`, the project of the mail of
[ingot-mail](https://pypi.org/project/ingot-mail/) with the addon's
settings, logging and `auth` unit, or takes the classes of the addon
among the bases of its own, as the
[addon guide](https://ingots.readthedocs.io/en/latest/defaults/addon.html)
of Ingots shows. It chooses its storage, its cache, its transports and its mailer
among those of {doc}`../contrib/index`.

The addon follows the
[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/): its
[authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html),
[password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html),
[session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html),
[forgot password](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html),
[multifactor authentication](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)
and [credential stuffing](https://cheatsheetseries.owasp.org/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.html)
cheat sheets. What of them is built, what is to come and what is left to
the client or the infrastructure in front is mapped in
[the design of the auth](https://github.com/ak-ingots/ingots-libs/blob/main/docs/design/auth/README.md#owasp).

```{toctree}
:maxdepth: 2

methods
sign-in
access
profiles
sessions
activities
configs
```
