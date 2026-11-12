"""
The mailer of the auth: the interface a backend in
``ingot_auth.contrib.mailers`` implements, which delivers the mail of the
methods, the code of the method of an email for one. A method builds its
mail and hands it to the mailer; the dispatcher of the auth runs the
sending in the background.
"""

__all__ = ("AuthMail", "BaseAuthMailer")

import abc
import typing as t
from dataclasses import dataclass, field

from ingots.puer import Entity

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthMail:
    """
    A mail to send: its address and its text stay out of the ``repr``, as
    the text may hold a code.
    """

    to: str = field(repr=False)
    subject: str
    text: str = field(repr=False)


class BaseAuthMailer(Entity):
    """
    The mailer of the auth, the slot ``mailer`` of the auth, abstract: what a
    backend implements.
    """

    project: "AuthProject"

    @t.final
    async def send(self, mail: AuthMail) -> None:
        """Delivers a mail."""
        await self._send(mail)

    @abc.abstractmethod
    async def _send(self, mail: AuthMail) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._send")
