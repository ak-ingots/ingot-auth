"""A call with a token: a player signed in ahead calls its own profile."""

import typing as t

from ingots.perf import LoadClient, LoadGroup, PerfUnit
from ingots.puer import Slot
from load import GamePerfProject, PlayersSeed, SeededPlayer, get_client
from scenarios.steps import bear

from ingot_auth.api.profiles.v1 import profiles_pb2


class Player(LoadClient["PerfProject", "PlayerGroup"]):
    @t.override
    async def asyncSetUp(self) -> None:
        seeded = self.group.seeded
        game = await get_client(self.project, seeded.is_second)
        self.profiles = game.auth_profiles
        self.metadata = bear(seeded.token)

    @t.override
    async def run(self) -> None:
        async with self.measure("get-own-profile"):
            await self.profiles.GetOwnProfile(
                profiles_pb2.GetOwnProfileRequest(), metadata=self.metadata
            )


class PlayerGroup(LoadGroup[SeededPlayer]):
    clients = (Player,)


class OwnProfilePerf(PerfUnit[SeededPlayer]):
    group = PlayerGroup
    seed = Slot(PlayersSeed)


class PerfProject(GamePerfProject):
    perf = Slot(OwnProfilePerf)
