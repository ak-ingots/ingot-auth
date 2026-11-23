"""
A password leaked, refused: the range of Pwned Passwords, by k-anonymity, its
SHA-1 told by its first five characters alone, the rest compared here.
"""

__all__ = ("AuthPwnedConfig", "AuthPwnedPolicy")

import asyncio
import hashlib
import logging
import typing as t
import urllib.request
from dataclasses import dataclass

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from ingot_auth.policies import AuthHasValue, AuthPolicyViolationError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthPwnedConfig:
    """
    The service and what to do without it: ``is_fail_open``, a password let
    through when the service does not answer, as OWASP has it, a warning
    logged; else refused by the policy ``pwned_unchecked``. ``min_count``,
    the leaks a password is refused at.
    """

    url: str = "https://api.pwnedpasswords.com/range/"
    timeout: float = 2.0
    is_fail_open: bool = True
    min_count: int = 1
    user_agent: str = "ingot-auth"


class AuthPwnedPolicy(BaseOperation[AuthHasValue, None]):
    """
    A value not among the leaked passwords, by the service of :attr:`CONFIG`,
    which a subclass replaces; the policy ``pwned``. A call over the network:
    an application takes it into ``policies_set`` of its password itself.
    """

    CONFIG: t.ClassVar[AuthPwnedConfig] = AuthPwnedConfig()

    # a check of a value the flow running it has given, nothing to require
    @t.override
    def _get_permissions(self) -> Permissions:
        return Permissions()

    @t.override
    async def _run(self, parameters: AuthHasValue, metadata: OperationMetadata) -> None:
        sha1 = hashlib.sha1(parameters.value.encode(), usedforsecurity=False)
        digest = sha1.hexdigest().upper()
        prefix, suffix = digest[:5], digest[5:]
        try:
            body = await self._fetch_range(prefix)
        except OSError as error:
            if not self.CONFIG.is_fail_open:
                raise AuthPolicyViolationError.for_policy("pwned_unchecked") from error
            logger.warning(
                "%r: the service did not answer, let through: %r", self, error
            )
            return
        for line in body.splitlines():
            found, _, count = line.strip().partition(":")
            if found == suffix and int(count) >= self.CONFIG.min_count:
                raise AuthPolicyViolationError.for_policy("pwned")

    async def _fetch_range(self, prefix: str) -> str:
        """
        The range of the prefix, ``SUFFIX:COUNT`` a line, padded by lines of
        none; an error of the network an :class:`OSError`.
        """
        config = self.CONFIG
        request = urllib.request.Request(
            config.url + prefix,
            headers={"Add-Padding": "true", "User-Agent": config.user_agent},
        )

        def fetch() -> str:
            with urllib.request.urlopen(request, timeout=config.timeout) as response:
                return t.cast(bytes, response.read()).decode()

        return await asyncio.to_thread(fetch)
