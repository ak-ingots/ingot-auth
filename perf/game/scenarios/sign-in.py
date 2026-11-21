"""A sign-in by a nickname, of a player signed up ahead: a session opened."""

import typing as t

from ingots.perf import LoadClient, LoadGroup, PerfUnit
from ingots.puer import Slot
from load import GamePerfProject, PlayersSeed, SeededPlayer, get_client
from scenarios.steps import PASSWORD

from ingot_auth.methods.nickname.v1 import nickname_pb2


class SigningIn(LoadClient["PerfProject", "SigningInGroup"]):
    @t.override
    async def asyncSetUp(self) -> None:
        seeded = self.group.seeded
        game = await get_client(self.project, seeded.is_second)
        self.nickname = game.auth_methods_nickname
        self.request = nickname_pb2.SignInRequest(
            nickname=seeded.nickname, password=PASSWORD
        )

    @t.override
    async def run(self) -> None:
        async with self.measure("sign-in"):
            await self.nickname.SignIn(self.request)


class SigningInGroup(LoadGroup[SeededPlayer]):
    clients = (SigningIn,)


class SignInPerf(PerfUnit[SeededPlayer]):
    group = SigningInGroup
    seed = Slot(PlayersSeed)


class PerfProject(GamePerfProject):
    perf = Slot(SignInPerf)
