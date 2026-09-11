from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from stack_lib import __version__, cli


class StackCliTests(unittest.TestCase):
    def invoke(self, args: list[str]) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli.main(args)
        return code, output.getvalue()

    def test_version(self) -> None:
        code, output = self.invoke(["--version"])
        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), __version__)

    def test_stack_raw_preserves_upstream_json_after_separator(self) -> None:
        with mock.patch.object(cli.stack, "execute_raw", return_value=0) as execute:
            code = cli.main(["raw", "--", "view", "--json"])
        self.assertEqual(code, 0)
        execute.assert_called_once_with(["--", "view", "--json"], json_mode=False)

    def test_stack_raw_accepts_wrapper_json_before_separator(self) -> None:
        with mock.patch.object(cli.stack, "execute_raw", return_value=0) as execute:
            code = cli.main(["raw", "--json", "--", "view"])
        self.assertEqual(code, 0)
        execute.assert_called_once_with(["--", "view"], json_mode=True)

    def test_typed_stack_arguments_are_forwarded_without_an_explicit_separator(self) -> None:
        cases = [
            (["--json", "init", "--base", "main", "layer-a", "layer-b"], "init", ["--base", "main", "layer-a", "layer-b"]),
            (["--json", "rebase", "--upstack"], "rebase", ["--upstack"]),
            (["--json", "submit", "--auto"], "submit", ["--auto"]),
        ]
        for args, verb, forwarded in cases:
            with self.subTest(args=args):
                with mock.patch.object(cli.stack, "execute", return_value=0) as execute:
                    code = cli.main(args)
                self.assertEqual(code, 0)
                execute.assert_called_once_with(verb, forwarded, json_mode=True)


if __name__ == "__main__":
    unittest.main()
