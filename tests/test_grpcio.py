import os
import socket
import typing as t
import unittest
from unittest import mock

import grpc
from grpc import aio
from ingot_grpcio import GrpcProject
from ingot_grpcio.grpc import GrpcUnit
from ingot_grpcio.grpc.clients import DefaultGrpcClient, GrpcClients
from ingot_grpcio.grpc.errors import GrpcError
from ingot_grpcio.grpc.servers import DefaultGrpcServer, GrpcServers
from ingot_grpcio.grpc.services import GrpcService
from ingot_grpcio.grpc.services.export import build_descriptor_set
from ingot_grpcio.logging import GrpcLogging
from ingot_grpcio.settings import GrpcSettings
from ingot_grpcio.settings.configs import GrpcConfigs
from ingots.defaults.operations import ANONYMOUS_CALLER, Caller, Permissions
from ingots.puer import Slot

from ingot_auth import AuthProject
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.contrib.transports.grpcio import (
    AuthGrpcAdminBinding,
    AuthGrpcAttrsServicer,
    AuthGrpcErrors,
    AuthGrpcMetadataBinding,
    AuthGrpcMetadataServicer,
    AuthGrpcSessionAttrsServicer,
    AuthGrpcTagsServicer,
)
from ingot_auth.contrib.transports.grpcio.proto.ingot_auth.metadata.v1 import (
    metadata_pb2,
    metadata_pb2_grpc,
)
from ingot_auth.contrib.transports.grpcio.proto.ingot_auth.profile.attrs.v1 import (
    attrs_pb2 as profile_attrs_pb2,
)
from ingot_auth.contrib.transports.grpcio.proto.ingot_auth.profile.attrs.v1 import (
    attrs_pb2_grpc as profile_attrs_pb2_grpc,
)
from ingot_auth.contrib.transports.grpcio.proto.ingot_auth.profile.tags.v1 import (
    tags_pb2 as profile_tags_pb2,
)
from ingot_auth.contrib.transports.grpcio.proto.ingot_auth.profile.tags.v1 import (
    tags_pb2_grpc as profile_tags_pb2_grpc,
)
from ingot_auth.contrib.transports.grpcio.proto.ingot_auth.session.attrs.v1 import (
    attrs_pb2 as session_attrs_pb2,
)
from ingot_auth.contrib.transports.grpcio.proto.ingot_auth.session.attrs.v1 import (
    attrs_pb2_grpc as session_attrs_pb2_grpc,
)
from ingot_auth.logging import AuthLogging
from ingot_auth.metadata import AuthMetadataPermissions
from ingot_auth.profile.attrs import AuthAttrsPermissions
from ingot_auth.profile.tags import AuthTagsPermissions
from ingot_auth.registry import AuthAttrType
from ingot_auth.session.attrs import AuthSessionAttrSource, AuthSessionAttrsPermissions
from ingot_auth.settings import AuthSettings
from ingot_auth.settings.configs import AuthConfigs

ADMIN: t.Final = Caller(
    uid="admin",
    permissions=Permissions(
        *AuthTagsPermissions, *AuthAttrsPermissions, *AuthSessionAttrsPermissions
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


class TstAdminBinding:
    auth_profile_tags = GrpcService(profile_tags_pb2_grpc.TagsStub, TagsServicer)
    auth_profile_attrs = GrpcService(profile_attrs_pb2_grpc.AttrsStub, AttrsServicer)
    auth_session_attrs = GrpcService(
        session_attrs_pb2_grpc.AttrsStub, SessionAttrsServicer
    )


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


class TstSettings(AuthSettings, GrpcSettings):
    configs = Slot(TstConfigs)


class TstLogging(AuthLogging, GrpcLogging):
    project: "TstProject"


class TstAuth(AuthUnit):
    storage = Slot(AuthMemoryStorage)


class TstClients(GrpcClients):
    default = Slot(TstClient)


class TstServers(GrpcServers):
    default = Slot(TstServer)


class TstAnonymousServers(GrpcServers):
    default = Slot(TstAnonymousServer)


class TstClosedServers(GrpcServers):
    default = Slot(TstClosedServer)


class TstGrpc(GrpcUnit):
    errors = Slot(AuthGrpcErrors)
    clients = Slot(TstClients)


class TstAdminGrpc(TstGrpc):
    servers = Slot(TstServers)


class TstAnonymousGrpc(TstGrpc):
    servers = Slot(TstAnonymousServers)


class TstClosedGrpc(TstGrpc):
    servers = Slot(TstClosedServers)


class TstProject(AuthProject, GrpcProject):
    settings = Slot(TstSettings)
    logging = Slot(TstLogging)
    auth = Slot(TstAuth)
    grpc = Slot(TstGrpc)


class TstAdminProject(TstProject):
    grpc = Slot(TstAdminGrpc)


class TstAnonymousProject(TstProject):
    grpc = Slot(TstAnonymousGrpc)


class TstClosedProject(TstProject):
    grpc = Slot(TstClosedGrpc)


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
        project = project_cls()
        await project._configure()
        self.addAsyncCleanup(project._do_shut_down)
        await project.grpc.servers.default
        return await project.grpc.clients.default

    async def test_the_metadata_is_public_by_default(self) -> None:
        client = await self.connect(TstAnonymousProject)
        reply = await client.auth_metadata.Get(metadata_pb2.GetMetadataRequest())
        self.assertEqual((list(reply.tags), list(reply.attrs)), ([], []))

    async def test_a_servicer_may_close_the_metadata(self) -> None:
        client = await self.connect(TstClosedProject)
        with self.assertRaises(GrpcError) as error:
            await client.auth_metadata.Get(metadata_pb2.GetMetadataRequest())
        self.assertEqual(error.exception.code, grpc.StatusCode.PERMISSION_DENIED)

    async def test_the_metadata_gives_the_registries(self) -> None:
        client = await self.connect()
        await client.auth_profile_tags.Create(
            profile_tags_pb2.CreateTagRequest(
                tag=profile_tags_pb2.Tag(id=1, name="beta")
            )
        )
        await client.auth_profile_attrs.Create(
            profile_attrs_pb2.CreateAttrRequest(
                attr=profile_attrs_pb2.Attr(
                    id=7, name="title/en", type=profile_attrs_pb2.ATTR_TYPE_STR
                )
            )
        )
        reply = await client.auth_metadata.Get(metadata_pb2.GetMetadataRequest())
        self.assertEqual(list(reply.tags), [metadata_pb2.Tag(id=1, name="beta")])
        self.assertEqual(
            list(reply.attrs),
            [metadata_pb2.Attr(id=7, name="title/en", type=metadata_pb2.ATTR_TYPE_STR)],
        )

    async def test_the_tags_are_managed(self) -> None:
        tags = (await self.connect()).auth_profile_tags
        beta = profile_tags_pb2.Tag(id=1, name="beta")
        self.assertEqual(
            (await tags.Create(profile_tags_pb2.CreateTagRequest(tag=beta))).tag, beta
        )
        preview = profile_tags_pb2.Tag(id=1, name="preview")
        self.assertEqual(
            (
                await tags.Rename(
                    profile_tags_pb2.RenameTagRequest(id=1, name="preview")
                )
            ).tag,
            preview,
        )
        reply = await tags.List(profile_tags_pb2.ListTagsRequest())
        self.assertEqual(list(reply.tags), [preview])
        await tags.Delete(profile_tags_pb2.DeleteTagRequest(id=1))
        self.assertEqual(
            len((await tags.List(profile_tags_pb2.ListTagsRequest())).tags), 0
        )

    async def test_the_attrs_are_managed(self) -> None:
        attrs = (await self.connect()).auth_profile_attrs
        attr = profile_attrs_pb2.Attr(
            id=1, name="phone", type=profile_attrs_pb2.ATTR_TYPE_STR
        )
        self.assertEqual(
            (await attrs.Create(profile_attrs_pb2.CreateAttrRequest(attr=attr))).attr,
            attr,
        )
        renamed = profile_attrs_pb2.Attr(
            id=1, name="mobile", type=profile_attrs_pb2.ATTR_TYPE_STR
        )
        self.assertEqual(
            (
                await attrs.Rename(
                    profile_attrs_pb2.RenameAttrRequest(id=1, name="mobile")
                )
            ).attr,
            renamed,
        )
        reply = await attrs.List(profile_attrs_pb2.ListAttrsRequest())
        self.assertEqual(list(reply.attrs), [renamed])
        await attrs.Delete(profile_attrs_pb2.DeleteAttrRequest(id=1))
        self.assertEqual(
            len((await attrs.List(profile_attrs_pb2.ListAttrsRequest())).attrs), 0
        )

    async def test_the_session_attrs_are_managed(self) -> None:
        session_attrs = (await self.connect()).auth_session_attrs
        ip = session_attrs_pb2.Attr(
            id=1,
            name="ip",
            type=session_attrs_pb2.ATTR_TYPE_STR,
            source=session_attrs_pb2.ATTR_SOURCE_TRANSPORT,
        )
        created = await session_attrs.Create(
            session_attrs_pb2.CreateAttrRequest(attr=ip)
        )
        self.assertEqual(created.attr, ip)
        renamed = session_attrs_pb2.Attr()
        renamed.CopyFrom(ip)
        renamed.name = "peer/ip"
        reply = await session_attrs.Rename(
            session_attrs_pb2.RenameAttrRequest(id=1, name="peer/ip")
        )
        self.assertEqual(reply.attr, renamed)
        listed = await session_attrs.List(session_attrs_pb2.ListAttrsRequest())
        self.assertEqual(list(listed.attrs), [renamed])
        await session_attrs.Delete(session_attrs_pb2.DeleteAttrRequest(id=1))
        listed = await session_attrs.List(session_attrs_pb2.ListAttrsRequest())
        self.assertEqual(len(listed.attrs), 0)

    async def test_every_source_of_the_session_attrs_has_a_message(self) -> None:
        expected = {f"ATTR_SOURCE_{item.name}" for item in AuthSessionAttrSource}
        names = set(session_attrs_pb2.AttrSource.keys())
        self.assertEqual(expected, names - {"ATTR_SOURCE_UNSPECIFIED"})

    async def test_a_session_attr_needs_a_type_and_a_source(self) -> None:
        session_attrs = (await self.connect()).auth_session_attrs
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
                await session_attrs.Create(
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
                    {"registry": "session.attrs", "key": key},
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
            (AuthMetadataPermissions, metadata_pb2.Permission),
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
        attrs = (await self.connect()).auth_profile_attrs
        with self.assertRaises(GrpcError) as error:
            await attrs.Create(
                profile_attrs_pb2.CreateAttrRequest(
                    attr=profile_attrs_pb2.Attr(
                        id=1, name="phone", type=profile_attrs_pb2.ATTR_TYPE_UNSPECIFIED
                    )
                )
            )
        self.assertEqual(error.exception.code, grpc.StatusCode.INVALID_ARGUMENT)
        self.assertEqual(error.exception.reason, "ITEM_INVALID")

    async def test_the_errors_of_the_registries_have_their_statuses(self) -> None:
        tags = (await self.connect()).auth_profile_tags
        await tags.Create(
            profile_tags_pb2.CreateTagRequest(
                tag=profile_tags_pb2.Tag(id=1, name="beta")
            )
        )
        for call, code, reason, key in (
            (
                tags.Create(
                    profile_tags_pb2.CreateTagRequest(
                        tag=profile_tags_pb2.Tag(id=1, name="staff")
                    )
                ),
                grpc.StatusCode.ALREADY_EXISTS,
                "ITEM_CONFLICT",
                "1",
            ),
            (
                tags.Create(
                    profile_tags_pb2.CreateTagRequest(
                        tag=profile_tags_pb2.Tag(id=2, name="Staff")
                    )
                ),
                grpc.StatusCode.INVALID_ARGUMENT,
                "ITEM_INVALID",
                "Staff",
            ),
            (
                tags.Delete(profile_tags_pb2.DeleteTagRequest(id=3)),
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
                (code, "ingot-auth", reason, {"registry": "profile.tags", "key": key}),
            )

    async def test_the_administration_refuses_who_it_cannot_tell(self) -> None:
        client = await self.connect(TstAnonymousProject)
        for call in (
            client.auth_profile_tags.List(profile_tags_pb2.ListTagsRequest()),
            client.auth_profile_tags.Create(
                profile_tags_pb2.CreateTagRequest(
                    tag=profile_tags_pb2.Tag(id=1, name="beta")
                )
            ),
            client.auth_profile_attrs.List(profile_attrs_pb2.ListAttrsRequest()),
            client.auth_session_attrs.List(session_attrs_pb2.ListAttrsRequest()),
        ):
            with self.assertRaises(GrpcError) as error:
                await call
            self.assertEqual(error.exception.code, grpc.StatusCode.PERMISSION_DENIED)
            self.assertEqual(error.exception.reason, "PERMISSION_DENIED")
