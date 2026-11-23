"""
The values of the attributes, as messages: those of
:mod:`~ingot_auth.api`.
Temporary: its names suffixed ``Temp``, its services bound as ``*_temp``
beside the old ones, till the old API is removed.
"""

__all__ = ("build_attr_value", "build_attr_value_message", "build_attr_values")

from ingot_auth.api.attrs.values import (
    build_attr_value,
    build_attr_value_message,
    build_attr_values,
)
