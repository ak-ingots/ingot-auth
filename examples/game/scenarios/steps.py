"""The steps of the scenarios, shared: functions and a mixin, called by name."""

import os
import typing as t
import unittest
import uuid

from grpc import aio

from ingot_auth.methods.nickname.v1 import nickname_pb2, nickname_pb2_grpc
from ingot_auth.profiles.v1 import profiles_pb2, profiles_pb2_grpc

PORT = os.environ.get("GAME_TEST_PORT")

skip_without_game = unittest.skipUnless(PORT, "no game: run make example-test")

Metadata: t.TypeAlias = list[tuple[str, str]]

if t.TYPE_CHECKING:
    TestCase: t.TypeAlias = unittest.IsolatedAsyncioTestCase
else:
    TestCase = object


def new_nickname() -> str:
    """A nickname no scenario took, the game kept running between them."""
    return f"player-{uuid.uuid4().hex[:12]}"


def bear(token: str) -> Metadata:
    return [("authorization", f"Bearer {token}")]


class GameMixin(TestCase):
    """The client of the game, its channel opened for each scenario."""

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        channel = aio.insecure_channel(f"127.0.0.1:{PORT}")
        self.addAsyncCleanup(channel.close)
        self.nickname = nickname_pb2_grpc.NicknameStub(channel)
        self.profiles = profiles_pb2_grpc.ProfilesStub(channel)

    async def sign_up_by_nickname(self, nickname: str, password: str) -> str:
        request = nickname_pb2.SignUpRequest(nickname=nickname, password=password)
        response = await self.nickname.SignUp(request)
        return response.result.signed_up.uid

    async def sign_in_by_nickname(self, nickname: str, password: str) -> str:
        request = nickname_pb2.SignInRequest(nickname=nickname, password=password)
        response = await self.nickname.SignIn(request)
        return response.result.signed_in.token

    async def get_own_profile(self, token: str) -> profiles_pb2.GetOwnProfileResponse:
        request = profiles_pb2.GetOwnProfileRequest()
        return await self.profiles.GetOwnProfile(request, metadata=bear(token))
