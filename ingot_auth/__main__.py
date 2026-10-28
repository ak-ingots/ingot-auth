"""
Runs the addon on its own: ``python -m ingot_auth logging info``. The
storage is in memory, so what a command stores is gone with it.
"""

import sys

from ingots.defaults.logging import configure_startup_logging
from ingots.puer.cli import CommandRunner

from .contrib.storages.memory import AuthMemoryProject


def main() -> None:
    configure_startup_logging()
    sys.exit(CommandRunner(AuthMemoryProject).run())


if __name__ == "__main__":
    main()
