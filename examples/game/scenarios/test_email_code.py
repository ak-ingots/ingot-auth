import unittest

import grpc

from .steps import GameMixin, new_email, skip_without_game


@skip_without_game
class EmailCodeScenario(GameMixin, unittest.IsolatedAsyncioTestCase):
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
        with self.assertRaises(grpc.aio.AioRpcError) as caught:
            await self.answer_sign_up(attempt_uid, wrong)
        self.assertEqual(caught.exception.code(), grpc.StatusCode.UNAUTHENTICATED)
