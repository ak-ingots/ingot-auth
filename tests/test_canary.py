"""
A canary for the development pipeline: the tests are found and run, and the
package they import is the one under test - the built wheel in `make
wheel-test`, not the working tree.
"""

import importlib.metadata
import importlib.resources
import os
import unittest

import ingot_auth


class CanaryTestCase(unittest.TestCase):
    def test_the_distribution_is_installed(self) -> None:
        self.assertTrue(importlib.metadata.version("ingot-auth"))

    def test_the_package_is_typed(self) -> None:
        self.assertTrue(
            importlib.resources.files(ingot_auth).joinpath("py.typed").is_file()
        )

    @unittest.skipUnless(os.environ.get("INGOT_AUTH_WHEEL_TEST"), "not a wheel test")
    def test_the_wheel_is_imported_not_the_working_tree(self) -> None:
        self.assertIn("site-packages", ingot_auth.__file__ or "")

    def test_the_framework_is_installed(self) -> None:
        self.assertTrue(importlib.metadata.version("ingots").startswith("0.32."))
