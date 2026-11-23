"""The servicer of the method of an email and a code sent to it."""

__all__ = ("AuthGrpcEmailCodeServicer",)

from .email_code_temp import (
    AuthGrpcEmailCodeServicerTemp,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcEmailCodeServicer = AuthGrpcEmailCodeServicerTemp
