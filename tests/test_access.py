import asyncio
import contextlib
import datetime
import io
import os
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import (
    OperationPermissionsError,
    PermissionFlags,
    Permissions,
)
from ingots.puer import Slot
from ingots.puer.cli import CommandRunner

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.contrib.storages.memory import (
    AuthMemoryAccessStorage,
    AuthMemoryMembersStorage,
    AuthMemoryProfilesStorage,
    AuthMemoryStorage,
)
from ingot_auth.access import AuthAccessUnit
from ingot_auth.access.groups import (
    AuthAnonymousGroup,
    AuthGroup,
    AuthGroupInfo,
    AuthGroupNotFoundError,
    AuthGroupsUnit,
    AuthSignedInGroup,
)
from ingot_auth.access.members import AuthMembersPermissions
from ingot_auth.metadata import AuthMetadataPermissions
from ingot_auth.methods import AuthMethodsUnit
from ingot_auth.sign_in import AuthSignInPermissions
from ingot_auth.sign_up import AuthSignUpPermissions
from ingot_auth.storages import AuthMembership, AuthProfile, AuthProfileNotFoundError
from ingot_auth.testing.methods import AuthTestingMethod, AuthTestingPermissions

from tests import ANONYMOUS, DOMAINS, ROOT, masks

NOW: t.Final = datetime.datetime(2026, 11, 9, tzinfo=datetime.UTC)


class ShopPermissions(PermissionFlags):
    CAN_BUY = 1 << 0
    CAN_REFUND = 1 << 1


class ArticlesPermissions(PermissionFlags):
    CAN_READ = 1 << 0
    CAN_PUBLISH = 1 << 1


# the domains of the units of two addons of the tests
DOMAINS.update({ShopPermissions: "shop", ArticlesPermissions: "articles"})


# an addon: grants to a group of the application, declares one of its own
class ShopAdminsGroup(AuthGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | masks(ShopPermissions.CAN_REFUND)


class BuyersGroup(AuthGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | masks(ShopPermissions.CAN_BUY)


class ShopGroupsUnit(AuthGroupsUnit):
    admins = Slot(ShopAdminsGroup)
    buyers = Slot(BuyersGroup)


# another addon, the same
class ArticlesAdminsGroup(AuthGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | masks(ArticlesPermissions.CAN_READ)


class EditorsGroup(AuthGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | masks(ArticlesPermissions.CAN_PUBLISH)


class ArticlesGroupsUnit(AuthGroupsUnit):
    admins = Slot(ArticlesAdminsGroup)
    editors = Slot(EditorsGroup)


# the application joins them, granting its own
class AppAdminsGroup(ShopAdminsGroup, ArticlesAdminsGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | masks(
            AuthMembersPermissions.CAN_ADD | AuthMembersPermissions.CAN_REMOVE
        )


# the shop grants every signed-in user
class ShopSignedInGroup(AuthSignedInGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | masks(ShopPermissions.CAN_BUY)


class AppGroupsUnit(ShopGroupsUnit, ArticlesGroupsUnit):
    admins = Slot(AppAdminsGroup)


class AppAccessUnit(AuthAccessUnit):
    groups = Slot(AppGroupsUnit)


class AppAuthUnit(AuthMemoryUnit):
    access = Slot(AppAccessUnit)


class AppProject(AuthMemoryProject):
    auth = Slot(AppAuthUnit)


class GroupsTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.project = AppProject()
        self.groups = self.project.auth.access.groups

    def test_the_groups_come_in_the_order_of_their_slots(self) -> None:
        # of the bases, the last first, as the slots of ingots go
        names = [group.get_name() for group in self.groups.get_all()]
        self.assertEqual(
            names, ["grp_anonymous", "grp_signed_in", "admins", "editors", "buyers"]
        )

    def test_a_group_is_got_by_its_name(self) -> None:
        self.assertIsInstance(self.groups.get("editors"), EditorsGroup)

    def test_an_unknown_name_is_not_found(self) -> None:
        for name in ("guests", "op_list"):
            with self.assertRaises(AuthGroupNotFoundError) as error:
                self.groups.get(name)
            self.assertEqual(error.exception.name, name)
            self.assertEqual(str(error.exception), f"no group {name!r}")

    def test_a_group_joins_what_the_addons_grant(self) -> None:
        self.assertEqual(
            self.groups.get("admins").get_permissions(),
            masks(
                ShopPermissions.CAN_REFUND,
                ArticlesPermissions.CAN_READ,
                AuthMembersPermissions.CAN_ADD | AuthMembersPermissions.CAN_REMOVE,
            ),
        )

    def test_the_digest_is_of_what_the_groups_grant(self) -> None:
        digest = self.groups.get_digest()
        project: AuthMemoryProject = AppProject()
        self.assertEqual(project.auth.access.groups.get_digest(), digest)
        for project in (AuthMemoryProject(), SignedInProject()):
            self.assertNotEqual(project.auth.access.groups.get_digest(), digest)
        refund = masks(ShopPermissions.CAN_REFUND)
        with mock.patch.object(BuyersGroup, "_get_permissions", return_value=refund):
            project = AppProject()
            self.assertNotEqual(project.auth.access.groups.get_digest(), digest)

    def test_the_digest_is_computed_once(self) -> None:
        digest = self.groups.get_digest()
        with mock.patch.object(BuyersGroup, "_get_permissions", side_effect=OSError):
            self.assertEqual(self.groups.get_digest(), digest)

    def test_the_core_declares_anonymous_and_signed_in(self) -> None:
        project = AuthMemoryProject()
        groups = project.auth.access.groups
        self.assertEqual(groups.get_all(), (groups.grp_anonymous, groups.grp_signed_in))
        self.assertIsInstance(groups.get("grp_anonymous"), AuthAnonymousGroup)
        self.assertIsInstance(groups.get("grp_signed_in"), AuthSignedInGroup)
        # no method bound: the flows, the metadata
        self.assertEqual(
            groups.grp_anonymous.get_permissions(),
            masks(
                AuthSignUpPermissions.CAN_SIGN_UP,
                AuthSignInPermissions.CAN_SIGN_IN,
                AuthMetadataPermissions.CAN_READ,
            ),
        )
        self.assertEqual(groups.grp_signed_in.get_permissions(), Permissions())

    def test_a_group_held_by_two_bases_must_be_joined(self) -> None:
        # refused by mypy too
        with self.assertRaises(TypeError):

            class UnjoinedGroupsUnit(  # type: ignore[misc]
                ShopGroupsUnit, ArticlesGroupsUnit
            ):
                pass

    def test_a_name_of_a_group_is_lowercase(self) -> None:
        with self.assertRaisesRegex(TypeError, "Admins"):

            class WrongGroups(AuthGroupsUnit):
                Admins = Slot(EditorsGroup)


class OperationsTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.project = AppProject()
        operations = self.project.operations
        self.runner = operations.runner
        self.metadata = operations.create_metadata(ROOT)
        self.access = self.project.auth.access
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        profiles = self.project.auth.storage.profiles
        for uid in ("a1", "b2"):
            asyncio.run(profiles.create(AuthProfile(uid=uid, created_at=NOW)))

    def test_the_groups_are_listed_with_their_grants(self) -> None:
        groups = asyncio.run(
            self.runner.run(self.access.groups.op_list, None, self.metadata)
        )
        self.assertEqual(
            [group.name for group in groups],
            ["grp_anonymous", "grp_signed_in", "admins", "editors", "buyers"],
        )
        self.assertEqual(
            groups[4],
            AuthGroupInfo(name="buyers", permissions=masks(ShopPermissions.CAN_BUY)),
        )

    def test_the_members_are_added_listed_removed(self) -> None:
        members = self.access.members

        async def run() -> tuple[tuple[str, ...], ...]:
            for group, uid in (("editors", "b2"), ("editors", "a1"), ("admins", "a1")):
                membership = AuthMembership(group=group, uid=uid)
                await self.runner.run(members.op_add, membership, self.metadata)
            removed = AuthMembership(group="editors", uid="b2")
            await self.runner.run(members.op_remove, removed, self.metadata)
            return (
                await self.runner.run(members.op_list, "editors", self.metadata),
                await self.runner.run(members.op_list_groups, "a1", self.metadata),
            )

        self.assertEqual(asyncio.run(run()), (("a1",), ("admins", "editors")))

    def test_an_unknown_group_is_refused(self) -> None:
        members = self.access.members
        membership = AuthMembership(group="guests", uid="a1")
        for call in (
            self.runner.run(members.op_add, membership, self.metadata),
            self.runner.run(members.op_remove, membership, self.metadata),
            self.runner.run(members.op_list, "guests", self.metadata),
        ):
            with self.assertRaises(AuthGroupNotFoundError) as error:
                asyncio.run(call)
            self.assertEqual(error.exception.name, "guests")

    def test_anonymous_and_signed_in_keep_no_members(self) -> None:
        members = self.access.members
        for group in ("grp_anonymous", "grp_signed_in"):
            membership = AuthMembership(group=group, uid="a1")
            for call in (
                self.runner.run(members.op_add, membership, self.metadata),
                self.runner.run(members.op_remove, membership, self.metadata),
                self.runner.run(members.op_list, group, self.metadata),
            ):
                with self.assertRaises(AuthGroupNotFoundError) as error:
                    asyncio.run(call)
                self.assertEqual(
                    str(error.exception), f"the group {group!r} keeps no members"
                )

    def test_a_uid_of_no_profile_is_refused(self) -> None:
        members = self.access.members
        membership = AuthMembership(group="editors", uid="c3")
        for call in (
            self.runner.run(members.op_add, membership, self.metadata),
            self.runner.run(members.op_remove, membership, self.metadata),
            self.runner.run(members.op_list_groups, "c3", self.metadata),
        ):
            with self.assertRaises(AuthProfileNotFoundError):
                asyncio.run(call)

    def test_an_anonymous_caller_may_do_nothing(self) -> None:
        metadata = self.project.operations.create_metadata(ANONYMOUS)
        membership = AuthMembership(group="editors", uid="a1")
        with self.assertRaises(OperationPermissionsError):
            asyncio.run(
                self.runner.run(self.access.members.op_add, membership, metadata)
            )
        with self.assertRaises(OperationPermissionsError):
            asyncio.run(self.runner.run(self.access.groups.op_list, None, metadata))


class GroupsGrantsTestCase(unittest.TestCase):
    project: AuthMemoryProject

    @t.override
    def setUp(self) -> None:
        self.project = AppProject()
        self.members = self.project.auth.storage.access.members

    def test_a_user_has_the_union_of_what_its_groups_grant(self) -> None:
        for group in ("editors", "buyers"):
            asyncio.run(self.members.add(AuthMembership(group=group, uid="a1")))
        self.assertEqual(
            self._get_permissions("a1"),
            masks(ShopPermissions.CAN_BUY, ArticlesPermissions.CAN_PUBLISH),
        )

    def test_a_user_of_no_group_has_nothing(self) -> None:
        self.assertEqual(self._get_permissions("b2"), Permissions())

    def test_every_user_has_what_signed_in_grants(self) -> None:
        self.project = SignedInProject()
        self.assertEqual(
            self._get_permissions("b2"),
            masks(ShopPermissions.CAN_BUY, AuthTestingPermissions.CAN_SIGN_IN),
        )

    def test_a_group_no_source_has_grants_nothing(self) -> None:
        for group in ("gone", "buyers"):
            asyncio.run(self.members.add(AuthMembership(group=group, uid="a1")))
        self.assertEqual(self._get_permissions("a1"), masks(ShopPermissions.CAN_BUY))

    def _get_permissions(self, uid: str) -> Permissions:
        return asyncio.run(self.project.auth.access.permissions.get_permissions(uid))


class SignedInGroupsUnit(AuthGroupsUnit):
    grp_signed_in = Slot(ShopSignedInGroup)


class SignedInAccessUnit(AuthAccessUnit):
    groups = Slot(SignedInGroupsUnit)


class SignedInMethodsUnit(AuthMethodsUnit):
    testing = Slot(AuthTestingMethod)


class SignedInAuthUnit(AuthMemoryUnit):
    access = Slot(SignedInAccessUnit)
    methods = Slot(SignedInMethodsUnit)


class SignedInProject(AuthMemoryProject):
    auth = Slot(SignedInAuthUnit)


class SeededProfilesStorage(AuthMemoryProfilesStorage):
    def __init__(self) -> None:
        super().__init__()
        self._profiles["a1"] = AuthProfile(uid="a1", created_at=NOW)


class SeededMembersStorage(AuthMemoryMembersStorage):
    def __init__(self) -> None:
        super().__init__()
        self._memberships.add(("editors", "a1"))


class SeededAccessStorage(AuthMemoryAccessStorage):
    members = Slot(SeededMembersStorage)


class SeededStorage(AuthMemoryStorage):
    profiles = Slot(SeededProfilesStorage)
    access = Slot(SeededAccessStorage)


class SeededAuthUnit(AppAuthUnit):
    storage = Slot(SeededStorage)


class SeededProject(AuthMemoryProject):
    auth = Slot(SeededAuthUnit)


class CommandsTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.enterContext(mock.patch.dict(os.environ, clear=True))
        self.enterContext(mock.patch("logging.config.dictConfig"))

    def run_project(self, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = CommandRunner(
                SeededProject, ["--config", "IS_PRINT_CONFIGS=off", *argv]
            ).run()
        return code, out.getvalue()

    def test_the_groups_are_printed_with_their_grants(self) -> None:
        self.assertEqual(
            self.run_project("auth", "access", "groups", "list"),
            (
                0,
                "grp_anonymous\tauth.metadata=1\tauth.sign_in=1\tauth.sign_up=1\n"
                "grp_signed_in\n"
                "admins\tarticles=1\tauth.access.members=3\tshop=2\n"
                "editors\tarticles=2\n"
                "buyers\tshop=1\n",
            ),
        )

    def test_the_members_are_printed(self) -> None:
        members = ("auth", "access", "members")
        self.assertEqual(self.run_project(*members, "list", "editors"), (0, "a1\n"))
        self.assertEqual(
            self.run_project(*members, "list-groups", "a1"), (0, "editors\n")
        )

    def test_a_user_is_added_and_removed_as_the_root(self) -> None:
        members = ("auth", "access", "members")
        self.assertEqual(self.run_project(*members, "add", "admins", "a1"), (0, ""))
        self.assertEqual(self.run_project(*members, "remove", "editors", "a1"), (0, ""))

    def test_an_unknown_group_fails_the_command(self) -> None:
        with self.assertLogs("ingots.puer.runner", "ERROR"):
            code, _ = self.run_project(
                "auth", "access", "members", "add", "guests", "a1"
            )
        self.assertEqual(code, 1)
