"""The logging of the application: the loggers of the addons and its own."""

__all__ = ("AppLoggingUnit",)

import typing as t

from ingot_pymongo.logging import MongoDbLoggingUnit
from ingot_redis.logging import RedisLoggingUnit
from ingot_starlette.logging import StarletteLoggingUnit

from ingot_auth.logging import AuthLoggingUnit

if t.TYPE_CHECKING:
    from project import AppProject


class AppLoggingUnit(
    AuthLoggingUnit, StarletteLoggingUnit, MongoDbLoggingUnit, RedisLoggingUnit
):
    project: "AppProject"
