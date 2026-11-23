"""A sign-up by a new nickname: a profile and its password made."""

import dataclasses
import typing as t

from ingots.perf import CsvSeed, LoadClient, LoadGroup, PerfUnit
from ingots.puer import Slot
from load import GamePerfProject, get_client
from scenarios.steps import PASSWORD, new_nickname

from ingot_auth.api.methods.nickname.v1 import nickname_pb2


@dataclasses.dataclass
class Process:
    """The process of the game a group calls: no player is made ahead."""

    is_second: bool


class ProcessesSeed(CsvSeed[Process]):
    @t.override
    async def _make(self, groups: int) -> list[Process]:
        return [Process(index % 2 == 1) for index in range(groups)]


class SigningUp(LoadClient["PerfProject", "SigningUpGroup"]):
    @t.override
    async def asyncSetUp(self) -> None:
        game = await get_client(self.project, self.group.seeded.is_second)
        self.nickname = game.auth_methods_nickname

    @t.override
    async def run(self) -> None:
        request = nickname_pb2.SignUpRequest(nickname=new_nickname(), password=PASSWORD)
        async with self.measure("sign-up"):
            await self.nickname.SignUp(request)


class SigningUpGroup(LoadGroup[Process]):
    clients = (SigningUp,)


class SignUpPerf(PerfUnit[Process]):
    group = SigningUpGroup
    seed = Slot(ProcessesSeed)


class PerfProject(GamePerfProject):
    perf = Slot(SignUpPerf)
