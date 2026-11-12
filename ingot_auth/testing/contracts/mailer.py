"""
The contract of a mailer: what a backend guarantees, whatever it delivers
by. A test case tells where the mail it delivered is read back, a server of
SMTP catching it for one.
"""

__all__ = ("AuthMailerContract",)

import abc
import typing as t

from ingot_auth.mailers import AuthMail

from .base import BaseAuthContract

CODE: t.Final = AuthMail(
    to="al@b.c", subject="Your code", text="Your code is 123456.\n"
)


class AuthMailerContract(BaseAuthContract):
    """
    The mailer of the auth of a project: a mail sent is delivered as it was
    sent, its address, its subject and its text.
    """

    @abc.abstractmethod
    async def get_delivered(self) -> tuple[AuthMail, ...]:
        """The mail the mailer of the project delivered so far."""
        raise NotImplementedError(f"{type(self).__qualname__}.get_delivered")

    async def test_a_mail_is_delivered_as_sent(self) -> None:
        await self.project.auth.mailer.send(CODE)
        self.assertEqual(await self.get_delivered(), (CODE,))

    async def test_a_mail_of_any_letters_is_delivered_intact(self) -> None:
        mail = AuthMail(to="al@b.c", subject="Ваш код", text="Код: 123456 — ✓\n")
        await self.project.auth.mailer.send(mail)
        self.assertEqual(await self.get_delivered(), (mail,))

    async def test_every_mail_is_delivered(self) -> None:
        mails = [
            AuthMail(to=f"{name}@b.c", subject="Your code", text=f"{name}\n")
            for name in ("al", "bo", "cy")
        ]
        for mail in mails:
            await self.project.auth.mailer.send(mail)
        delivered = await self.get_delivered()
        self.assertEqual(sorted(delivered, key=lambda mail: mail.to), mails)
