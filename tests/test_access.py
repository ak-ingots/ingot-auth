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
from ingots.puer import Slot, Unit
from ingots.puer.cli import CommandRunner

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.contrib.storages.memory import (
    AuthMemoryAccessStorage,
    AuthMemoryMembersStorage,
    AuthMemoryProfilesStorage,
    AuthMemoryStorage,
)
from ingot_auth.access.groups import (
    AuthAnonymousGroup,
    AuthGroup,
    AuthGroupInfo,
    AuthGroupNotFoundError,
    AuthGroupsOwner,
    AuthGroupsUnit,
    AuthSignedInGroup,
)
from ingot_auth.access.members import AuthMembersPermissions
from ingot_auth.metadata import AuthMetadataPermissions
from ingot_auth.methods import AuthMethodsUnit
from ingot_auth.profiles import AuthProfilesPermissions
from ingot_auth.profiles.attrs import AuthAttrsPermissions
from ingot_auth.profiles.tags import AuthTagsPermissions
from ingot_auth.sessions.attrs import AuthSessionAttrsPermissions
from ingot_auth.sessions import AuthSessionsPermissions
from ingot_auth.sessions.presets import AuthSessionPresetsPermissions
from ingot_auth.sign_in import AuthSignInPermissions
from ingot_auth.sign_up import AuthSignUpPermissions
from ingot_auth.storages import AuthMembership, AuthProfile, AuthProfileNotFoundError
from ingot_auth.testing.methods import AuthTestingMethod, AuthTestingPermissions

from tests import ANONYMOUS, DOMAINS, OWN, ROOT, masks

NOW: t.Final = datetime.datetime(2026, 11, 9, tzinfo=datetime.UTC)


class ShopPermissions(PermissionFlags):
    CAN_BUY = 1 << 0
    CAN_REFUND = 1 << 1


class ArticlesPermissions(PermissionFlags):
    CAN_READ = 1 << 0
    CAN_PUBLISH = 1 << 1


# the domains of the units of two addons of the tests
DOMAINS.update({ShopPermissions: "shop", ArticlesPermissions: "articles"})


# an addon: its domain owns its groups; it grants to a group of the
# application by a class of no name, a mixin of what it grants
class ShopAdminsGroup(AuthGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | masks(ShopPermissions.CAN_REFUND)


class ShopBuyersGroup(AuthGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | masks(ShopPermissions.CAN_BUY)


class ShopUnit(AuthGroupsOwner):
    grp_buyers = Slot(ShopBuyersGroup)


# another addon, the same
class ArticlesAdminsGroup(AuthGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | masks(ArticlesPermissions.CAN_READ)


class ArticlesEditorsGroup(AuthGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | masks(ArticlesPermissions.CAN_PUBLISH)


class ArticlesUnit(AuthGroupsOwner):
    grp_editors = Slot(ArticlesEditorsGroup)


# the application joins them in a group of its own, granting its own
class AppAdminsGroup(ShopAdminsGroup, ArticlesAdminsGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | masks(
            AuthMembersPermissions.CAN_ADD | AuthMembersPermissions.CAN_REMOVE
        )


class AppUnit(AuthGroupsOwner):
    grp_admins = Slot(AppAdminsGroup)


class AppProject(AuthMemoryProject):
    shop = Slot(ShopUnit)
    articles = Slot(ArticlesUnit)
    app = Slot(AppUnit)


# the shop grants every signed-in user, the articles too
class ShopSignedInGroup(AuthSignedInGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | masks(ShopPermissions.CAN_BUY)


class ArticlesSignedInGroup(AuthSignedInGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | masks(ArticlesPermissions.CAN_READ)


class ShopAuthUnit(AuthMemoryUnit):
    grp_signed_in = Slot(ShopSignedInGroup)


class ArticlesAuthUnit(AuthMemoryUnit):
    grp_signed_in = Slot(ArticlesSignedInGroup)


CORE_GROUPS: t.Final = (
    "auth.grp_anonymous",
    "auth.grp_signed_in",
    "auth.profiles.grp_consumers",
    "auth.profiles.grp_managers",
    "auth.sessions.grp_consumers",
    "auth.sessions.grp_managers",
    "auth.sessions.grp_admins",
    "auth.activities.grp_auditors",
)


class GroupsTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.project = AppProject()
        self.groups = self.project.auth.access.groups

    def test_the_groups_come_in_the_order_of_the_walk(self) -> None:
        names = [group.get_name() for group in self.groups.get_all()]
        self.assertEqual(
            names,
            [*CORE_GROUPS, "shop.grp_buyers", "articles.grp_editors", "app.grp_admins"],
        )

    def test_a_group_is_got_by_its_name(self) -> None:
        group = self.groups.get("articles.grp_editors")
        self.assertIs(group, self.project.articles.grp_editors)

    def test_an_unknown_name_is_not_found(self) -> None:
        # a name is the full name of a group: not its class, not its slot alone
        for name in ("guests", "shop.buyers", "grp_buyers", "op_list"):
            with self.assertRaises(AuthGroupNotFoundError) as error:
                self.groups.get(name)
            self.assertEqual(error.exception.name, name)
            self.assertEqual(str(error.exception), f"no group {name!r}")

    def test_a_group_joins_what_the_addons_grant(self) -> None:
        self.assertEqual(
            self.groups.get("app.grp_admins").get_permissions(),
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
        with mock.patch.object(
            ShopBuyersGroup, "_get_permissions", return_value=refund
        ):
            project = AppProject()
            self.assertNotEqual(project.auth.access.groups.get_digest(), digest)

    def test_the_digest_is_computed_once(self) -> None:
        digest = self.groups.get_digest()
        with mock.patch.object(
            ShopBuyersGroup, "_get_permissions", side_effect=OSError
        ):
            self.assertEqual(self.groups.get_digest(), digest)

    def test_the_core_declares_the_groups_of_the_auth(self) -> None:
        project = AuthMemoryProject()
        auth = project.auth
        groups = auth.access.groups
        self.assertEqual(
            [group.get_name() for group in groups.get_all()], list(CORE_GROUPS)
        )
        self.assertIs(groups.get("auth.grp_anonymous"), auth.grp_anonymous)
        self.assertIsInstance(auth.grp_anonymous, AuthAnonymousGroup)
        self.assertIsInstance(groups.get("auth.grp_signed_in"), AuthSignedInGroup)
        # no method bound: the flows, the metadata
        self.assertEqual(
            auth.grp_anonymous.get_permissions(),
            masks(
                AuthSignUpPermissions.CAN_SIGN_UP,
                AuthSignInPermissions.CAN_SIGN_IN,
                AuthMetadataPermissions.CAN_READ,
            ),
        )
        self.assertEqual(auth.grp_signed_in.get_permissions(), OWN)

    def test_the_profiles_have_their_readers_and_keepers(self) -> None:
        project = AuthMemoryProject()
        profiles = project.auth.profiles
        self.assertEqual(
            profiles.grp_consumers.get_permissions(),
            masks(AuthTagsPermissions.CAN_READ, AuthAttrsPermissions.CAN_READ),
        )
        self.assertEqual(
            profiles.grp_managers.get_permissions(),
            masks(
                AuthProfilesPermissions.CAN_UPDATE,
                *AuthTagsPermissions,
                *AuthAttrsPermissions,
            ),
        )

    def test_the_sessions_have_their_readers_keepers_and_binders(self) -> None:
        project = AuthMemoryProject()
        sessions = project.auth.sessions
        binding = masks(
            AuthSessionPresetsPermissions.CAN_BIND
            | AuthSessionPresetsPermissions.CAN_UNBIND
        )
        everything = masks(*AuthSessionAttrsPermissions, *AuthSessionPresetsPermissions)
        self.assertEqual(
            sessions.grp_consumers.get_permissions(),
            masks(
                AuthSessionAttrsPermissions.CAN_READ,
                AuthSessionPresetsPermissions.CAN_READ,
            ),
        )
        self.assertEqual(sessions.grp_managers.get_permissions(), everything - binding)
        self.assertEqual(
            sessions.grp_admins.get_permissions(),
            everything | masks(AuthSessionsPermissions.CAN_LIST),
        )

    def test_a_group_held_by_two_bases_must_be_joined(self) -> None:
        # refused by mypy too
        with self.assertRaises(TypeError):

            class UnjoinedAuthUnit(  # type: ignore[misc]
                ShopAuthUnit, ArticlesAuthUnit
            ):
                pass

    def test_the_groups_unit_holds_no_group(self) -> None:
        class OwnGroupsUnit(AuthGroupsUnit):
            cli_description = "The groups, ours."

        self.assertEqual(list(OwnGroupsUnit.slots_iter(AuthGroup)), [])
        with self.assertRaisesRegex(TypeError, "WrongGroupsUnit.grp_admins"):

            class WrongGroupsUnit(AuthGroupsUnit):
                grp_admins = Slot(AppAdminsGroup)

    def test_a_plain_unit_hides_its_groups(self) -> None:
        class PlainUnit(Unit):
            grp_admins = Slot(AppAdminsGroup)

        class PlainProject(AuthMemoryProject):
            plain = Slot(PlainUnit)

        project = PlainProject()
        groups = project.auth.access.groups
        self.assertEqual(
            [group.get_name() for group in groups.get_all()], list(CORE_GROUPS)
        )
        with self.assertRaises(AuthGroupNotFoundError):
            groups.get("app.grp_admins")


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
            [*CORE_GROUPS, "shop.grp_buyers", "articles.grp_editors", "app.grp_admins"],
        )
        self.assertEqual(
            groups[len(CORE_GROUPS)],
            AuthGroupInfo(
                name="shop.grp_buyers", permissions=masks(ShopPermissions.CAN_BUY)
            ),
        )

    def test_the_members_are_added_listed_removed(self) -> None:
        members = self.access.members

        async def run() -> tuple[tuple[str, ...], ...]:
            for group, uid in (
                ("articles.grp_editors", "b2"),
                ("articles.grp_editors", "a1"),
                ("app.grp_admins", "a1"),
            ):
                membership = AuthMembership(group=group, profile_uid=uid)
                await self.runner.run(members.op_add, membership, self.metadata)
            removed = AuthMembership(group="articles.grp_editors", profile_uid="b2")
            await self.runner.run(members.op_remove, removed, self.metadata)
            return (
                await self.runner.run(
                    members.op_list, "articles.grp_editors", self.metadata
                ),
                await self.runner.run(members.op_list_groups, "a1", self.metadata),
            )

        self.assertEqual(
            asyncio.run(run()), (("a1",), ("app.grp_admins", "articles.grp_editors"))
        )

    def test_an_unknown_group_is_refused(self) -> None:
        members = self.access.members
        membership = AuthMembership(group="guests", profile_uid="a1")
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
        for group in ("auth.grp_anonymous", "auth.grp_signed_in"):
            membership = AuthMembership(group=group, profile_uid="a1")
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
        membership = AuthMembership(group="articles.grp_editors", profile_uid="c3")
        for call in (
            self.runner.run(members.op_add, membership, self.metadata),
            self.runner.run(members.op_remove, membership, self.metadata),
            self.runner.run(members.op_list_groups, "c3", self.metadata),
        ):
            with self.assertRaises(AuthProfileNotFoundError):
                asyncio.run(call)

    def test_an_anonymous_caller_may_do_nothing(self) -> None:
        metadata = self.project.operations.create_metadata(ANONYMOUS)
        membership = AuthMembership(group="articles.grp_editors", profile_uid="a1")
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
        for group in ("articles.grp_editors", "shop.grp_buyers"):
            asyncio.run(self.members.add(AuthMembership(group=group, profile_uid="a1")))
        self.assertEqual(
            self._get_permissions("a1"),
            masks(ShopPermissions.CAN_BUY, ArticlesPermissions.CAN_PUBLISH) | OWN,
        )

    def test_a_user_of_no_group_has_nothing(self) -> None:
        self.assertEqual(self._get_permissions("b2"), OWN)

    def test_every_user_has_what_signed_in_grants(self) -> None:
        self.project = SignedInProject()
        self.assertEqual(
            self._get_permissions("b2"),
            masks(ShopPermissions.CAN_BUY, AuthTestingPermissions.CAN_SIGN_IN) | OWN,
        )

    def test_a_group_no_source_has_grants_nothing(self) -> None:
        for group in ("gone", "shop.grp_buyers"):
            asyncio.run(self.members.add(AuthMembership(group=group, profile_uid="a1")))
        self.assertEqual(
            self._get_permissions("a1"), masks(ShopPermissions.CAN_BUY) | OWN
        )

    def _get_permissions(self, uid: str) -> Permissions:
        return asyncio.run(self.project.auth.access.permissions.get_permissions(uid))


class SignedInMethodsUnit(AuthMethodsUnit):
    testing = Slot(AuthTestingMethod)


class SignedInAuthUnit(ShopAuthUnit):
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
        self._memberships.add(("articles.grp_editors", "a1"))


class SeededAccessStorage(AuthMemoryAccessStorage):
    members = Slot(SeededMembersStorage)


class SeededStorage(AuthMemoryStorage):
    profiles = Slot(SeededProfilesStorage)
    access = Slot(SeededAccessStorage)


class SeededAuthUnit(AuthMemoryUnit):
    storage = Slot(SeededStorage)


class SeededProject(AppProject):
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
                "auth.grp_anonymous\tauth.metadata=1\tauth.sign_in=1"
                "\tauth.sign_up=1\n"
                "auth.grp_signed_in\tauth.profiles=2\tauth.sessions=3\n"
                "auth.profiles.grp_consumers\tauth.profiles.attrs=2"
                "\tauth.profiles.tags=2\n"
                "auth.profiles.grp_managers\tauth.profiles=1\tauth.profiles.attrs=15"
                "\tauth.profiles.tags=15\n"
                "auth.sessions.grp_consumers\tauth.sessions.attrs=2"
                "\tauth.sessions.presets=2\n"
                "auth.sessions.grp_managers\tauth.sessions.attrs=15"
                "\tauth.sessions.presets=15\n"
                "auth.sessions.grp_admins\tauth.sessions=4\tauth.sessions.attrs=15"
                "\tauth.sessions.presets=63\n"
                "auth.activities.grp_auditors\tauth.activities=1\n"
                "shop.grp_buyers\tshop=1\n"
                "articles.grp_editors\tarticles=2\n"
                "app.grp_admins\tarticles=1\tauth.access.members=3\tshop=2\n",
            ),
        )

    def test_the_members_are_printed(self) -> None:
        members = ("auth", "access", "members")
        self.assertEqual(
            self.run_project(*members, "list", "articles.grp_editors"), (0, "a1\n")
        )
        self.assertEqual(
            self.run_project(*members, "list-groups", "a1"),
            (0, "articles.grp_editors\n"),
        )

    def test_a_user_is_added_and_removed_as_the_root(self) -> None:
        members = ("auth", "access", "members")
        self.assertEqual(
            self.run_project(*members, "add", "app.grp_admins", "a1"), (0, "")
        )
        self.assertEqual(
            self.run_project(*members, "remove", "articles.grp_editors", "a1"), (0, "")
        )

    def test_an_unknown_group_fails_the_command(self) -> None:
        with self.assertLogs("ingots.puer.runner", "ERROR"):
            code, _ = self.run_project(
                "auth", "access", "members", "add", "guests", "a1"
            )
        self.assertEqual(code, 1)
