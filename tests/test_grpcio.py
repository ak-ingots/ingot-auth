import datetime
import os
import socket
import typing as t
import unittest
from unittest import mock

import grpc
from grpc import aio
from ingot_grpcio import GrpcProject
from ingot_grpcio.grpc import GrpcUnit
from ingot_grpcio.grpc.clients import DefaultGrpcClient, GrpcClientsUnit
from ingot_grpcio.grpc.errors import GrpcError
from ingot_grpcio.grpc.servers import DefaultGrpcServer, GrpcServersUnit
from ingot_grpcio.grpc.services import GrpcService
from ingot_grpcio.grpc.services.export import build_descriptor_set
from ingot_grpcio.logging import GrpcLoggingUnit
from ingot_grpcio.settings import GrpcSettingsUnit
from ingot_grpcio.settings.configs import GrpcConfigs
from ingots.defaults.operations import ANONYMOUS_CALLER, Caller, Permissions
from ingots.defaults.settings.configs import BoolConfig
from ingots.puer import Slot

from ingot_auth import AuthProject
from ingot_auth.access import AuthAccessUnit
from ingot_auth.access.groups import AuthGroup, AuthGroupsUnit, AuthGroupsPermissions
from ingot_auth.access.members import AuthMembersPermissions
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.contrib.transports.grpcio import (
    AuthGrpcAdminBinding,
    AuthGrpcAttrsServicer,
    AuthGrpcErrorsUnit,
    AuthGrpcGroupsServicer,
    AuthGrpcMembersServicer,
    AuthGrpcMetadataBinding,
    AuthGrpcMetadataServicer,
    AuthGrpcSessionAttrsServicer,
    AuthGrpcSessionPresetsServicer,
    AuthGrpcTagsServicer,
)
from ingot_auth.access.groups.v1 import (
    groups_pb2,
    groups_pb2_grpc,
)
from ingot_auth.access.members.v1 import (
    members_pb2,
    members_pb2_grpc,
)
from ingot_auth.metadata.v1 import (
    metadata_pb2,
    metadata_pb2_grpc,
)
from ingot_auth.profiles.attrs.v1 import (
    attrs_pb2 as profile_attrs_pb2,
)
from ingot_auth.profiles.attrs.v1 import (
    attrs_pb2_grpc as profile_attrs_pb2_grpc,
)
from ingot_auth.profiles.tags.v1 import (
    tags_pb2 as profile_tags_pb2,
)
from ingot_auth.profiles.tags.v1 import (
    tags_pb2_grpc as profile_tags_pb2_grpc,
)
from ingot_auth.sessions.attrs.v1 import (
    attrs_pb2 as session_attrs_pb2,
)
from ingot_auth.sessions.attrs.v1 import (
    attrs_pb2_grpc as session_attrs_pb2_grpc,
)
from ingot_auth.sessions.presets.v1 import (
    presets_pb2,
    presets_pb2_grpc,
)
from ingot_auth.logging import AuthLoggingUnit
from ingot_auth.metadata import AuthMetadataPermissions
from ingot_auth.methods import AuthMethodsUnit, BaseAuthMethod
from ingot_auth.methods.nickname import AuthNicknameConfigs, AuthNicknameMethod
from ingot_auth.profiles.attrs import AuthAttrsPermissions
from ingot_auth.profiles.tags import AuthTagsPermissions
from ingot_auth.sessions.attrs import AuthSessionAttrsPermissions
from ingot_auth.sessions.presets import AuthSessionPresetsPermissions
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.settings.configs import AuthConfigs
from ingot_auth.storages import AuthAttrType, AuthProfile, AuthSessionAttrSource

NOW: t.Final = datetime.datetime(2026, 11, 9, tzinfo=datetime.UTC)
ADMIN: t.Final = Caller(
    uid="admin",
    permissions=Permissions(
        *AuthTagsPermissions,
        *AuthAttrsPermissions,
        *AuthSessionAttrsPermissions,
        *AuthSessionPresetsPermissions,
        *AuthGroupsPermissions,
        *AuthMembersPermissions,
    ),
)


class AdminCaller:
    def _get_caller(self, context: aio.ServicerContext[t.Any, t.Any]) -> Caller:
        return ADMIN


class TagsServicer(AdminCaller, AuthGrpcTagsServicer):
    pass


class AttrsServicer(AdminCaller, AuthGrpcAttrsServicer):
    pass


class SessionAttrsServicer(AdminCaller, AuthGrpcSessionAttrsServicer):
    pass


class SessionPresetsServicer(AdminCaller, AuthGrpcSessionPresetsServicer):
    pass


class GroupsServicer(AdminCaller, AuthGrpcGroupsServicer):
    pass


class MembersServicer(AdminCaller, AuthGrpcMembersServicer):
    pass


class TstAdminBinding:
    auth_profiles_tags = GrpcService(profile_tags_pb2_grpc.TagsStub, TagsServicer)
    auth_profiles_attrs = GrpcService(profile_attrs_pb2_grpc.AttrsStub, AttrsServicer)
    auth_sessions_attrs = GrpcService(
        session_attrs_pb2_grpc.AttrsStub, SessionAttrsServicer
    )
    auth_sessions_presets = GrpcService(
        presets_pb2_grpc.PresetsStub, SessionPresetsServicer
    )
    auth_access_groups = GrpcService(groups_pb2_grpc.GroupsStub, GroupsServicer)
    auth_access_members = GrpcService(members_pb2_grpc.MembersStub, MembersServicer)


class TstAnonymousServer(
    AuthGrpcMetadataBinding, AuthGrpcAdminBinding, DefaultGrpcServer
):
    pass


class TstServer(AuthGrpcMetadataBinding, TstAdminBinding, DefaultGrpcServer):
    pass


class ClosedMetadataServicer(AuthGrpcMetadataServicer):
    @t.override
    def _get_caller(self, context: aio.ServicerContext[t.Any, t.Any]) -> Caller:
        return ANONYMOUS_CALLER


class TstClosedServer(DefaultGrpcServer):
    auth_metadata = GrpcService(metadata_pb2_grpc.MetadataStub, ClosedMetadataServicer)


class TstClient(AuthGrpcMetadataBinding, AuthGrpcAdminBinding, DefaultGrpcClient):
    pass


class TstConfigs(AuthConfigs, GrpcConfigs):
    pass


class TstSettingsUnit(AuthSettingsUnit, GrpcSettingsUnit):
    configs = Slot(TstConfigs)


class TstLoggingUnit(AuthLoggingUnit, GrpcLoggingUnit):
    project: "TstProject"


class AdminsGroup(AuthGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | Permissions(*AuthMembersPermissions)


class TstGroupsUnit(AuthGroupsUnit):
    admins = Slot(AdminsGroup)


class TstAccessUnit(AuthAccessUnit):
    groups = Slot(TstGroupsUnit)


class TstAuthUnit(AuthUnit):
    storage = Slot(AuthMemoryStorage)
    access = Slot(TstAccessUnit)


class TstClientsUnit(GrpcClientsUnit):
    default = Slot(TstClient)


class TstServersUnit(GrpcServersUnit):
    default = Slot(TstServer)


class TstAnonymousServersUnit(GrpcServersUnit):
    default = Slot(TstAnonymousServer)


class TstClosedServersUnit(GrpcServersUnit):
    default = Slot(TstClosedServer)


class TstGrpcUnit(GrpcUnit):
    errors = Slot(AuthGrpcErrorsUnit)
    clients = Slot(TstClientsUnit)


class TstAdminGrpcUnit(TstGrpcUnit):
    servers = Slot(TstServersUnit)


class TstAnonymousGrpcUnit(TstGrpcUnit):
    servers = Slot(TstAnonymousServersUnit)


class TstClosedGrpcUnit(TstGrpcUnit):
    servers = Slot(TstClosedServersUnit)


class TstProject(AuthProject, GrpcProject):
    settings = Slot(TstSettingsUnit)
    logging = Slot(TstLoggingUnit)
    auth = Slot(TstAuthUnit)
    grpc = Slot(TstGrpcUnit)


class TstAdminProject(TstProject):
    grpc = Slot(TstAdminGrpcUnit)


class TstAnonymousProject(TstProject):
    grpc = Slot(TstAnonymousGrpcUnit)


class TstClosedProject(TstProject):
    grpc = Slot(TstClosedGrpcUnit)


class NoFlowMethod(BaseAuthMethod[str, str, None]):
    pass


class TstMethodsUnit(AuthMethodsUnit):
    nickname = Slot(AuthNicknameMethod)
    no_flow = Slot(NoFlowMethod)


class TstMethodsAuthUnit(TstAuthUnit):
    methods = Slot(TstMethodsUnit)


class TstMethodsConfigs(AuthNicknameConfigs, TstConfigs):
    AUTH_SIGN_UP_NICKNAME_ENABLED = BoolConfig(False)


class TstMethodsSettingsUnit(TstSettingsUnit):
    configs = Slot(TstMethodsConfigs)


class TstMethodsProject(TstAnonymousProject):
    settings = Slot(TstMethodsSettingsUnit)
    auth = Slot(TstMethodsAuthUnit)


def find_free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


class GrpcTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        environ = {
            "INGOT_GRPC_DEFAULT_LISTEN_HOST": "127.0.0.1",
            "INGOT_GRPC_DEFAULT_HOST": "127.0.0.1",
            "INGOT_GRPC_DEFAULT_PORT": str(find_free_port()),
            "INGOT_IS_PRINT_CONFIGS": "off",
        }
        self.enterContext(mock.patch.dict(os.environ, environ, clear=True))
        # the logging is not under test: keep the handlers of the test run
        self.enterContext(mock.patch("logging.config.dictConfig"))

    async def connect(
        self, project_cls: type[TstProject] = TstAdminProject
    ) -> TstClient:
        self.project = project_cls()
        await self.project._configure()
        self.addAsyncCleanup(self.project._do_shut_down)
        await self.project.grpc.servers.default
        return await self.project.grpc.clients.default

    async def test_the_metadata_is_public_by_default(self) -> None:
        client = await self.connect(TstAnonymousProject)
        reply = await client.auth_metadata.GetMetadata(
            metadata_pb2.GetMetadataRequest()
        )
        self.assertEqual(
            reply,
            metadata_pb2.GetMetadataResponse(
                profile=metadata_pb2.Profile(), session=metadata_pb2.Session()
            ),
        )

    async def test_a_servicer_may_close_the_metadata(self) -> None:
        client = await self.connect(TstClosedProject)
        with self.assertRaises(GrpcError) as error:
            await client.auth_metadata.GetMetadata(metadata_pb2.GetMetadataRequest())
        self.assertEqual(error.exception.code, grpc.StatusCode.PERMISSION_DENIED)

    async def test_the_metadata_gives_the_methods_with_their_flows(self) -> None:
        client = await self.connect(TstMethodsProject)
        reply = await client.auth_metadata.GetMetadata(
            metadata_pb2.GetMetadataRequest()
        )
        self.assertEqual(
            list(reply.methods),
            [
                metadata_pb2.Method(name="nickname", sign_up=False, sign_in=True),
                metadata_pb2.Method(name="no_flow", sign_up=False, sign_in=False),
            ],
        )

    async def test_the_metadata_gives_the_registries(self) -> None:
        client = await self.connect()
        await client.auth_profiles_tags.CreateTag(
            profile_tags_pb2.CreateTagRequest(
                tag=profile_tags_pb2.Tag(id=1, name="beta")
            )
        )
        await client.auth_profiles_attrs.CreateAttr(
            profile_attrs_pb2.CreateAttrRequest(
                attr=profile_attrs_pb2.Attr(
                    id=7, name="title/en", type=profile_attrs_pb2.ATTR_TYPE_STR
                )
            )
        )
        for attr_id, name, source in (
            (1, "device", session_attrs_pb2.ATTR_SOURCE_CLIENT),
            (2, "ip", session_attrs_pb2.ATTR_SOURCE_TRANSPORT),
        ):
            await client.auth_sessions_attrs.CreateAttr(
                session_attrs_pb2.CreateAttrRequest(
                    attr=session_attrs_pb2.Attr(
                        id=attr_id,
                        name=name,
                        type=session_attrs_pb2.ATTR_TYPE_STR,
                        source=source,
                    )
                )
            )
        presets = client.auth_sessions_presets
        await presets.CreatePreset(
            presets_pb2.CreatePresetRequest(
                preset=presets_pb2.Preset(id=1, name="sign_in")
            )
        )
        for attr_id in (1, 2):
            await presets.BindAttr(
                presets_pb2.BindAttrRequest(
                    binding=presets_pb2.Binding(
                        preset_id=1, attr_id=attr_id, required=True
                    )
                )
            )
        reply = await client.auth_metadata.GetMetadata(
            metadata_pb2.GetMetadataRequest()
        )
        self.assertEqual(
            reply.profile,
            metadata_pb2.Profile(
                tags=[metadata_pb2.Profile.Tag(id=1, name="beta")],
                attrs=[
                    metadata_pb2.Profile.Attr(
                        id=7, name="title/en", type=metadata_pb2.ATTR_TYPE_STR
                    )
                ],
            ),
        )
        # the transport gives the IP: neither it nor its binding is the client's
        self.assertEqual(
            reply.session,
            metadata_pb2.Session(
                attrs=[
                    metadata_pb2.Session.Attr(
                        id=1, name="device", type=metadata_pb2.ATTR_TYPE_STR
                    )
                ],
                presets=[metadata_pb2.Session.Preset(id=1, name="sign_in")],
                bindings=[
                    metadata_pb2.Session.Binding(preset_id=1, attr_id=1, required=True)
                ],
            ),
        )

    async def test_the_tags_are_managed(self) -> None:
        tags = (await self.connect()).auth_profiles_tags
        beta = profile_tags_pb2.Tag(id=1, name="beta")
        self.assertEqual(
            (await tags.CreateTag(profile_tags_pb2.CreateTagRequest(tag=beta))).tag,
            beta,
        )
        preview = profile_tags_pb2.Tag(id=1, name="preview")
        self.assertEqual(
            (
                await tags.RenameTag(
                    profile_tags_pb2.RenameTagRequest(id=1, name="preview")
                )
            ).tag,
            preview,
        )
        reply = await tags.ListTags(profile_tags_pb2.ListTagsRequest())
        self.assertEqual(list(reply.tags), [preview])
        await tags.DeleteTag(profile_tags_pb2.DeleteTagRequest(id=1))
        self.assertEqual(
            len((await tags.ListTags(profile_tags_pb2.ListTagsRequest())).tags), 0
        )

    async def test_the_groups_are_listed_with_their_grants(self) -> None:
        groups = (await self.connect()).auth_access_groups
        reply = await groups.ListGroups(groups_pb2.ListGroupsRequest())
        self.assertEqual(
            list(reply.groups),
            [groups_pb2.Group(name="admins", permissions={"auth.access.members": 7})],
        )

    async def test_the_members_are_managed(self) -> None:
        members = (await self.connect()).auth_access_members
        await self.project.auth.storage.profiles.create(
            AuthProfile(uid="a1", created_at=NOW)
        )
        membership = members_pb2.Membership(group="admins", uid="a1")
        await members.AddMember(members_pb2.AddMemberRequest(membership=membership))
        reply = await members.ListMembers(
            members_pb2.ListMembersRequest(group="admins")
        )
        self.assertEqual(list(reply.uids), ["a1"])
        groups = await members.ListMemberGroups(
            members_pb2.ListMemberGroupsRequest(uid="a1")
        )
        self.assertEqual(list(groups.groups), ["admins"])
        await members.RemoveMember(
            members_pb2.RemoveMemberRequest(membership=membership)
        )
        reply = await members.ListMembers(
            members_pb2.ListMembersRequest(group="admins")
        )
        self.assertEqual(list(reply.uids), [])

    async def test_the_errors_of_the_members_have_their_statuses(self) -> None:
        members = (await self.connect()).auth_access_members
        for membership, reason, metadata in (
            (
                members_pb2.Membership(group="guests", uid="a1"),
                "GROUP_NOT_FOUND",
                {"group": "guests"},
            ),
            (
                members_pb2.Membership(group="admins", uid="a1"),
                "PROFILE_NOT_FOUND",
                {"uid": "a1"},
            ),
        ):
            with self.assertRaises(GrpcError) as error:
                await members.AddMember(
                    members_pb2.AddMemberRequest(membership=membership)
                )
            self.assertEqual(
                (
                    error.exception.code,
                    error.exception.domain,
                    error.exception.reason,
                    error.exception.metadata,
                ),
                (grpc.StatusCode.NOT_FOUND, "ingot-auth", reason, metadata),
            )

    async def test_the_attrs_are_managed(self) -> None:
        attrs = (await self.connect()).auth_profiles_attrs
        attr = profile_attrs_pb2.Attr(
            id=1, name="phone", type=profile_attrs_pb2.ATTR_TYPE_STR
        )
        self.assertEqual(
            (
                await attrs.CreateAttr(profile_attrs_pb2.CreateAttrRequest(attr=attr))
            ).attr,
            attr,
        )
        renamed = profile_attrs_pb2.Attr(
            id=1, name="mobile", type=profile_attrs_pb2.ATTR_TYPE_STR
        )
        self.assertEqual(
            (
                await attrs.RenameAttr(
                    profile_attrs_pb2.RenameAttrRequest(id=1, name="mobile")
                )
            ).attr,
            renamed,
        )
        reply = await attrs.ListAttrs(profile_attrs_pb2.ListAttrsRequest())
        self.assertEqual(list(reply.attrs), [renamed])
        await attrs.DeleteAttr(profile_attrs_pb2.DeleteAttrRequest(id=1))
        self.assertEqual(
            len((await attrs.ListAttrs(profile_attrs_pb2.ListAttrsRequest())).attrs), 0
        )

    async def test_the_session_attrs_are_managed(self) -> None:
        session_attrs = (await self.connect()).auth_sessions_attrs
        ip = session_attrs_pb2.Attr(
            id=1,
            name="ip",
            type=session_attrs_pb2.ATTR_TYPE_STR,
            source=session_attrs_pb2.ATTR_SOURCE_TRANSPORT,
        )
        created = await session_attrs.CreateAttr(
            session_attrs_pb2.CreateAttrRequest(attr=ip)
        )
        self.assertEqual(created.attr, ip)
        renamed = session_attrs_pb2.Attr()
        renamed.CopyFrom(ip)
        renamed.name = "peer/ip"
        reply = await session_attrs.RenameAttr(
            session_attrs_pb2.RenameAttrRequest(id=1, name="peer/ip")
        )
        self.assertEqual(reply.attr, renamed)
        listed = await session_attrs.ListAttrs(session_attrs_pb2.ListAttrsRequest())
        self.assertEqual(list(listed.attrs), [renamed])
        await session_attrs.DeleteAttr(session_attrs_pb2.DeleteAttrRequest(id=1))
        listed = await session_attrs.ListAttrs(session_attrs_pb2.ListAttrsRequest())
        self.assertEqual(len(listed.attrs), 0)

    async def test_the_session_presets_are_managed(self) -> None:
        client = await self.connect()
        await client.auth_sessions_attrs.CreateAttr(
            session_attrs_pb2.CreateAttrRequest(
                attr=session_attrs_pb2.Attr(
                    id=1,
                    name="device",
                    type=session_attrs_pb2.ATTR_TYPE_STR,
                    source=session_attrs_pb2.ATTR_SOURCE_CLIENT,
                )
            )
        )
        presets = client.auth_sessions_presets
        preset = presets_pb2.Preset(id=1, name="sign_in")
        created = await presets.CreatePreset(
            presets_pb2.CreatePresetRequest(preset=preset)
        )
        self.assertEqual(created.preset, preset)
        renamed = await presets.RenamePreset(
            presets_pb2.RenamePresetRequest(id=1, name="sign_up")
        )
        self.assertEqual(renamed.preset, presets_pb2.Preset(id=1, name="sign_up"))
        listed = await presets.ListPresets(presets_pb2.ListPresetsRequest())
        self.assertEqual(list(listed.presets), [renamed.preset])
        binding = presets_pb2.Binding(preset_id=1, attr_id=1, required=True)
        bound = await presets.BindAttr(presets_pb2.BindAttrRequest(binding=binding))
        self.assertEqual(bound.binding, binding)
        bindings = await presets.ListBindings(presets_pb2.ListBindingsRequest())
        self.assertEqual(list(bindings.bindings), [binding])
        await presets.UnbindAttr(presets_pb2.UnbindAttrRequest(preset_id=1, attr_id=1))
        bindings = await presets.ListBindings(presets_pb2.ListBindingsRequest())
        self.assertEqual(len(bindings.bindings), 0)
        await presets.DeletePreset(presets_pb2.DeletePresetRequest(id=1))
        listed = await presets.ListPresets(presets_pb2.ListPresetsRequest())
        self.assertEqual(len(listed.presets), 0)

    async def test_an_attr_not_bound_is_not_found(self) -> None:
        presets = (await self.connect()).auth_sessions_presets
        await presets.CreatePreset(
            presets_pb2.CreatePresetRequest(preset=presets_pb2.Preset(id=1, name="a"))
        )
        with self.assertRaises(GrpcError) as error:
            await presets.UnbindAttr(
                presets_pb2.UnbindAttrRequest(preset_id=1, attr_id=2)
            )
        self.assertEqual(
            (error.exception.code, error.exception.metadata),
            (
                grpc.StatusCode.NOT_FOUND,
                {"registry": "sessions.presets", "key": "1:2"},
            ),
        )

    async def test_every_source_of_the_session_attrs_has_a_message(self) -> None:
        expected = {f"ATTR_SOURCE_{item.name}" for item in AuthSessionAttrSource}
        names = set(session_attrs_pb2.AttrSource.keys())
        self.assertEqual(expected, names - {"ATTR_SOURCE_UNSPECIFIED"})

    async def test_a_session_attr_needs_a_type_and_a_source(self) -> None:
        session_attrs = (await self.connect()).auth_sessions_attrs
        for attr_type, source, key in (
            (
                session_attrs_pb2.ATTR_TYPE_UNSPECIFIED,
                session_attrs_pb2.ATTR_SOURCE_CLIENT,
                "0",
            ),
            (
                session_attrs_pb2.ATTR_TYPE_STR,
                session_attrs_pb2.ATTR_SOURCE_UNSPECIFIED,
                "0",
            ),
        ):
            session_attr = session_attrs_pb2.Attr(
                id=1, name="device", type=attr_type, source=source
            )
            with self.assertRaises(GrpcError) as error:
                await session_attrs.CreateAttr(
                    session_attrs_pb2.CreateAttrRequest(attr=session_attr)
                )
            self.assertEqual(
                (
                    error.exception.code,
                    error.exception.reason,
                    error.exception.metadata,
                ),
                (
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "ITEM_INVALID",
                    {"registry": "sessions.attrs", "key": key},
                ),
            )

    async def test_every_type_of_the_attrs_has_a_message(self) -> None:
        expected = {f"ATTR_TYPE_{item.name}" for item in AuthAttrType}
        for attr_type in (
            metadata_pb2.AttrType,
            profile_attrs_pb2.AttrType,
            session_attrs_pb2.AttrType,
        ):
            names = set(attr_type.keys()) - {"ATTR_TYPE_UNSPECIFIED"}
            self.assertEqual(expected, names)

    async def test_the_permissions_of_the_contract_are_those_of_the_auth(self) -> None:
        for flags, permission in (
            (AuthTagsPermissions, profile_tags_pb2.Permission),
            (AuthAttrsPermissions, profile_attrs_pb2.Permission),
            (AuthSessionAttrsPermissions, session_attrs_pb2.Permission),
            (AuthSessionPresetsPermissions, presets_pb2.Permission),
            (AuthMetadataPermissions, metadata_pb2.Permission),
            (AuthGroupsPermissions, groups_pb2.Permission),
            (AuthMembersPermissions, members_pb2.Permission),
        ):
            expected = {
                f"PERMISSION_{name}": item.value
                for name, item in flags.__members__.items()
            }
            values = dict(permission.items())
            del values["PERMISSION_UNSPECIFIED"]
            self.assertEqual(values, expected)

    async def test_a_public_export_holds_the_metadata_alone(self) -> None:
        exported = build_descriptor_set([AuthGrpcMetadataBinding.auth_metadata])
        self.assertEqual(
            [file.name for file in exported.file],
            ["ingot_auth/metadata/v1/metadata.proto"],
        )

    async def test_an_attr_needs_a_type(self) -> None:
        attrs = (await self.connect()).auth_profiles_attrs
        with self.assertRaises(GrpcError) as error:
            await attrs.CreateAttr(
                profile_attrs_pb2.CreateAttrRequest(
                    attr=profile_attrs_pb2.Attr(
                        id=1, name="phone", type=profile_attrs_pb2.ATTR_TYPE_UNSPECIFIED
                    )
                )
            )
        self.assertEqual(error.exception.code, grpc.StatusCode.INVALID_ARGUMENT)
        self.assertEqual(error.exception.reason, "ITEM_INVALID")

    async def test_the_errors_of_the_registries_have_their_statuses(self) -> None:
        tags = (await self.connect()).auth_profiles_tags
        await tags.CreateTag(
            profile_tags_pb2.CreateTagRequest(
                tag=profile_tags_pb2.Tag(id=1, name="beta")
            )
        )
        for call, code, reason, key in (
            (
                tags.CreateTag(
                    profile_tags_pb2.CreateTagRequest(
                        tag=profile_tags_pb2.Tag(id=1, name="staff")
                    )
                ),
                grpc.StatusCode.ALREADY_EXISTS,
                "ITEM_CONFLICT",
                "1",
            ),
            (
                tags.CreateTag(
                    profile_tags_pb2.CreateTagRequest(
                        tag=profile_tags_pb2.Tag(id=2, name="Staff")
                    )
                ),
                grpc.StatusCode.INVALID_ARGUMENT,
                "ITEM_INVALID",
                "Staff",
            ),
            (
                tags.DeleteTag(profile_tags_pb2.DeleteTagRequest(id=3)),
                grpc.StatusCode.NOT_FOUND,
                "ITEM_NOT_FOUND",
                "3",
            ),
        ):
            with self.assertRaises(GrpcError) as error:
                await call
            self.assertEqual(
                (
                    error.exception.code,
                    error.exception.domain,
                    error.exception.reason,
                    error.exception.metadata,
                ),
                (code, "ingot-auth", reason, {"registry": "profiles.tags", "key": key}),
            )

    async def test_the_administration_refuses_who_it_cannot_tell(self) -> None:
        client = await self.connect(TstAnonymousProject)
        for call in (
            client.auth_profiles_tags.ListTags(profile_tags_pb2.ListTagsRequest()),
            client.auth_profiles_tags.CreateTag(
                profile_tags_pb2.CreateTagRequest(
                    tag=profile_tags_pb2.Tag(id=1, name="beta")
                )
            ),
            client.auth_profiles_attrs.ListAttrs(profile_attrs_pb2.ListAttrsRequest()),
            client.auth_sessions_attrs.ListAttrs(session_attrs_pb2.ListAttrsRequest()),
            client.auth_sessions_presets.ListBindings(
                presets_pb2.ListBindingsRequest()
            ),
            client.auth_access_groups.ListGroups(groups_pb2.ListGroupsRequest()),
            client.auth_access_members.ListMembers(
                members_pb2.ListMembersRequest(group="admins")
            ),
        ):
            with self.assertRaises(GrpcError) as error:
                await call
            self.assertEqual(error.exception.code, grpc.StatusCode.PERMISSION_DENIED)
            self.assertEqual(error.exception.reason, "PERMISSION_DENIED")
