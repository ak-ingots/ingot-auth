import typing as t
import unittest
from unittest import mock

from ingots.puer import Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.methods import AuthMethodsUnit
from ingot_auth.methods.password import AuthPassword
from ingot_auth.methods.password.scrypt import hash_password, verify_password


class TstPassword(AuthPassword):
    # cheap for the tests
    SCRYPT_LOG_N = 4


class TstMethodsUnit(AuthMethodsUnit):
    password = Slot(TstPassword)


class TstAuthUnit(AuthMemoryUnit):
    methods = Slot(TstMethodsUnit)


class TstProject(AuthMemoryProject):
    auth = Slot(TstAuthUnit)


class PasswordTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.project = TstProject()
        self.password = self.project.auth.methods.password

    async def test_a_password_verifies_against_the_secret_of_its_profile(
        self,
    ) -> None:
        secret = await self.password.hash("correct horse")
        await self.project.auth.storage.profiles.secrets.put("a1", secret)
        self.assertTrue(await self.password.verify("correct horse", "a1"))
        self.assertFalse(await self.password.verify("correct horsE", "a1"))

    async def test_no_profile_and_no_secret_verify_against_a_dummy(self) -> None:
        with mock.patch.object(
            TstPassword, "_verify", autospec=True, return_value=True
        ) as verify:
            self.assertFalse(await self.password.verify("x", None))
            self.assertFalse(await self.password.verify("x", "a1"))
        self.assertEqual(verify.call_count, 2)
        self.assertEqual(len({call.args[2] for call in verify.call_args_list}), 1)

    def test_a_password_is_normalized_to_nfkc(self) -> None:
        self.assertEqual(self.password.normalize("ｃｏｒｒｅｃｔ"), "correct")


class ScryptTestCase(unittest.TestCase):
    def test_a_hash_verifies_its_password_only(self) -> None:
        secret = hash_password("correct horse", 4, 8, 1)
        self.assertTrue(verify_password("correct horse", secret))
        self.assertFalse(verify_password("correct horsE", secret))

    def test_a_password_gets_a_new_salt_each_time(self) -> None:
        self.assertNotEqual(hash_password("x", 4, 8, 1), hash_password("x", 4, 8, 1))

    def test_what_is_not_a_hash_verifies_nothing(self) -> None:
        secret = hash_password("x", 4, 8, 1)
        _, _, parameters, salt, digest = secret.split("$")
        for other in (
            "",
            "x" + secret,
            secret.replace("$scrypt$", "$argon2id$"),
            f"$scrypt$ln=4,r=8${salt}${digest}",
            f"$scrypt$ln=four,r=8,p=1${salt}${digest}",
            f"$scrypt${parameters}$!!${digest}",
        ):
            with self.subTest(other=other):
                self.assertFalse(verify_password("x", other))
