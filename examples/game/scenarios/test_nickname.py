import unittest

import grpc

from .steps import PASSWORD, GameMixin, new_nickname, skip_without_game


@skip_without_game
class NicknameScenario(GameMixin, unittest.IsolatedAsyncioTestCase):
    async def test_a_player_signs_up_signs_in_and_calls_with_the_token(
        self,
    ) -> None:
        nickname = new_nickname()
        uid = await self.sign_up_by_nickname(nickname, "s3cret-password")
        self.assertTrue(uid)
        token = await self.sign_in_by_nickname(nickname, "s3cret-password")
        profile = await self.get_own_profile(token)
        self.assertIn("auth.profiles", profile.permissions)
        self.assertTrue(profile.hash)

    async def test_a_wrong_password_is_refused(self) -> None:
        nickname = new_nickname()
        await self.sign_up_by_nickname(nickname, "s3cret-password")
        with self.assertRaises(grpc.aio.AioRpcError) as caught:
            await self.sign_in_by_nickname(nickname, "wrong-password")
        self.assertEqual(caught.exception.code(), grpc.StatusCode.UNAUTHENTICATED)

    async def test_a_call_with_a_token_of_no_session_is_refused(self) -> None:
        with self.assertRaises(grpc.aio.AioRpcError) as caught:
            await self.get_own_profile("no-such-token")
        self.assertEqual(caught.exception.code(), grpc.StatusCode.UNAUTHENTICATED)

    async def test_a_taken_nickname_is_refused_on_the_sign_up(self) -> None:
        nickname = new_nickname()
        await self.sign_up_by_nickname(nickname, PASSWORD)
        error = await self.assert_refused(
            self.sign_up_by_nickname(nickname, PASSWORD),
            grpc.StatusCode.ALREADY_EXISTS,
            "IDENTITY_CONFLICT",
        )
        self.assertEqual(error.metadata, {"kind": "nickname"})

    async def test_a_sign_in_of_no_player_replies_as_a_wrong_password(self) -> None:
        nickname = new_nickname()
        await self.sign_up_by_nickname(nickname, PASSWORD)
        wrong = await self.assert_refused(
            self.sign_in_by_nickname(nickname, "wrong-password"),
            grpc.StatusCode.UNAUTHENTICATED,
            "METHOD_REFUSED",
        )
        nobody = await self.assert_refused(
            self.sign_in_by_nickname(new_nickname(), PASSWORD),
            grpc.StatusCode.UNAUTHENTICATED,
            "METHOD_REFUSED",
        )
        self.assertEqual(nobody.status, wrong.status)
