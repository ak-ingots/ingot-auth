"""The errors of the methods."""

__all__ = (
    "AuthMethodError",
    "AuthMethodInvalidError",
    "AuthMethodNotFoundError",
    "AuthMethodRefusedError",
    "AuthMethodUnsupportedError",
)

import typing as t


class AuthMethodError(Exception):
    """
    An error of a method. ``args`` are the message and what it is about, so
    the error survives pickling; create it with the class methods of its
    subclasses. Nothing a client gave is in it.
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


class AuthMethodInvalidError(AuthMethodError):
    """
    What a client starts a sign-up with breaks a policy of the method, a
    password too short, say: the field and the binding of the policy broken
    are named, the value is not.
    """

    @classmethod
    def for_field(cls, field: str, binding: str) -> t.Self:
        return cls(f"the {field} breaks the policy of {binding!r}", field, binding)

    @property
    def field(self) -> str:
        return t.cast(str, self.args[1])

    @property
    def binding(self) -> str:
        return t.cast(str, self.args[2])


class AuthMethodUnsupportedError(AuthMethodError):
    """The method takes no part in the flow: a password signs no one out."""

    @classmethod
    def for_flow(cls, flow: str) -> t.Self:
        return cls(f"the method takes no {flow}", flow)

    @property
    def flow(self) -> str:
        return t.cast(str, self.args[1])
