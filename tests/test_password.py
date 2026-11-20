import typing as t
import unittest
from unittest import mock

from ingots.puer import Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.methods import AuthMethodsUnit
from ingot_auth.methods.password import (
    AuthPassword,
    AuthPbkdf2PasswordHasher,
    AuthScryptPasswordHasher,
)
from ingot_auth.methods.password import phc


class TstScryptHasher(AuthScryptPasswordHasher):
    # cheap for the tests
    SCRYPT_LOG_N = 4


class TstCostlierScryptHasher(AuthScryptPasswordHasher):
    SCRYPT_LOG_N = 5


class TstPbkdf2Hasher(AuthPbkdf2PasswordHasher):
    ITERATIONS = 10


class TstMoreIterationsHasher(AuthPbkdf2PasswordHasher):
    ITERATIONS = 11


class TstPassword(AuthPassword):
    hasher_default = Slot(TstScryptHasher)
    hasher_pbkdf2 = Slot(TstPbkdf2Hasher)
    # hashers of another cost for the tests, verifying as the others
    hasher_costlier = Slot(TstCostlierScryptHasher)
    hasher_more_iterations = Slot(TstMoreIterationsHasher)


class TstPbkdf2Password(AuthPassword):
    hasher_default = Slot(TstPbkdf2Hasher)
    hasher_scrypt = Slot(TstScryptHasher)


class TstMethodsUnit(AuthMethodsUnit):
    password = Slot(TstPassword)


class TstAuthUnit(AuthMemoryUnit):
    methods = Slot(TstMethodsUnit)


class TstProject(AuthMemoryProject):
    auth = Slot(TstAuthUnit)


class TstPbkdf2MethodsUnit(AuthMethodsUnit):
    password = Slot(TstPbkdf2Password)


class TstPbkdf2AuthUnit(AuthMemoryUnit):
    methods = Slot(TstPbkdf2MethodsUnit)


class TstPbkdf2Project(AuthMemoryProject):
    auth = Slot(TstPbkdf2AuthUnit)


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

    async def test_another_hasher_keeps_the_passwords_set_before(self) -> None:
        scrypt_secret = await self.password.hash("correct horse")
        pbkdf2_project = TstPbkdf2Project()
        pbkdf2_password = pbkdf2_project.auth.methods.password
        pbkdf2_secret = pbkdf2_password._hash("correct horse")
        self.assertTrue(pbkdf2_secret.startswith("$pbkdf2-sha256$i=10$"))
        for secret in (scrypt_secret, pbkdf2_secret):
            with self.subTest(secret=secret[:16]):
                self.assertTrue(pbkdf2_password._verify("correct horse", secret))
                self.assertTrue(self.password._verify("correct horse", secret))
                self.assertFalse(pbkdf2_password._verify("correct horsE", secret))

    async def test_a_sign_in_hashes_again_by_the_cost_of_today(self) -> None:
        secrets = self.project.auth.storage.profiles.secrets
        costlier = self.password.hasher_costlier.hash("correct horse")
        await secrets.put("a1", costlier)
        self.assertFalse(await self.password.verify("correct horsE", "a1"))
        self.assertTrue((await secrets.get("a1")).startswith("$scrypt$ln=5,"))
        self.assertTrue(await self.password.verify("correct horse", "a1"))
        secret = await secrets.get("a1")
        self.assertTrue(secret.startswith("$scrypt$ln=4,r=8,p=1$"))
        self.assertTrue(await self.password.verify("correct horse", "a1"))
        self.assertEqual(await secrets.get("a1"), secret)

    async def test_a_sign_in_hashes_again_by_another_hasher(self) -> None:
        pbkdf2_project = TstPbkdf2Project()
        pbkdf2_password = pbkdf2_project.auth.methods.password
        secrets = pbkdf2_project.auth.storage.profiles.secrets
        await secrets.put("a1", await self.password.hash("correct horse"))
        self.assertTrue(await pbkdf2_password.verify("correct horse", "a1"))
        self.assertTrue((await secrets.get("a1")).startswith("$pbkdf2-sha256$i=10$"))

    def test_a_hash_of_no_algorithm_known_verifies_nothing(self) -> None:
        for secret in ("", "x", "$argon2id$v=19$m=65536,t=3,p=4$c2FsdA$aGFzaA"):
            with self.subTest(secret=secret):
                self.assertFalse(self.password._verify("x", secret))


class HasherTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.project = TstProject()
        self.password = self.project.auth.methods.password

    def test_a_hash_verifies_its_password_only(self) -> None:
        for hasher in (self.password.hasher_default, self.password.hasher_pbkdf2):
            with self.subTest(hasher=hasher.NAME):
                secret = hasher.hash("correct horse")
                self.assertTrue(secret.startswith(f"${hasher.NAME}$"))
                self.assertTrue(hasher.verify("correct horse", secret))
                self.assertFalse(hasher.verify("correct horsE", secret))
                self.assertNotEqual(hasher.hash("x"), hasher.hash("x"))

    def test_a_hash_of_another_cost_verifies_and_needs_a_rehash(self) -> None:
        for hasher, other in (
            (self.password.hasher_default, self.password.hasher_costlier),
            (self.password.hasher_pbkdf2, self.password.hasher_more_iterations),
        ):
            with self.subTest(hasher=hasher.NAME):
                secret = other.hash("x")
                self.assertTrue(hasher.verify("x", secret))
                self.assertTrue(hasher.needs_rehash(secret))
                self.assertFalse(hasher.needs_rehash(hasher.hash("x")))

    def test_a_hash_of_another_algorithm_verifies_nothing(self) -> None:
        scrypt = self.password.hasher_default
        pbkdf2 = self.password.hasher_pbkdf2
        self.assertFalse(scrypt.verify("x", pbkdf2.hash("x")))
        self.assertFalse(pbkdf2.verify("x", scrypt.hash("x")))
        self.assertTrue(scrypt.needs_rehash(pbkdf2.hash("x")))

    def test_what_is_not_a_hash_of_scrypt_verifies_nothing(self) -> None:
        hasher = self.password.hasher_default
        secret = hasher.hash("x")
        _, _, parameters, salt, digest = secret.split("$")
        for other in (
            "",
            "x" + secret,
            f"$scrypt$ln=4,r=8${salt}${digest}",
            f"$scrypt$ln=four,r=8,p=1${salt}${digest}",
            f"$scrypt${parameters}$!!${digest}",
        ):
            with self.subTest(other=other):
                self.assertFalse(hasher.verify("x", other))

    def test_what_is_not_a_hash_of_pbkdf2_verifies_nothing(self) -> None:
        hasher = self.password.hasher_pbkdf2
        secret = hasher.hash("x")
        _, _, parameters, salt, digest = secret.split("$")
        for other in (
            "",
            f"$pbkdf2-sha256$n=10${salt}${digest}",
            f"$pbkdf2-sha256$i${salt}${digest}",
            f"$pbkdf2-sha256${parameters}$!!${digest}",
        ):
            with self.subTest(other=other):
                self.assertFalse(hasher.verify("x", other))


class PhcTestCase(unittest.TestCase):
    def test_the_name_of_a_hash(self) -> None:
        self.assertEqual(phc.get_name("$scrypt$ln=4,r=8,p=1$s$h"), "scrypt")
        self.assertEqual(phc.get_name("scrypt$ln=4"), "")
        self.assertEqual(phc.get_name(""), "")
