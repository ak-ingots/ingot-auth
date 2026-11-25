import grpc
from ingots.testing import ProjectTestCase

from .steps import PASSWORD, GameMixin, new_nickname

NEW_PASSWORD = "an0ther-s3cret-password"


class PasswordScenario(GameMixin, ProjectTestCase):
    async def test_a_player_changes_its_password_on_its_laptop(self) -> None:
        nickname = new_nickname()
        await self.sign_up_by_nickname(nickname, PASSWORD)
        phone = await self.sign_in_by_nickname(nickname, PASSWORD)
        laptop = await self.sign_in_by_nickname(nickname, PASSWORD)
        await self.assert_refused(
            self.change_password(laptop, "not-my-password", NEW_PASSWORD),
            grpc.StatusCode.PERMISSION_DENIED,
            "PASSWORD_REFUSED",
        )
        self.assertEqual(await self.change_password(laptop, PASSWORD, NEW_PASSWORD), 1)
        # the phone signed out, the laptop kept; the old password works no more
        await self.assert_refused(
            self.get_own_profile(phone),
            grpc.StatusCode.UNAUTHENTICATED,
            "SESSION_NOT_FOUND",
        )
        await self.get_own_profile(laptop)
        await self.assert_refused(
            self.sign_in_by_nickname(nickname, PASSWORD),
            grpc.StatusCode.UNAUTHENTICATED,
            "METHOD_REFUSED",
        )
        await self.sign_in_by_nickname(nickname, NEW_PASSWORD)

    async def test_a_new_password_too_short_is_refused(self) -> None:
        [token] = await self.sign_up_and_in()
        error = await self.assert_refused(
            self.change_password(token, PASSWORD, "short-password"),
            grpc.StatusCode.INVALID_ARGUMENT,
            "METHOD_INVALID",
        )
        self.assertEqual(error.metadata, {"field": "password", "policies": "length"})
