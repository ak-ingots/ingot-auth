"""The settings of the application: the configs of the addons and its own."""

__all__ = ("AppConfigs", "AppSettingsUnit")

from ingot_pymongo.settings import MongoDbSettingsUnit
from ingot_pymongo.settings.configs import MongoDbConfigs
from ingot_redis.settings import RedisSettingsUnit
from ingot_redis.settings.configs import RedisConfigs
from ingot_starlette.settings import StarletteSettingsUnit
from ingot_starlette.settings.configs import StarletteConfigs
from ingots.defaults.settings.configs import IntConfig
from ingots.puer import Slot

from ingot_auth.methods.email_code import AuthEmailCodeConfigs
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.settings.configs import AuthConfigs


class AppConfigs(
    AuthEmailCodeConfigs,
    AuthConfigs,
    StarletteConfigs,
    MongoDbConfigs,
    RedisConfigs,
):
    # a session slides a month while used, and lasts a quarter at most, the
    # absolute timeout of OWASP
    AUTH_SESSION_IDLE_TTL = IntConfig(30 * 86400)
    AUTH_SESSION_TTL = IntConfig(90 * 86400)


class AppSettingsUnit(
    AuthSettingsUnit, StarletteSettingsUnit, MongoDbSettingsUnit, RedisSettingsUnit
):
    configs = Slot(AppConfigs)
