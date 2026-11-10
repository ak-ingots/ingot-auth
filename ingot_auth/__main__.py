"""
Runs the addon on its own: ``python -m ingot_auth logging info``. The
storage and the cache are in memory, so what a command stores is gone with
it.
"""

import sys

from ingots.defaults.logging import configure_startup_logging
from ingots.puer import Slot
from ingots.puer.cli import CommandRunner

from .auth import AuthUnit
from .contrib.caches.memory import AuthMemoryCache
from .contrib.storages.memory import AuthMemoryStorage
from .project import AuthProject
from .sessions import AuthFixedLifetime, AuthSessionsUnit


class AuthMemorySessionsUnit(AuthSessionsUnit):
    lifetime = Slot(AuthFixedLifetime)


class AuthMemoryUnit(AuthUnit):
    storage = Slot(AuthMemoryStorage)
    cache = Slot(AuthMemoryCache)
    sessions = Slot(AuthMemorySessionsUnit)


class AuthMemoryProject(AuthProject):
    auth = Slot(AuthMemoryUnit)


def main() -> None:
    configure_startup_logging()
    sys.exit(CommandRunner(AuthMemoryProject).run())


if __name__ == "__main__":
    main()
