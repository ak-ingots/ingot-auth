import secrets

import grpc
from ingots.testing import ProjectTestCase

from ingot_auth.api.attrs.v1 import attrs_pb2
from ingot_auth.api.metadata.v1 import metadata_pb2
from ingot_auth.api.sessions.v1 import sessions_pb2

from .steps import GameMixin, bear, read_lines


def new_registry_uid() -> int:
    """An id of a tag or an attribute no scenario took, the game kept running."""
    return 1 + secrets.randbelow(2**31 - 1)


class OperatorScenario(GameMixin, ProjectTestCase):
    async def test_the_operator_lists_the_groups_and_their_grants(self) -> None:
        groups = {
            row[0]: row[1:]
            for row in read_lines(
                await self.operator.run("auth", "access", "groups", "list")
            )
        }
        self.assertEqual(
            groups["auth.grp_signed_in"][-2:], ["auth.profiles=2", "auth.sessions=3"]
        )
        self.assertIn("auth.activities.grp_auditors", groups)

    async def test_a_group_granted_shows_on_the_next_call(self) -> None:
        uid, (token,) = await self.new_player()
        before = await self.get_own_profile(token)
        self.assertNotIn("auth.profiles.tags", before.permissions)
        group = "auth.profiles.grp_managers"
        await self.operator.run("auth", "access", "members", "add", group, uid)
        granted = await self.get_own_profile(token)
        self.assertEqual(granted.permissions["auth.profiles.tags"], 15)
        self.assertNotEqual(granted.hash, before.hash)
        members = await self.operator.run("auth", "access", "members", "list", group)
        self.assertIn(uid, members.split())
        self.assertEqual(
            await self.operator.run("auth", "access", "members", "list-groups", uid),
            f"{group}\n",
        )
        await self.operator.run("auth", "access", "members", "remove", group, uid)
        removed = await self.get_own_profile(token)
        self.assertEqual(
            (dict(removed.permissions), removed.hash),
            (dict(before.permissions), before.hash),
        )

    async def test_the_first_administrator_is_made_on_the_command_line(self) -> None:
        admin, (token,) = await self.new_player()
        player, _ = await self.new_player()
        request = sessions_pb2.ListSessionsRequest(profile_uid=player)
        await self.assert_refused(
            self.sessions.ListSessions(request, metadata=bear(token)),
            grpc.StatusCode.PERMISSION_DENIED,
            "PERMISSION_DENIED",
        )
        await self.operator.run(
            "auth", "access", "members", "add", "auth.sessions.grp_admins", admin
        )
        reply = await self.sessions.ListSessions(request, metadata=bear(token))
        self.assertEqual(len(reply.sessions), 1)

    async def test_the_tags_and_the_attrs_registered_are_set_on_a_player(
        self,
    ) -> None:
        tag_uid, attr_uid = new_registry_uid(), new_registry_uid()
        tag, attr = f"beta_{tag_uid}", f"level_{attr_uid}"
        auth = ("auth", "profiles")
        await self.operator.run(
            *auth, "tags", "create", "--uid", str(tag_uid), "--name", tag
        )
        await self.operator.run(
            *auth,
            "attrs",
            "create",
            "--uid",
            str(attr_uid),
            "--name",
            attr,
            "--type",
            "int",
        )
        metadata = (await self.get_metadata()).profile
        self.assertIn(metadata_pb2.Profile.Tag(uid=tag_uid, name=tag), metadata.tags)
        self.assertIn(
            metadata_pb2.Profile.Attr(
                uid=attr_uid, name=attr, type=metadata_pb2.ATTR_TYPE_INT
            ),
            metadata.attrs,
        )
        uid, (token,) = await self.new_player()
        before = await self.get_own_profile(token)
        await self.operator.run(*auth, "tags", "set", uid, str(tag_uid))
        await self.operator.run(
            *auth, "attrs", "values", "set", uid, "--value", f"{attr_uid}=5"
        )
        profile = await self.get_own_profile(token)
        self.assertEqual(list(profile.values.tag_uids), [tag_uid])
        self.assertEqual(
            list(profile.values.attr_values),
            [attrs_pb2.AttrValue(attr_uid=attr_uid, int_value=5)],
        )
        self.assertNotEqual(profile.hash, before.hash)

    async def test_the_operator_revokes_every_session_of_a_stolen_account(
        self,
    ) -> None:
        uid, tokens = await self.new_player(times=2)
        revoked = await self.operator.run("auth", "sessions", "revoke-all", uid)
        self.assertEqual(revoked, "2\n")
        for token in tokens:
            await self.assert_refused(
                self.get_own_profile(token),
                grpc.StatusCode.UNAUTHENTICATED,
                "SESSION_NOT_FOUND",
            )

    async def test_the_operator_reads_when_a_player_signed_in(self) -> None:
        uid, (kept, signed_out) = await self.new_player(times=2)
        await self.sign_out_of(signed_out)
        rows = read_lines(
            await self.operator.run("auth", "sessions", "list", uid, "--closed")
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual({row[1] for row in rows}, {"nickname"})
        self.assertEqual([row[-1] for row in rows if len(row) == 6], ["signed_out"])
        open_rows = read_lines(await self.operator.run("auth", "sessions", "list", uid))
        self.assertEqual(len(open_rows), 1)
        await self.get_own_profile(kept)

    async def test_the_operator_sweeps_the_expired_sessions(self) -> None:
        # none expired: a session lives longer than a run of the scenarios
        swept = await self.operator.run("auth", "sessions", "sweep")
        self.assertTrue(swept.strip().isdigit())

    async def test_the_auditor_finds_the_changes_of_a_player(self) -> None:
        uid, (token,) = await self.new_player()
        group = "auth.profiles.grp_consumers"
        await self.operator.run("auth", "access", "members", "add", group, uid)
        rows = read_lines(
            await self.operator.run(
                "auth", "activities", "list", "--entity", f"auth.access.members:{uid}"
            )
        )
        self.assertEqual(
            [(row[1], row[3], row[7]) for row in rows],
            [("root", "bind", f'group="{group}"')],
        )
        sign_ins = read_lines(
            await self.operator.run(
                "auth", "activities", "list", "--action", "sign_in", "--limit", "50"
            )
        )
        self.assertIn(f'uid="{uid}"', [field for row in sign_ins for field in row])
        await self.get_own_profile(token)

    async def test_a_profile_of_nobody_is_refused_by_its_error(self) -> None:
        told = await self.operator.run_refused(
            "auth", "access", "members", "list-groups", "nobody"
        )
        self.assertIn("no profile 'nobody'", told)
