"""The servicer of the method of a nickname and a password."""

__all__ = ("AuthGrpcNicknameServicer",)

from .nickname_temp import (
    AuthGrpcNicknameServicerTemp,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcNicknameServicer = AuthGrpcNicknameServicerTemp
