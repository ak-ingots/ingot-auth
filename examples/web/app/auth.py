"""
The auth of the site: the sign-up and the sign-in by the code of an email
alone, the sessions sliding a month, the oldest evicted over the limit, the
replies of a sign-in held to a floor, the activity log strict; MongoDB,
Redis and SMTP. What a starter of the web will give (auth.1.3).
"""

from ingot_mail.contrib.aiosmtplib import AiosmtplibMailer
from ingot_mail.mail import MailUnit
from ingots.puer import Slot

from ingot_auth.activities import AuthActivitiesUnit, AuthStrictActivityFailure
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.caches.redis import AuthRedisCache
from ingot_auth.contrib.dispatchers.memory import AuthMemoryDispatcher
from ingot_auth.contrib.storages.mongodb import AuthMongoDbStorage
from ingot_auth.methods import AuthMethodsUnit
from ingot_auth.methods.email_code import AuthEmailCodeMethod
from ingot_auth.sessions import (
    AuthEvictOldestLimit,
    AuthNoSessionAttrsDeriver,
    AuthSessionsUnit,
    AuthSlidingFixedLifetime,
)
from ingot_auth.sign_in import AuthFloorTiming, AuthSignInUnit


class AppMailUnit(MailUnit):
    mailer = Slot(AiosmtplibMailer)


class AppMethodsUnit(AuthMethodsUnit):
    email_code = Slot(AuthEmailCodeMethod)


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
