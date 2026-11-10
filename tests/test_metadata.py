import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import ROOT_CALLER
from ingots.defaults.settings.configs import BoolConfig
from ingots.puer import Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.metadata import AuthMetadata, AuthMethodMetadata
from ingot_auth.methods import AuthMethodsUnit, BaseAuthMethod
from ingot_auth.methods.email_code import AuthEmailCodeConfigs, BaseAuthEmailCodeMethod
from ingot_auth.methods.nickname import AuthNicknameConfigs, AuthNicknameMethod
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.settings.configs import AuthConfigs


class EmailCodeMethod(BaseAuthEmailCodeMethod):
    @t.override
    async def _send_code(self, email: str, code: str) -> None:
        pass


class NoFlowMethod(BaseAuthMethod[str, str, None]):
    pass


class TstMethodsUnit(AuthMethodsUnit):
    nickname = Slot(AuthNicknameMethod)
    email_code = Slot(EmailCodeMethod)
    no_flow = Slot(NoFlowMethod)


class TstAuthUnit(AuthMemoryUnit):
    methods = Slot(TstMethodsUnit)


class TstConfigs(AuthNicknameConfigs, AuthEmailCodeConfigs, AuthConfigs):
    AUTH_SIGN_UP_NICKNAME_ENABLED = BoolConfig(False)  # by invitation only


class TstSettingsUnit(AuthSettingsUnit):
    configs = Slot(TstConfigs)


class TstProject(AuthMemoryProject):
    settings = Slot(TstSettingsUnit)
    auth = Slot(TstAuthUnit)


class MetadataOfTheMethodsTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    def setUp(self) -> None:
        self.project = TstProject()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))

    async def get(self, project: AuthMemoryProject) -> AuthMetadata:
        operations = project.operations
        return await operations.runner.run(
            project.auth.metadata.op_get,
            None,
            operations.create_metadata(ROOT_CALLER),
        )

    async def test_the_methods_are_those_of_the_slots_with_their_flows(self) -> None:
        metadata = await self.get(self.project)
        self.assertEqual(
            metadata.methods,
            (
                AuthMethodMetadata(name="nickname", sign_up=False, sign_in=True),
                AuthMethodMetadata(name="email_code", sign_up=True, sign_in=True),
                AuthMethodMetadata(name="no_flow", sign_up=False, sign_in=False),
            ),
        )

    async def test_a_toggle_closes_a_flow_by_the_settings(self) -> None:
        self.project.settings.configs.apply({"AUTH_SIGN_IN_EMAIL_CODE_ENABLED": False})
        method = self.project.auth.methods.email_code
        self.assertTrue(method.get_sign_up_enabled())
        self.assertFalse(method.get_sign_in_enabled())

    async def test_no_method_no_methods(self) -> None:
        self.assertEqual((await self.get(AuthMemoryProject())).methods, ())
