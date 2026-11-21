"""The steps of the scenarios, shared: functions and a mixin, called by name."""

import asyncio
import json
import re
import time
import typing as t
import urllib.parse
import urllib.request
import uuid

import httpx
from ingots.testing import ProjectFixture, ProjectTestCase

from ingot_auth.contrib.transports.contract import PROFILE_HASH_KEY

from .project import ScenariosProject

# the mail of a code goes in the background: how long a scenario waits for it
MAIL_TIMEOUT = 10.0

# the auth of the site; a path is absolute, as a relative one of a custom
# verb, signUp:answer, would read as a scheme of a URL (RFC 3986)
AUTH: t.Final = "/api/auth/v1/"

if t.TYPE_CHECKING:
    TestCase: t.TypeAlias = ProjectTestCase
else:
    TestCase = object


def new_email() -> str:
    """An email no scenario took, the site kept running between them."""
    return f"user-{uuid.uuid4().hex[:12]}@example.com"


def bear(token: str) -> dict[str, str]:
    return {"authorization": f"Bearer {token}"}


class Mailpit:
    """The mailbox of every user, read by the API of Mailpit."""

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


class SiteMixin(TestCase):
    """
    The client of the site over HTTP, of the project of each scenario,
    configured as ``testing run`` is; a scenario takes it before
    ``ProjectTestCase``.
    """

    project = ProjectFixture(ScenariosProject)

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        configs = self.project.settings.configs
        base_url = f"http://{configs.SITE_HOST}:{configs.SITE_PORT}"
        self.http = httpx.AsyncClient(base_url=base_url, timeout=10)
        self.addAsyncCleanup(self.http.aclose)
        self.mailpit = Mailpit(configs.MAILPIT_PORT)

    async def call(
        self, path: str, body: object = None, token: str | None = None
    ) -> httpx.Response:
        """A call of the auth: POST of a body, GET of none."""
        headers = bear(token) if token else {}
        if body is None:
            return await self.http.get(AUTH + path, headers=headers)
        return await self.http.post(AUTH + path, json=body, headers=headers)

    async def ok(
        self, path: str, body: object = None, token: str | None = None
    ) -> t.Any:
        """The JSON of a call that passes."""
        response = await self.call(path, body, token)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    async def refused(
        self,
        path: str,
        body: object,
        status: int,
        reason: str,
        token: str | None = None,
    ) -> dict[str, t.Any]:
        """The problem of a call refused by its status and its reason."""
        response = await self.call(path, body, token)
        self.assertEqual(response.status_code, status, response.text)
        self.assertEqual(response.headers["content-type"], "application/problem+json")
        problem: dict[str, t.Any] = response.json()
        self.assertEqual((problem["domain"], problem["reason"]), ("ingot-auth", reason))
        return problem

    async def start(self, flow: str, email: str) -> str:
        """The attempt of a flow started by the email, ``SignUp`` or ``SignIn``."""
        result = await self.ok(f"methods/emailCode:start{flow}", {"email": email})
        attempt_uid: str = result["result"]["challenge"]["attempt_uid"]
        return attempt_uid

    async def sign_up(self, email: str) -> str:
        """A user signed up by the code of its email: its uid."""
        attempt_uid = await self.start("SignUp", email)
        code = await self.mailpit.read_code(email)
        result = await self.ok(
            "signUp:answer", {"attempt_uid": attempt_uid, "code": code}
        )
        uid: str = result["result"]["signed_up"]["uid"]
        return uid

    async def sign_in(self, email: str) -> str:
        """A user signed in by the code of its email: the token of its session."""
        attempt_uid = await self.start("SignIn", email)
        code = await self.mailpit.read_code(email)
        result = await self.ok(
            "signIn:answer", {"attempt_uid": attempt_uid, "code": code}
        )
        token: str = result["result"]["signed_in"]["token"]
        return token

    async def new_user(self) -> tuple[str, str]:
        """A user signed up and in: its email and its token."""
        email = new_email()
        await self.sign_up(email)
        return email, await self.sign_in(email)


__all__ = ("AUTH", "PROFILE_HASH_KEY", "SiteMixin", "bear", "new_email")
