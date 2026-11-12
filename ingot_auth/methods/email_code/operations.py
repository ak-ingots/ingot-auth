"""
The operations of the method run in the background by the dispatcher of the
auth: the mail of the method, built by its hooks and sent by the mailer of
the auth.
"""

__all__ = (
    "AuthSendCodeOperation",
    "AuthSendCodeParameters",
    "AuthSendDenialOperation",
    "AuthSendDenialParameters",
)

import typing as t
from dataclasses import dataclass, field

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject

    from . import AuthEmailCodeMethod


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSendCodeParameters:
    """
    A code to send to an email, by the method of the name: the email and the
    code stay out of the ``repr``, as the runner logs the parameters.
    """

    method: str
    email: str = field(repr=False)
    code: str = field(repr=False)


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSendDenialParameters:
    """
    An email to tell the sign-in by the method of the name is closed to its
    profile: the email stays out of the ``repr``.
    """

    method: str
    email: str = field(repr=False)


class AuthSendCodeOperation(BaseOperation[AuthSendCodeParameters, None]):
    """Sends a code to an email, the mail built by the method."""

    # run by the method for the caller its flow checked, nothing to require
    PERMISSIONS = Permissions()

    project: "AuthProject"

    @t.override
    async def _run(
        self, parameters: AuthSendCodeParameters, metadata: OperationMetadata
    ) -> None:
        method = _get_method(self.project, parameters.method)
        mail = method._build_code_mail(parameters.email, parameters.code)
        await self.project.auth.mailer.send(mail)


class AuthSendDenialOperation(BaseOperation[AuthSendDenialParameters, None]):
    """
    Tells an email the sign-in is closed to its profile, the mail built by
    the method.
    """

    # run by the method for the caller its flow checked, nothing to require
    PERMISSIONS = Permissions()

    project: "AuthProject"

    @t.override
    async def _run(
        self, parameters: AuthSendDenialParameters, metadata: OperationMetadata
    ) -> None:
        method = _get_method(self.project, parameters.method)
        await self.project.auth.mailer.send(method._build_denial_mail(parameters.email))


def _get_method(project: "AuthProject", name: str) -> "AuthEmailCodeMethod":
    # the method gives its own name to the parameters
    return t.cast("AuthEmailCodeMethod", project.auth.methods.get(name))
