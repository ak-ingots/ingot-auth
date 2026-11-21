"""
Runs the game, from its root: ``python . components run-forever
--component grpc.servers.default`` serves the players, ``python . auth ...``
is the operator's.
"""

import sys

from ingots.defaults.logging import configure_startup_logging
from ingots.puer.cli import CommandRunner

from project import AppProject


def main() -> None:
    configure_startup_logging()
    sys.exit(CommandRunner(AppProject).run())


if __name__ == "__main__":
    main()
