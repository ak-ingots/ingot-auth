import unittest


from ingot_auth.__main__ import AuthMemoryProject
from ingot_auth.metadata import (
    AuthMetadataUnit,
)
from ingot_auth.methods.email_code import (
    AuthEmailCodeMethod,
)
from ingot_auth.methods.nickname import (
    AuthNicknameMethod,
)
from ingot_auth.operations import AuthCallersProvider
from ingot_auth.sign_in import (
    AuthSignInUnit,
)
from ingot_auth.sign_up import (
    AuthSignUpUnit,
)

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
                AuthSignUpUnit.Flags.CAN_SIGN_UP,
                AuthSignInUnit.Flags.CAN_SIGN_IN,
                AuthNicknameMethod.Flags.CAN_SIGN_IN,
                AuthEmailCodeMethod.Flags.CAN_SIGN_UP
                | AuthEmailCodeMethod.Flags.CAN_SIGN_IN,
                AuthMetadataUnit.Flags.CAN_READ,
            ),
        )

    def test_the_toggles_reach_the_anonymous_caller(self) -> None:
        project = TstProject()
        project.settings.configs.apply({"AUTH_SIGN_UP_ENABLED": False})
        self.assertEqual(
            project.operations.callers.get_anonymous().permissions,
            masks(
                AuthSignInUnit.Flags.CAN_SIGN_IN,
                AuthNicknameMethod.Flags.CAN_SIGN_IN,
                AuthEmailCodeMethod.Flags.CAN_SIGN_IN,
                AuthMetadataUnit.Flags.CAN_READ,
            ),
        )
