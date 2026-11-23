"""
What a step of a flow asks for, as a message: that of
:mod:`~ingot_auth.api`.
Temporary: its names suffixed ``Temp``, its services bound as ``*_temp``
beside the old ones, till the old API is removed.
"""

__all__ = ("build_challenge",)

from ingot_auth.api.challenges import build_challenge
