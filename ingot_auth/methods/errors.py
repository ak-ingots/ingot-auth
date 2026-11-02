"""The errors of the methods and of their attempts."""

__all__ = (
    "AuthAttemptNotFoundError",
    "AuthMethodError",
    "AuthMethodNotFoundError",
    "AuthMethodRefusedError",
)

import typing as t


class AuthMethodError(Exception):
    """
    An error of a method or of an attempt. ``args`` are the message and what
    it is about, so the error survives pickling; create it with the class
    methods of its subclasses. Nothing a client gave is in it.
    """

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])


class AuthMethodNotFoundError(AuthMethodError):
    """No method has the name."""

    @classmethod
    def for_name(cls, name: str) -> t.Self:
        return cls(f"no method {name!r}", name)

    @property
    def name(self) -> str:
        return t.cast(str, self.args[1])


class AuthMethodRefusedError(AuthMethodError):
    """
    The method refuses what it is given: the same error whatever the reason,
    a wrong password or no such user, so that a client learns nothing more.
    """

    @classmethod
    def create(cls) -> t.Self:
        return cls("the method refuses")


class AuthAttemptNotFoundError(AuthMethodError):
    """No attempt has the id: there never was one, it expired or it is over."""

    @classmethod
    def create(cls) -> t.Self:
        return cls("no such attempt")
