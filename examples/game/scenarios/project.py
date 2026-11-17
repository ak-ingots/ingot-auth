"""The project of the scenarios: a client of the game, its tests the scenarios."""

from ingot_grpcio import GrpcProject
from ingot_grpcio.grpc import GrpcUnit
from ingot_grpcio.grpc.clients import DefaultGrpcClient, GrpcClientsUnit
from ingot_grpcio.settings import GrpcSettingsUnit
from ingot_grpcio.settings.configs import GrpcConfigs
from ingots.defaults.settings.configs import IntConfig
from ingots.puer import Slot
from ingots.testing import TestingProject

from ingot_auth.contrib.transports.grpcio import (
    AuthGrpcEmailCodeBinding,
    AuthGrpcFlowsBinding,
    AuthGrpcMetadataBinding,
    AuthGrpcNicknameBinding,
    AuthGrpcProfilesBinding,
    AuthGrpcSessionsBinding,
)


class ScenariosConfigs(GrpcConfigs):
    # the port of the API of Mailpit, the mailbox of every player
    MAILPIT_PORT = IntConfig(18025)


class ScenariosSettingsUnit(GrpcSettingsUnit):
    configs = Slot(ScenariosConfigs)


class GameClient(
    AuthGrpcMetadataBinding,
    AuthGrpcNicknameBinding,
    AuthGrpcEmailCodeBinding,
    AuthGrpcFlowsBinding,
    AuthGrpcProfilesBinding,
    AuthGrpcSessionsBinding,
    DefaultGrpcClient,
):
    """The client of the game, of the services a player calls."""


class ScenariosClientsUnit(GrpcClientsUnit):
    default = Slot(GameClient)


class ScenariosGrpcUnit(GrpcUnit):
    clients = Slot(ScenariosClientsUnit)


class ScenariosProject(TestingProject, GrpcProject):
    env_configs_prefix = "GAME_TEST"
    settings = Slot(ScenariosSettingsUnit)
    grpc = Slot(ScenariosGrpcUnit)
