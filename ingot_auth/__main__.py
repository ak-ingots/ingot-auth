"""
Runs the addon on its own: ``python -m ingot_auth logging info``. The
storage, the cache, the dispatcher and the mailer are in memory, so what
a command stores is gone with it, and no mail goes out.
"""

import sys

from ingots.defaults.logging import configure_startup_logging
from ingots.puer import Slot
from ingots.puer.cli import CommandRunner

from .auth import AuthUnit
from .contrib.caches.memory import AuthMemoryCache
from .contrib.dispatchers.memory import AuthMemoryDispatcher
from .contrib.mailers.memory import AuthMemoryMailer
from .contrib.storages.memory import AuthMemoryStorage
from .project import AuthProject
from .sessions import AuthFixedLifetime, AuthSessionsUnit
from .sign_in import AuthNoTiming, AuthSignInUnit


class AuthMemorySessionsUnit(AuthSessionsUnit):
    lifetime = Slot(AuthFixedLifetime)


class AuthMemorySignInUnit(AuthSignInUnit):
    timing = Slot(AuthNoTiming)


class AuthMemoryUnit(AuthUnit):
    storage = Slot(AuthMemoryStorage)
    cache = Slot(AuthMemoryCache)
    dispatcher = Slot(AuthMemoryDispatcher)
    mailer = Slot(AuthMemoryMailer)
    sessions = Slot(AuthMemorySessionsUnit)
    sign_in = Slot(AuthMemorySignInUnit)


class AuthMemoryProject(AuthProject):
    auth = Slot(AuthMemoryUnit)


def main() -> None:
    configure_startup_logging()
    sys.exit(CommandRunner(AuthMemoryProject).run())


if __name__ == "__main__":
    main()
