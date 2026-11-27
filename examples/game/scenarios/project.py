"""The project of the scenarios: a client of the game, its tests the scenarios."""

import typing as t

from ingot_grpcio import GrpcProject
from ingot_grpcio.grpc import GrpcCliUnit, GrpcUnit
from ingot_grpcio.grpc.clients import DefaultGrpcClient, GrpcClientsUnit
from ingot_grpcio.settings import GrpcSettingsUnit
from ingot_grpcio.settings.configs import GrpcConfigs
from ingots.defaults.settings.configs import IntConfig, StrConfig
from ingots.puer import Slot
from ingots.testing import TestingCliUnit, TestingProject

from ingot_auth.contrib.transports.grpcio import (
    AuthGrpcEmailCodeBinding,
    AuthGrpcFlowsBinding,
    AuthGrpcMetadataBinding,
    AuthGrpcNicknameBinding,
    AuthGrpcPasswordBinding,
    AuthGrpcProfilesBinding,
    AuthGrpcSessionsBinding,
)


class ScenariosConfigs(GrpcConfigs):
    # the port of the second process of the game, the first on GRPC_DEFAULT_*
    GAME_SECOND_PORT = IntConfig(50062)
    # the file of compose running the game, its service cli the operator's
    GAME_COMPOSE_FILE = StrConfig("docker-compose.yml")
    # the port of the API of Mailpit, the mailbox of every player
    MAILPIT_PORT = IntConfig(18025)


class ScenariosSettingsUnit(GrpcSettingsUnit):
    configs = Slot(ScenariosConfigs)


class GameClient(
    AuthGrpcMetadataBinding,
    AuthGrpcNicknameBinding,
    AuthGrpcPasswordBinding,
    AuthGrpcEmailCodeBinding,
    AuthGrpcFlowsBinding,
    AuthGrpcProfilesBinding,
    AuthGrpcSessionsBinding,
    DefaultGrpcClient,
):
    """The client of the game, of the services a player calls."""


class SecondGameClient(GameClient):
    """The client of the second process of the game, on ``GAME_SECOND_PORT``."""

    project: "ScenariosProject"

    @t.override
    def _get_target(self) -> str:
        configs = self.project.settings.configs
        return f"{configs.GRPC_DEFAULT_HOST}:{configs.GAME_SECOND_PORT}"


class ScenariosClientsUnit(GrpcClientsUnit):
    default = Slot(GameClient)
    second = Slot(SecondGameClient)


class ScenariosGrpcUnit(GrpcUnit):
    clients = Slot(ScenariosClientsUnit)


class ScenariosCliUnit(TestingCliUnit, GrpcCliUnit):
    pass


class ScenariosProject(TestingProject, GrpcProject):
    env_configs_prefix = "GAME_TEST"
    settings = Slot(ScenariosSettingsUnit)
    grpc = Slot(ScenariosGrpcUnit)
    cli = Slot(ScenariosCliUnit)
