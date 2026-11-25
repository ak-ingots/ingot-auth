"""
The operations of the password: its change by its user, the event of it, and
the mail telling it, the subscriber the core declares.
"""

__all__ = (
    "AuthChangePasswordOperation",
    "AuthChangePasswordParameters",
    "AuthChangePasswordResult",
    "AuthMailPasswordChangedOperation",
    "AuthPasswordChanged",
)

import asyncio
import datetime
import logging
import typing as t
from dataclasses import dataclass, field

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from ingot_auth.caches import AuthCaller
from ingot_auth.storages import (
    AuthActivityAction,
    AuthSecretChangedError,
    AuthSecretNotFoundError,
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
)

from .errors import AuthPasswordRefusedError
from .policies import AuthPasswordSetParameters

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.project import AuthProject
    from ingot_auth.storages import AuthAttrValue

    from . import AuthPassword

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthPasswordChanged:
    """
    The password of a profile was changed, in a session: its uid, and the
    values of its attributes by their names, the device, the place.
    """

    profile_uid: str
    session_uid: str
    session_attr_values: "Mapping[str, AuthAttrValue]"
    changed_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthChangePasswordParameters:
    """The old password and the new one: neither in its ``repr``."""

    old: str = field(repr=False)
    new: str = field(repr=False)


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthChangePasswordResult:
    """How many other sessions of the profile the change closed."""

    revoked: int


class AuthChangePasswordOperation(
    BaseOperation[AuthChangePasswordParameters, AuthChangePasswordResult]
):
    """
    Changes the password of the caller, in its session, the old one given:
    the old verified, the new checked by ``policies_change`` and written on
    the condition that the hash read is still there; the other sessions of
    the profile closed, ``REVOKED`` by the user, and the change recorded,
    all in one transaction. Then its event, ``ev_changed``: the user told.

    :raises AuthPasswordRefusedError: the old password is not that of the
        profile, it has none, the caller has no session, or the password
        was changed meanwhile.
    :raises AuthMethodInvalidError: the new one breaks policies.
    """

    project: "AuthProject"
    parent: "AuthPassword"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_CHANGE)

    @t.override
    async def _run(
        self, parameters: AuthChangePasswordParameters, metadata: OperationMetadata
    ) -> AuthChangePasswordResult:
        caller = metadata.caller
        if not isinstance(caller, AuthCaller):
            raise AuthPasswordRefusedError.create()
        password, auth = self.parent, self.project.auth
        storage = auth.storage
        try:
            secret = await storage.profiles.secrets.get(caller.uid)
        except AuthSecretNotFoundError:
            secret = None
        old = password.normalize(parameters.old)
        if not await password._verify_secret(old, secret):
            raise AuthPasswordRefusedError.create()
        assert secret is not None
        new = password.normalize(parameters.new)
        identities = await storage.profiles.identities.get_of(caller.uid)
        await password._check_new(
            password.policies_change,
            AuthPasswordSetParameters(
                value=new,
                identifiers=tuple(identity.value for identity in identities),
            ),
            metadata,
        )
        hashed = await password.hash(new)
        sessions = auth.sessions
        revoked = 0
        attr_values: "Mapping[int, AuthAttrValue]" = {}
        try:
            async with storage.transaction():
                await storage.profiles.secrets.replace(caller.uid, secret, hashed)
                await auth.activities.record(
                    password, caller.uid, AuthActivityAction.UPDATE, metadata
                )
                for session in await storage.sessions.get_open(caller.uid):
                    if session.uid == caller.session_uid:
                        attr_values = session.attr_values
                        continue
                    try:
                        await sessions.close(
                            caller.uid, session.uid, AuthSessionCloseReason.REVOKED
                        )
                    except AuthSessionNotFoundError:
                        continue  # closed meanwhile, by another request
                    await auth.activities.record(
                        sessions, session.uid, AuthActivityAction.REVOKE, metadata
                    )
                    revoked += 1
        except AuthSecretChangedError:
            raise AuthPasswordRefusedError.create() from None
        event = AuthPasswordChanged(
            profile_uid=caller.uid,
            session_uid=caller.session_uid,
            session_attr_values=await self._name_attr_values(attr_values),
            changed_at=sessions._get_now(),
        )
        self.project.events.publish(password.ev_changed, event, metadata)
        return AuthChangePasswordResult(revoked=revoked)

    async def _name_attr_values(
        self, values: "Mapping[int, AuthAttrValue]"
    ) -> "Mapping[str, AuthAttrValue]":
        """The values of the attributes of a session, by their names."""
        attrs = await self.project.auth.storage.sessions.attrs.get_all()
        names = {attr.uid: attr.name for attr in attrs}
        return {names[uid]: value for uid, value in values.items() if uid in names}


class AuthMailPasswordChangedOperation(BaseOperation[AuthPasswordChanged, None]):
    """
    The subscriber of the change of a password the core declares: a mail to
    every email bound to the profile, by the mailer of the project, built by
    :meth:`AuthPassword._build_changed_mail`; a profile with no email gets
    none, logged. The identities of the kinds of :attr:`IDENTIFIER_KINDS`
    are the emails.
    """

    IDENTIFIER_KINDS: t.ClassVar[tuple[str, ...]] = ("email",)

    project: "AuthProject"
    parent: "AuthPassword"

    # the subscriber of a change the caller made: nothing more to require
    @t.override
    def _get_permissions(self) -> Permissions:
        return Permissions()

    @t.override
    async def _run(
        self, parameters: AuthPasswordChanged, metadata: OperationMetadata
    ) -> None:
        identities = await self.project.auth.storage.profiles.identities.get_of(
            parameters.profile_uid
        )
        emails = [
            identity.value
            for identity in identities
            if identity.kind in self.IDENTIFIER_KINDS
        ]
        if not emails:
            logger.info("%s: no email to tell of its password", parameters.profile_uid)
            return
        mailer = self.project.mail.mailer
        await asyncio.gather(
            *(
                mailer.send(self.parent._build_changed_mail(parameters, email))
                for email in emails
            )
        )
