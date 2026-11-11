"""The operations of the sign-in."""

__all__ = (
    "AuthAnswerSignInOperation",
    "AuthStartSignInOperation",
    "BaseAuthSignInOperation",
)

import typing as t

from ingots.defaults.operations import OperationMetadata, Permissions

from ingot_auth.methods import (
    AuthMethodDeniedError,
    AuthMethodRefusedError,
    AuthStep,
    AuthVerified,
    BaseAuthFlowOperation,
)
from ingot_auth.storages import AuthIdentityNotFoundError

from .items import (
    AuthAnswerSignInParameters,
    AuthSignedIn,
    AuthSignInChallenge,
    AuthSignInResult,
    AuthStartSignInParameters,
)
from .permissions import AuthSignInPermissions

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.methods import BaseAuthMethod
    from ingot_auth.storages import AuthAttrValue


class BaseAuthSignInOperation[ParametersType](
    BaseAuthFlowOperation[ParametersType, AuthSignInResult]
):
    """
    A step of the sign-in: a challenge keeps an attempt for the answer, the
    verified subject ends the sign-in with a session of its profile. A
    sign-in by a method needs its ``CAN_SIGN_IN``, of the caller first, of
    the profile once the method found it. A step replies no sooner than the
    strategy of the timing of the sign-in says, a refusal as late as a
    success.
    """

    FLOW: t.ClassVar[str] = "sign_in"
    PERMISSIONS = Permissions(AuthSignInPermissions.CAN_SIGN_IN)

    @t.override
    def _get_method_permissions(
        self, method: "BaseAuthMethod[t.Any, t.Any, t.Any]"
    ) -> Permissions:
        return method.get_sign_in_permissions()

    @t.override
    async def _start_method(
        self, method: "BaseAuthMethod[t.Any, t.Any, t.Any]", parameters: object
    ) -> AuthStep:
        return await method.start_sign_in(parameters)

    @t.override
    def _create_challenge(self, attempt_id: str, challenge: object) -> AuthSignInResult:
        return AuthSignInChallenge(attempt_id=attempt_id, challenge=challenge)

    @t.override
    async def _complete(
        self,
        method: "BaseAuthMethod[t.Any, t.Any, t.Any]",
        verified: AuthVerified,
        attr_values: "Mapping[int, AuthAttrValue]",
    ) -> AuthSignInResult:
        """
        Ends the sign-in: finds the profile of the subject, an identifier of
        the kind of the method, checks the profile may sign in by the method,
        by the permissions the access gives it, and opens a session.

        :raises AuthMethodRefusedError: the subject is bound to no profile,
            refused as a wrong secret is.
        :raises AuthMethodDeniedError: the profile may not sign in by the
            method.
        """
        auth = self.project.auth
        identities = auth.storage.profiles.identities
        try:
            uid = await identities.find_uid(method.IDENTIFIER_KIND, verified.subject)
        except AuthIdentityNotFoundError:
            raise AuthMethodRefusedError.create() from None
        permissions = await auth.access.permissions.get_permissions(uid)
        if not permissions.has(method.get_sign_in_permissions()):
            raise AuthMethodDeniedError.for_name(method.get_name())
        opened = await auth.sessions.open(uid, method.get_name(), attr_values)
        return AuthSignedIn(session_id=opened.session_id, token=opened.token)


class AuthStartSignInOperation(BaseAuthSignInOperation[AuthStartSignInParameters]):
    """
    Starts a sign-in by a method, with the values of the attributes of the
    session the client gives.

    :raises AuthMethodNotFoundError: no method has the name.
    :raises AuthMethodUnsupportedError: the method signs no one in.
    :raises OperationPermissionsError: the caller may not sign in by it.
    :raises AuthItemNotFoundError, AuthItemInvalidError: a value is not one
        of an attribute of the client, or not of its type.
    :raises AuthMethodRefusedError: the method refuses what it starts with,
        or what it verified is bound to no profile.
    :raises AuthMethodDeniedError: the profile may not sign in by the method.
    """

    @t.override
    async def _run(
        self, parameters: AuthStartSignInParameters, metadata: OperationMetadata
    ) -> AuthSignInResult:
        async with self.project.auth.sign_in.timing.hold():
            return await self.start(
                parameters.method,
                parameters.parameters,
                parameters.attr_values,
                metadata,
            )


class AuthAnswerSignInOperation(BaseAuthSignInOperation[AuthAnswerSignInParameters]):
    """
    Answers the challenge of a sign-in. The attempt is taken by the answer: a
    refused one keeps it until the answers refused reach
    ``AUTH_ATTEMPT_MAX_FAILURES``, then it is over.

    :raises AuthAttemptNotFoundError: no sign-in waits under the id.
    :raises OperationPermissionsError: the caller may not sign in by the
        method of the attempt, closed meanwhile.
    :raises AuthMethodRefusedError: the method refuses the answer, or what it
        verified is bound to no profile.
    :raises AuthMethodDeniedError: the profile may not sign in by the method.
    """

    @t.override
    async def _run(
        self, parameters: AuthAnswerSignInParameters, metadata: OperationMetadata
    ) -> AuthSignInResult:
        async with self.project.auth.sign_in.timing.hold():
            return await self.answer(parameters.attempt_id, parameters.answer, metadata)
