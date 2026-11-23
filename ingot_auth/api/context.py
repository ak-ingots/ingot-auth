"""The context of a call, of no transport: what a transport tells of it."""

__all__ = ("BaseAuthRpcContext",)

import abc
import typing as t

if t.TYPE_CHECKING:
    from ingot_auth.storages import AuthAttrValue


class BaseAuthRpcContext(abc.ABC):
    """
    A call, as its transport tells it to the RPCs of the auth, of gRPC or of
    HTTP alike: its metadata, a header of HTTP or a key of gRPC, the values
    of the attributes of its transport, the IP, and where a reply tells the
    hash of the profile of the caller. A transport adapts its own context.
    """

    @abc.abstractmethod
    def get_metadata(self, key: str) -> str | None:
        """The value of a key of the metadata of the call, lowercase, or ``None``."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_transport_attr_values(self) -> "dict[str, AuthAttrValue]":
        """The values of the attributes of the transport of the call, by name."""
        raise NotImplementedError

    @abc.abstractmethod
    def set_profile_hash(self, profile_hash: str) -> None:
        """Tells the hash of the profile of the caller in the reply."""
        raise NotImplementedError
