"""
What a step of a flow asks for, as a message: that of
:mod:`~ingot_auth.contrib.transports.contract`.
"""

__all__ = ("build_challenge",)

from ..contract.challenges import build_challenge
