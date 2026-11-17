from ingots.testing import ProjectTestCase

from ingot_auth.metadata.v1 import metadata_pb2

from .steps import GameMixin


class MetadataScenario(GameMixin, ProjectTestCase):
    async def test_the_client_learns_the_methods_before_any_sign_in(self) -> None:
        metadata = await self.get_metadata()
        self.assertEqual(
            sorted(metadata.methods, key=lambda method: method.name),
            [
                metadata_pb2.Method(name="email_code", sign_up=True, sign_in=True),
                metadata_pb2.Method(name="nickname", sign_up=True, sign_in=True),
            ],
        )
