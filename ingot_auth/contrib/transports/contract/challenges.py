"""
What a step of a flow asks for, as a message, by any method or factor,
shared by the flows.
"""

__all__ = ("build_challenge",)

from ingot_auth.methods import AuthCodeChallenge

from ingot_auth.methods.v1 import challenges_pb2


def build_challenge(attempt_uid: str, challenge: object) -> challenges_pb2.Challenge:
    """
    Internal: the message of what a step asks for, by the kind of its answer.

    :raises TypeError: the contract has no message for the challenge.
    """
    if isinstance(challenge, AuthCodeChallenge):
        code = challenges_pb2.CodeChallenge(length=challenge.length)
        return challenges_pb2.Challenge(attempt_uid=attempt_uid, code=code)
    raise TypeError(f"no message of a challenge {type(challenge).__qualname__}")
