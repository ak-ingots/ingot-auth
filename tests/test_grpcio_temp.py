"""
The tests of test_grpcio over :mod:`ingot_auth.api`, its services bound as
``*_temp`` beside the old ones. Temporary, till the old API is removed.
"""

import datetime
import decimal
import hashlib
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
from ingot_mail.contrib.memory import MemoryMailer
from ingots.defaults.operations import Caller, Permissions
from ingots.defaults.settings.configs import BoolConfig
from google.protobuf.timestamp_pb2 import Timestamp
from ingots.puer import Slot
from ingots.testing import ProjectFixture

from ingot_auth import AuthProject
from ingot_auth.__main__ import (
    AuthMemoryMailUnit,
    AuthMemorySessionsUnit,
    AuthMemorySignInUnit,
)
from ingot_auth.access.groups import (
    AuthAnonymousGroup,
    AuthGroup,
    AuthGroupsOwner,
    AuthGroupsUnit,
)
from ingot_auth.access.members import (
    AuthMembersUnit,
)
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.caches.memory import AuthMemoryCache
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.contrib.transports.grpcio import (
    AuthGrpcMetadataServicer,
    AuthGrpcMetadataServicerTemp,
    AuthGrpcAdminBinding,
    AuthGrpcAttrsServicerTemp,
    AuthGrpcEmailCodeBinding,
    AuthGrpcErrorsUnit,
    AuthGrpcFlowsBinding,
    AuthGrpcGroupsServicerTemp,
    AuthGrpcMembersServicerTemp,
    AuthGrpcMetadataBinding,
    AuthGrpcNicknameBinding,
    AuthGrpcNicknameServicerTemp,
    AuthGrpcSessionAttrsServicerTemp,
    AuthGrpcSessionPresetsServicerTemp,
    AuthGrpcSessionsBinding,
    AuthGrpcSignOutBinding,
    AuthGrpcTagsServicerTemp,
)
from ingot_auth.api.attrs.v1 import attrs_pb2
from ingot_auth.api.access.groups.v1 import (
    groups_pb2,
    groups_pb2_grpc,
)
from ingot_auth.api.access.members.v1 import (
    members_pb2,
    members_pb2_grpc,
)
from ingot_auth.contrib.transports.grpcio.base import (
    PROFILE_HASH_KEY,
    Context,
    get_bearer_token,
    get_peer_ip,
)
from ingot_auth.contrib.transports.grpcio.sessions.sessions import CLOSE_REASONS
from ingot_auth.contrib.transports.grpcio.attrs_temp import (
    build_attr_value,
    build_attr_value_message,
    build_attr_values,
)
from ingot_auth.api.metadata.v1 import metadata_pb2
from ingot_auth.api.methods.nickname.v1 import nickname_pb2, nickname_pb2_grpc
from ingot_auth.api.profiles.attrs.v1 import (
    attrs_pb2 as profile_attrs_pb2,
)
from ingot_auth.api.profiles.attrs.v1 import (
    attrs_pb2_grpc as profile_attrs_pb2_grpc,
)
from ingot_auth.api.profiles.tags.v1 import (
    tags_pb2 as profile_tags_pb2,
)
from ingot_auth.api.profiles.tags.v1 import (
    tags_pb2_grpc as profile_tags_pb2_grpc,
)
from ingot_auth.api.sessions.attrs.v1 import (
    attrs_pb2 as session_attrs_pb2,
)
from ingot_auth.api.sessions.attrs.v1 import (
    attrs_pb2_grpc as session_attrs_pb2_grpc,
)
from ingot_auth.api.sessions.presets.v1 import (
    presets_pb2,
    presets_pb2_grpc,
)
from ingot_auth.api.sign_in.v1 import sign_in_pb2
from ingot_auth.api.sign_out.v1 import sign_out_pb2
from ingot_auth.api.sessions.v1 import sessions_pb2
from ingot_auth.activities import (
    AuthActivitiesUnit,
)
from ingot_auth.api.activities.v1 import activities_pb2
from ingot_auth.contrib.transports.grpcio.activities_temp import ACTIONS
from ingot_auth.testing.contracts import create_record
from ingot_auth.api.profiles.v1 import profiles_pb2
from ingot_auth.profiles import (
    AuthProfilesUnit,
    AuthSetProfileTagsParameters,
)
from ingot_auth.api.sign_up.v1 import sign_up_pb2
from ingot_auth.caches import AuthAttemptNotFoundError
from ingot_auth.contrib.dispatchers.memory import AuthMemoryDispatcher
from ingot_auth.contrib.transports.grpcio.challenges_temp import build_challenge
from ingot_auth.methods.email_code import (
    AuthEmailCodeConfigs,
    AuthEmailCodeMethod,
)
from ingot_auth.api.methods.email_code.v1 import email_code_pb2
from ingot_auth.api.methods.v1 import challenges_pb2
from ingot_auth.logging import AuthLoggingUnit
from ingot_auth.metadata import (
    AuthMetadataUnit,
)
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
)
from ingot_auth.methods.password import AuthPassword, AuthScryptPasswordHasher
from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.profiles.attrs import (
    AuthAttrsUnit,
)
from ingot_auth.profiles.tags import (
    AuthTagsUnit,
)
from ingot_auth.sessions.attrs import (
    AuthSessionAttrsUnit,
)
from ingot_auth.sessions.presets import (
    AuthSessionPresetsUnit,
)
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.settings import AuthConfigs
from ingot_auth.sessions import (
    AuthSessionExpiredError,
    AuthSessionsLimitError,
    AuthSessionsUnit,
)
from ingot_auth.sign_in import (
    AuthSignInUnit,
)
from ingot_auth.sign_up import (
    AuthSignUpUnit,
)
from ingot_auth.storages import (
    AuthAttr,
    AuthAttrType,
    AuthActivityAction,
    AuthAttrValue,
    AuthIdentityConflictError,
    AuthMembership,
    AuthProfile,
    AuthSessionAttr,
    AuthSessionAttrSource,
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
    AuthTag,
)

from tests import ROOT, masks

NOW: t.Final = datetime.datetime(2026, 11, 9, tzinfo=datetime.UTC)
HOUR: t.Final = datetime.timedelta(hours=1)
ADMIN: t.Final = Caller(
    uid="admin",
    permissions=masks(
        *AuthTagsUnit.Flags,
        *AuthAttrsUnit.Flags,
        *AuthSessionAttrsUnit.Flags,
        *AuthSessionPresetsUnit.Flags,
        *AuthGroupsUnit.Flags,
        *AuthMembersUnit.Flags,
    ),
)


class AdminCaller:
    async def _get_caller(self, context: aio.ServicerContext[t.Any, t.Any]) -> Caller:
        return ADMIN


class TagsServicer(AdminCaller, AuthGrpcTagsServicerTemp):
    pass


class AttrsServicer(AdminCaller, AuthGrpcAttrsServicerTemp):
    pass


class SessionAttrsServicer(AdminCaller, AuthGrpcSessionAttrsServicerTemp):
    pass


class SessionPresetsServicer(AdminCaller, AuthGrpcSessionPresetsServicerTemp):
    pass


class GroupsServicer(AdminCaller, AuthGrpcGroupsServicerTemp):
    pass


class MembersServicer(AdminCaller, AuthGrpcMembersServicerTemp):
    pass


class TstAdminBinding:
    auth_profiles_tags_temp = GrpcService(profile_tags_pb2_grpc.TagsStub, TagsServicer)
    auth_profiles_attrs_temp = GrpcService(
        profile_attrs_pb2_grpc.AttrsStub, AttrsServicer
    )
    auth_sessions_attrs_temp = GrpcService(
        session_attrs_pb2_grpc.AttrsStub, SessionAttrsServicer
    )
    auth_sessions_presets_temp = GrpcService(
        presets_pb2_grpc.PresetsStub, SessionPresetsServicer
    )
    auth_access_groups_temp = GrpcService(groups_pb2_grpc.GroupsStub, GroupsServicer)
    auth_access_members_temp = GrpcService(
        members_pb2_grpc.MembersStub, MembersServicer
    )


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
    AuthGrpcSessionsBinding,
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
        return super()._get_permissions() | masks(*AuthMembersUnit.Flags)


class TstAppUnit(AuthGroupsOwner):
    grp_admins = Slot(AdminsGroup)


class TstAuthUnit(AuthUnit):
    storage = Slot(AuthMemoryStorage)


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
    app = Slot(TstAppUnit)


class TstAdminProject(TstProject):
    grpc = Slot(TstAdminGrpcUnit)


class TstAnonymousProject(TstProject):
    grpc = Slot(TstAnonymousGrpcUnit)


class ClosedAnonymousGroup(AuthAnonymousGroup):
    """The metadata closed to anyone."""

    @t.override
    def _get_permissions(self) -> Permissions:
        readers = masks(AuthMetadataUnit.Flags.CAN_READ)
        return super()._get_permissions() - readers


class ClosedAuthUnit(TstAuthUnit):
    grp_anonymous = Slot(ClosedAnonymousGroup)


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


class CheapHasher(AuthScryptPasswordHasher):
    SCRYPT_LOG_N = 4


class CheapPassword(AuthPassword):
    hasher_default = Slot(CheapHasher)


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
    AuthGrpcSessionsBinding,
    AuthGrpcSignOutBinding,
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
    mail = Slot(AuthMemoryMailUnit)
    settings = Slot(TstEmailCodeSettingsUnit)
    auth = Slot(TstEmailCodeAuthUnit)
    grpc = Slot(TstEmailCodeGrpcUnit)


def get_forwarded_ip(context: Context) -> str | None:
    """The IP the proxy of a test sets."""
    for key, value in context.invocation_metadata() or ():
        if key == "x-forwarded-for" and isinstance(value, str):
            return value
    return None


class ForwardedNicknameServicer(AuthGrpcNicknameServicerTemp):
    """Behind a proxy: the IP is of the header it sets."""

    @t.override
    def _get_transport_attr_values(
        self, context: Context
    ) -> dict[str, AuthAttrValue | None]:
        return super()._get_transport_attr_values(context) | {
            "ip": get_forwarded_ip(context)
        }


class ForwardedNicknameBinding(AuthGrpcNicknameBinding):
    auth_methods_nickname_temp = GrpcService(
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
    async def connect(
        self, project_cls: type[TstProject] = TstAdminProject, **configs: str
    ) -> TstClient:
        """The project of the test, of the class it chooses, its server and client."""
        fixture = ProjectFixture(
            project_cls,
            configs={
                "GRPC_DEFAULT_LISTEN_HOST": "127.0.0.1",
                "GRPC_DEFAULT_HOST": "127.0.0.1",
                "GRPC_DEFAULT_PORT": str(find_free_port()),
                **configs,
            },
        )
        self.project = await fixture.create(self)
        await self.project.grpc.servers.default
        return await self.project.grpc.clients.default

    async def test_the_old_names_alias_those_of_the_api(self) -> None:
        client = await self.connect(TstAnonymousProject)
        self.assertIs(client.auth_metadata, client.auth_metadata_temp)
        server = t.cast(TstAnonymousServer, await self.project.grpc.servers.default)
        self.assertIs(server.auth_metadata, server.auth_metadata_temp)
        self.assertIs(
            AuthGrpcMetadataBinding.auth_metadata,
            AuthGrpcMetadataBinding.auth_metadata_temp,
        )
        self.assertIs(AuthGrpcMetadataServicer, AuthGrpcMetadataServicerTemp)
        # each service bound once, under the name of the API
        names = [service.name for service in TstAnonymousServer.grpc_services_iter()]
        self.assertIn("auth_metadata_temp", names)
        self.assertNotIn("auth_metadata", names)

    def test_the_old_modules_give_the_names_of_the_api(self) -> None:
        from ingot_auth.contrib.transports.grpcio import attrs as old_attrs
        from ingot_auth.contrib.transports.grpcio import attrs_temp
        from ingot_auth.contrib.transports.grpcio import challenges as old_challenges
        from ingot_auth.contrib.transports.grpcio import challenges_temp

        self.assertIs(old_attrs.build_attr_values, attrs_temp.build_attr_values)
        self.assertIs(old_challenges.build_challenge, challenges_temp.build_challenge)

    async def test_the_metadata_is_public_by_default(self) -> None:
        client = await self.connect(TstAnonymousProject)
        reply = await client.auth_metadata_temp.GetMetadata(
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
            await client.auth_metadata_temp.GetMetadata(
                metadata_pb2.GetMetadataRequest()
            )
        self.assertEqual(error.exception.code, grpc.StatusCode.PERMISSION_DENIED)

    async def test_the_metadata_gives_the_methods_with_their_flows(self) -> None:
        client = await self.connect(TstMethodsProject)
        reply = await client.auth_metadata_temp.GetMetadata(
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
        await client.auth_profiles_tags_temp.CreateTag(
            profile_tags_pb2.CreateTagRequest(
                tag=profile_tags_pb2.Tag(uid=1, name="beta")
            )
        )
        await client.auth_profiles_attrs_temp.CreateAttr(
            profile_attrs_pb2.CreateAttrRequest(
                attr=profile_attrs_pb2.Attr(
                    uid=7, name="title/en", type=profile_attrs_pb2.ATTR_TYPE_STR
                )
            )
        )
        for attr_uid, name, source in (
            (1, "device", session_attrs_pb2.ATTR_SOURCE_CLIENT),
            (2, "ip", session_attrs_pb2.ATTR_SOURCE_TRANSPORT),
        ):
            await client.auth_sessions_attrs_temp.CreateAttr(
                session_attrs_pb2.CreateAttrRequest(
                    attr=session_attrs_pb2.Attr(
                        uid=attr_uid,
                        name=name,
                        type=session_attrs_pb2.ATTR_TYPE_STR,
                        source=source,
                    )
                )
            )
        presets = client.auth_sessions_presets_temp
        await presets.CreatePreset(
            presets_pb2.CreatePresetRequest(
                preset=presets_pb2.Preset(uid=1, name="sign_in")
            )
        )
        for attr_uid in (1, 2):
            await presets.BindAttr(
                presets_pb2.BindAttrRequest(
                    binding=presets_pb2.Binding(
                        preset_uid=1, attr_uid=attr_uid, required=True
                    )
                )
            )
        reply = await client.auth_metadata_temp.GetMetadata(
            metadata_pb2.GetMetadataRequest()
        )
        self.assertEqual(
            reply.profile,
            metadata_pb2.Profile(
                tags=[metadata_pb2.Profile.Tag(uid=1, name="beta")],
                attrs=[
                    metadata_pb2.Profile.Attr(
                        uid=7, name="title/en", type=metadata_pb2.ATTR_TYPE_STR
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
                        uid=1, name="device", type=metadata_pb2.ATTR_TYPE_STR
                    )
                ],
                presets=[metadata_pb2.Session.Preset(uid=1, name="sign_in")],
                bindings=[
                    metadata_pb2.Session.Binding(
                        preset_uid=1, attr_uid=1, required=True
                    )
                ],
            ),
        )

    async def test_the_tags_are_managed(self) -> None:
        tags = (await self.connect()).auth_profiles_tags_temp
        beta = profile_tags_pb2.Tag(uid=1, name="beta")
        self.assertEqual(
            (await tags.CreateTag(profile_tags_pb2.CreateTagRequest(tag=beta))).tag,
            beta,
        )
        preview = profile_tags_pb2.Tag(uid=1, name="preview")
        self.assertEqual(
            (
                await tags.RenameTag(
                    profile_tags_pb2.RenameTagRequest(uid=1, name="preview")
                )
            ).tag,
            preview,
        )
        reply = await tags.ListTags(profile_tags_pb2.ListTagsRequest())
        self.assertEqual(list(reply.tags), [preview])
        await tags.DeleteTag(profile_tags_pb2.DeleteTagRequest(uid=1))
        self.assertEqual(
            len((await tags.ListTags(profile_tags_pb2.ListTagsRequest())).tags), 0
        )

    async def test_the_groups_are_listed_with_their_grants(self) -> None:
        groups = (await self.connect()).auth_access_groups_temp
        reply = await groups.ListGroups(groups_pb2.ListGroupsRequest())
        self.assertEqual(
            list(reply.groups),
            [
                groups_pb2.Group(
                    name="auth.grp_anonymous",
                    permissions={
                        "auth.metadata": 1,
                        "auth.sign_in": 1,
                        "auth.sign_up": 1,
                    },
                ),
                groups_pb2.Group(
                    name="auth.grp_signed_in",
                    permissions={"auth.profiles": 2, "auth.sessions": 3},
                ),
                groups_pb2.Group(
                    name="auth.grp_system",
                    permissions={"auth.sessions": 16},
                ),
                groups_pb2.Group(
                    name="auth.profiles.grp_consumers",
                    permissions={"auth.profiles.attrs": 2, "auth.profiles.tags": 2},
                ),
                groups_pb2.Group(
                    name="auth.profiles.grp_managers",
                    permissions={
                        "auth.profiles": 1,
                        "auth.profiles.attrs": 15,
                        "auth.profiles.tags": 15,
                    },
                ),
                groups_pb2.Group(
                    name="auth.sessions.grp_consumers",
                    permissions={"auth.sessions.attrs": 2, "auth.sessions.presets": 2},
                ),
                groups_pb2.Group(
                    name="auth.sessions.grp_managers",
                    permissions={
                        "auth.sessions.attrs": 15,
                        "auth.sessions.presets": 15,
                    },
                ),
                groups_pb2.Group(
                    name="auth.sessions.grp_admins",
                    permissions={
                        "auth.sessions": 28,
                        "auth.sessions.attrs": 15,
                        "auth.sessions.presets": 63,
                    },
                ),
                groups_pb2.Group(
                    name="auth.activities.grp_auditors",
                    permissions={"auth.activities": 1},
                ),
                groups_pb2.Group(
                    name="app.grp_admins", permissions={"auth.access.members": 7}
                ),
            ],
        )

    async def test_the_members_are_managed(self) -> None:
        members = (await self.connect()).auth_access_members_temp
        await self.project.auth.storage.profiles.create(
            AuthProfile(uid="a1", created_at=NOW)
        )
        membership = members_pb2.Membership(group="app.grp_admins", profile_uid="a1")
        await members.AddMember(members_pb2.AddMemberRequest(membership=membership))
        reply = await members.ListMembers(
            members_pb2.ListMembersRequest(group="app.grp_admins")
        )
        self.assertEqual(list(reply.profile_uids), ["a1"])
        groups = await members.ListMemberGroups(
            members_pb2.ListMemberGroupsRequest(profile_uid="a1")
        )
        self.assertEqual(list(groups.groups), ["app.grp_admins"])
        await members.RemoveMember(
            members_pb2.RemoveMemberRequest(membership=membership)
        )
        reply = await members.ListMembers(
            members_pb2.ListMembersRequest(group="app.grp_admins")
        )
        self.assertEqual(list(reply.profile_uids), [])

    async def test_the_errors_of_the_members_have_their_statuses(self) -> None:
        members = (await self.connect()).auth_access_members_temp
        for membership, reason, metadata in (
            (
                members_pb2.Membership(group="guests", profile_uid="a1"),
                "GROUP_NOT_FOUND",
                {"group": "guests"},
            ),
            (
                members_pb2.Membership(group="app.grp_admins", profile_uid="a1"),
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
        attrs = (await self.connect()).auth_profiles_attrs_temp
        attr = profile_attrs_pb2.Attr(
            uid=1, name="phone", type=profile_attrs_pb2.ATTR_TYPE_STR
        )
        self.assertEqual(
            (
                await attrs.CreateAttr(profile_attrs_pb2.CreateAttrRequest(attr=attr))
            ).attr,
            attr,
        )
        renamed = profile_attrs_pb2.Attr(
            uid=1, name="mobile", type=profile_attrs_pb2.ATTR_TYPE_STR
        )
        self.assertEqual(
            (
                await attrs.RenameAttr(
                    profile_attrs_pb2.RenameAttrRequest(uid=1, name="mobile")
                )
            ).attr,
            renamed,
        )
        reply = await attrs.ListAttrs(profile_attrs_pb2.ListAttrsRequest())
        self.assertEqual(list(reply.attrs), [renamed])
        await attrs.DeleteAttr(profile_attrs_pb2.DeleteAttrRequest(uid=1))
        self.assertEqual(
            len((await attrs.ListAttrs(profile_attrs_pb2.ListAttrsRequest())).attrs), 0
        )

    async def test_the_session_attrs_are_managed(self) -> None:
        session_attrs = (await self.connect()).auth_sessions_attrs_temp
        ip = session_attrs_pb2.Attr(
            uid=1,
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
            session_attrs_pb2.RenameAttrRequest(uid=1, name="peer/ip")
        )
        self.assertEqual(reply.attr, renamed)
        listed = await session_attrs.ListAttrs(session_attrs_pb2.ListAttrsRequest())
        self.assertEqual(list(listed.attrs), [renamed])
        await session_attrs.DeleteAttr(session_attrs_pb2.DeleteAttrRequest(uid=1))
        listed = await session_attrs.ListAttrs(session_attrs_pb2.ListAttrsRequest())
        self.assertEqual(len(listed.attrs), 0)

    async def test_the_session_presets_are_managed(self) -> None:
        client = await self.connect()
        await client.auth_sessions_attrs_temp.CreateAttr(
            session_attrs_pb2.CreateAttrRequest(
                attr=session_attrs_pb2.Attr(
                    uid=1,
                    name="device",
                    type=session_attrs_pb2.ATTR_TYPE_STR,
                    source=session_attrs_pb2.ATTR_SOURCE_CLIENT,
                )
            )
        )
        presets = client.auth_sessions_presets_temp
        preset = presets_pb2.Preset(uid=1, name="sign_in")
        created = await presets.CreatePreset(
            presets_pb2.CreatePresetRequest(preset=preset)
        )
        self.assertEqual(created.preset, preset)
        renamed = await presets.RenamePreset(
            presets_pb2.RenamePresetRequest(uid=1, name="sign_up")
        )
        self.assertEqual(renamed.preset, presets_pb2.Preset(uid=1, name="sign_up"))
        listed = await presets.ListPresets(presets_pb2.ListPresetsRequest())
        self.assertEqual(list(listed.presets), [renamed.preset])
        binding = presets_pb2.Binding(preset_uid=1, attr_uid=1, required=True)
        bound = await presets.BindAttr(presets_pb2.BindAttrRequest(binding=binding))
        self.assertEqual(bound.binding, binding)
        bindings = await presets.ListBindings(presets_pb2.ListBindingsRequest())
        self.assertEqual(list(bindings.bindings), [binding])
        await presets.UnbindAttr(
            presets_pb2.UnbindAttrRequest(preset_uid=1, attr_uid=1)
        )
        bindings = await presets.ListBindings(presets_pb2.ListBindingsRequest())
        self.assertEqual(len(bindings.bindings), 0)
        await presets.DeletePreset(presets_pb2.DeletePresetRequest(uid=1))
        listed = await presets.ListPresets(presets_pb2.ListPresetsRequest())
        self.assertEqual(len(listed.presets), 0)

    async def test_an_attr_not_bound_is_not_found(self) -> None:
        presets = (await self.connect()).auth_sessions_presets_temp
        await presets.CreatePreset(
            presets_pb2.CreatePresetRequest(preset=presets_pb2.Preset(uid=1, name="a"))
        )
        with self.assertRaises(GrpcError) as error:
            await presets.UnbindAttr(
                presets_pb2.UnbindAttrRequest(preset_uid=1, attr_uid=2)
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
        session_attrs = (await self.connect()).auth_sessions_attrs_temp
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
                uid=1, name="device", type=attr_type, source=source
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
            (AuthTagsUnit.Flags, profile_tags_pb2.Permission),
            (AuthAttrsUnit.Flags, profile_attrs_pb2.Permission),
            (AuthSessionAttrsUnit.Flags, session_attrs_pb2.Permission),
            (AuthSessionPresetsUnit.Flags, presets_pb2.Permission),
            (AuthMetadataUnit.Flags, metadata_pb2.Permission),
            (AuthGroupsUnit.Flags, groups_pb2.Permission),
            (AuthMembersUnit.Flags, members_pb2.Permission),
            (AuthNicknameMethod.Flags, nickname_pb2.Permission),
            (AuthEmailCodeMethod.Flags, email_code_pb2.Permission),
            (AuthSignUpUnit.Flags, sign_up_pb2.Permission),
            (AuthSignInUnit.Flags, sign_in_pb2.Permission),
            (AuthSessionsUnit.Flags, sessions_pb2.Permission),
            (AuthProfilesUnit.Flags, profiles_pb2.Permission),
            (AuthActivitiesUnit.Flags, activities_pb2.Permission),
        ):
            expected = {
                f"PERMISSION_{name}": item.value
                for name, item in flags.__members__.items()
            }
            values = dict(permission.items())
            del values["PERMISSION_UNSPECIFIED"]
            self.assertEqual(values, expected)

    async def test_a_public_export_holds_the_metadata_alone(self) -> None:
        exported = build_descriptor_set([AuthGrpcMetadataBinding.auth_metadata_temp])
        names = [file.name for file in exported.file]
        # of the auth the metadata alone, beside the annotations of HTTP it needs
        self.assertEqual(
            [name for name in names if name.startswith("ingot_auth/")],
            ["ingot_auth/api/metadata/v1/metadata.proto"],
        )
        self.assertIn("google/api/annotations.proto", names)

    async def test_an_attr_needs_a_type(self) -> None:
        attrs = (await self.connect()).auth_profiles_attrs_temp
        with self.assertRaises(GrpcError) as error:
            await attrs.CreateAttr(
                profile_attrs_pb2.CreateAttrRequest(
                    attr=profile_attrs_pb2.Attr(
                        uid=1,
                        name="phone",
                        type=profile_attrs_pb2.ATTR_TYPE_UNSPECIFIED,
                    )
                )
            )
        self.assertEqual(error.exception.code, grpc.StatusCode.INVALID_ARGUMENT)
        self.assertEqual(error.exception.reason, "ITEM_INVALID")

    async def test_the_errors_of_the_registries_have_their_statuses(self) -> None:
        tags = (await self.connect()).auth_profiles_tags_temp
        await tags.CreateTag(
            profile_tags_pb2.CreateTagRequest(
                tag=profile_tags_pb2.Tag(uid=1, name="beta")
            )
        )
        for call, code, reason, key in (
            (
                tags.CreateTag(
                    profile_tags_pb2.CreateTagRequest(
                        tag=profile_tags_pb2.Tag(uid=1, name="staff")
                    )
                ),
                grpc.StatusCode.ALREADY_EXISTS,
                "ITEM_CONFLICT",
                "1",
            ),
            (
                tags.CreateTag(
                    profile_tags_pb2.CreateTagRequest(
                        tag=profile_tags_pb2.Tag(uid=2, name="Staff")
                    )
                ),
                grpc.StatusCode.INVALID_ARGUMENT,
                "ITEM_INVALID",
                "Staff",
            ),
            (
                tags.DeleteTag(profile_tags_pb2.DeleteTagRequest(uid=3)),
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
            client.auth_profiles_tags_temp.ListTags(profile_tags_pb2.ListTagsRequest()),
            client.auth_profiles_tags_temp.CreateTag(
                profile_tags_pb2.CreateTagRequest(
                    tag=profile_tags_pb2.Tag(uid=1, name="beta")
                )
            ),
            client.auth_profiles_attrs_temp.ListAttrs(
                profile_attrs_pb2.ListAttrsRequest()
            ),
            client.auth_sessions_attrs_temp.ListAttrs(
                session_attrs_pb2.ListAttrsRequest()
            ),
            client.auth_sessions_presets_temp.ListBindings(
                presets_pb2.ListBindingsRequest()
            ),
            client.auth_access_groups_temp.ListGroups(groups_pb2.ListGroupsRequest()),
            client.auth_access_members_temp.ListMembers(
                members_pb2.ListMembersRequest(group="app.grp_admins")
            ),
        ):
            with self.assertRaises(GrpcError) as error:
                await call
            self.assertEqual(error.exception.code, grpc.StatusCode.PERMISSION_DENIED)
            self.assertEqual(error.exception.reason, "PERMISSION_DENIED")

    async def test_a_nickname_signs_up_and_in_by_its_service(self) -> None:
        nickname = (await self.connect(TstNicknameProject)).auth_methods_nickname_temp
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
            (caller.uid, caller.session_uid), (signed_up.uid, signed_in.session_uid)
        )

    async def test_a_caller_signs_out_by_its_service(self) -> None:
        client = await self.connect(TstNicknameProject)
        nickname = client.auth_methods_nickname_temp
        await nickname.SignUp(
            nickname_pb2.SignUpRequest(nickname="Alice", password="correct horse")
        )
        signed_in = (
            await nickname.SignIn(
                nickname_pb2.SignInRequest(nickname="alice", password="correct horse")
            )
        ).result.signed_in
        bearer = [("authorization", f"Bearer {signed_in.token}")]
        request = sign_out_pb2.SignOutRequest()
        await client.auth_sign_out_temp.SignOut(request, metadata=bearer)
        with self.assertRaises(AuthSessionNotFoundError):
            await self.project.auth.sessions.authenticate(signed_in.token)
        # a token closed, unknown or none signs out of nothing: a client retries
        for metadata in (bearer, [("authorization", "Bearer unknown")], []):
            with self.subTest(metadata=metadata):
                await client.auth_sign_out_temp.SignOut(request, metadata=metadata)

    async def test_a_user_lists_and_revokes_its_sessions_by_its_service(
        self,
    ) -> None:
        client = await self.connect(TstNicknameProject)
        nickname = client.auth_methods_nickname_temp
        await nickname.SignUp(
            nickname_pb2.SignUpRequest(nickname="Alice", password="correct horse")
        )
        sign_in = nickname_pb2.SignInRequest(nickname="alice", password="correct horse")
        phone, laptop = [
            (await nickname.SignIn(sign_in)).result.signed_in for _ in range(2)
        ]
        bearer = [("authorization", f"Bearer {laptop.token}")]
        sessions = client.auth_sessions_temp
        own = (
            await sessions.ListOwnSessions(
                sessions_pb2.ListOwnSessionsRequest(), metadata=bearer
            )
        ).sessions
        self.assertEqual(
            [(s.uid, s.is_current) for s in own],
            [(phone.session_uid, False), (laptop.session_uid, True)],
        )
        self.assertTrue(own[0].opened_at.seconds and own[0].seen_at.seconds)
        lost = sessions_pb2.RevokeOwnSessionRequest(session_uid=phone.session_uid)
        await sessions.RevokeOwnSession(lost, metadata=bearer)
        with self.assertRaises(GrpcError) as error:
            await sessions.RevokeOwnSession(lost, metadata=bearer)
        self.assertEqual(
            (error.exception.code, error.exception.reason, error.exception.metadata),
            (
                grpc.StatusCode.NOT_FOUND,
                "OWN_SESSION_NOT_FOUND",
                {"session_uid": phone.session_uid},
            ),
        )
        others = await sessions.RevokeOtherSessions(
            sessions_pb2.RevokeOtherSessionsRequest(), metadata=bearer
        )
        self.assertEqual(others.count, 0)

    async def test_an_operator_reads_the_record_of_a_profile(self) -> None:
        client = await self.connect(TstNicknameProject)
        nickname = client.auth_methods_nickname_temp
        uids, tokens = [], []
        for name in ("Alice", "Eve"):
            uids.append(
                (
                    await nickname.SignUp(
                        nickname_pb2.SignUpRequest(nickname=name, password="pass word")
                    )
                ).result.signed_up.uid
            )
            tokens.append(
                (
                    await nickname.SignIn(
                        nickname_pb2.SignInRequest(nickname=name, password="pass word")
                    )
                ).result.signed_in.token
            )
        alice, eve = uids
        await client.auth_sign_out_temp.SignOut(
            sign_out_pb2.SignOutRequest(),
            metadata=[("authorization", f"Bearer {tokens[0]}")],
        )
        await self.project.auth.storage.access.members.add(
            AuthMembership(group="auth.sessions.grp_admins", profile_uid=eve)
        )
        record = (
            await client.auth_sessions_temp.ListSessions(
                sessions_pb2.ListSessionsRequest(profile_uid=alice, closed=True),
                metadata=[("authorization", f"Bearer {tokens[1]}")],
            )
        ).sessions
        self.assertEqual(
            [(s.profile_uid, s.method, s.close_reason) for s in record],
            [(alice, "nickname", sessions_pb2.CLOSE_REASON_SIGNED_OUT)],
        )
        self.assertTrue(record[0].HasField("closed_at"))
        # an open one has no time, reason nor closer
        open_only = (
            await client.auth_sessions_temp.ListSessions(
                sessions_pb2.ListSessionsRequest(profile_uid=eve),
                metadata=[("authorization", f"Bearer {tokens[1]}")],
            )
        ).sessions
        self.assertEqual(
            [s.close_reason for s in open_only],
            [sessions_pb2.CLOSE_REASON_UNSPECIFIED],
        )
        self.assertFalse(open_only[0].HasField("closed_at"))

    async def test_an_operator_revokes_every_session_of_a_profile(self) -> None:
        client = await self.connect(TstNicknameProject)
        nickname = client.auth_methods_nickname_temp
        alice, eve = [
            (
                await nickname.SignUp(
                    nickname_pb2.SignUpRequest(nickname=name, password="pass word")
                )
            ).result.signed_up.uid
            for name in ("Alice", "Eve")
        ]
        tokens = []
        for name in ("Alice", "Alice", "Eve"):  # Alice on two devices
            tokens.append(
                (
                    await nickname.SignIn(
                        nickname_pb2.SignInRequest(nickname=name, password="pass word")
                    )
                ).result.signed_in.token
            )
        await self.project.auth.storage.access.members.add(
            AuthMembership(group="auth.sessions.grp_admins", profile_uid=eve)
        )
        revoked = await client.auth_sessions_temp.RevokeSessions(
            sessions_pb2.RevokeSessionsRequest(profile_uid=alice),
            metadata=[("authorization", f"Bearer {tokens[2]}")],
        )
        self.assertEqual(revoked.count, 2)
        with self.assertRaises(GrpcError) as raised:
            await client.auth_sessions_temp.ListOwnSessions(
                sessions_pb2.ListOwnSessionsRequest(),
                metadata=[("authorization", f"Bearer {tokens[0]}")],
            )
        self.assertEqual(raised.exception.code, grpc.StatusCode.UNAUTHENTICATED)

    async def test_an_operator_sweeps_the_expired_sessions(self) -> None:
        client = await self.connect(TstNicknameProject)
        nickname = client.auth_methods_nickname_temp
        _, eve = [
            (
                await nickname.SignUp(
                    nickname_pb2.SignUpRequest(nickname=name, password="pass word")
                )
            ).result.signed_up.uid
            for name in ("Alice", "Eve")
        ]
        await self.project.auth.storage.access.members.add(
            AuthMembership(group="auth.sessions.grp_admins", profile_uid=eve)
        )
        await nickname.SignIn(
            nickname_pb2.SignInRequest(nickname="Alice", password="pass word")
        )
        later = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=31)
        with mock.patch.object(AuthSessionsUnit, "_get_now", return_value=later):
            token = (
                await nickname.SignIn(
                    nickname_pb2.SignInRequest(nickname="Eve", password="pass word")
                )
            ).result.signed_in.token
            swept = await client.auth_sessions_temp.SweepSessions(
                sessions_pb2.SweepSessionsRequest(),
                metadata=[("authorization", f"Bearer {token}")],
            )
        self.assertEqual(swept.count, 1)

    async def test_an_operator_sets_the_values_of_a_profile(self) -> None:
        client = await self.connect(TstNicknameProject)
        nickname = client.auth_methods_nickname_temp
        uids, tokens = [], []
        for name in ("Alice", "Eve"):
            uids.append(
                (
                    await nickname.SignUp(
                        nickname_pb2.SignUpRequest(nickname=name, password="pass word")
                    )
                ).result.signed_up.uid
            )
            tokens.append(
                (
                    await nickname.SignIn(
                        nickname_pb2.SignInRequest(nickname=name, password="pass word")
                    )
                ).result.signed_in.token
            )
        storage = self.project.auth.storage
        await storage.profiles.tags.create(AuthTag(uid=1, name="beta"))
        await storage.profiles.attrs.create(
            AuthAttr(uid=1, name="first_name", type=AuthAttrType.STR)
        )
        await storage.access.members.add(
            AuthMembership(group="auth.profiles.grp_managers", profile_uid=uids[1])
        )
        bearer = [("authorization", f"Bearer {tokens[1]}")]
        profiles = client.auth_profiles_temp
        await profiles.SetProfileTags(
            profiles_pb2.SetProfileTagsRequest(uid=uids[0], tag_uids=[1]),
            metadata=bearer,
        )
        reply = await profiles.SetProfileAttrValues(
            profiles_pb2.SetProfileAttrValuesRequest(
                uid=uids[0],
                attr_values=[attrs_pb2.AttrValue(attr_uid=1, str_value="Alice")],
            ),
            metadata=bearer,
        )
        self.assertEqual(
            (list(reply.values.tag_uids), list(reply.values.attr_values)),
            ([1], [attrs_pb2.AttrValue(attr_uid=1, str_value="Alice")]),
        )
        with self.assertRaises(GrpcError) as error:
            await profiles.SetProfileTags(
                profiles_pb2.SetProfileTagsRequest(uid=uids[0], tag_uids=[9]),
                metadata=bearer,
            )
        self.assertEqual(
            (error.exception.code, error.exception.reason),
            (grpc.StatusCode.NOT_FOUND, "ITEM_NOT_FOUND"),
        )

    async def test_every_reply_tells_the_hash_of_the_profile(self) -> None:
        client = await self.connect(TstNicknameProject)
        nickname = client.auth_methods_nickname_temp
        signed_up = (
            await nickname.SignUp(
                nickname_pb2.SignUpRequest(nickname="Alice", password="pass word")
            )
        ).result.signed_up
        signed_in = (
            await nickname.SignIn(
                nickname_pb2.SignInRequest(nickname="alice", password="pass word")
            )
        ).result.signed_in
        bearer = [("authorization", f"Bearer {signed_in.token}")]
        call = client.auth_profiles_temp.GetOwnProfile(
            profiles_pb2.GetOwnProfileRequest(), metadata=bearer
        )
        profile = await call
        told = dict(await call.trailing_metadata())[PROFILE_HASH_KEY]
        self.assertEqual(told, profile.hash)
        self.assertEqual(dict(profile.permissions)["auth.profiles"], 2)
        await self.project.auth.storage.profiles.tags.create(
            AuthTag(uid=1, name="beta")
        )
        await self.run_as_root(
            self.project.auth.profiles.op_set_tags,
            AuthSetProfileTagsParameters(uid=signed_up.uid, tag_uids=frozenset({1})),
        )
        sessions_call = client.auth_sessions_temp.ListOwnSessions(
            sessions_pb2.ListOwnSessionsRequest(), metadata=bearer
        )
        await sessions_call
        changed = dict(await sessions_call.trailing_metadata())[PROFILE_HASH_KEY]
        self.assertNotEqual(changed, told)
        profile = await client.auth_profiles_temp.GetOwnProfile(
            profiles_pb2.GetOwnProfileRequest(), metadata=bearer
        )
        self.assertEqual((list(profile.values.tag_uids), profile.hash), ([1], changed))
        # the anonymous caller has no profile to tell
        metadata_call = client.auth_metadata_temp.GetMetadata(
            metadata_pb2.GetMetadataRequest()
        )
        await metadata_call
        self.assertNotIn(
            PROFILE_HASH_KEY, dict(await metadata_call.trailing_metadata())
        )

    async def run_as_root(self, factory: t.Any, parameters: t.Any) -> t.Any:
        operations = self.project.operations
        metadata = operations.create_metadata(ROOT)
        return await operations.runner.run(factory, parameters, metadata)

    async def test_the_auditors_read_the_log(self) -> None:
        client = await self.connect(TstNicknameProject)
        nickname = client.auth_methods_nickname_temp
        signed_up = (
            await nickname.SignUp(
                nickname_pb2.SignUpRequest(nickname="Eve", password="pass word")
            )
        ).result.signed_up
        signed_in = (
            await nickname.SignIn(
                nickname_pb2.SignInRequest(nickname="eve", password="pass word")
            )
        ).result.signed_in
        storage = self.project.auth.storage
        await storage.access.members.add(
            AuthMembership(
                group="auth.activities.grp_auditors", profile_uid=signed_up.uid
            )
        )
        context = {"price": decimal.Decimal("1.50"), "at": NOW, "ids": [1], "m": {}}
        await storage.activities.append(create_record(context=context, when=NOW))
        await storage.activities.append(
            create_record(session_uid="s1", entity_uid="2", when=NOW + HOUR)
        )
        bearer = [("authorization", f"Bearer {signed_in.token}")]
        request = activities_pb2.ListActivitiesRequest(
            entity_type="auth.profiles.tags",
            entity_uid="1",
            who="root",
            action=activities_pb2.ACTION_CREATE,
        )
        request.since.FromDatetime(NOW)
        request.until.FromDatetime(NOW + HOUR)
        (activity,) = (
            await client.auth_activities_temp.ListActivities(request, metadata=bearer)
        ).activities
        self.assertEqual(
            (activity.who, activity.session_uid, activity.action, activity.run_uid),
            ("root", "", activities_pb2.ACTION_CREATE, "r1"),
        )
        self.assertEqual(
            dict(activity.context),
            {"price": "1.50", "at": NOW.isoformat(), "ids": [1.0], "m": {}},
        )
        everything = await client.auth_activities_temp.ListActivities(
            activities_pb2.ListActivitiesRequest(session_uid="s1"), metadata=bearer
        )
        self.assertEqual([a.entity_uid for a in everything.activities], ["2"])

    async def test_every_action_has_its_message(self) -> None:
        self.assertEqual(set(ACTIONS), set(AuthActivityAction))

    async def test_every_close_reason_has_its_message(self) -> None:
        self.assertEqual(set(CLOSE_REASONS), set(AuthSessionCloseReason))

    async def test_every_value_of_an_attr_has_its_message(self) -> None:
        for value in (
            True,
            7,
            decimal.Decimal("1.50"),
            datetime.datetime(2026, 11, 15, tzinfo=datetime.UTC),
            "iPhone",
        ):
            with self.subTest(value=value):
                message = build_attr_value_message(1, value)
                self.assertEqual(build_attr_value(message, "sessions.attrs"), value)
                self.assertIs(
                    type(build_attr_value(message, "sessions.attrs")), type(value)
                )

    async def test_the_values_of_the_attributes_go_with_the_flows(self) -> None:
        nickname = (await self.connect(TstNicknameProject)).auth_methods_nickname_temp
        attrs = self.project.auth.storage.sessions.attrs
        for attr_uid, attr_type in enumerate(AuthAttrType, start=1):
            await attrs.create(
                AuthSessionAttr(
                    uid=attr_uid,
                    name=attr_type.value,
                    type=attr_type,
                    source=AuthSessionAttrSource.CLIENT,
                )
            )
        moment = datetime.datetime(2026, 11, 11, 12, 30, tzinfo=datetime.UTC)
        timestamp = Timestamp()
        timestamp.FromDatetime(moment)
        attr_values = [
            attrs_pb2.AttrValue(attr_uid=1, bool_value=True),
            attrs_pb2.AttrValue(attr_uid=2, int_value=7),
            attrs_pb2.AttrValue(attr_uid=3, decimal_value="1.50"),
            attrs_pb2.AttrValue(attr_uid=4, datetime_value=timestamp),
            attrs_pb2.AttrValue(attr_uid=5, str_value="iPhone"),
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
                uid=1,
                name="ip",
                type=AuthAttrType.STR,
                source=AuthSessionAttrSource.TRANSPORT,
            )
        )

    async def test_the_ip_of_the_peer_goes_with_the_flows(self) -> None:
        nickname = (await self.connect(TstNicknameProject)).auth_methods_nickname_temp
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
        nickname = (await self.connect(TstForwardedProject)).auth_methods_nickname_temp
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
        nickname = (await self.connect(TstNicknameProject)).auth_methods_nickname_temp
        await nickname.SignUp(
            nickname_pb2.SignUpRequest(nickname="alice", password="x")
        )
        no_value = attrs_pb2.AttrValue(attr_uid=1)
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
        mailer = t.cast(MemoryMailer, self.project.mail.mailer)
        text = mailer.get_sent()[-1].text
        match = re.match(r"Your code is (\d+)\.", text)
        assert match is not None
        return match[1]

    async def test_an_email_signs_up_and_in_by_its_code(self) -> None:
        client = await self.connect(TstEmailCodeProject)
        email_code = client.auth_methods_email_code_temp
        challenge = (
            await email_code.StartSignUp(
                email_code_pb2.StartSignUpRequest(email="al@b.c")
            )
        ).result.challenge
        self.assertEqual(challenge.code, challenges_pb2.CodeChallenge(length=6))
        answer = sign_up_pb2.AnswerSignUpRequest(
            attempt_uid=challenge.attempt_uid, code=await self.get_code()
        )
        signed_up = (
            await client.auth_sign_up_temp.AnswerSignUp(answer)
        ).result.signed_up
        challenge = (
            await email_code.StartSignIn(
                email_code_pb2.StartSignInRequest(email="AL@b.c")
            )
        ).result.challenge
        answer_in = sign_in_pb2.AnswerSignInRequest(
            attempt_uid=challenge.attempt_uid, code=await self.get_code()
        )
        signed_in = (
            await client.auth_sign_in_temp.AnswerSignIn(answer_in)
        ).result.signed_in
        caller = await self.project.auth.sessions.authenticate(signed_in.token)
        self.assertEqual(
            (caller.uid, caller.session_uid), (signed_up.uid, signed_in.session_uid)
        )

    async def test_the_answers_tell_their_errors(self) -> None:
        client = await self.connect(TstEmailCodeProject)
        start = email_code_pb2.StartSignUpRequest(email="al@b.c")
        challenge = (
            await client.auth_methods_email_code_temp.StartSignUp(start)
        ).result.challenge
        code = await self.get_code()
        wrong = f"{(int(code) + 1) % 10**6:06d}"
        # a call starts once made: made in turn, so that the answer of another
        # flow, taking the attempt, comes last
        for call, code_of_status, reason in (
            (
                lambda: client.auth_sign_up_temp.AnswerSignUp(
                    sign_up_pb2.AnswerSignUpRequest(
                        attempt_uid=challenge.attempt_uid, code=wrong
                    )
                ),
                grpc.StatusCode.UNAUTHENTICATED,
                "METHOD_REFUSED",
            ),
            (
                lambda: client.auth_sign_up_temp.AnswerSignUp(
                    sign_up_pb2.AnswerSignUpRequest(attempt_uid="gone", code=code)
                ),
                grpc.StatusCode.NOT_FOUND,
                "ATTEMPT_NOT_FOUND",
            ),
            (
                # an attempt of another flow
                lambda: client.auth_sign_in_temp.AnswerSignIn(
                    sign_in_pb2.AnswerSignInRequest(
                        attempt_uid=challenge.attempt_uid, code=code
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
        nickname = (
            await self.connect(TstNicknameProject, AUTH_SIGN_UP_NICKNAME_ENABLED="off")
        ).auth_methods_nickname_temp
        with self.assertRaises(GrpcError) as error:
            await nickname.SignUp(
                nickname_pb2.SignUpRequest(nickname="a", password="x")
            )
        self.assertEqual(error.exception.code, grpc.StatusCode.PERMISSION_DENIED)

    async def test_the_sign_up_its_toggle_closes_is_refused_the_sign_in_not(
        self,
    ) -> None:
        nickname = (
            await self.connect(TstNicknameProject, AUTH_SIGN_UP_ENABLED="off")
        ).auth_methods_nickname_temp
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
        nickname = client.auth_methods_nickname_temp
        sign_in = nickname_pb2.SignInRequest(nickname="alice", password="x")
        signed_up = (
            await nickname.SignUp(
                nickname_pb2.SignUpRequest(nickname="alice", password="x")
            )
        ).result.signed_up
        await self.project.auth.storage.access.members.add(
            AuthMembership(group="app.grp_admins", profile_uid=signed_up.uid)
        )
        token = (await nickname.SignIn(sign_in)).result.signed_in.token
        bearer = [("authorization", f"Bearer {token}")]
        members = client.auth_access_members_temp
        request = members_pb2.ListMembersRequest(group="app.grp_admins")
        reply = await members.ListMembers(request, metadata=bearer)
        self.assertEqual(list(reply.profile_uids), [signed_up.uid])
        # open to anyone, signed in or not
        await client.auth_metadata_temp.GetMetadata(
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
            (
                errors.auth_sessions_limit,
                AuthSessionsLimitError.for_count(3),
                grpc.StatusCode.RESOURCE_EXHAUSTED,
                "SESSIONS_LIMIT",
                {"count": "3"},
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
            [attrs_pb2.AttrValue(attr_uid=1)],
            [attrs_pb2.AttrValue(attr_uid=1, decimal_value="1,50")],
            [attrs_pb2.AttrValue(attr_uid=1, decimal_value="NaN")],
            [
                attrs_pb2.AttrValue(attr_uid=1, int_value=1),
                attrs_pb2.AttrValue(attr_uid=1, int_value=2),
            ],
        ):
            with self.subTest(attr_values=attr_values):
                with self.assertRaises(AuthItemInvalidError) as error:
                    build_attr_values(attr_values, "sessions.attrs")
                self.assertEqual(error.exception.key, 1)


class ChallengesTestCase(unittest.TestCase):
    def test_a_challenge_with_no_message_is_refused(self) -> None:
        with self.assertRaises(TypeError) as error:
            build_challenge("x", "a code")
        self.assertEqual(str(error.exception), "no message of a challenge str")
