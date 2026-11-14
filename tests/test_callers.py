import unittest


from ingot_auth.__main__ import AuthMemoryProject
from ingot_auth.metadata import AuthMetadataPermissions
from ingot_auth.methods.email_code import AuthEmailCodePermissions
from ingot_auth.methods.nickname import AuthNicknamePermissions
from ingot_auth.operations import AuthCallersProvider
from ingot_auth.sign_in import AuthSignInPermissions
from ingot_auth.sign_up import AuthSignUpPermissions

from tests import masks

from .test_metadata import TstProject


class AnonymousCallerTestCase(unittest.TestCase):
    def test_the_callers_are_those_of_the_auth(self) -> None:
        project = AuthMemoryProject()
        self.assertIsInstance(project.operations.callers, AuthCallersProvider)

    def test_anyone_may_what_the_units_of_the_auth_give(self) -> None:
        # the sign-up by nickname closed by its toggle
        project = TstProject()
        anonymous = project.operations.callers.get_anonymous()
        self.assertEqual(anonymous.uid, "anonymous")
        self.assertEqual(
            anonymous.permissions,
            masks(
                AuthSignUpPermissions.CAN_SIGN_UP,
                AuthSignInPermissions.CAN_SIGN_IN,
                AuthNicknamePermissions.CAN_SIGN_IN,
                AuthEmailCodePermissions.CAN_SIGN_UP
                | AuthEmailCodePermissions.CAN_SIGN_IN,
                AuthMetadataPermissions.CAN_READ,
            ),
        )

    def test_the_toggles_reach_the_anonymous_caller(self) -> None:
        project = TstProject()
        project.settings.configs.apply({"AUTH_SIGN_UP_ENABLED": False})
        self.assertEqual(
            project.operations.callers.get_anonymous().permissions,
            masks(
                AuthSignInPermissions.CAN_SIGN_IN,
                AuthNicknamePermissions.CAN_SIGN_IN,
                AuthEmailCodePermissions.CAN_SIGN_IN,
                AuthMetadataPermissions.CAN_READ,
            ),
        )
