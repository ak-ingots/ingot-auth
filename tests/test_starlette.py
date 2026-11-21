"""The auth over HTTP: the RPCs of the contract, transcoded to JSON."""

import subprocess
import sys
import typing as t
import unittest

from google.rpc import code_pb2
from ingot_starlette import StarletteProject
from ingot_starlette.contrib.protobuf import get_http_status
from ingot_starlette.logging import StarletteLoggingUnit
from ingot_starlette.runner import StarletteRunner
from ingot_starlette.settings import StarletteSettingsUnit
from ingot_starlette.settings.configs import StarletteConfigs
from ingot_starlette.starlette import StarletteApiUnit, StarletteEndpoint, StarletteUnit
from ingots.puer import Slot, Unit
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.routing import Mount
from starlette.testclient import TestClient, WebSocketDenialResponse

from ingot_auth import AuthProject
from ingot_auth.__main__ import AuthMemorySessionsUnit, AuthMemorySignInUnit
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.caches.memory import AuthMemoryCache
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.contrib.transports.contract import PROFILE_HASH_KEY
from ingot_auth.contrib.transports.grpcio import AuthGrpcErrorsUnit
from ingot_auth.contrib.transports.grpcio.errors import BaseAuthGrpcErrorPolicy
from ingot_auth.contrib.transports.starlette import (
    AuthStarletteErrorsUnit,
    AuthStarletteMetadataEndpoint,
    AuthStarletteNicknameEndpoint,
    AuthStarletteProfileHashMiddleware,
    AuthStarletteSignOutEndpoint,
    BaseAuthStarletteErrorPolicy,
)
from ingot_auth.logging import AuthLoggingUnit
from ingot_auth.methods import AuthMethodsUnit
from ingot_auth.methods.nickname import AuthNicknameConfigs, AuthNicknameMethod
from ingot_auth.methods.password import AuthPassword, AuthScryptPasswordHasher
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.settings.configs import AuthConfigs

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from starlette.routing import BaseRoute

PASSWORD: t.Final = "a passphrase long enough"
PROBLEM: t.Final = "application/problem+json"


class TstConfigs(AuthNicknameConfigs, AuthConfigs, StarletteConfigs):
    pass


class TstSettingsUnit(AuthSettingsUnit, StarletteSettingsUnit):
    configs = Slot(TstConfigs)


class TstLoggingUnit(AuthLoggingUnit, StarletteLoggingUnit):
    project: "TstProject"


class CheapHasher(AuthScryptPasswordHasher):
    SCRYPT_LOG_N = 4


class CheapPassword(AuthPassword):
    hasher_default = Slot(CheapHasher)


class TstMethodsUnit(AuthMethodsUnit):
    nickname = Slot(AuthNicknameMethod)
    password = Slot(CheapPassword)


class TstAuthUnit(AuthUnit):
    storage = Slot(AuthMemoryStorage)
    cache = Slot(AuthMemoryCache)
    sessions = Slot(AuthMemorySessionsUnit)
    sign_in = Slot(AuthMemorySignInUnit)
    methods = Slot(TstMethodsUnit)


class TstAuthEndpoint(StarletteEndpoint, Unit):
    metadata = Slot(AuthStarletteMetadataEndpoint)
    nickname = Slot(AuthStarletteNicknameEndpoint)
    sign_out = Slot(AuthStarletteSignOutEndpoint)

    @t.override
    def _iter_routes(self) -> "Iterator[BaseRoute]":
        yield from self.metadata.get_routes()
        yield from self.nickname.get_routes()
        yield from self.sign_out.get_routes()


class TstApiUnit(StarletteApiUnit):
    auth = Slot(TstAuthEndpoint)

    @t.override
    def _iter_routes(self) -> "Iterator[BaseRoute]":
        yield Mount("/auth", routes=self.auth.get_routes())

    @t.override
    def _iter_middleware(self) -> "Iterator[Middleware]":
        yield Middleware(AuthStarletteProfileHashMiddleware)


class TstStarletteUnit(StarletteUnit):
    errors = Slot(AuthStarletteErrorsUnit)
    api = Slot(TstApiUnit)


class TstProject(AuthProject, StarletteProject):
    settings = Slot(TstSettingsUnit)
    logging = Slot(TstLoggingUnit)
    auth = Slot(TstAuthUnit)
    starlette = Slot(TstStarletteUnit)


class StarletteTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.runner = StarletteRunner(TstProject)
        self.client = self.enterContext(TestClient(self.runner))

    def post(self, path: str, body: object, token: str | None = None) -> t.Any:
        headers = {"authorization": f"Bearer {token}"} if token else {}
        return self.client.post(f"/api/auth/v1/{path}", json=body, headers=headers)

    def sign_up_and_in(self, nickname: str = "al") -> str:
        credentials = {"nickname": nickname, "password": PASSWORD}
        signed_up = self.post("methods/nickname:signUp", credentials)
        self.assertEqual(signed_up.status_code, 200, signed_up.text)
        self.assertIn("uid", signed_up.json()["result"]["signed_up"])
        signed_in = self.post("methods/nickname:signIn", credentials)
        self.assertEqual(signed_in.status_code, 200, signed_in.text)
        token: str = signed_in.json()["result"]["signed_in"]["token"]
        return token

    def test_the_metadata_is_open_to_anyone(self) -> None:
        for headers in ({}, {"authorization": "Bearer unknown"}):
            with self.subTest(headers=headers):
                response = self.client.get("/api/auth/v1/metadata", headers=headers)
                self.assertEqual(response.status_code, 200)
                methods = response.json()["methods"]
                self.assertIn(
                    {"name": "nickname", "sign_up": True, "sign_in": True}, methods
                )
                self.assertNotIn(PROFILE_HASH_KEY, response.headers)

    def test_a_user_signs_up_in_and_out(self) -> None:
        token = self.sign_up_and_in()
        signed_out = self.post("session:signOut", {}, token)
        self.assertEqual((signed_out.status_code, signed_out.json()), (200, {}))
        self.assertTrue(signed_out.headers[PROFILE_HASH_KEY])
        # the token works no more: a sign-out again signs out of nothing
        again = self.post("session:signOut", {}, token)
        self.assertEqual(again.status_code, 200)
        self.assertNotIn(PROFILE_HASH_KEY, again.headers)

    def test_a_wrong_password_is_refused(self) -> None:
        self.sign_up_and_in()
        response = self.post(
            "methods/nickname:signIn", {"nickname": "al", "password": "wrong one!"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers["content-type"], PROBLEM)
        problem = response.json()
        self.assertEqual(
            (problem["domain"], problem["reason"], problem["metadata"]),
            ("ingot-auth", "METHOD_REFUSED", {}),
        )

    def test_a_nickname_taken_is_a_conflict(self) -> None:
        self.sign_up_and_in()
        response = self.post(
            "methods/nickname:signUp", {"nickname": "al", "password": PASSWORD}
        )
        self.assertEqual(response.status_code, 409)
        problem = response.json()
        self.assertEqual(problem["reason"], "IDENTITY_CONFLICT")
        self.assertEqual(problem["metadata"], {"kind": "nickname"})

    def test_a_request_not_of_its_message_is_bad(self) -> None:
        response = self.post("methods/nickname:signIn", {"nick": "al"})
        self.assertEqual(response.status_code, 400)

    def test_a_websocket_passes_the_middleware_to_the_refusal_of_the_api(self) -> None:
        with self.assertRaises(WebSocketDenialResponse) as caught:
            with self.client.websocket_connect("/api/auth/v1/metadata"):
                pass  # pragma: no cover
        self.assertEqual(caught.exception.status_code, 404)

    def test_the_ip_is_an_attribute_of_the_transport(self) -> None:
        project = t.cast(TstProject, self.runner.project)
        endpoint = project.starlette.api.auth.nickname
        scope = {"type": "http", "headers": [], "client": ("10.0.0.1", 5000)}
        self.assertEqual(
            endpoint.get_transport_attr_values(Request(scope)), {"ip": "10.0.0.1"}
        )
        no_client: dict[str, t.Any] = {"type": "http", "headers": [], "client": None}
        self.assertEqual(endpoint.get_transport_attr_values(Request(no_client)), {})


class ErrorsTestCase(unittest.TestCase):
    def test_both_transports_tell_the_same_statuses(self) -> None:
        grpc = dict(AuthGrpcErrorsUnit.slots_iter())
        http = dict(AuthStarletteErrorsUnit.slots_iter())
        names = [name for name in grpc if name.startswith("auth_")]
        self.assertEqual(names, [name for name in http if name.startswith("auth_")])
        for name in names:
            with self.subTest(name=name):
                grpc_policy, http_policy = grpc[name].cls, http[name].cls
                self.assertIs(grpc_policy.EXCEPTION, http_policy.EXCEPTION)
                self.assertEqual(grpc_policy.REASON, http_policy.REASON)
                self.assertEqual(
                    get_http_status(grpc_policy.CODE.value[0]), http_policy.STATUS
                )
        self.assertEqual(
            http["auth_sessions_limit"].cls.STATUS,
            get_http_status(code_pb2.RESOURCE_EXHAUSTED),
        )

    def test_a_base_of_no_code_takes_none(self) -> None:
        class AppGrpcErrorPolicy(BaseAuthGrpcErrorPolicy):
            pass

        class AppStarletteErrorPolicy(BaseAuthStarletteErrorPolicy):
            pass

        self.assertFalse(hasattr(AppGrpcErrorPolicy, "CODE"))
        self.assertFalse(hasattr(AppStarletteErrorPolicy, "STATUS"))

    def test_it_needs_no_grpcio(self) -> None:
        code = (
            "import sys, ingot_auth.contrib.transports.starlette; "
            "print(sorted({'grpc', 'ingot_grpcio'} & set(sys.modules)))"
        )
        done = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=True
        )
        self.assertEqual(done.stdout.strip(), "[]")
