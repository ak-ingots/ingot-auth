import grpc
from ingots.testing import ProjectTestCase

from .steps import GameMixin


class ProcessesScenario(GameMixin, ProjectTestCase):
    async def test_a_session_opened_on_one_process_is_known_to_the_other(
        self,
    ) -> None:
        (token,) = await self.sign_up_and_in()
        first = await self.get_own_profile(token)
        second = await self.get_own_profile_on_second(token)
        self.assertEqual(second.hash, first.hash)

    async def test_a_sign_out_on_one_process_is_refused_by_the_other(
        self,
    ) -> None:
        (token,) = await self.sign_up_and_in()
        await self.get_own_profile(token)  # cached by the first
        await self.sign_out_on_second(token)
        await self.assert_refused(
            self.get_own_profile(token),
            grpc.StatusCode.UNAUTHENTICATED,
            "SESSION_NOT_FOUND",
        )

    async def test_a_group_granted_shows_on_both_processes(self) -> None:
        uid, (token,) = await self.new_player()
        await self.get_own_profile(token)
        await self.get_own_profile_on_second(token)
        await self.operator.run(
            "auth", "access", "members", "add", "auth.profiles.grp_managers", uid
        )
        first = await self.get_own_profile(token)
        second = await self.get_own_profile_on_second(token)
        self.assertEqual(first.permissions["auth.profiles.tags"], 15)
        self.assertEqual(second.hash, first.hash)
