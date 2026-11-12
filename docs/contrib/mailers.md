# Mailers

The mailer delivers the mail of the methods: the code of a sign-up or a
sign-in by email, the word of a sign-in closed. `BaseAuthMailer` of
`ingot_auth.mailers` is the facade, the slot `mailer` of the auth:
`send(mail)` delivers an `AuthMail`, its address, its subject and its text,
the address and the text out of its `repr`, as the text may hold a code. A
method builds its mail, the dispatcher runs the sending in the background.

## In memory

`AuthMemoryMailer` of `ingot_auth.contrib.mailers.memory`, with no extra,
for the tests and the addon run on its own: it delivers nothing, and keeps
the mail sent, `get_sent()` giving it in its order.

```python
from ingot_auth.contrib.mailers.memory import AuthMemoryMailer


class AppAuthUnit(AuthUnit):
    mailer = Slot(AuthMemoryMailer)
```

`AuthMailerContract` of `ingot_auth.testing.contracts` tells what a
mailer guarantees: a mail sent is delivered as it was sent. A test case of
a backend runs it and reads the mail back by `get_delivered()`, from the
memory here, from a server catching SMTP, Mailpit in a container, for a
mailer that delivers.

A mailer that delivers, by SMTP or a service of mail, comes with the addon
of the ecosystem it is written against, as the storage in MongoDB comes
with ingot-pymongo: the configs of the server are of the environment, of
that addon.
