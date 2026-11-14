import datetime
import decimal
import hashlib
import os
import re
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
from ingots.defaults.operations import Caller, Permissions
from ingots.defaults.settings.configs import BoolConfig
from google.protobuf.timestamp_pb2 import Timestamp
from ingots.puer import Slot

from ingot_auth import AuthProject
from ingot_auth.__main__ import AuthMemorySessionsUnit, AuthMemorySignInUnit
from ingot_auth.access import AuthAccessUnit
from ingot_auth.access.groups import (
    AuthAnonymousGroup,
    AuthGroup,
    AuthGroupsUnit,
    AuthGroupsPermissions,
)
from ingot_auth.access.members import AuthMembersPermissions
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.caches.memory import AuthMemoryCache
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.contrib.transports.grpcio import (
    AuthGrpcAdminBinding,
    AuthGrpcAttrsServicer,
    AuthGrpcEmailCodeBinding,
    AuthGrpcErrorsUnit,
    AuthGrpcFlowsBinding,
    AuthGrpcGroupsServicer,
    AuthGrpcMembersServicer,
    AuthGrpcMetadataBinding,
    AuthGrpcNicknameBinding,
    AuthGrpcNicknameServicer,
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
from ingot_auth.contrib.transports.grpcio.base import (
    Context,
    get_bearer_token,
    get_peer_ip,
)
from ingot_auth.contrib.transports.grpcio.sessions.attrs import build_attr_values
from ingot_auth.metadata.v1 import metadata_pb2
from ingot_auth.methods.nickname.v1 import nickname_pb2, nickname_pb2_grpc
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
from ingot_auth.sign_in.v1 import sign_in_pb2
from ingot_auth.sign_up.v1 import sign_up_pb2
from ingot_auth.caches import AuthAttemptNotFoundError
from ingot_auth.contrib.dispatchers.memory import AuthMemoryDispatcher
from ingot_auth.contrib.mailers.memory import AuthMemoryMailer
from ingot_auth.contrib.transports.grpcio.challenges import build_challenge
from ingot_auth.methods.email_code import (
    AuthEmailCodeConfigs,
    AuthEmailCodeMethod,
    AuthEmailCodePermissions,
)
from ingot_auth.methods.email_code.v1 import email_code_pb2
from ingot_auth.methods.v1 import challenges_pb2
from ingot_auth.logging import AuthLoggingUnit
from ingot_auth.metadata import AuthMetadataPermissions
from ingot_auth.methods import (
    AuthMethodDeniedError,
    AuthMethodInvalidError,
    AuthMethodNotFoundError,
    AuthMethodRefusedError,
    AuthMethodsUnit,
    AuthMethodUnsupportedError,
    BaseAuthMethod,
)
from ingot_auth.methods.nickname import (
    AuthNicknameConfigs,
    AuthNicknameMethod,
    AuthNicknamePermissions,
)
from ingot_auth.methods.password import AuthPassword
from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.profiles.attrs import AuthAttrsPermissions
from ingot_auth.profiles.tags import AuthTagsPermissions
from ingot_auth.sessions.attrs import AuthSessionAttrsPermissions
from ingot_auth.sessions.presets import AuthSessionPresetsPermissions
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.settings.configs import AuthConfigs
from ingot_auth.sessions import AuthSessionExpiredError
from ingot_auth.sign_in import AuthSignInPermissions
from ingot_auth.sign_up import AuthSignUpPermissions
from ingot_auth.storages import (
    AuthAttrType,
    AuthAttrValue,
    AuthIdentityConflictError,
    AuthMembership,
    AuthProfile,
    AuthSessionAttr,
    AuthSessionAttrSource,
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
)

from tests import masks

NOW: t.Final = datetime.datetime(2026, 11, 9, tzinfo=datetime.UTC)
ADMIN: t.Final = Caller(
    uid="admin",
    permissions=masks(
        *AuthTagsPermissions,
        *AuthAttrsPermissions,
        *AuthSessionAttrsPermissions,
        *AuthSessionPresetsPermissions,
        *AuthGroupsPermissions,
        *AuthMembersPermissions,
    ),
)


class AdminCaller:
    async def _get_caller(self, context: aio.ServicerContext[t.Any, t.Any]) -> Caller:
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


class TstClient(
    AuthGrpcMetadataBinding,
    AuthGrpcAdminBinding,
    AuthGrpcNicknameBinding,
    AuthGrpcEmailCodeBinding,
    AuthGrpcFlowsBinding,
    DefaultGrpcClient,
):
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
        return super()._get_permissions() | masks(*AuthMembersPermissions)


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


class TstGrpcUnit(GrpcUnit):
    errors = Slot(AuthGrpcErrorsUnit)
    clients = Slot(TstClientsUnit)


class TstAdminGrpcUnit(TstGrpcUnit):
    servers = Slot(TstServersUnit)


class TstAnonymousGrpcUnit(TstGrpcUnit):
    servers = Slot(TstAnonymousServersUnit)


class TstProject(AuthProject, GrpcProject):
    settings = Slot(TstSettingsUnit)
    logging = Slot(TstLoggingUnit)
    auth = Slot(TstAuthUnit)
    grpc = Slot(TstGrpcUnit)


class TstAdminProject(TstProject):
    grpc = Slot(TstAdminGrpcUnit)


class TstAnonymousProject(TstProject):
    grpc = Slot(TstAnonymousGrpcUnit)


class ClosedAnonymousGroup(AuthAnonymousGroup):
    """The metadata closed to anyone."""

    @t.override
    def _get_permissions(self) -> Permissions:
        readers = masks(AuthMetadataPermissions.CAN_READ)
        return super()._get_permissions() - readers


class ClosedGroupsUnit(TstGroupsUnit):
    grp_anonymous = Slot(ClosedAnonymousGroup)


class ClosedAccessUnit(TstAccessUnit):
    groups = Slot(ClosedGroupsUnit)


class ClosedAuthUnit(TstAuthUnit):
    access = Slot(ClosedAccessUnit)


class TstClosedProject(TstAnonymousProject):
    auth = Slot(ClosedAuthUnit)


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


class CheapPassword(AuthPassword):
    SCRYPT_LOG_N = 4


class TstNicknameMethodsUnit(AuthMethodsUnit):
    nickname = Slot(AuthNicknameMethod)
    password = Slot(CheapPassword)


class TstNicknameAuthUnit(TstAuthUnit):
    cache = Slot(AuthMemoryCache)
    sessions = Slot(AuthMemorySessionsUnit)
    sign_in = Slot(AuthMemorySignInUnit)
    methods = Slot(TstNicknameMethodsUnit)


class TstNicknameConfigs(AuthNicknameConfigs, TstConfigs):
    pass


class TstNicknameSettingsUnit(TstSettingsUnit):
    configs = Slot(TstNicknameConfigs)


class TstNicknameServer(
    AuthGrpcMetadataBinding,
    AuthGrpcAdminBinding,
    AuthGrpcNicknameBinding,
    DefaultGrpcServer,
):
    pass


class TstNicknameServersUnit(GrpcServersUnit):
    default = Slot(TstNicknameServer)


class TstNicknameGrpcUnit(TstGrpcUnit):
    servers = Slot(TstNicknameServersUnit)


class TstNicknameProject(TstProject):
    settings = Slot(TstNicknameSettingsUnit)
    auth = Slot(TstNicknameAuthUnit)
    grpc = Slot(TstNicknameGrpcUnit)


class TstEmailCodeMethodsUnit(AuthMethodsUnit):
    email_code = Slot(AuthEmailCodeMethod)


class TstEmailCodeAuthUnit(TstAuthUnit):
    cache = Slot(AuthMemoryCache)
    dispatcher = Slot(AuthMemoryDispatcher)
    mailer = Slot(AuthMemoryMailer)
    sessions = Slot(AuthMemorySessionsUnit)
    sign_in = Slot(AuthMemorySignInUnit)
    methods = Slot(TstEmailCodeMethodsUnit)


class TstEmailCodeConfigs(AuthEmailCodeConfigs, TstConfigs):
    pass


class TstEmailCodeSettingsUnit(TstSettingsUnit):
    configs = Slot(TstEmailCodeConfigs)


class TstEmailCodeServer(
    AuthGrpcMetadataBinding,
    AuthGrpcEmailCodeBinding,
    AuthGrpcFlowsBinding,
    DefaultGrpcServer,
):
    pass


class TstEmailCodeServersUnit(GrpcServersUnit):
    default = Slot(TstEmailCodeServer)


class TstEmailCodeGrpcUnit(TstGrpcUnit):
    servers = Slot(TstEmailCodeServersUnit)


class TstEmailCodeProject(TstProject):
    settings = Slot(TstEmailCodeSettingsUnit)
    auth = Slot(TstEmailCodeAuthUnit)
    grpc = Slot(TstEmailCodeGrpcUnit)


def get_forwarded_ip(context: Context) -> str | None:
    """The IP the proxy of a test sets."""
    for key, value in context.invocation_metadata() or ():
        if key == "x-forwarded-for" and isinstance(value, str):
            return value
    return None


class ForwardedNicknameServicer(AuthGrpcNicknameServicer):
    """Behind a proxy: the IP is of the header it sets."""

    @t.override
    def _get_transport_attr_values(
        self, context: Context
    ) -> dict[str, AuthAttrValue | None]:
        return super()._get_transport_attr_values(context) | {
            "ip": get_forwarded_ip(context)
        }


class ForwardedNicknameBinding(AuthGrpcNicknameBinding):
    auth_methods_nickname = GrpcService(
        nickname_pb2_grpc.NicknameStub, ForwardedNicknameServicer
    )


class TstForwardedServer(ForwardedNicknameBinding, TstNicknameServer):
    pass


class TstForwardedServersUnit(TstNicknameServersUnit):
    default = Slot(TstForwardedServer)


class TstForwardedGrpcUnit(TstNicknameGrpcUnit):
    servers = Slot(TstForwardedServersUnit)


class TstForwardedProject(TstNicknameProject):
    grpc = Slot(TstForwardedGrpcUnit)


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

    async def test_an_application_may_close_the_metadata(self) -> None:
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
            [
                groups_pb2.Group(
                    name="grp_anonymous",
                    permissions={
                        "auth.metadata": 1,
                        "auth.sign_in": 1,
                        "auth.sign_up": 1,
                    },
                ),
                groups_pb2.Group(name="grp_signed_in"),
                groups_pb2.Group(name="admins", permissions={"auth.access.members": 7}),
            ],
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
            (AuthNicknamePermissions, nickname_pb2.Permission),
            (AuthEmailCodePermissions, email_code_pb2.Permission),
            (AuthSignUpPermissions, sign_up_pb2.Permission),
            (AuthSignInPermissions, sign_in_pb2.Permission),
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

    async def test_a_nickname_signs_up_and_in_by_its_service(self) -> None:
        nickname = (await self.connect(TstNicknameProject)).auth_methods_nickname
        signed_up = (
            await nickname.SignUp(
                nickname_pb2.SignUpRequest(nickname="Alice", password="correct horse")
            )
        ).result.signed_up
        signed_in = (
            await nickname.SignIn(
                nickname_pb2.SignInRequest(nickname="alice", password="correct horse")
            )
        ).result.signed_in
        caller = await self.project.auth.sessions.authenticate(signed_in.token)
        self.assertEqual(
            (caller.uid, caller.session_id), (signed_up.uid, signed_in.session_id)
        )

    async def test_the_values_of_the_attributes_go_with_the_flows(self) -> None:
        nickname = (await self.connect(TstNicknameProject)).auth_methods_nickname
        attrs = self.project.auth.storage.sessions.attrs
        for attr_id, attr_type in enumerate(AuthAttrType, start=1):
            await attrs.create(
                AuthSessionAttr(
                    id=attr_id,
                    name=attr_type.value,
                    type=attr_type,
                    source=AuthSessionAttrSource.CLIENT,
                )
            )
        moment = datetime.datetime(2026, 11, 11, 12, 30, tzinfo=datetime.UTC)
        timestamp = Timestamp()
        timestamp.FromDatetime(moment)
        attr_values = [
            session_attrs_pb2.AttrValue(attr_id=1, bool_value=True),
            session_attrs_pb2.AttrValue(attr_id=2, int_value=7),
            session_attrs_pb2.AttrValue(attr_id=3, decimal_value="1.50"),
            session_attrs_pb2.AttrValue(attr_id=4, datetime_value=timestamp),
            session_attrs_pb2.AttrValue(attr_id=5, str_value="iPhone"),
        ]
        expected = {1: True, 2: 7, 3: decimal.Decimal("1.50"), 4: moment, 5: "iPhone"}
        signed_up = (
            await nickname.SignUp(
                nickname_pb2.SignUpRequest(
                    nickname="alice", password="x", attr_values=attr_values
                )
            )
        ).result.signed_up
        record = await self.project.auth.storage.sign_up.records.get(signed_up.uid)
        self.assertEqual(record.attr_values, expected)
        signed_in = (
            await nickname.SignIn(
                nickname_pb2.SignInRequest(
                    nickname="alice", password="x", attr_values=attr_values
                )
            )
        ).result.signed_in
        token_hash = hashlib.sha256(signed_in.token.encode()).hexdigest()
        session = await self.project.auth.storage.sessions.find(token_hash)
        self.assertEqual(session.attr_values, expected)

    async def create_ip_attr(self) -> None:
        await self.project.auth.storage.sessions.attrs.create(
            AuthSessionAttr(
                id=1,
                name="ip",
                type=AuthAttrType.STR,
                source=AuthSessionAttrSource.TRANSPORT,
            )
        )

    async def test_the_ip_of_the_peer_goes_with_the_flows(self) -> None:
        nickname = (await self.connect(TstNicknameProject)).auth_methods_nickname
        await self.create_ip_attr()
        signed_up = (
            await nickname.SignUp(
                nickname_pb2.SignUpRequest(nickname="a", password="x")
            )
        ).result.signed_up
        record = await self.project.auth.storage.sign_up.records.get(signed_up.uid)
        self.assertEqual(record.attr_values, {1: "127.0.0.1"})
        signed_in = (
            await nickname.SignIn(
                nickname_pb2.SignInRequest(nickname="a", password="x")
            )
        ).result.signed_in
        token_hash = hashlib.sha256(signed_in.token.encode()).hexdigest()
        session = await self.project.auth.storage.sessions.find(token_hash)
        self.assertEqual(session.attr_values, {1: "127.0.0.1"})

    async def test_an_application_binds_the_ip_to_the_header_of_its_proxy(
        self,
    ) -> None:
        nickname = (await self.connect(TstForwardedProject)).auth_methods_nickname
        await self.create_ip_attr()
        signed_up = (
            await nickname.SignUp(
                nickname_pb2.SignUpRequest(nickname="a", password="x"),
                metadata=(("x-forwarded-for", "203.0.113.7"),),
            )
        ).result.signed_up
        record = await self.project.auth.storage.sign_up.records.get(signed_up.uid)
        self.assertEqual(record.attr_values, {1: "203.0.113.7"})
        # no header, no value: nothing kept
        signed_in = (
            await nickname.SignIn(
                nickname_pb2.SignInRequest(nickname="a", password="x")
            )
        ).result.signed_in
        token_hash = hashlib.sha256(signed_in.token.encode()).hexdigest()
        session = await self.project.auth.storage.sessions.find(token_hash)
        self.assertEqual(session.attr_values, {})

    async def test_the_flows_of_a_nickname_tell_their_errors(self) -> None:
        nickname = (await self.connect(TstNicknameProject)).auth_methods_nickname
        await nickname.SignUp(
            nickname_pb2.SignUpRequest(nickname="alice", password="x")
        )
        no_value = session_attrs_pb2.AttrValue(attr_id=1)
        for call, code, reason, metadata in (
            (
                nickname.SignUp(
                    nickname_pb2.SignUpRequest(nickname="Alice", password="y")
                ),
                grpc.StatusCode.ALREADY_EXISTS,
                "IDENTITY_CONFLICT",
                {"kind": "nickname"},
            ),
            (
                nickname.SignIn(
                    nickname_pb2.SignInRequest(nickname="alice", password="y")
                ),
                grpc.StatusCode.UNAUTHENTICATED,
                "METHOD_REFUSED",
                {},
            ),
            (
                nickname.SignIn(
                    nickname_pb2.SignInRequest(nickname="bob", password="x")
                ),
                grpc.StatusCode.UNAUTHENTICATED,
                "METHOD_REFUSED",
                {},
            ),
            (
                nickname.SignIn(
                    nickname_pb2.SignInRequest(
                        nickname="alice", password="x", attr_values=[no_value]
                    )
                ),
                grpc.StatusCode.INVALID_ARGUMENT,
                "ITEM_INVALID",
                {"registry": "sessions.attrs", "key": "1"},
            ),
        ):
            with self.assertRaises(GrpcError) as error:
                await call
            self.assertEqual(
                (
                    error.exception.code,
                    error.exception.reason,
                    error.exception.metadata,
                ),
                (code, reason, metadata),
            )

    async def get_code(self) -> str:
        """The code of the last mail, once the mail is out."""
        auth = t.cast(TstEmailCodeAuthUnit, self.project.auth)
        await auth.dispatcher.join()
        text = auth.mailer.get_sent()[-1].text
        match = re.match(r"Your code is (\d+)\.", text)
        assert match is not None
        return match[1]

    async def test_an_email_signs_up_and_in_by_its_code(self) -> None:
        client = await self.connect(TstEmailCodeProject)
        email_code = client.auth_methods_email_code
        challenge = (
            await email_code.StartSignUp(
                email_code_pb2.StartSignUpRequest(email="al@b.c")
            )
        ).result.challenge
        self.assertEqual(challenge.code, challenges_pb2.CodeChallenge(length=6))
        answer = sign_up_pb2.AnswerSignUpRequest(
            attempt_id=challenge.attempt_id, code=await self.get_code()
        )
        signed_up = (await client.auth_sign_up.AnswerSignUp(answer)).result.signed_up
        challenge = (
            await email_code.StartSignIn(
                email_code_pb2.StartSignInRequest(email="AL@b.c")
            )
        ).result.challenge
        answer_in = sign_in_pb2.AnswerSignInRequest(
            attempt_id=challenge.attempt_id, code=await self.get_code()
        )
        signed_in = (await client.auth_sign_in.AnswerSignIn(answer_in)).result.signed_in
        caller = await self.project.auth.sessions.authenticate(signed_in.token)
        self.assertEqual(
            (caller.uid, caller.session_id), (signed_up.uid, signed_in.session_id)
        )

    async def test_the_answers_tell_their_errors(self) -> None:
        client = await self.connect(TstEmailCodeProject)
        start = email_code_pb2.StartSignUpRequest(email="al@b.c")
        challenge = (
            await client.auth_methods_email_code.StartSignUp(start)
        ).result.challenge
        code = await self.get_code()
        wrong = f"{(int(code) + 1) % 10**6:06d}"
        # a call starts once made: made in turn, so that the answer of another
        # flow, taking the attempt, comes last
        for call, code_of_status, reason in (
            (
                lambda: client.auth_sign_up.AnswerSignUp(
                    sign_up_pb2.AnswerSignUpRequest(
                        attempt_id=challenge.attempt_id, code=wrong
                    )
                ),
                grpc.StatusCode.UNAUTHENTICATED,
                "METHOD_REFUSED",
            ),
            (
                lambda: client.auth_sign_up.AnswerSignUp(
                    sign_up_pb2.AnswerSignUpRequest(attempt_id="gone", code=code)
                ),
                grpc.StatusCode.NOT_FOUND,
                "ATTEMPT_NOT_FOUND",
            ),
            (
                # an attempt of another flow
                lambda: client.auth_sign_in.AnswerSignIn(
                    sign_in_pb2.AnswerSignInRequest(
                        attempt_id=challenge.attempt_id, code=code
                    )
                ),
                grpc.StatusCode.NOT_FOUND,
                "ATTEMPT_NOT_FOUND",
            ),
        ):
            with self.assertRaises(GrpcError) as error:
                await call()
            self.assertEqual(
                (error.exception.code, error.exception.reason),
                (code_of_status, reason),
            )

    async def test_a_flow_its_toggle_closes_is_refused(self) -> None:
        os.environ["INGOT_AUTH_SIGN_UP_NICKNAME_ENABLED"] = "off"
        nickname = (await self.connect(TstNicknameProject)).auth_methods_nickname
        with self.assertRaises(GrpcError) as error:
            await nickname.SignUp(
                nickname_pb2.SignUpRequest(nickname="a", password="x")
            )
        self.assertEqual(error.exception.code, grpc.StatusCode.PERMISSION_DENIED)

    async def test_the_sign_up_its_toggle_closes_is_refused_the_sign_in_not(
        self,
    ) -> None:
        os.environ["INGOT_AUTH_SIGN_UP_ENABLED"] = "off"
        nickname = (await self.connect(TstNicknameProject)).auth_methods_nickname
        for call, code_of_status in (
            (
                nickname.SignUp(nickname_pb2.SignUpRequest(nickname="a", password="x")),
                grpc.StatusCode.PERMISSION_DENIED,
            ),
            (
                nickname.SignIn(nickname_pb2.SignInRequest(nickname="a", password="x")),
                grpc.StatusCode.UNAUTHENTICATED,
            ),
        ):
            with self.assertRaises(GrpcError) as error:
                await call
            self.assertEqual(error.exception.code, code_of_status)

    async def test_a_user_signs_up_and_in_then_calls_by_its_token(self) -> None:
        client = await self.connect(TstNicknameProject)
        nickname = client.auth_methods_nickname
        sign_in = nickname_pb2.SignInRequest(nickname="alice", password="x")
        signed_up = (
            await nickname.SignUp(
                nickname_pb2.SignUpRequest(nickname="alice", password="x")
            )
        ).result.signed_up
        await self.project.auth.storage.access.members.add(
            AuthMembership(group="admins", uid=signed_up.uid)
        )
        token = (await nickname.SignIn(sign_in)).result.signed_in.token
        bearer = [("authorization", f"Bearer {token}")]
        members = client.auth_access_members
        request = members_pb2.ListMembersRequest(group="admins")
        reply = await members.ListMembers(request, metadata=bearer)
        self.assertEqual(list(reply.uids), [signed_up.uid])
        # open to anyone, signed in or not
        await client.auth_metadata.GetMetadata(
            metadata_pb2.GetMetadataRequest(), metadata=bearer
        )
        await nickname.SignIn(sign_in, metadata=bearer)
        for metadata, code, reason in (
            ([], grpc.StatusCode.PERMISSION_DENIED, "PERMISSION_DENIED"),
            (
                [("authorization", "Bearer unknown")],
                grpc.StatusCode.UNAUTHENTICATED,
                "SESSION_NOT_FOUND",
            ),
        ):
            with self.subTest(metadata=metadata):
                with self.assertRaises(GrpcError) as error:
                    await members.ListMembers(request, metadata=metadata)
                self.assertEqual(
                    (error.exception.code, error.exception.reason), (code, reason)
                )


class BearerTokenTestCase(unittest.TestCase):
    def test_the_token_is_that_of_the_bearer_scheme(self) -> None:
        for metadata, token in (
            (None, None),
            ((), None),
            ((("authorization", "Bearer abc"),), "abc"),
            ((("x-trace", "1"), ("authorization", "bearer abc")), "abc"),
            ((("authorization", "Basic abc"),), None),
            ((("authorization", "Bearer "),), None),
            ((("authorization", b"Bearer abc"),), None),
        ):
            with self.subTest(metadata=metadata):
                self.assertEqual(get_bearer_token(metadata), token)


class PeerIpTestCase(unittest.TestCase):
    def test_the_ip_is_that_of_the_peer_if_it_has_one(self) -> None:
        for peer, ip in (
            ("ipv4:10.0.0.1:5000", "10.0.0.1"),
            ("ipv6:[2001:db8::1]:5000", "2001:db8::1"),
            ("ipv6:%5B2001:db8::1%5D:5000", "2001:db8::1"),
            ("ipv6:[::ffff:10.0.0.1]:5000", "10.0.0.1"),
            ("unix:/run/app.sock", None),
            ("ipv4:nowhere:5000", None),
            ("", None),
        ):
            with self.subTest(peer=peer):
                context = mock.Mock(**{"peer.return_value": peer})
                self.assertEqual(get_peer_ip(context), ip)


class ErrorPoliciesTestCase(unittest.TestCase):
    def test_the_errors_of_the_methods_have_their_statuses(self) -> None:
        project = TstProject()
        errors = project.grpc.errors
        for policy, error, code, reason, metadata in (
            (
                errors.auth_method_not_found,
                AuthMethodNotFoundError.for_name("nickname"),
                grpc.StatusCode.NOT_FOUND,
                "METHOD_NOT_FOUND",
                {"method": "nickname"},
            ),
            (
                errors.auth_method_refused,
                AuthMethodRefusedError.create(),
                grpc.StatusCode.UNAUTHENTICATED,
                "METHOD_REFUSED",
                {},
            ),
            (
                errors.auth_method_denied,
                AuthMethodDeniedError.for_name("nickname"),
                grpc.StatusCode.PERMISSION_DENIED,
                "METHOD_DENIED",
                {"method": "nickname"},
            ),
            (
                errors.auth_method_invalid,
                AuthMethodInvalidError.for_field("password", ("length", "chars")),
                grpc.StatusCode.INVALID_ARGUMENT,
                "METHOD_INVALID",
                {"field": "password", "policies": "length,chars"},
            ),
            (
                errors.auth_attempt_not_found,
                AuthAttemptNotFoundError.create(),
                grpc.StatusCode.NOT_FOUND,
                "ATTEMPT_NOT_FOUND",
                {},
            ),
            (
                errors.auth_method_unsupported,
                AuthMethodUnsupportedError.for_flow("sign_up"),
                grpc.StatusCode.FAILED_PRECONDITION,
                "METHOD_UNSUPPORTED",
                {"flow": "sign_up"},
            ),
            (
                errors.auth_identity_conflict,
                AuthIdentityConflictError.for_kind("nickname"),
                grpc.StatusCode.ALREADY_EXISTS,
                "IDENTITY_CONFLICT",
                {"kind": "nickname"},
            ),
            (
                errors.auth_session_not_found,
                AuthSessionNotFoundError.for_token(),
                grpc.StatusCode.UNAUTHENTICATED,
                "SESSION_NOT_FOUND",
                {},
            ),
            (
                errors.auth_session_expired,
                AuthSessionExpiredError.for_reason(
                    AuthSessionCloseReason.EXPIRED_ABSOLUTE
                ),
                grpc.StatusCode.UNAUTHENTICATED,
                "SESSION_EXPIRED",
                {"reason": "expired_absolute"},
            ),
        ):
            with self.subTest(reason=reason):
                failure = GrpcError.from_status(policy.encode(error))
                self.assertEqual(
                    (failure.code, failure.domain, failure.reason, failure.metadata),
                    (code, "ingot-auth", reason, metadata),
                )


class AttrValuesTestCase(unittest.TestCase):
    def test_what_is_no_value_of_an_attribute_is_refused(self) -> None:
        for attr_values in (
            [session_attrs_pb2.AttrValue(attr_id=1)],
            [session_attrs_pb2.AttrValue(attr_id=1, decimal_value="1,50")],
            [session_attrs_pb2.AttrValue(attr_id=1, decimal_value="NaN")],
            [
                session_attrs_pb2.AttrValue(attr_id=1, int_value=1),
                session_attrs_pb2.AttrValue(attr_id=1, int_value=2),
            ],
        ):
            with self.subTest(attr_values=attr_values):
                with self.assertRaises(AuthItemInvalidError) as error:
                    build_attr_values(attr_values)
                self.assertEqual(error.exception.key, 1)


class ChallengesTestCase(unittest.TestCase):
    def test_a_challenge_with_no_message_is_refused(self) -> None:
        with self.assertRaises(TypeError) as error:
            build_challenge("x", "a code")
        self.assertEqual(str(error.exception), "no message of a challenge str")
