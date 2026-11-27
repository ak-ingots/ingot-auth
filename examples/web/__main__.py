"""
The commands of the site, from its root: ``python . auth ...``, the
operator's; the site itself is served by ``uvicorn asgi:app``.
"""

import sys

from ingots.defaults.logging import configure_startup_logging
from ingots.defaults.cli import CommandRunner

from project import AppProject


def main() -> None:
    configure_startup_logging()
    sys.exit(CommandRunner(AppProject).run())


if __name__ == "__main__":
    main()
