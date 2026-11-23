"""The servicer of the tags."""

__all__ = ("AuthGrpcTagsServicer",)

from .tags_temp import (
    AuthGrpcTagsServicerTemp,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcTagsServicer = AuthGrpcTagsServicerTemp
