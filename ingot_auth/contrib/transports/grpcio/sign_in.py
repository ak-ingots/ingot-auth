"""The sign-in over gRPC: the results of its steps."""

__all__ = ("build_sign_in_result",)

from ingot_auth.sign_in import AuthSignedIn, AuthSignInResult

from ingot_auth.sign_in.v1 import sign_in_pb2


def build_sign_in_result(result: AuthSignInResult) -> sign_in_pb2.SignInResult:
    """Internal: the message of the result of a step of a sign-in."""
    if isinstance(result, AuthSignedIn):
        return sign_in_pb2.SignInResult(
            signed_in=sign_in_pb2.SignedIn(
                session_id=result.session_id, token=result.token
            )
        )
    # the challenge joins the contract with the first method of more steps
    raise NotImplementedError("a challenge of a sign-in")
