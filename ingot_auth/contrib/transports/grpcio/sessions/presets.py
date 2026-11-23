"""The servicer of the presets of the sessions."""

__all__ = ("AuthGrpcSessionPresetsServicer",)

from .presets_temp import (
    AuthGrpcSessionPresetsServicerTemp,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcSessionPresetsServicer = AuthGrpcSessionPresetsServicerTemp
