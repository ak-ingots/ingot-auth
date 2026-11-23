"""The results of the steps of the flows, as messages, by any method."""

__all__ = ("build_sign_in_result", "build_sign_up_result")

from ingot_auth.sign_in import AuthSignedIn, AuthSignInResult
from ingot_auth.sign_up import AuthSignedUp, AuthSignUpResult

from .challenges import build_challenge
from .sign_in.v1 import sign_in_pb2
from .sign_up.v1 import sign_up_pb2


def build_sign_in_result(result: AuthSignInResult) -> sign_in_pb2.SignInResult:
    """Internal: the message of the result of a step of a sign-in."""
    if isinstance(result, AuthSignedIn):
        return sign_in_pb2.SignInResult(
            signed_in=sign_in_pb2.SignedIn(
                session_uid=result.session_uid, token=result.token
            )
        )
    return sign_in_pb2.SignInResult(
        challenge=build_challenge(result.attempt_uid, result.challenge)
    )


def build_sign_up_result(result: AuthSignUpResult) -> sign_up_pb2.SignUpResult:
    """Internal: the message of the result of a step of a sign-up."""
    if isinstance(result, AuthSignedUp):
        return sign_up_pb2.SignUpResult(signed_up=sign_up_pb2.SignedUp(uid=result.uid))
    return sign_up_pb2.SignUpResult(
        challenge=build_challenge(result.attempt_uid, result.challenge)
    )
