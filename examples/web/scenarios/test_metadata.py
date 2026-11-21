from ingots.testing import ProjectTestCase

from .steps import AUTH, SiteMixin


class MetadataScenario(SiteMixin, ProjectTestCase):
    async def test_a_visitor_reads_the_methods_of_the_site(self) -> None:
        metadata = await self.ok("metadata")
        self.assertEqual(
            metadata["methods"],
            [{"name": "email_code", "sign_up": True, "sign_in": True}],
        )

    async def test_the_api_speaks_json_alone(self) -> None:
        response = await self.http.get(
            AUTH + "metadata", headers={"accept": "text/html"}
        )
        self.assertEqual(response.status_code, 406)
        response = await self.http.post(
            AUTH + "methods/emailCode:startSignUp", data={"email": "a@example.com"}
        )
        self.assertEqual(response.status_code, 415)
