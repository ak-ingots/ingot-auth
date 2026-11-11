"""The strategies of the timing of the replies of the sign-in."""

__all__ = ("AuthFloorTiming", "AuthNoTiming", "BaseAuthTiming")

import abc
import asyncio
import contextlib
import time
import typing as t

from ingots.puer import Entity

if t.TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from ingot_auth.project import AuthProject


class BaseAuthTiming(Entity):
    """
    How soon a step of the sign-in replies: the strategy in the slot
    ``timing`` of the sign-in, which has none by default. A reply comes no
    sooner than the floor of :meth:`_get_floor`, a refusal raised as late
    as a success, so that its time tells nothing of the branch it took, a
    bound identifier or a free one.
    """

    project: "AuthProject"

    @t.final
    @contextlib.asynccontextmanager
    async def hold(self) -> "AsyncIterator[None]":
        """
        Holds the end of a block until the floor, whether it returns or
        raises; a task cancelled is not held.
        """
        started = time.monotonic()
        try:
            yield
        except Exception:
            await self._wait(started)
            raise
        await self._wait(started)

    @abc.abstractmethod
    def _get_floor(self) -> float:
        """The seconds a reply comes no sooner than."""
        raise NotImplementedError(f"{type(self).__qualname__}._get_floor")

    @t.final
    async def _wait(self, started: float) -> None:
        rest = self._get_floor() - (time.monotonic() - started)
        if rest > 0:
            await asyncio.sleep(rest)


class AuthNoTiming(BaseAuthTiming):
    """No floor: a reply comes as soon as it is ready, for the tests among others."""

    @t.override
    def _get_floor(self) -> float:
        return 0


class AuthFloorTiming(BaseAuthTiming):
    """
    A floor of ``AUTH_SIGN_IN_MIN_DURATION`` seconds, over the slowest branch
    of a step: every reply waits for it. A floor, not the mean latency, as
    half the replies are slower than the mean and their branches tell again.
    """

    @t.override
    def _get_floor(self) -> float:
        return self.project.settings.configs.AUTH_SIGN_IN_MIN_DURATION
