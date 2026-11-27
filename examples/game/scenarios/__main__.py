import sys

from ingots.defaults.logging import configure_startup_logging
from ingots.defaults.cli import CommandRunner

from .project import ScenariosProject

if __name__ == "__main__":
    configure_startup_logging()
    sys.exit(CommandRunner(ScenariosProject).run())
