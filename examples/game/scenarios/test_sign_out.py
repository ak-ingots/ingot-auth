import unittest

import grpc

from .steps import GameMixin, new_nickname, skip_without_game


@skip_without_game
class SignOutScenario(GameMixin, unittest.IsolatedAsyncioTestCase):
    async def test_a_player_signs_out_and_its_token_is_refused(self) -> None:
        nickname = new_nickname()
        await self.sign_up_by_nickname(nickname, "s3cret-password")
        token = await self.sign_in_by_nickname(nickname, "s3cret-password")
        await self.get_own_profile(token)
        await self.sign_out_of(token)
        with self.assertRaises(grpc.aio.AioRpcError) as caught:
            await self.get_own_profile(token)
        self.assertEqual(caught.exception.code(), grpc.StatusCode.UNAUTHENTICATED)
