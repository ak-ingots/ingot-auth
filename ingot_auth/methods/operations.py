"""The base of the operations of the flows the methods run in."""

__all__ = ("BaseAuthFlowOperation",)

import abc
import dataclasses
import datetime
import secrets
import typing as t

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from ingot_auth.caches import AuthAttempt, AuthAttemptNotFoundError
from ingot_auth.sessions.attrs import check_client_attr_values

from .base import BaseAuthMethod
from .errors import AuthMethodRefusedError
from .steps import AuthChallenge, AuthStep, AuthVerified

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.project import AuthProject
    from ingot_auth.storages import AuthAttrValue


class BaseAuthFlowOperation[ParametersType, ResultType](
    BaseOperation[ParametersType, ResultType]
):
    """
    A step of a flow, a sign-up, a sign-in, by any method: :meth:`start`
    runs the start of the method, :meth:`answer` an answer to its challenge,
    and :meth:`proceed` goes on from the step the method gives, a challenge
    keeping an attempt of the flow, :attr:`FLOW`, for the answer, the subject
    verified ending the flow by :meth:`_complete`.

    The runner checks the caller may run the flow, the step that it may by
    the method, as the runner cannot: one operation serves every method. A
    flow tells what of a method it needs and runs, its hooks.
    """

    # the flow of the attempts this one keeps and takes: sign_up, sign_in
    FLOW: t.ClassVar[str]

    project: "AuthProject"

    @t.final
    async def get_method(
        self, name: str, metadata: OperationMetadata
    ) -> BaseAuthMethod[t.Any, t.Any, t.Any]:
        """
        The method of a name, which the caller may run the flow by: it has
        the flag of the flow of the method, which its toggle gives, checked
        by the checker of the operations as the runner checks any.

        :raises AuthMethodNotFoundError: no method has the name.
        :raises AuthMethodUnsupportedError: the method takes no such flow.
        :raises OperationPermissionsError: the caller may not run it by it.
        """
        method = self.project.auth.methods.get(name)
        await self.project.operations.checker.check(
            type(self), self._get_method_permissions(method), metadata
        )
        return method

    @t.final
    async def start(
        self,
        name: str,
        parameters: object,
        attr_values: "Mapping[int, AuthAttrValue]",
        metadata: OperationMetadata,
    ) -> ResultType:
        """
        Starts the flow by a method, with the values of the attributes of the
        session the client gives.

        :raises AuthMethodNotFoundError: no method has the name.
        :raises AuthMethodUnsupportedError: the method takes no such flow.
        :raises OperationPermissionsError: the caller may not run it by it.
        :raises AuthItemNotFoundError, AuthItemInvalidError: a value is not one
            of an attribute of the client, or not of its type.
        :raises AuthMethodInvalidError: it breaks policies of the method.
        :raises AuthMethodRefusedError: the method refuses what it starts with.
        """
        method = await self.get_method(name, metadata)
        attrs = await self.project.auth.storage.sessions.attrs.get_all()
        check_client_attr_values(attrs, attr_values)
        step = await self._start_method(method, parameters, metadata)
        return await self.proceed(method, step, attr_values)

    @t.final
    async def answer(
        self, attempt_id: str, answer: object, metadata: OperationMetadata
    ) -> ResultType:
        """
        Answers the challenge of an attempt of the flow. The attempt is taken
        by the answer: a refused one keeps it until the answers refused reach
        ``AUTH_ATTEMPT_MAX_FAILURES``, then it is over.

        :raises AuthAttemptNotFoundError: no attempt of the flow has the id.
        :raises OperationPermissionsError: the caller may not run the flow by
            the method of the attempt, closed meanwhile.
        :raises AuthMethodRefusedError: the method refuses the answer.
        """
        attempts = self.project.auth.cache.attempts
        attempt = await attempts.take(attempt_id)
        if attempt.flow != self.FLOW:
            raise AuthAttemptNotFoundError.create()
        method = await self.get_method(attempt.method, metadata)
        try:
            step = await method.answer(attempt.state, answer)
        except AuthMethodRefusedError:
            failures = attempt.failures + 1
            configs = self.project.settings.configs
            if failures < configs.AUTH_ATTEMPT_MAX_FAILURES:
                await attempts.put(dataclasses.replace(attempt, failures=failures))
            raise
        return await self.proceed(method, step, attempt.attr_values, attempt.failures)

    @t.final
    async def proceed(
        self,
        method: BaseAuthMethod[t.Any, t.Any, t.Any],
        step: AuthStep,
        attr_values: "Mapping[int, AuthAttrValue]",
        failures: int = 0,
    ) -> ResultType:
        """Goes on after a step of the method: to its challenge, or to the end."""
        if isinstance(step, AuthChallenge):
            attempt = AuthAttempt(
                id=secrets.token_urlsafe(32),
                flow=self.FLOW,
                method=method.get_name(),
                state=step.state,
                attr_values=attr_values,
                expires_at=self._get_now() + self._get_attempt_ttl(),
                failures=failures,
            )
            await self.project.auth.cache.attempts.put(attempt)
            return self._create_challenge(attempt.id, step.challenge)
        return await self._complete(method, step, attr_values)

    @abc.abstractmethod
    def _get_method_permissions(
        self, method: BaseAuthMethod[t.Any, t.Any, t.Any]
    ) -> Permissions:
        """
        What the caller needs to run the flow by a method, its flag of it.

        :raises AuthMethodUnsupportedError: the method takes no such flow.
        """
        raise NotImplementedError(f"{type(self).__qualname__}._get_method_permissions")

    @abc.abstractmethod
    async def _start_method(
        self,
        method: BaseAuthMethod[t.Any, t.Any, t.Any],
        parameters: object,
        metadata: OperationMetadata,
    ) -> AuthStep:
        """The start of the flow of a method, on what the client starts with."""
        raise NotImplementedError(f"{type(self).__qualname__}._start_method")

    @abc.abstractmethod
    def _create_challenge(self, attempt_id: str, challenge: object) -> ResultType:
        """The result of a challenge of the method, kept by an attempt."""
        raise NotImplementedError(f"{type(self).__qualname__}._create_challenge")

    @abc.abstractmethod
    async def _complete(
        self,
        method: BaseAuthMethod[t.Any, t.Any, t.Any],
        verified: AuthVerified,
        attr_values: "Mapping[int, AuthAttrValue]",
    ) -> ResultType:
        """Ends the flow on the subject a method verified."""
        raise NotImplementedError(f"{type(self).__qualname__}._complete")

    def _get_now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)

    def _get_attempt_ttl(self) -> datetime.timedelta:
        configs = self.project.settings.configs
        return datetime.timedelta(seconds=configs.AUTH_ATTEMPT_TTL)
