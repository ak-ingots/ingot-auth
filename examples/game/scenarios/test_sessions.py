import grpc
from ingots.testing import ProjectTestCase

from ingot_auth.api.sessions.v1 import sessions_pb2

from .steps import GameMixin, bear, read_lines

UNAUTHENTICATED = grpc.StatusCode.UNAUTHENTICATED

# APP_AUTH_SESSIONS_MAX of the game in its compose
SESSIONS_MAX = 3


class SessionsScenario(GameMixin, ProjectTestCase):
    async def test_a_player_sees_the_session_of_each_device(self) -> None:
        phone, laptop = await self.sign_up_and_in(times=2)
        sessions = await self.list_own_sessions(phone)
        self.assertEqual(len(sessions), 2)
        self.assertEqual([session.is_current for session in sessions].count(True), 1)
        current = next(session for session in sessions if session.is_current)
        from_laptop = await self.list_own_sessions(laptop)
        self.assertNotIn(
            current.uid, [session.uid for session in from_laptop if session.is_current]
        )

    async def test_a_player_revokes_a_lost_phone(self) -> None:
        laptop, phone = await self.sign_up_and_in(times=2)
        sessions = await self.list_own_sessions(laptop)
        lost = next(session for session in sessions if not session.is_current)
        await self.revoke_own_session(laptop, lost.uid)
        await self.assert_refused(
            self.get_own_profile(phone), UNAUTHENTICATED, "SESSION_NOT_FOUND"
        )
        self.assertEqual(len(await self.list_own_sessions(laptop)), 1)

    async def test_a_player_revokes_all_its_sessions_but_this_one(self) -> None:
        this, *others = await self.sign_up_and_in(times=3)
        self.assertEqual(await self.revoke_other_sessions(this), 2)
        for token in others:
            await self.assert_refused(
                self.get_own_profile(token), UNAUTHENTICATED, "SESSION_NOT_FOUND"
            )
        await self.get_own_profile(this)

    async def test_a_sign_in_over_the_limit_signs_out_the_oldest_device(
        self,
    ) -> None:
        uid, (oldest, *kept) = await self.new_player(times=SESSIONS_MAX + 1)
        await self.assert_refused(
            self.get_own_profile(oldest), UNAUTHENTICATED, "SESSION_NOT_FOUND"
        )
        for token in kept:
            await self.get_own_profile(token)
        self.assertEqual(len(await self.list_own_sessions(kept[-1])), SESSIONS_MAX)
        rows = read_lines(
            await self.operator.run("auth", "sessions", "list", uid, "--closed")
        )
        self.assertEqual([row[-1] for row in rows if len(row) == 6], ["evicted"])

    async def test_a_session_of_another_player_is_not_found(self) -> None:
        (mine,) = await self.sign_up_and_in()
        (theirs,) = await self.sign_up_and_in()
        [session] = await self.list_own_sessions(theirs)
        await self.assert_refused(
            self.revoke_own_session(mine, session.uid),
            grpc.StatusCode.NOT_FOUND,
            "OWN_SESSION_NOT_FOUND",
        )
        await self.get_own_profile(theirs)

    async def test_a_token_closed_is_refused_as_one_of_no_session(self) -> None:
        # an expired one tells SESSION_EXPIRED and why, after its lifetime: the
        # unit tests of the sessions prove it, no scenario waits hours
        (token,) = await self.sign_up_and_in()
        await self.sign_out_of(token)
        closed = await self.assert_refused(
            self.get_own_profile(token), UNAUTHENTICATED, "SESSION_NOT_FOUND"
        )
        unknown = await self.assert_refused(
            self.get_own_profile("no-such-token"), UNAUTHENTICATED, "SESSION_NOT_FOUND"
        )
        self.assertEqual(closed.status, unknown.status)

    async def test_the_sessions_of_the_others_are_closed_to_a_player(self) -> None:
        (token,) = await self.sign_up_and_in()
        await self.assert_refused(
            self.sessions.ListSessions(
                sessions_pb2.ListSessionsRequest(profile_uid="a1"),
                metadata=bear(token),
            ),
            grpc.StatusCode.PERMISSION_DENIED,
            "PERMISSION_DENIED",
        )
