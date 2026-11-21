from ingots.puer import Slot

from ingot_auth.activities import AuthActivitiesUnit, AuthStrictActivityFailure
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.caches.redis import AuthRedisCache
from ingot_auth.contrib.dispatchers.memory import AuthMemoryDispatcher
from ingot_auth.contrib.storages.mongodb import AuthMongoDbStorage
from ingot_auth.methods import AuthMethodsUnit
from ingot_auth.methods.email_code import AuthEmailCodeMethod
from ingot_auth.methods.nickname import AuthNicknameMethod
from ingot_auth.methods.password import AuthPassword, AuthScryptPasswordHasher
from ingot_auth.sessions import (
    AuthEvictOldestLimit,
    AuthNoSessionAttrsDeriver,
    AuthSessionsUnit,
    AuthSlidingFixedLifetime,
)
from ingot_auth.sign_in import AuthFloorTiming, AuthSignInUnit


class AppPasswordHasher(AuthScryptPasswordHasher):
    # of a like defence by OWASP, 16 MiB a hash and half the CPU of the
    # default on the servers of the game, as their load measured
    SCRYPT_LOG_N = 14
    SCRYPT_P = 5


class AppPassword(AuthPassword):
    hasher_default = Slot(AppPasswordHasher)


class AppMethodsUnit(AuthMethodsUnit):
    nickname = Slot(AuthNicknameMethod)
    email_code = Slot(AuthEmailCodeMethod)
    password = Slot(AppPassword)


class AppSessionsUnit(AuthSessionsUnit):
    lifetime = Slot(AuthSlidingFixedLifetime)
    deriver = Slot(AuthNoSessionAttrsDeriver)
    limit = Slot(AuthEvictOldestLimit)


class AppSignInUnit(AuthSignInUnit):
    timing = Slot(AuthFloorTiming)


class AppActivitiesUnit(AuthActivitiesUnit):
    failure = Slot(AuthStrictActivityFailure)


class AppAuthUnit(AuthUnit):
    storage = Slot(AuthMongoDbStorage)
    cache = Slot(AuthRedisCache)
    dispatcher = Slot(AuthMemoryDispatcher)
    methods = Slot(AppMethodsUnit)
    sessions = Slot(AppSessionsUnit)
    sign_in = Slot(AppSignInUnit)
    activities = Slot(AppActivitiesUnit)
