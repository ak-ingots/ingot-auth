"""
The mailer in memory: for the tests and the addon run on its own, delivering
nothing. An application declares it in the slot of its auth:
``mailer = Slot(AuthMemoryMailer)``.
"""

__all__ = ("AuthMemoryMailer",)

import typing as t

from ingot_auth.mailers import AuthMail, BaseAuthMailer

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemoryMailer(BaseAuthMailer):
    """The mail is kept, in the order it is sent, for the tests to read."""

    def __init__(self, project: "Project") -> None:
        super().__init__(project)
        self._sent: list[AuthMail] = []

    @t.final
    def get_sent(self) -> tuple[AuthMail, ...]:
        """The mail sent so far, in its order."""
        return tuple(self._sent)

    @t.override
    async def _send(self, mail: AuthMail) -> None:
        self._sent.append(mail)
