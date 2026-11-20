"""
The hashers of passwords, the strategies of the slots ``hasher_*`` of
``AuthPassword``: :class:`BaseAuthPasswordHasher`, what a hasher of an
algorithm implements.
"""

__all__ = ("BaseAuthPasswordHasher",)

import abc
import typing as t

from ingots.puer import Entity


class BaseAuthPasswordHasher(Entity):
    """
    A hasher of one algorithm, :attr:`NAME`, its hashes strings of the PHC
    format, ``$<NAME>$<parameters>$<salt>$<hash>``, so that a hash holds
    its algorithm and its cost: :meth:`hash` makes one by the cost of its
    class, :meth:`verify` verifies one of its algorithm at whatever cost
    it holds, :meth:`needs_rehash` tells one it would not make.
    """

    NAME: t.ClassVar[str]

    @abc.abstractmethod
    def hash(self, password: str) -> str:
        """The hash of a password with a new salt; run in a thread."""
        raise NotImplementedError

    @abc.abstractmethod
    def verify(self, password: str, secret: str) -> bool:
        """
        Whether a password is that of a hash of :attr:`NAME`; ``False`` for
        what is no such hash. Run in a thread.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def needs_rehash(self, secret: str) -> bool:
        """Whether a hash is of another algorithm or cost than :meth:`hash` makes."""
        raise NotImplementedError
