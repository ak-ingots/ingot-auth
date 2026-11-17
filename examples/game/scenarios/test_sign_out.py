import grpc
from ingots.testing import ProjectTestCase

from .steps import GameMixin, new_nickname


class SignOutScenario(GameMixin, ProjectTestCase):
    async def test_a_player_signs_out_and_its_token_is_refused(self) -> None:
        nickname = new_nickname()
        await self.sign_up_by_nickname(nickname, "s3cret-password")
        token = await self.sign_in_by_nickname(nickname, "s3cret-password")
        await self.get_own_profile(token)
        await self.sign_out_of(token)
        await self.assert_refused(
            self.get_own_profile(token),
            grpc.StatusCode.UNAUTHENTICATED,
            "SESSION_NOT_FOUND",
        )
