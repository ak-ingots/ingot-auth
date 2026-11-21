"""
The project of the site: the auth over HTTP, on MongoDB, Redis and SMTP;
``extensions``, what it extends of the framework and of the addons,
collected here.
"""

__all__ = ("AppProject",)

from ingot_pymongo import MongoDbProject
from ingot_redis import RedisProject
from ingot_starlette import StarletteProject
from ingots.puer import Slot

from ingot_auth import AuthProject

from extensions.auth import AppAuthUnit
from extensions.logging import AppLoggingUnit
from extensions.mail import AppMailUnit
from extensions.settings import AppSettingsUnit
from extensions.starlette import AppStarletteUnit


class AppProject(AuthProject, StarletteProject, MongoDbProject, RedisProject):
    env_configs_prefix = "APP"
    settings = Slot(AppSettingsUnit)
    logging = Slot(AppLoggingUnit)
    mail = Slot(AppMailUnit)
    starlette = Slot(AppStarletteUnit)
    auth = Slot(AppAuthUnit)
