"""The operations of the sign-up."""

__all__ = (
    "AuthAnswerSignUpOperation",
    "AuthStartSignUpOperation",
    "BaseAuthSignUpOperation",
)

import os
import typing as t

from ingots.defaults.operations import OperationMetadata, Permissions

from ingot_auth.methods import AuthStep, AuthVerified, BaseAuthFlowOperation
from ingot_auth.storages import AuthIdentity, AuthProfile, AuthSignUpRecord

from .items import (
    AuthAnswerSignUpParameters,
    AuthSignedUp,
    AuthSignUpChallenge,
    AuthSignUpResult,
    AuthStartSignUpParameters,
)

if t.TYPE_CHECKING:
    from . import AuthSignUpUnit
    from collections.abc import Mapping

    from ingot_auth.methods import BaseAuthMethod
    from ingot_auth.storages import AuthAttrValue


class BaseAuthSignUpOperation[ParametersType](
    BaseAuthFlowOperation[ParametersType, AuthSignUpResult]
):
    """
    A step of the sign-up: a challenge keeps an attempt for the answer, the
    verified subject ends the sign-up with a profile bound to it. A sign-up
    by a method needs its ``CAN_SIGN_UP``. The uid of a new profile comes
    from :meth:`_create_uid`, the time from :meth:`_get_now`.
    """

    FLOW: t.ClassVar[str] = "sign_up"
    parent: "AuthSignUpUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_SIGN_UP)

    @t.override
    def _get_method_permissions(
        self, method: "BaseAuthMethod[t.Any, t.Any, t.Any]"
    ) -> Permissions:
        return method.get_sign_up_permissions()

    @t.override
    async def _start_method(
        self,
        method: "BaseAuthMethod[t.Any, t.Any, t.Any]",
        parameters: object,
        metadata: OperationMetadata,
    ) -> AuthStep:
        return await method.start_sign_up(parameters, metadata)

    @t.override
    def _create_challenge(self, attempt_id: str, challenge: object) -> AuthSignUpResult:
        return AuthSignUpChallenge(attempt_id=attempt_id, challenge=challenge)

    @t.override
    async def _complete(
        self,
        method: "BaseAuthMethod[t.Any, t.Any, t.Any]",
        verified: AuthVerified,
        attr_values: "Mapping[int, AuthAttrValue]",
    ) -> AuthSignUpResult:
        """
        Ends the sign-up, in one transaction of the storage: binds the
        subject, an identifier of the kind of the method, to a new profile,
        keeps the secret of the profile if the method gave one, creates the
        profile and keeps the record. The binding goes first, so of two
        sign-ups of one identifier, by one method or two of its kind, only one
        goes on.

        :raises AuthIdentityConflictError: the identifier is bound already.
        """
        storage = self.project.auth.storage
        uid = self._create_uid()
        now = self._get_now()
        identity = AuthIdentity(
            kind=method.IDENTIFIER_KIND, value=verified.subject, uid=uid
        )
        record = AuthSignUpRecord(
            uid=uid, method=method.get_name(), signed_up_at=now, attr_values=attr_values
        )
        async with storage.transaction():
            await storage.profiles.identities.create(identity)
            if verified.secret is not None:
                await storage.profiles.secrets.put(uid, verified.secret)
            await storage.profiles.create(AuthProfile(uid=uid, created_at=now))
            await storage.sign_up.records.add(record)
        return AuthSignedUp(uid=uid)

    def _create_uid(self) -> str:
        """
        The uid of a new profile: random, telling nothing of the user; 128 bits,
        32 hexadecimal digits, as the uids of the runs of ingots.
        """
        return os.urandom(16).hex()


class AuthStartSignUpOperation(BaseAuthSignUpOperation[AuthStartSignUpParameters]):
    """
    Starts a sign-up by a method, with the values of the attributes of the
    session the client and the transport give.

    :raises AuthMethodNotFoundError: no method has the name.
    :raises AuthMethodUnsupportedError: the method signs no one up.
    :raises OperationPermissionsError: the caller may not sign up by it.
    :raises AuthItemNotFoundError, AuthItemInvalidError: a value is not one
        of an attribute of the client, or not of its type.
    :raises AuthMethodInvalidError: it breaks a policy of the method.
    :raises AuthMethodRefusedError: the method refuses what it starts with.
    :raises AuthIdentityConflictError: the subject is bound already.
    """

    @t.override
    async def _run(
        self, parameters: AuthStartSignUpParameters, metadata: OperationMetadata
    ) -> AuthSignUpResult:
        return await self.start(
            parameters.method,
            parameters.parameters,
            parameters.attr_values,
            parameters.transport_attr_values,
            metadata,
        )


class AuthAnswerSignUpOperation(BaseAuthSignUpOperation[AuthAnswerSignUpParameters]):
    """
    Answers the challenge of a sign-up. The attempt is taken by the answer: a
    refused one keeps it until the answers refused reach
    ``AUTH_ATTEMPT_MAX_FAILURES``, then it is over.

    :raises AuthAttemptNotFoundError: no sign-up waits under the id.
    :raises OperationPermissionsError: the caller may not sign up by the
        method of the attempt, closed meanwhile.
    :raises AuthMethodRefusedError: the method refuses the answer.
    :raises AuthIdentityConflictError: the subject is bound already.
    """

    @t.override
    async def _run(
        self, parameters: AuthAnswerSignUpParameters, metadata: OperationMetadata
    ) -> AuthSignUpResult:
        return await self.answer(parameters.attempt_id, parameters.answer, metadata)
