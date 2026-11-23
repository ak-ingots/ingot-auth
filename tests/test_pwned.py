"""The policy of a password leaked, by a range of Pwned Passwords, no network."""

import hashlib
import http.server
import threading
import typing as t
import unittest
from dataclasses import dataclass
from unittest import mock

from ingots.defaults.operations import Caller, Permissions
from ingots.puer import Factory, Slot, Unit

from ingot_auth.contrib.policies import AuthPwnedConfig, AuthPwnedPolicy
from ingot_auth.policies import AuthPolicyViolationError
from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit

ANONYMOUS: t.Final = Caller(uid="anonymous", permissions=Permissions())
LEAKED = "password123"
DIGEST = hashlib.sha1(LEAKED.encode()).hexdigest().upper()


@dataclass(frozen=True, slots=True, kw_only=True)
class Value:
    value: str


class RangePwned(AuthPwnedPolicy):
    """A range given here: the leaked password twice, padding of none."""

    RANGE = f"0018A45C4D1DEF81644B54AB7F969B88D65:1\r\n{DIGEST[5:]}:2\r\n"

    @t.override
    async def _fetch_range(self, prefix: str) -> str:
        return (
            self.RANGE
            if prefix == DIGEST[:5]
            else "0018A45C4D1DEF81644B54AB7F969B88D65:0"
        )


class PaddedPwned(RangePwned):
    RANGE = f"{DIGEST[5:]}:0\r\n"


class OftenPwned(RangePwned):
    CONFIG = AuthPwnedConfig(min_count=3)


class DownPwned(AuthPwnedPolicy):
    @t.override
    async def _fetch_range(self, prefix: str) -> str:
        raise TimeoutError("timed out")


class StrictDownPwned(DownPwned):
    CONFIG = AuthPwnedConfig(is_fail_open=False)


class TstPoliciesUnit(Unit):
    range = Factory(RangePwned)
    padded = Factory(PaddedPwned)
    often = Factory(OftenPwned)
    down = Factory(DownPwned)
    strict_down = Factory(StrictDownPwned)


class TstAuthUnit(AuthMemoryUnit):
    policies = Slot(TstPoliciesUnit)


class TstProject(AuthMemoryProject):
    auth = Slot(TstAuthUnit)


class PwnedTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = TstProject()
        self.metadata = self.project.operations.create_metadata(ANONYMOUS)

    async def get_broken(self, policy: t.Any, value: str) -> str | None:
        try:
            await self.project.operations.runner.run(
                policy, Value(value=value), self.metadata
            )
        except AuthPolicyViolationError as error:
            return error.policy
        return None

    async def test_a_leaked_password_is_refused(self) -> None:
        policies = self.project.auth.policies
        self.assertEqual(await self.get_broken(policies.range, LEAKED), "pwned")
        self.assertIsNone(
            await self.get_broken(policies.range, "correct horse battery staple")
        )

    async def test_the_padding_and_a_count_under_the_minimum_pass(self) -> None:
        policies = self.project.auth.policies
        self.assertIsNone(await self.get_broken(policies.padded, LEAKED))
        self.assertIsNone(await self.get_broken(policies.often, LEAKED))

    async def test_a_service_down_lets_through_unless_told(self) -> None:
        policies = self.project.auth.policies
        with self.assertLogs("ingot_auth.contrib.policies.pwned", "WARNING"):
            self.assertIsNone(await self.get_broken(policies.down, LEAKED))
        self.assertEqual(
            await self.get_broken(policies.strict_down, LEAKED), "pwned_unchecked"
        )


class RangeHandler(http.server.BaseHTTPRequestHandler):
    """The service, its range of a prefix, the headers of the request kept."""

    headers_seen: t.ClassVar[list[dict[str, str]]] = []

    def do_GET(self) -> None:
        type(self).headers_seen.append(dict(self.headers))
        body = f"{DIGEST[5:]}:7\r\n".encode() if self.path.endswith(DIGEST[:5]) else b""
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @t.override
    def log_message(self, format: str, *args: t.Any) -> None:
        pass


class FetchTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_the_range_is_fetched_by_its_prefix_padded(self) -> None:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), RangeHandler)
        self.addCleanup(server.server_close)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.shutdown)

        class LocalPwned(AuthPwnedPolicy):
            CONFIG = AuthPwnedConfig(
                url=f"http://127.0.0.1:{server.server_port}/range/"
            )

        class LocalUnit(Unit):
            pwned = Factory(LocalPwned)

        class LocalAuth(AuthMemoryUnit):
            policies = Slot(LocalUnit)

        class LocalProject(AuthMemoryProject):
            auth = Slot(LocalAuth)

        project = LocalProject()
        metadata = project.operations.create_metadata(ANONYMOUS)
        with self.assertRaises(AuthPolicyViolationError) as error:
            await project.operations.runner.run(
                project.auth.policies.pwned, Value(value=LEAKED), metadata
            )
        self.assertEqual(error.exception.policy, "pwned")
        headers = RangeHandler.headers_seen[-1]
        self.assertEqual(headers["Add-Padding"], "true")
        self.assertEqual(headers["User-Agent"], "ingot-auth")
