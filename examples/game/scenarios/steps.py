"""The steps of the scenarios, shared: functions and a mixin, called by name."""

import asyncio
import json
import re
import time
import typing as t
import urllib.parse
import urllib.request
import uuid

import grpc
from ingot_grpcio.grpc.errors import GrpcError
from ingots.testing import ProjectFixture, ProjectTestCase

from ingot_auth.contrib.transports.grpcio.base import PROFILE_HASH_KEY
from ingot_auth.metadata.v1 import metadata_pb2
from ingot_auth.methods.email_code.v1 import email_code_pb2
from ingot_auth.methods.nickname.v1 import nickname_pb2
from ingot_auth.profiles.v1 import profiles_pb2
from ingot_auth.sessions.v1 import sessions_pb2
from ingot_auth.sign_in.v1 import sign_in_pb2
from ingot_auth.sign_out.v1 import sign_out_pb2
from ingot_auth.sign_up.v1 import sign_up_pb2

from .project import ScenariosProject

# the mail of a code goes in the background: how long a scenario waits for it
MAIL_TIMEOUT = 10.0

# the password of every player of a scenario: its strength is not under test
PASSWORD = "s3cret-password"

Metadata: t.TypeAlias = list[tuple[str, str]]

if t.TYPE_CHECKING:
    TestCase: t.TypeAlias = ProjectTestCase
else:
    TestCase = object


def new_nickname() -> str:
    """A nickname no scenario took, the game kept running between them."""
    return f"player-{uuid.uuid4().hex[:12]}"


def new_email() -> str:
    """An email no scenario took."""
    return f"player-{uuid.uuid4().hex[:12]}@example.com"


def bear(token: str) -> Metadata:
    return [("authorization", f"Bearer {token}")]


async def read_profile_hash(call: t.Any) -> str:
    """The hash of the profile of the caller a reply tells, trailing it."""
    for key, value in await call.trailing_metadata() or ():
        if key == PROFILE_HASH_KEY:
            return str(value)
    raise AssertionError("no hash of the profile")


class Mailpit:
    """The mailbox of every player, read by the API of Mailpit."""

    def __init__(self, port: int) -> None:
        self.url = f"http://127.0.0.1:{port}/api/v1"

    async def read_code(self, email: str) -> str:
        """
        The code of the mail to the email, waited for, and the mail deleted:
        the next code read is of the next mail.
        """
        text = await asyncio.to_thread(self._wait_text, email)
        found = re.search(r"Your code is (\d+)\.", text)
        assert found, text
        return found.group(1)

    def _wait_text(self, email: str) -> str:
        query = urllib.parse.urlencode({"query": f'to:"{email}"', "limit": 1})
        deadline = time.monotonic() + MAIL_TIMEOUT
        while True:
            messages = self._get(f"/search?{query}")["messages"]
            if messages:
                uid = messages[0]["ID"]
                text = str(self._get(f"/message/{uid}")["Text"])
                self._delete({"IDs": [uid]})
                return text
            if time.monotonic() > deadline:
                raise TimeoutError(f"no mail to {email}")
            time.sleep(0.1)

    def _get(self, path: str) -> t.Any:
        with urllib.request.urlopen(self.url + path, timeout=5) as response:
            return json.load(response)

    def _delete(self, body: dict[str, list[str]]) -> None:
        request = urllib.request.Request(
            self.url + "/messages",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="DELETE",
        )
        urllib.request.urlopen(request, timeout=5).close()


class GameMixin(TestCase):
    """
    The client of the game, of the project of each scenario, configured as
    ``testing run`` is; a scenario takes it before ``ProjectTestCase``.
    """

    project = ProjectFixture(ScenariosProject)

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        game = await self.project.grpc.clients.default
        self.nickname = game.auth_methods_nickname
        self.email_code = game.auth_methods_email_code
        self.sign_up = game.auth_sign_up
        self.sign_in = game.auth_sign_in
        self.sign_out = game.auth_sign_out
        self.profiles = game.auth_profiles
        self.sessions = game.auth_sessions
        self.metadata = game.auth_metadata
        self.mailpit = Mailpit(self.project.settings.configs.MAILPIT_PORT)

    async def sign_up_by_nickname(self, nickname: str, password: str) -> str:
        request = nickname_pb2.SignUpRequest(nickname=nickname, password=password)
        response = await self.nickname.SignUp(request)
        return response.result.signed_up.uid

    async def sign_in_by_nickname(self, nickname: str, password: str) -> str:
        request = nickname_pb2.SignInRequest(nickname=nickname, password=password)
        response = await self.nickname.SignIn(request)
        return response.result.signed_in.token

    async def start_sign_up_by_email(self, email: str) -> str:
        request = email_code_pb2.StartSignUpRequest(email=email)
        response = await self.email_code.StartSignUp(request)
        return response.result.challenge.attempt_uid

    async def answer_sign_up(self, attempt_uid: str, code: str) -> str:
        request = sign_up_pb2.AnswerSignUpRequest(attempt_uid=attempt_uid, code=code)
        response = await self.sign_up.AnswerSignUp(request)
        return response.result.signed_up.uid

    async def start_sign_in_by_email(self, email: str) -> str:
        request = email_code_pb2.StartSignInRequest(email=email)
        response = await self.email_code.StartSignIn(request)
        return response.result.challenge.attempt_uid

    async def answer_sign_in(self, attempt_uid: str, code: str) -> str:
        request = sign_in_pb2.AnswerSignInRequest(attempt_uid=attempt_uid, code=code)
        response = await self.sign_in.AnswerSignIn(request)
        return response.result.signed_in.token

    async def sign_out_of(self, token: str) -> None:
        await self.sign_out.SignOut(sign_out_pb2.SignOutRequest(), metadata=bear(token))

    async def get_own_profile(self, token: str) -> profiles_pb2.GetOwnProfileResponse:
        request = profiles_pb2.GetOwnProfileRequest()
        return await self.profiles.GetOwnProfile(request, metadata=bear(token))

    async def sign_up_and_in(self, times: int = 1) -> list[str]:
        """A new player, signed in ``times``, a device each: its tokens."""
        nickname = new_nickname()
        await self.sign_up_by_nickname(nickname, PASSWORD)
        return [
            await self.sign_in_by_nickname(nickname, PASSWORD) for _ in range(times)
        ]

    async def list_own_sessions(self, token: str) -> list[sessions_pb2.Session]:
        request = sessions_pb2.ListOwnSessionsRequest()
        response = await self.sessions.ListOwnSessions(request, metadata=bear(token))
        return list(response.sessions)

    async def revoke_own_session(self, token: str, session_uid: str) -> None:
        request = sessions_pb2.RevokeOwnSessionRequest(session_uid=session_uid)
        await self.sessions.RevokeOwnSession(request, metadata=bear(token))

    async def revoke_other_sessions(self, token: str) -> int:
        request = sessions_pb2.RevokeOtherSessionsRequest()
        response = await self.sessions.RevokeOtherSessions(
            request, metadata=bear(token)
        )
        return response.count

    async def get_metadata(self) -> metadata_pb2.GetMetadataResponse:
        return await self.metadata.GetMetadata(metadata_pb2.GetMetadataRequest())

    async def assert_refused(
        self, call: t.Awaitable[object], code: grpc.StatusCode, reason: str
    ) -> GrpcError:
        """A call refused with the code and the reason: its error."""
        with self.assertRaises(GrpcError) as caught:
            await call
        error = caught.exception
        self.assertEqual((error.code, error.reason), (code, reason))
        return error
