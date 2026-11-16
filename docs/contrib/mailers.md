# Mailers

The mail of the methods, the code of a sign-up or a sign-in by email, the
word of a sign-in closed, goes by the mailer of the project, that of
[ingot-mail](https://pypi.org/project/ingot-mail/): `AuthProject` is its
`MailProject`, so the auth adds no mailer of its own and an application
sends its other mail by the same one. A method builds a `Mail` of
ingot-mail, the dispatcher runs the sending in the background; the sender
is `MAIL_FROM`, the configs of the server are those of ingot-mail,
`MAIL_SMTP_*`.

The mail unit of the project declares the mailer: one in memory, which
delivers nothing and keeps the mail sent, for the tests and the addon run
on its own,

```python
from ingot_mail.contrib.memory import MemoryMailer
from ingot_mail.mail import MailUnit


class AppMailUnit(MailUnit):
    mailer = Slot(MemoryMailer)


class AppProject(AuthProject):
    mail = Slot(AppMailUnit)
```

or that of SMTP, `AiosmtplibMailer` of `ingot_mail.contrib.aiosmtplib`,
under the extra `aiosmtplib` of ingot-mail. The mailers and their contract
are described by ingot-mail.
