"""
The project of the game: the auth of its players over gRPC, on MongoDB,
Redis and SMTP; ``extensions``, what it extends of the framework and of
the addons, collected here.
"""

__all__ = ("AppProject",)

from ingot_grpcio import GrpcProject
from ingot_pymongo import MongoDbProject
from ingot_redis import RedisProject
from ingots.puer import Slot

from ingot_auth import AuthProject

from extensions.auth import AppAuthUnit
from extensions.grpcio import AppGrpcUnit
from extensions.logging import AppLoggingUnit
from extensions.mail import AppMailUnit
from extensions.settings import AppSettingsUnit


class AppProject(AuthProject, GrpcProject, MongoDbProject, RedisProject):
    env_configs_prefix = "APP"
    settings = Slot(AppSettingsUnit)
    logging = Slot(AppLoggingUnit)
    mail = Slot(AppMailUnit)
    grpc = Slot(AppGrpcUnit)
    auth = Slot(AppAuthUnit)
