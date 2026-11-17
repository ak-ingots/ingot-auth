from ingots.testing import ProjectTestCase

from ingot_auth.profiles.v1 import profiles_pb2
from ingot_auth.sessions.v1 import sessions_pb2

from .steps import GameMixin, bear, read_profile_hash


class ProfileScenario(GameMixin, ProjectTestCase):
    async def test_a_player_gets_its_profile_and_its_permissions(self) -> None:
        (token,) = await self.sign_up_and_in()
        profile = await self.get_own_profile(token)
        self.assertEqual(
            (
                profile.permissions["auth.profiles"],
                profile.permissions["auth.sessions"],
            ),
            (2, 3),  # its own profile read, its own sessions listed and revoked
        )
        self.assertNotIn("auth.access", profile.permissions)

    async def test_every_reply_tells_the_hash_of_the_profile(self) -> None:
        (token,) = await self.sign_up_and_in()
        call = self.profiles.GetOwnProfile(
            profiles_pb2.GetOwnProfileRequest(), metadata=bear(token)
        )
        profile = await call
        self.assertEqual(await read_profile_hash(call), profile.hash)
        listed = self.sessions.ListOwnSessions(
            sessions_pb2.ListOwnSessionsRequest(), metadata=bear(token)
        )
        await listed
        self.assertEqual(await read_profile_hash(listed), profile.hash)
