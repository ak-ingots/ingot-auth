from ingots.testing import ProjectTestCase

from .steps import AUTH, PROFILE_HASH_KEY, SiteMixin, bear, new_email


class EmailCodeScenario(SiteMixin, ProjectTestCase):
    async def test_a_user_signs_up_and_in_by_the_code_of_its_email(self) -> None:
        email = new_email()
        self.assertTrue(await self.sign_up(email))
        token = await self.sign_in(email)
        response = await self.http.get(AUTH + "ownProfile", headers=bear(token))
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["hash"], response.headers[PROFILE_HASH_KEY])

    async def test_a_wrong_code_is_refused(self) -> None:
        email = new_email()
        attempt_uid = await self.start("SignUp", email)
        code = await self.mailpit.read_code(email)
        wrong = "0" * len(code) if code != "0" * len(code) else "1" * len(code)
        answer = {"attempt_uid": attempt_uid, "code": wrong}
        await self.refused("signUp:answer", answer, 401, "METHOD_REFUSED")

    async def test_a_taken_email_is_refused_on_the_sign_up(self) -> None:
        email = new_email()
        await self.sign_up(email)
        attempt_uid = await self.start("SignUp", email)
        answer = {
            "attempt_uid": attempt_uid,
            "code": await self.mailpit.read_code(email),
        }
        problem = await self.refused("signUp:answer", answer, 409, "IDENTITY_CONFLICT")
        self.assertEqual(problem["metadata"], {"kind": "email"})

    async def test_a_sign_in_of_an_unknown_email_is_asked_alike(self) -> None:
        attempt_uid = await self.start("SignIn", new_email())
        answer = {"attempt_uid": attempt_uid, "code": "000000"}
        await self.refused("signIn:answer", answer, 401, "METHOD_REFUSED")
