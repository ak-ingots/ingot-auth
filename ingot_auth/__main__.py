"""
Runs the addon on its own: ``python -m ingot_auth logging info``. The
storage, the cache, the dispatcher and the mailer are in memory, so what
a command stores is gone with it, and no mail goes out.
"""

import sys

from ingot_mail.contrib.memory import MemoryMailer
from ingot_mail.mail import MailUnit
from ingots.defaults.logging import configure_startup_logging
from ingots.puer import Slot
from ingots.puer.cli import CommandRunner

from .activities import AuthActivitiesUnit, AuthStrictActivityFailure
from .auth import AuthUnit
from .contrib.caches.memory import AuthMemoryCache
from .contrib.dispatchers.memory import AuthMemoryDispatcher
from .contrib.storages.memory import AuthMemoryStorage
from .project import AuthProject
from .sessions import (
    AuthEvictOldestLimit,
    AuthFixedLifetime,
    AuthNoSessionAttrsDeriver,
    AuthSessionsUnit,
)
from .sign_in import AuthNoTiming, AuthSignInUnit


class AuthMemorySessionsUnit(AuthSessionsUnit):
    lifetime = Slot(AuthFixedLifetime)
    deriver = Slot(AuthNoSessionAttrsDeriver)
    limit = Slot(AuthEvictOldestLimit)


class AuthMemorySignInUnit(AuthSignInUnit):
    timing = Slot(AuthNoTiming)


class AuthMemoryActivitiesUnit(AuthActivitiesUnit):
    failure = Slot(AuthStrictActivityFailure)


class AuthMemoryMailUnit(MailUnit):
    mailer = Slot(MemoryMailer)


class AuthMemoryUnit(AuthUnit):
    storage = Slot(AuthMemoryStorage)
    cache = Slot(AuthMemoryCache)
    dispatcher = Slot(AuthMemoryDispatcher)
    sessions = Slot(AuthMemorySessionsUnit)
    sign_in = Slot(AuthMemorySignInUnit)
    activities = Slot(AuthMemoryActivitiesUnit)


class AuthMemoryProject(AuthProject):
    mail = Slot(AuthMemoryMailUnit)
    auth = Slot(AuthMemoryUnit)


def main() -> None:
    configure_startup_logging()
    sys.exit(CommandRunner(AuthMemoryProject).run())


if __name__ == "__main__":
    main()
