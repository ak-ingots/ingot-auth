"""The settings of the application: the configs of the addons and its own."""

__all__ = ("AppConfigs", "AppSettingsUnit")

from ingot_grpcio.settings import GrpcSettingsUnit
from ingot_grpcio.settings.configs import GrpcConfigs
from ingot_pymongo.settings import MongoDbSettingsUnit
from ingot_pymongo.settings.configs import MongoDbConfigs
from ingot_redis.settings import RedisSettingsUnit
from ingot_redis.settings.configs import RedisConfigs
from ingots.puer import Slot

from ingot_auth.methods.email_code import AuthEmailCodeConfigs
from ingot_auth.methods.nickname import AuthNicknameConfigs
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.settings.configs import AuthConfigs


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
