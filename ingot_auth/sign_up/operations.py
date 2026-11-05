"""The operations of the sign-up."""

__all__ = ("AuthAnswerSignUp", "AuthStartSignUp", "BaseAuthSignUpOperation")

import dataclasses
import datetime
import os
import secrets
import typing as t

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from ingot_auth.methods import (
    AuthAttempt,
    AuthAttemptNotFoundError,
    AuthChallenge,
    AuthMethodRefusedError,
    AuthStep,
    AuthVerified,
)
from ingot_auth.profiles.identities import AuthIdentity
from ingot_auth.profiles import AuthProfile
from ingot_auth.sessions.attrs import check_client_values

from .items import (
    AuthAnswerSignUpParameters,
    AuthSignedUp,
    AuthSignUpChallenge,
    AuthSignUpRecord,
    AuthSignUpResult,
    AuthStartSignUpParameters,
)
from .permissions import AuthSignUpPermissions

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.project import AuthProject
    from ingot_auth.registry import AuthAttrValue

FLOW: t.Final = "sign_up"


class BaseAuthSignUpOperation[ParametersType](
    BaseOperation[ParametersType, AuthSignUpResult]
):
    """
    A step of the sign-up: a challenge keeps an attempt for the answer, the
    verified subject ends the sign-up with a profile bound to it. The uid of
    a new profile comes from :meth:`_create_uid`, the time from
    :meth:`_get_now`.
    """

    PERMISSIONS = Permissions(AuthSignUpPermissions.CAN_SIGN_UP)

    project: "AuthProject"

    @t.final
    async def proceed(
        self,
        method: str,
        step: AuthStep,
        values: "Mapping[int, AuthAttrValue]",
        failures: int = 0,
    ) -> AuthSignUpResult:
        """Goes on after a step of the method: to its challenge, or to the end."""
        if isinstance(step, AuthChallenge):
            attempt = AuthAttempt(
                id=secrets.token_urlsafe(32),
                flow=FLOW,
                method=method,
                state=step.state,
                values=values,
                expires_at=self._get_now() + self._get_attempt_ttl(),
                failures=failures,
            )
            await self.project.auth.cache.attempts.put(attempt)
            return AuthSignUpChallenge(attempt_id=attempt.id, challenge=step.challenge)
        return await self.complete(method, step, values)

    @t.final
    async def complete(
        self,
        method: str,
        verified: AuthVerified,
        values: "Mapping[int, AuthAttrValue]",
    ) -> AuthSignedUp:
        """
        Ends the sign-up, in one transaction of the storage: binds the
        subject to a new profile, keeps its secret if the method gave one,
        creates the profile and keeps the record. The binding goes first, so
        of two sign-ups of one subject only one goes on.

        :raises AuthIdentityConflictError: the subject is bound already.
        """
        storage = self.project.auth.storage
        uid = self._create_uid()
        now = self._get_now()
        identity = AuthIdentity(method=method, subject=verified.subject, uid=uid)
        record = AuthSignUpRecord(
            uid=uid, method=method, signed_up_at=now, values=values
        )
        async with storage.transaction():
            await storage.profiles.identities.create(identity)
            if verified.secret is not None:
                await storage.profiles.secrets.put(
                    method, verified.subject, verified.secret
                )
            await storage.profiles.create(AuthProfile(uid=uid, created_at=now))
            await storage.sign_up.records.add(record)
        return AuthSignedUp(uid=uid)

    def _create_uid(self) -> str:
        """
        The uid of a new profile: random, telling nothing of the user; 128 bits,
        32 hexadecimal digits, as the uids of the runs of ingots.
        """
        return os.urandom(16).hex()

    def _get_now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)

    def _get_attempt_ttl(self) -> datetime.timedelta:
        configs = self.project.settings.configs
        return datetime.timedelta(seconds=configs.AUTH_ATTEMPT_TTL)


class AuthStartSignUp(BaseAuthSignUpOperation[AuthStartSignUpParameters]):
    """
    Starts a sign-up by a method, with the values of the attributes of the
    session the client gives.

    :raises AuthMethodNotFoundError: no method has the name.
    :raises AuthItemNotFoundError, AuthItemInvalidError: a value is not one
        of an attribute of the client, or not of its type.
    :raises AuthMethodUnsupportedError: the method signs no one up.
    :raises AuthMethodInvalidError: it breaks a policy of the method.
    :raises AuthMethodRefusedError: the method refuses what it starts with.
    :raises AuthIdentityConflictError: the subject is bound already.
    """

    @t.override
    async def _run(
        self, parameters: AuthStartSignUpParameters, metadata: OperationMetadata
    ) -> AuthSignUpResult:
        method = self.project.auth.methods.get(parameters.method)
        attrs = await self.project.auth.storage.sessions.attrs.get_all()
        check_client_values(attrs, parameters.values)
        step = await method.start_sign_up(parameters.parameters)
        return await self.proceed(parameters.method, step, parameters.values)


class AuthAnswerSignUp(BaseAuthSignUpOperation[AuthAnswerSignUpParameters]):
    """
    Answers the challenge of a sign-up. The attempt is taken by the answer: a
    refused one keeps it until the answers refused reach
    ``AUTH_ATTEMPT_MAX_FAILURES``, then it is over.

    :raises AuthAttemptNotFoundError: no sign-up waits under the id.
    :raises AuthMethodRefusedError: the method refuses the answer.
    :raises AuthIdentityConflictError: the subject is bound already.
    """

    @t.override
    async def _run(
        self, parameters: AuthAnswerSignUpParameters, metadata: OperationMetadata
    ) -> AuthSignUpResult:
        attempts = self.project.auth.cache.attempts
        attempt = await attempts.take(parameters.attempt_id)
        if attempt.flow != FLOW:
            raise AuthAttemptNotFoundError.create()
        method = self.project.auth.methods.get(attempt.method)
        try:
            step = await method.answer(attempt.state, parameters.answer)
        except AuthMethodRefusedError:
            failures = attempt.failures + 1
            configs = self.project.settings.configs
            if failures < configs.AUTH_ATTEMPT_MAX_FAILURES:
                await attempts.put(dataclasses.replace(attempt, failures=failures))
            raise
        return await self.proceed(
            attempt.method, step, attempt.values, attempt.failures
        )
