"""The base of the RPCs of the methods."""

__all__ = ("BaseAuthMethodRpcMixin",)

import typing as t

from ..base import AuthRpcMixin


class BaseAuthMethodRpcMixin(AuthRpcMixin):
    """
    The RPCs of a method, its starts open to anyone, as every flow is: they
    run for the anonymous caller of the project, whatever a call bears,
    given the flags of the flows by the group ``auth.grp_anonymous``.
    :attr:`METHOD` is the name of the slot of the method it serves: an
    application binding the method under another name subclasses it. A start
    gives the values of the attributes of the transport its context tells,
    kept as the registry of the attributes of the sessions has them, of the
    source ``transport``.
    """

    # the name of the method served: the path of its slot in the methods
    METHOD: t.ClassVar[str]
