"""
ingot-auth: the sign-up, the sign-in and the sessions of the users of Ingots
applications. An application inherits from :class:`AuthProject`, or joins
the units of the addon, ``settings``, ``logging`` and ``auth``, with those of
its other addons.
"""

__all__ = ("AuthProject",)

from .project import AuthProject
