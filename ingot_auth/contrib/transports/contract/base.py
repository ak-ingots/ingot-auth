"""The base of the RPCs of the auth, of no transport."""

__all__ = (
    "PROFILE_HASH_KEY",
    "AuthRpcMixin",
    "AuthSessionRpcMixin",
    "parse_bearer_token",
)

import typing as t

if t.TYPE_CHECKING:
    from ingots.defaults.operations import BaseOperation, Caller
    from ingots.puer import BoundFactory

    from ingot_auth.project import AuthProject

    from .context import BaseAuthRpcContext

# the key telling the hash of the profile of the caller in a reply, one for
# every transport, a trailing key of gRPC, a header of HTTP: lowercase with
# hyphens, as gRPC takes no other key, and no X- (RFC 6648)
PROFILE_HASH_KEY: t.Final = "ingot-auth-user-profile-hash"


class AuthRpcMixin:
    """
    The RPCs of a service of the auth, of no transport, mixed into the
    servicer of gRPC and the endpoint of HTTP alike: an RPC turns its
    request, a message, into the parameters of an operation and the result
    into its reply, nothing else. The operation runs by
    :meth:`rpc_run_operation` for the caller of :meth:`_rpc_get_caller`, the
    anonymous one of the project here, whatever the call bears: what is open
    to anyone, the metadata, the flows.
    """

    project: "AuthProject"

    @t.final
    async def rpc_run_operation[ParametersType, ResultType](
        self,
        factory: "BoundFactory[BaseOperation[ParametersType, ResultType]]",
        parameters: ParametersType,
        context: "BaseAuthRpcContext",
    ) -> ResultType:
        """Runs an operation for the caller of a call."""
        operations = self.project.operations
        metadata = operations.create_metadata(await self._rpc_get_caller(context))
        return await operations.runner.run(factory, parameters, metadata)

    async def _rpc_get_caller(self, context: "BaseAuthRpcContext") -> "Caller":
        """The caller of a call: the anonymous one of the project, here."""
        return self.project.operations.callers.get_anonymous()


class AuthSessionRpcMixin(AuthRpcMixin):
    """
    The RPCs of a service of the signed-in callers: the caller of a call is
    that of the session of its token, ``Bearer <token>`` in the key
    ``authorization``, or with no token the anonymous one; every reply to one
    tells the hash of its profile, ``PROFILE_HASH_KEY``; a reply refused tells
    it not, the refusal itself telling the client to ask again.
    """

    @t.override
    async def _rpc_get_caller(self, context: "BaseAuthRpcContext") -> "Caller":
        """
        :raises AuthSessionNotFoundError: no open session has the token.
        :raises AuthSessionExpiredError: its session expired, closed now.
        """
        # the one way a call bears its credential for now, Bearer; it moves
        # into a strategy in a slot later (a cookie, mTLS, an API key...), for
        # an application to pick one or write its own, which until then
        # overrides this hook
        token = parse_bearer_token(context.get_metadata("authorization"))
        if token is None:
            return await super()._rpc_get_caller(context)
        caller = await self.project.auth.sessions.authenticate(token)
        context.set_profile_hash(caller.profile_hash)
        return caller


def parse_bearer_token(authorization: str | None) -> str | None:
    """
    The token of a value of ``authorization``, of the scheme ``Bearer`` in
    any case (RFC 6750), ``None`` without one: a value of another scheme
    tells no token either.
    """
    if authorization is None:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() == "bearer" and token.strip():
        return token.strip()
    return None
