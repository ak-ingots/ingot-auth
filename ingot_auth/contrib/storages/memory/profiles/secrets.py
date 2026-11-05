"""The secrets in memory."""

__all__ = ("AuthMemorySecretsStorage",)

import typing as t

from ingot_auth.profiles.secrets import AuthSecretNotFoundError, BaseAuthSecretsStorage

from ..state import AuthMemoryStateMixin

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemorySecretsStorage(AuthMemoryStateMixin, BaseAuthSecretsStorage):
    """The secrets in memory, by the method and the subject."""

    def __init__(self, project: "Project") -> None:
        super().__init__(project)
        self._secrets: dict[tuple[str, str], str] = {}

    @t.override
    async def _put(self, method: str, subject: str, secret: str) -> None:
        self._secrets[method, subject] = secret

    @t.override
    async def _get(self, method: str, subject: str) -> str:
        try:
            return self._secrets[method, subject]
        except KeyError:
            raise AuthSecretNotFoundError.for_method(method) from None
