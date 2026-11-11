"""The secrets in memory."""

__all__ = ("AuthMemorySecretsStorage",)

import typing as t

from ingot_auth.profiles.secrets import AuthSecretNotFoundError, BaseAuthSecretsStorage

from ..state import AuthMemoryStateMixin

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemorySecretsStorage(AuthMemoryStateMixin, BaseAuthSecretsStorage):
    """The secrets in memory, by the uids of their profiles."""

    def __init__(self, project: "Project") -> None:
        super().__init__(project)
        self._secrets: dict[str, str] = {}

    @t.override
    async def _put(self, uid: str, secret: str) -> None:
        self._secrets[uid] = secret

    @t.override
    async def _get(self, uid: str) -> str:
        try:
            return self._secrets[uid]
        except KeyError:
            raise AuthSecretNotFoundError.for_uid(uid) from None
