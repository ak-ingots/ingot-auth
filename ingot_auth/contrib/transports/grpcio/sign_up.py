"""The sign-up over gRPC: the results of its steps."""

__all__ = ("build_sign_up_result",)

from ingot_auth.sign_up import AuthSignedUp, AuthSignUpResult

from ingot_auth.sign_up.v1 import sign_up_pb2


def build_sign_up_result(result: AuthSignUpResult) -> sign_up_pb2.SignUpResult:
    """Internal: the message of the result of a step of a sign-up."""
    if isinstance(result, AuthSignedUp):
        return sign_up_pb2.SignUpResult(signed_up=sign_up_pb2.SignedUp(uid=result.uid))
    # the challenge joins the contract with the first method of more steps
    raise NotImplementedError("a challenge of a sign-up")
