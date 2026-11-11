"""The contract of the storage of the sign-up: its records."""

__all__ = ("AuthSignUpRecordsStorageContract",)

import decimal

from ingot_auth.storages import AuthSignUpRecord, AuthSignUpRecordNotFoundError

from .base import BaseAuthContract
from .profiles import NOW


class AuthSignUpRecordsStorageContract(BaseAuthContract):
    """The records of the sign-ups of a storage: each value keeps its type."""

    async def test_a_record_is_given_as_added(self) -> None:
        records = self.project.auth.storage.sign_up.records
        record = AuthSignUpRecord(
            uid="a1",
            method="mail",
            signed_up_at=NOW,
            attr_values={
                1: True,
                2: 7,
                3: decimal.Decimal("1.50"),
                4: NOW,
                5: "iPhone",
            },
        )
        await records.add(record)
        self.assertEqual(await records.get("a1"), record)

    async def test_a_profile_not_signed_up_is_not_found(self) -> None:
        with self.assertRaises(AuthSignUpRecordNotFoundError) as error:
            await self.project.auth.storage.sign_up.records.get("a1")
        self.assertEqual(error.exception.uid, "a1")
