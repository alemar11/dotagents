from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

import ghflow  # noqa: E402
from ghflow import runtime  # noqa: E402


class ParseRootArgsTests(unittest.TestCase):
    def test_project_package_exports_main(self) -> None:
        self.assertTrue(callable(ghflow.main))

    def test_match_longest_nested_command(self) -> None:
        parsed = runtime.parse_root_args(["stars", "lists", "delete", "--list", "later"])
        self.assertEqual(parsed["mode"], "command")
        self.assertEqual(parsed["command"], ("stars", "lists", "delete"))
        self.assertEqual(parsed["tail"], ["--list", "later"])

    def test_render_stars_help_includes_direct_verbs_and_nested_group(self) -> None:
        help_text = runtime.render_noun_help(("stars",))
        self.assertIn("ghflow [--json] stars <list|add|remove> [args...]", help_text)
        self.assertIn("ghflow [--json] stars lists <list|items|delete|assign|unassign> [args...]", help_text)

    def test_render_stars_lists_help_is_generated_from_schema(self) -> None:
        help_text = runtime.render_noun_help(("stars", "lists"))
        self.assertIn("stars lists <list|items|delete|assign|unassign>", help_text)

    def test_parse_leaf_help_routes_to_noun_help(self) -> None:
        parsed = runtime.parse_root_args(["reviews", "address", "--help"])
        self.assertEqual(parsed["mode"], "noun_help")
        self.assertEqual(parsed["command"], ("reviews", "address"))

    def test_removed_doctor_command_fails(self) -> None:
        with self.assertRaises(runtime.GhflowError) as ctx:
            runtime.parse_root_args(["doctor"])
        self.assertEqual(ctx.exception.code, "invalid_arguments")

    def test_removed_top_level_lists_command_fails(self) -> None:
        with self.assertRaises(runtime.GhflowError) as ctx:
            runtime.parse_root_args(["lists", "list"])
        self.assertEqual(ctx.exception.code, "invalid_arguments")


class ContractTests(unittest.TestCase):
    def test_reviews_address_requires_selection_when_replying(self) -> None:
        spec = runtime.COMMAND_SPECS[("reviews", "address")]
        with self.assertRaises(runtime.GhflowError) as ctx:
            spec.handler(spec, ["--pr", "123", "--repo", "openai/codex", "--reply-body", "thanks"], False)
        self.assertEqual(ctx.exception.code, "invalid_arguments")


class UtilityTests(unittest.TestCase):
    def test_normalize_remote_url(self) -> None:
        self.assertEqual(
            runtime.normalize_remote_url("https://github.com/openai/codex.git"),
            "openai/codex",
        )
        self.assertEqual(
            runtime.normalize_remote_url("git@github.com:openai/codex.git"),
            "openai/codex",
        )

    def test_filter_runtime_noise_prefers_real_error(self) -> None:
        result = runtime.RunResult(
            1,
            "",
            "\n".join(
                [
                    "gh is installed: 2.89.0.",
                    "Authenticated to github.com as <unknown>.",
                    "Current directory is a git repository.",
                    "gh preflight checks passed.",
                    "HTTP 403: Resource not accessible by personal access token",
                ]
            ),
        )
        self.assertEqual(
            runtime.extract_runtime_error_message(result),
            "HTTP 403: Resource not accessible by personal access token",
        )

    def test_schema_commands_have_help_and_handlers(self) -> None:
        for command_path, spec in runtime.COMMAND_SPECS.items():
            with self.subTest(command_path=command_path):
                self.assertTrue(callable(spec.handler))
        for prefix in runtime.GROUP_HELP_PREFIXES:
            with self.subTest(prefix=prefix):
                help_text = runtime.render_noun_help(prefix)
                self.assertTrue(help_text.startswith("Usage:\n"))


if __name__ == "__main__":
    unittest.main()
