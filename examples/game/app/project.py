from ingot_grpcio import GrpcProject
from ingot_grpcio.logging import GrpcLoggingUnit
from ingot_grpcio.settings import GrpcSettingsUnit
from ingot_grpcio.settings.configs import GrpcConfigs
from ingot_pymongo import MongoDbProject
from ingot_pymongo.logging import MongoDbLoggingUnit
from ingot_pymongo.settings import MongoDbSettingsUnit
from ingot_pymongo.settings.configs import MongoDbConfigs
from ingot_redis import RedisProject
from ingot_redis.logging import RedisLoggingUnit
from ingot_redis.settings import RedisSettingsUnit
from ingot_redis.settings.configs import RedisConfigs
from ingots.puer import Slot

from ingot_auth import AuthProject
from ingot_auth.logging import AuthLoggingUnit
from ingot_auth.methods.email_code import AuthEmailCodeConfigs
from ingot_auth.methods.nickname import AuthNicknameConfigs
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.settings.configs import AuthConfigs

from .auth import AppAuthUnit, AppMailUnit
from .grpc import AppGrpcUnit


class AppConfigs(
    AuthNicknameConfigs,
    AuthEmailCodeConfigs,
    AuthConfigs,
    GrpcConfigs,
    MongoDbConfigs,
    RedisConfigs,
):
    pass


class AppSettingsUnit(
    AuthSettingsUnit, GrpcSettingsUnit, MongoDbSettingsUnit, RedisSettingsUnit
):
    configs = Slot(AppConfigs)


class AppLoggingUnit(
    AuthLoggingUnit, GrpcLoggingUnit, MongoDbLoggingUnit, RedisLoggingUnit
):
    project: "AppProject"


class AppProject(AuthProject, GrpcProject, MongoDbProject, RedisProject):
    env_configs_prefix = "APP"
    settings = Slot(AppSettingsUnit)
    logging = Slot(AppLoggingUnit)
    mail = Slot(AppMailUnit)
    grpc = Slot(AppGrpcUnit)
    auth = Slot(AppAuthUnit)
