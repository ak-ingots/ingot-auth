import grpc
from ingots.testing import ProjectTestCase

from .steps import GameMixin, new_email


class EmailCodeScenario(GameMixin, ProjectTestCase):
    async def test_a_player_signs_up_and_in_by_the_code_of_its_email(
        self,
    ) -> None:
        email = new_email()
        attempt_uid = await self.start_sign_up_by_email(email)
        code = await self.mailpit.read_code(email)
        uid = await self.answer_sign_up(attempt_uid, code)
        self.assertTrue(uid)
        attempt_uid = await self.start_sign_in_by_email(email)
        code = await self.mailpit.read_code(email)
        token = await self.answer_sign_in(attempt_uid, code)
        profile = await self.get_own_profile(token)
        self.assertTrue(profile.hash)

    async def test_a_wrong_code_is_refused(self) -> None:
        email = new_email()
        attempt_uid = await self.start_sign_up_by_email(email)
        code = await self.mailpit.read_code(email)
        wrong = "0" * len(code) if code != "0" * len(code) else "1" * len(code)
        await self.assert_refused(
            self.answer_sign_up(attempt_uid, wrong),
            grpc.StatusCode.UNAUTHENTICATED,
            "METHOD_REFUSED",
        )

    async def test_a_taken_email_is_refused_on_the_sign_up(self) -> None:
        email = new_email()
        attempt_uid = await self.start_sign_up_by_email(email)
        await self.answer_sign_up(attempt_uid, await self.mailpit.read_code(email))
        attempt_uid = await self.start_sign_up_by_email(email)
        code = await self.mailpit.read_code(email)
        error = await self.assert_refused(
            self.answer_sign_up(attempt_uid, code),
            grpc.StatusCode.ALREADY_EXISTS,
            "IDENTITY_CONFLICT",
        )
        self.assertEqual(error.metadata, {"kind": "email"})

    async def test_a_sign_in_of_an_unknown_email_is_asked_alike(self) -> None:
        attempt_uid = await self.start_sign_in_by_email(new_email())
        self.assertTrue(attempt_uid)
        await self.assert_refused(
            self.answer_sign_in(attempt_uid, "000000"),
            grpc.StatusCode.UNAUTHENTICATED,
            "METHOD_REFUSED",
        )
