"""The project of the scenarios: a client of the site, its tests the scenarios."""

from ingots.defaults.settings import SettingsUnit
from ingots.defaults.settings.configs import Configs, IntConfig, StrConfig
from ingots.puer import Slot
from ingots.testing import TestingProject


class ScenariosConfigs(Configs):
    # the site, as compose publishes it
    SITE_HOST = StrConfig("127.0.0.1")
    SITE_PORT = IntConfig(8080)
    # the port of the API of Mailpit, the mailbox of every user
    MAILPIT_PORT = IntConfig(8081)


class ScenariosSettingsUnit(SettingsUnit):
    configs = Slot(ScenariosConfigs)


class ScenariosProject(TestingProject):
    env_configs_prefix = "WEB_TEST"
    settings = Slot(ScenariosSettingsUnit)
