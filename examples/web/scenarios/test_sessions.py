from ingots.testing import ProjectTestCase

from .steps import AUTH, SiteMixin


class SessionsScenario(SiteMixin, ProjectTestCase):
    async def test_a_user_lists_and_revokes_its_own_sessions(self) -> None:
        email, laptop = await self.new_user()
        phone = await self.sign_in(email)
        sessions = (await self.ok("ownSessions", token=laptop))["sessions"]
        self.assertEqual(len(sessions), 2)
        (other,) = [session for session in sessions if not session["is_current"]]
        await self.ok(f"ownSessions/{other['uid']}:revoke", {}, laptop)
        await self.refused("ownProfile", None, 401, "SESSION_NOT_FOUND", phone)
        tablet = await self.sign_in(email)
        self.assertEqual(
            await self.ok("ownSessions:revokeOthers", {}, laptop), {"count": 1}
        )
        await self.refused("ownProfile", None, 401, "SESSION_NOT_FOUND", tablet)

    async def test_a_user_signs_out(self) -> None:
        _, token = await self.new_user()
        self.assertEqual(await self.ok("session:signOut", {}, token), {})
        await self.refused("ownProfile", None, 401, "SESSION_NOT_FOUND", token)
        # signing out again signs out of nothing
        self.assertEqual(await self.ok("session:signOut", {}, token), {})

    async def test_a_visitor_has_no_profile(self) -> None:
        response = await self.http.get(AUTH + "ownProfile")
        self.assertEqual(response.status_code, 403)
