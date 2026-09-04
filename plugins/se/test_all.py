"""Package-level unittest discovery for the SE plugin."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parent
TEST_FILES = (
    PLUGIN / "tests/test_plugin_runtime_alignment.py",
    PLUGIN / "skills/implement/tests/test_repository_claims.py",
)


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    for index, test_file in enumerate(TEST_FILES):
        spec = importlib.util.spec_from_file_location(f"se_test_{index}", test_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load SE test module: {test_file}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite.addTests(loader.loadTestsFromModule(module))
    return suite
