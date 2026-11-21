"""The project of the site: the auth over HTTP, on MongoDB, Redis and SMTP."""

from ingot_pymongo import MongoDbProject
from ingot_pymongo.logging import MongoDbLoggingUnit
from ingot_pymongo.settings import MongoDbSettingsUnit
from ingot_pymongo.settings.configs import MongoDbConfigs
from ingot_redis import RedisProject
from ingot_redis.logging import RedisLoggingUnit
from ingot_redis.settings import RedisSettingsUnit
from ingot_redis.settings.configs import RedisConfigs
from ingot_starlette import StarletteProject
from ingot_starlette.logging import StarletteLoggingUnit
from ingot_starlette.settings import StarletteSettingsUnit
from ingot_starlette.settings.configs import StarletteConfigs
from ingots.defaults.settings.configs import IntConfig
from ingots.puer import Slot

from ingot_auth import AuthProject
from ingot_auth.logging import AuthLoggingUnit
from ingot_auth.methods.email_code import AuthEmailCodeConfigs
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.settings.configs import AuthConfigs

from .auth import AppAuthUnit, AppMailUnit
from .http import AppStarletteUnit


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


class AppLoggingUnit(
    AuthLoggingUnit, StarletteLoggingUnit, MongoDbLoggingUnit, RedisLoggingUnit
):
    project: "AppProject"


class AppProject(AuthProject, StarletteProject, MongoDbProject, RedisProject):
    env_configs_prefix = "APP"
    settings = Slot(AppSettingsUnit)
    logging = Slot(AppLoggingUnit)
    mail = Slot(AppMailUnit)
    starlette = Slot(AppStarletteUnit)
    auth = Slot(AppAuthUnit)
