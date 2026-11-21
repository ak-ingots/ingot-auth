"""
What the scenarios of the load of the game share, in perf/game:
the project of the scenarios with the configs of a run, ``PerfConfigs`` of
ingots joined to its own, and the players seeded ahead, each to one of the
two processes of the game in turn.
"""

import asyncio
import dataclasses
import typing as t

from ingots.perf import CsvSeed, PerfConfigs
from ingots.puer import Slot

from ingot_auth.methods.nickname.v1 import nickname_pb2

from scenarios.project import GameClient, ScenariosConfigs, ScenariosProject
from scenarios.project import ScenariosSettingsUnit
from scenarios.steps import PASSWORD, new_nickname

# how many players are signed up and in at once, the hashes of their passwords
SEED_CONCURRENCY = 16


class GamePerfConfigs(ScenariosConfigs, PerfConfigs):
    pass


class GamePerfSettingsUnit(ScenariosSettingsUnit):
    configs = Slot(GamePerfConfigs)


class GamePerfProject(ScenariosProject):
    """The project of a scenario of the load, which adds its unit ``perf``."""

    settings = Slot(GamePerfSettingsUnit)


@dataclasses.dataclass
class SeededPlayer:
    """A player signed up and in, of the process of the game it calls."""

    nickname: str
    token: str
    is_second: bool


async def get_client(project: GamePerfProject, is_second: bool) -> GameClient:
    """The client of the process of the game: the first or the second."""
    clients = project.grpc.clients
    return await (clients.second if is_second else clients.default)


class PlayersSeed(CsvSeed[SeededPlayer]):
    """Players signed up and in by a nickname, a process of the game in turn."""

    project: GamePerfProject

    @t.override
    async def _make(self, groups: int) -> list[SeededPlayer]:
        semaphore = asyncio.Semaphore(SEED_CONCURRENCY)

        async def create(index: int) -> SeededPlayer:
            is_second = index % 2 == 1
            nickname = new_nickname()
            client = await get_client(self.project, is_second)
            async with semaphore:
                await client.auth_methods_nickname.SignUp(
                    nickname_pb2.SignUpRequest(nickname=nickname, password=PASSWORD)
                )
                response = await client.auth_methods_nickname.SignIn(
                    nickname_pb2.SignInRequest(nickname=nickname, password=PASSWORD)
                )
            return SeededPlayer(nickname, response.result.signed_in.token, is_second)

        return list(await asyncio.gather(*(create(i) for i in range(groups))))
