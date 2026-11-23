"""The API of the auth, its contract and its RPCs, of no transport."""

import subprocess
import sys
import unittest

from ingot_auth.api import parse_bearer_token


class ProtobufTestCase(unittest.TestCase):
    def test_it_needs_no_grpcio(self) -> None:
        # a process of its own: this one has imported grpc already
        code = (
            "import sys, ingot_auth.api; "
            "print(sorted({'grpc', 'ingot_grpcio'} & set(sys.modules)))"
        )
        done = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=True
        )
        self.assertEqual(done.stdout.strip(), "[]")

    def test_parse_bearer_token(self) -> None:
        for authorization, token in (
            (None, None),
            ("Bearer abc", "abc"),
            ("bearer  abc ", "abc"),
            ("Basic abc", None),
            ("Bearer ", None),
            ("Bearer", None),
        ):
            with self.subTest(authorization=authorization):
                self.assertEqual(parse_bearer_token(authorization), token)
