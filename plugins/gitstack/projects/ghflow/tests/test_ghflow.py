from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
import zipfile
from pathlib import Path
from unittest import mock


GHFLOW_PROJECT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = GHFLOW_PROJECT.parents[1]
PROJECT_SRC = GHFLOW_PROJECT / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

import ghflow  # noqa: E402
from ghflow import checks  # noqa: E402
from ghflow import runtime  # noqa: E402


@contextlib.contextmanager
def working_directory(path: Path):
    original = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def init_git_repo(repo: Path) -> None:
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test User")
    (repo / "README.md").write_text("test\n")
    git(repo, "add", "README.md")
    git(repo, "commit", "-m", "init")


class ParseRootArgsTests(unittest.TestCase):
    def test_project_package_exports_main(self) -> None:
        self.assertTrue(callable(ghflow.main))

    def test_package_entrypoint_exits_with_runtime_code(self) -> None:
        stderr = io.StringIO()
        with (
            mock.patch.object(sys, "argv", ["ghflow", "doctor"]),
            contextlib.redirect_stderr(stderr),
            self.assertRaises(SystemExit) as ctx,
        ):
            ghflow.main()
        self.assertEqual(ctx.exception.code, 64)
        self.assertIn("Unknown command group: doctor", stderr.getvalue())

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

    def test_parse_ci_inspect_command(self) -> None:
        parsed = runtime.parse_root_args(["ci", "inspect", "--pr", "123"])
        self.assertEqual(parsed["mode"], "command")
        self.assertEqual(parsed["command"], ("ci", "inspect"))
        self.assertEqual(parsed["tail"], ["--pr", "123"])

    def test_parse_portfolio_scan_repeated_repo_command(self) -> None:
        parsed = runtime.parse_root_args(
            ["portfolio", "scan", "--repo", "openai/codex", "--repo", "openai/openai"]
        )
        self.assertEqual(parsed["mode"], "command")
        self.assertEqual(parsed["command"], ("portfolio", "scan"))
        self.assertEqual(parsed["tail"], ["--repo", "openai/codex", "--repo", "openai/openai"])

    def test_render_ci_help_mentions_inspect(self) -> None:
        help_text = runtime.render_noun_help(("ci",))
        self.assertIn("ghflow [--json] ci inspect", help_text)

    def test_render_portfolio_help_mentions_scan(self) -> None:
        help_text = runtime.render_noun_help(("portfolio",))
        self.assertIn("ghflow [--json] portfolio scan", help_text)

    def test_render_publish_help_mentions_template_and_body_file(self) -> None:
        help_text = runtime.render_noun_help(("publish",))
        self.assertIn("ghflow [--json] publish <context|template|open>", help_text)
        open_help = runtime.render_noun_help(("publish", "open"))
        self.assertIn("--body-file <path>", open_help)

    def test_removed_doctor_command_fails(self) -> None:
        with self.assertRaises(runtime.GhflowError) as ctx:
            runtime.parse_root_args(["doctor"])
        self.assertEqual(ctx.exception.code, "invalid_arguments")

    def test_removed_top_level_lists_command_fails(self) -> None:
        with self.assertRaises(runtime.GhflowError) as ctx:
            runtime.parse_root_args(["lists", "list"])
        self.assertEqual(ctx.exception.code, "invalid_arguments")


class ContractTests(unittest.TestCase):
    def test_plugin_manifest_and_cli_metadata_versions_match(self) -> None:
        with (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").open() as handle:
            plugin_manifest = json.load(handle)
        with (GHFLOW_PROJECT / "pyproject.toml").open("rb") as handle:
            cli_metadata = tomllib.load(handle)
        self.assertEqual(plugin_manifest["version"], cli_metadata["project"]["version"])
        self.assertEqual(runtime.VERSION, cli_metadata["project"]["version"])

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


class PublishTemplateTests(unittest.TestCase):
    def test_base_ref_template_wins_over_worktree_edit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            init_git_repo(repo)
            template = repo / ".github" / "pull_request_template.md"
            template.parent.mkdir()
            template.write_text("base template\n")
            git(repo, "add", ".github/pull_request_template.md")
            git(repo, "commit", "-m", "add template")
            template.write_text("worktree template\n")

            with working_directory(repo):
                payload = runtime.resolve_pr_template("main", command_path=("publish", "template"))

        self.assertEqual(payload["status"], "found")
        self.assertEqual(payload["source"], "base_ref")
        self.assertEqual(payload["template"]["path"], ".github/pull_request_template.md")
        self.assertEqual(payload["template"]["content"], "base template\n")

    def test_local_template_fallback_when_base_has_none(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            init_git_repo(repo)
            template = repo / "docs" / "pull_request_template.md"
            template.parent.mkdir()
            template.write_text("local docs template\n")

            with working_directory(repo):
                payload = runtime.resolve_pr_template("main", command_path=("publish", "template"))

        self.assertEqual(payload["status"], "found")
        self.assertEqual(payload["source"], "worktree")
        self.assertTrue(payload["fallback_used"])
        self.assertEqual(payload["template"]["path"], "docs/pull_request_template.md")
        self.assertEqual(payload["template"]["content"], "local docs template\n")

    def test_local_template_discovery_prefers_github_then_root_then_docs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / "docs").mkdir()
            (repo / ".github").mkdir()
            (repo / "docs" / "pull_request_template.md").write_text("docs\n")
            (repo / "pull_request_template.md").write_text("root\n")
            (repo / ".github" / "PULL_REQUEST_TEMPLATE.md").write_text("github\n")

            candidates = runtime.discover_local_template_candidates(repo)

        self.assertEqual([candidate["path"] for candidate in candidates], [".github/PULL_REQUEST_TEMPLATE.md"])

    def test_multiple_named_templates_are_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            init_git_repo(repo)
            template_dir = repo / ".github" / "PULL_REQUEST_TEMPLATE"
            template_dir.mkdir(parents=True)
            (template_dir / "bug.md").write_text("bug\n")
            (template_dir / "feature.md").write_text("feature\n")

            with working_directory(repo):
                payload = runtime.resolve_pr_template("main", command_path=("publish", "template"))

        self.assertEqual(payload["status"], "ambiguous")
        self.assertEqual([candidate["path"] for candidate in payload["candidates"]], [".github/PULL_REQUEST_TEMPLATE/bug.md", ".github/PULL_REQUEST_TEMPLATE/feature.md"])

    def test_missing_template_reports_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            init_git_repo(repo)

            with working_directory(repo):
                payload = runtime.resolve_pr_template("main", command_path=("publish", "template"))

        self.assertEqual(payload["status"], "missing")
        self.assertIsNone(payload["template"])


class PublishOpenTests(unittest.TestCase):
    def test_publish_open_rejects_body_file_with_body(self) -> None:
        spec = runtime.COMMAND_SPECS[("publish", "open")]
        with self.assertRaises(runtime.GhflowError) as ctx:
            spec.handler(spec, ["--body-file", "body.md", "--body", "body"], False)
        self.assertEqual(ctx.exception.code, "invalid_arguments")

    def test_publish_open_dry_run_uses_body_file_argument(self) -> None:
        spec = runtime.COMMAND_SPECS[("publish", "open")]
        with tempfile.TemporaryDirectory() as temp:
            body_file = Path(temp) / "body.md"
            body_file.write_text("template-aware body\n")
            with (
                mock.patch.object(runtime, "current_branch", return_value="feature"),
                mock.patch.object(runtime, "resolve_repo", return_value="OWNER/REPO"),
                mock.patch.object(runtime, "tracking_remote_name", return_value="origin"),
                mock.patch.object(runtime, "tracking_branch_name", return_value="feature"),
                mock.patch.object(runtime, "run_git_text", return_value=runtime.RunResult(0, "", "")),
                mock.patch.object(runtime, "gh_json", side_effect=[[], {"defaultBranchRef": {"name": "main"}}]),
            ):
                response = spec.handler(spec, ["--title", "Test PR", "--body-file", str(body_file), "--dry-run"], False)

        self.assertEqual(response.result.returncode, 0)
        self.assertIn(f"Body source: file {body_file}", response.result.stdout)
        self.assertIn("--body-file", response.result.stdout)
        self.assertIn("template-aware body", response.result.stdout)


class CiInspectRuntimeTests(unittest.TestCase):
    def test_ci_inspect_json_success_returns_zero(self) -> None:
        payload = {
            "repo": "openai/codex",
            "pr": "123",
            "failingCount": 0,
            "results": [],
            "summary": "no_failing_checks",
        }
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(runtime, "is_git_repo", return_value=False),
            mock.patch.object(runtime.checks, "inspect_pr_failures", return_value=(payload, 0)),
        ):
            exit_code = runtime.main(
                ["--json", "ci", "inspect", "--repo", "openai/codex", "--allow-non-project"]
            )
        body = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertTrue(body["ok"])
        self.assertEqual(body["command"], ["ci", "inspect"])
        self.assertEqual(body["data"]["summary"], "no_failing_checks")

    def test_ci_inspect_json_failures_return_nonzero_with_data(self) -> None:
        payload = {
            "repo": "openai/codex",
            "pr": "123",
            "failingCount": 1,
            "results": [{"name": "test", "status": "ok"}],
            "summary": "failing_checks",
        }
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(runtime, "is_git_repo", return_value=False),
            mock.patch.object(runtime.checks, "inspect_pr_failures", return_value=(payload, 1)),
        ):
            exit_code = runtime.main(
                ["--json", "ci", "inspect", "--repo", "openai/codex", "--allow-non-project"]
            )
        body = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertFalse(body["ok"])
        self.assertEqual(body["command"], ["ci", "inspect"])
        self.assertEqual(body["error"]["code"], "failing_checks")
        self.assertEqual(body["data"]["failingCount"], 1)


class PortfolioScanTests(unittest.TestCase):
    def fake_gh_json(self, args, *, command_path, cwd=None, input_text=None):
        repo = args[2] if args[:2] == ["repo", "view"] else args[args.index("--repo") + 1]
        if repo == "bad/repo":
            raise runtime.GhflowError(
                "HTTP 404: Not Found",
                code="command_failed",
                exit_code=1,
                command_path=command_path,
            )
        if args[:2] == ["repo", "view"]:
            return {
                "url": f"https://github.com/{repo}",
                "isArchived": False,
                "isFork": False,
                "pushedAt": "2026-06-15T10:10:00Z",
                "issues": {"totalCount": 7},
                "pullRequests": {"totalCount": 3},
                "latestRelease": {
                    "tagName": "v1.2.3",
                    "name": "v1.2.3",
                    "url": f"https://github.com/{repo}/releases/tag/v1.2.3",
                    "isDraft": False,
                    "isPrerelease": False,
                    "isLatest": True,
                    "publishedAt": "2026-06-14T10:00:00Z",
                },
            }
        if args[:2] == ["issue", "list"]:
            return [
                {
                    "number": 1,
                    "title": "Bug",
                    "author": {"login": "alice"},
                    "labels": [{"name": "bug"}],
                    "updatedAt": "2026-06-15T09:00:00Z",
                    "url": f"https://github.com/{repo}/issues/1",
                }
            ]
        if args[:2] == ["pr", "list"]:
            return [
                {
                    "number": 2,
                    "title": "Fix",
                    "author": {"login": "bob"},
                    "isDraft": False,
                    "reviewDecision": "REVIEW_REQUIRED",
                    "mergeStateStatus": "CLEAN",
                    "statusCheckRollup": [{"state": "SUCCESS"}],
                    "updatedAt": "2026-06-15T10:00:00Z",
                    "url": f"https://github.com/{repo}/pull/2",
                }
            ]
        if args[:2] == ["run", "list"]:
            return [
                {
                    "workflowName": "CI",
                    "displayTitle": "test",
                    "headBranch": "main",
                    "status": "completed",
                    "conclusion": "success",
                    "updatedAt": "2026-06-15T10:05:00Z",
                    "url": f"https://github.com/{repo}/actions/runs/1",
                }
            ]
        raise AssertionError(f"unexpected gh_json args: {args}")

    def test_portfolio_scan_json_success(self) -> None:
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(runtime, "gh_json", side_effect=self.fake_gh_json),
        ):
            exit_code = runtime.main(["--json", "portfolio", "scan", "--repo", "openai/codex"])
        body = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertTrue(body["ok"])
        self.assertEqual(body["command"], ["portfolio", "scan"])
        self.assertEqual(body["data"]["summary"]["successful"], 1)
        self.assertEqual(body["data"]["repos"][0]["open_issues"], 7)
        self.assertEqual(body["data"]["repos"][0]["open_prs"], 3)
        self.assertIn("7 open issues", body["data"]["repos"][0]["top_queue_signals"])
        self.assertEqual(body["data"]["repos"][0]["latest_release"]["url"], "https://github.com/openai/codex/releases/tag/v1.2.3")

    def test_portfolio_scan_repo_file_and_partial_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo_file = Path(temp) / "repos.txt"
            repo_file.write_text("# comment\nopenai/codex\nbad/repo\nopenai/codex duplicate\n")
            stdout = io.StringIO()
            with (
                contextlib.redirect_stdout(stdout),
                mock.patch.object(runtime, "gh_json", side_effect=self.fake_gh_json),
            ):
                exit_code = runtime.main(["--json", "portfolio", "scan", "--repo-file", str(repo_file), "--limit", "5"])
        body = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertTrue(body["ok"])
        self.assertEqual(body["data"]["summary"]["requested"], 2)
        self.assertEqual(body["data"]["summary"]["successful"], 1)
        self.assertEqual(body["data"]["summary"]["failed"], 1)
        self.assertFalse(body["data"]["repos"][1]["ok"])
        self.assertEqual(body["data"]["repos"][1]["error"]["message"], "HTTP 404: Not Found")

    def test_portfolio_scan_all_failures_return_nonzero_with_data(self) -> None:
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(runtime, "gh_json", side_effect=self.fake_gh_json),
        ):
            exit_code = runtime.main(["--json", "portfolio", "scan", "--repo", "bad/repo"])
        body = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 2)
        self.assertFalse(body["ok"])
        self.assertEqual(body["error"]["code"], "portfolio_scan_failed")
        self.assertEqual(body["data"]["summary"]["successful"], 0)

    def test_portfolio_scan_invalid_repo_json_preserves_command_path(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = runtime.main(["--json", "portfolio", "scan", "--repo", "bad"])
        body = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 64)
        self.assertFalse(body["ok"])
        self.assertEqual(body["command"], ["portfolio", "scan"])
        self.assertEqual(body["error"]["code"], "invalid_arguments")

    def test_summarize_ci_treats_startup_failure_as_failure(self) -> None:
        payload = runtime.summarize_ci(
            [
                {
                    "workflowName": "CI",
                    "displayTitle": "build",
                    "status": "completed",
                    "conclusion": "startup_failure",
                }
            ]
        )
        self.assertEqual(payload["state"], "failing")
        self.assertIn("failing", payload["text"])

    def test_status_rollup_summary_reads_pending_check_run_status(self) -> None:
        summary = runtime.status_rollup_summary(
            [
                {"status": "IN_PROGRESS", "conclusion": None},
                {"state": "EXPECTED"},
                {"state": "SUCCESS"},
            ]
        )
        self.assertEqual(summary, "2 pending")

    def test_status_rollup_summary_treats_startup_failure_as_failure(self) -> None:
        summary = runtime.status_rollup_summary([{"conclusion": "STARTUP_FAILURE"}])
        self.assertEqual(summary, "1 failing")


class ChecksTests(unittest.TestCase):
    def test_extract_run_id_and_job_id(self) -> None:
        url = "https://github.com/openai/codex/actions/runs/123456789/job/987654321"
        self.assertEqual(checks.extract_run_id(url), "123456789")
        self.assertEqual(checks.extract_job_id(url), "987654321")

    def test_parse_available_fields_from_gh_error(self) -> None:
        message = "\n".join(
            [
                "Unknown JSON field: detailsUrl",
                "Available fields:",
                "name",
                "state",
                "bucket",
                "link",
            ]
        )
        self.assertEqual(
            checks.parse_available_fields(message),
            ["name", "state", "bucket", "link"],
        )

    def test_external_check_stays_report_only(self) -> None:
        result = checks.analyze_check(
            {"name": "Buildkite", "detailsUrl": "https://buildkite.example/job/1"},
            repo="openai/codex",
            repo_root=None,
            max_lines=80,
            context=20,
        )
        self.assertEqual(result["status"], "external")
        self.assertIn("No GitHub Actions run id", result["note"])

    def test_extract_failure_snippet_prefers_failure_marker_window(self) -> None:
        log_text = "\n".join(
            [
                "step 1",
                "step 2",
                "AssertionError: boom",
                "step 4",
                "step 5",
            ]
        )
        snippet = checks.extract_failure_snippet(log_text, max_lines=3, context=1)
        self.assertEqual(snippet, "\n".join(["step 2", "AssertionError: boom", "step 4"]))

    def test_extract_log_from_job_archive_reads_zip_payload(self) -> None:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("job.txt", "line 1\nline 2\n")
        text, error = checks.extract_log_from_job_archive(buffer.getvalue())
        self.assertEqual(error, "")
        self.assertIn("line 2", text)


if __name__ == "__main__":
    unittest.main()
