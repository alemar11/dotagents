from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from typing import Any
from unittest import mock


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "codex-cli"
loader = importlib.machinery.SourceFileLoader("codex_cli_script", str(SCRIPT_PATH))
spec = importlib.util.spec_from_loader(loader.name, loader)
assert spec is not None
cli = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = cli
loader.exec_module(cli)


class CodexCliContractTests(unittest.TestCase):
    def test_version(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(["--version"])
        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), "codex-cli 0.1.2")

    def test_model_registry_and_effort_resolution(self) -> None:
        sol_default = cli.resolve_reasoning("sol", None)
        self.assertEqual(sol_default.task_profile, "standard")
        self.assertEqual(sol_default.reasoning_effort, "medium")

        terra_default = cli.resolve_reasoning("terra", None)
        self.assertEqual(terra_default.task_profile, "complex")
        self.assertEqual(terra_default.reasoning_effort, "high")

        luna_default = cli.resolve_reasoning("luna", None)
        self.assertEqual(luna_default.task_profile, "critical")
        self.assertEqual(luna_default.reasoning_effort, "max")

        self.assertEqual(
            cli.resolve_reasoning("luna", "routine").reasoning_effort,
            "low",
        )
        self.assertEqual(
            cli.resolve_reasoning("luna", "standard").reasoning_effort,
            "max",
        )
        self.assertEqual(
            cli.resolve_reasoning("luna", "complex").reasoning_effort,
            "max",
        )

        sol = cli.resolve_reasoning("sol", "extreme")
        self.assertEqual(sol.model_id, "gpt-5.6-sol")
        self.assertEqual(sol.reasoning_effort, "ultra")
        self.assertIsNone(sol.reasoning_adjustment)

        terra = cli.resolve_reasoning("terra", "risky")
        self.assertEqual(terra.reasoning_effort, "xhigh")

        luna = cli.resolve_reasoning("luna", "extreme")
        self.assertEqual(luna.reasoning_effort, "max")
        self.assertEqual(luna.reasoning_adjustment, "task-profile-ultra-capped-at-max")

    def test_all_supported_model_efforts_resolve(self) -> None:
        expected_defaults = {
            "sol": ("standard", "medium"),
            "terra": ("complex", "high"),
            "luna": ("critical", "max"),
        }
        for model, profile in cli.MODEL_PROFILES.items():
            default_profile, default_effort = expected_defaults[model]
            default = cli.resolve_reasoning(model, None)
            self.assertEqual(default.task_profile, default_profile)
            self.assertEqual(default.reasoning_effort, default_effort)
            self.assertEqual(
                len(profile["reasoning_efforts"]),
                6 if model != "luna" else 5,
            )
            for effort in profile["reasoning_efforts"]:
                resolved = cli.resolve_reasoning(model, None, effort)
                self.assertEqual(resolved.model, model)
                self.assertEqual(resolved.model_id, profile["model_id"])
                self.assertEqual(resolved.requested_reasoning_effort, effort)
                self.assertEqual(resolved.reasoning_effort, effort)
                self.assertIsNone(resolved.reasoning_adjustment)

    def test_caller_selection_contract(self) -> None:
        cases = (
            ((), "sol", "standard", "medium"),
            (("--model", "terra"), "terra", "complex", "high"),
            (("--model", "luna"), "luna", "critical", "max"),
            (("--reasoning-effort", "xhigh"), "sol", None, "xhigh"),
            (
                ("--model", "terra", "--reasoning-effort", "medium"),
                "terra",
                None,
                "medium",
            ),
        )
        for options, expected_model, expected_profile, expected_effort in cases:
            args = cli.parser().parse_args([*options, "--prompt", "complete prompt"])
            resolution = cli.resolve_reasoning(
                args.model,
                args.task_profile,
                args.reasoning_effort,
            )
            self.assertEqual(resolution.model, expected_model)
            self.assertEqual(resolution.task_profile, expected_profile)
            self.assertEqual(resolution.reasoning_effort, expected_effort)

    def test_dry_run_applies_model_defaults_and_reasoning_override(self) -> None:
        cases = (
            ((), "sol", "gpt-5.6-sol", "medium"),
            (("--model", "terra"), "terra", "gpt-5.6-terra", "high"),
            (("--model", "luna"), "luna", "gpt-5.6-luna", "max"),
            (
                ("--reasoning-effort", "ultra"),
                "sol",
                "gpt-5.6-sol",
                "ultra",
            ),
        )
        for options, expected_model, expected_id, expected_effort in cases:
            stdout = io.StringIO()
            with (
                mock.patch.object(cli, "resolve_executable", return_value="/fake/codex"),
                contextlib.redirect_stdout(stdout),
            ):
                code = cli.main(
                    [
                        "--json",
                        "--dry-run",
                        *options,
                        "--prompt",
                        "complete prompt",
                    ]
                )
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["model"], expected_model)
            self.assertEqual(payload["model_id"], expected_id)
            self.assertEqual(payload["reasoning_effort"], expected_effort)

    def test_explicit_incompatible_effort_is_rejected(self) -> None:
        with self.assertRaises(cli.CodexCliError) as raised:
            cli.resolve_reasoning("luna", "standard", "ultra")
        self.assertEqual(raised.exception.code, "reasoning-effort-unsupported")

    def test_prompt_file_is_complete_utf8_and_non_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompt_path = root / "prompt.md"
            prompt_path.write_text("Full prompt.\n", encoding="utf-8")
            args = cli.parser().parse_args(["--prompt-file", str(prompt_path)])
            self.assertEqual(cli.load_prompt(args), "Full prompt.\n")

            invalid_path = root / "invalid.md"
            invalid_path.write_bytes(b"\xff")
            invalid_args = cli.parser().parse_args(["--prompt-file", str(invalid_path)])
            with self.assertRaises(cli.CodexCliError) as raised:
                cli.load_prompt(invalid_args)
            self.assertEqual(raised.exception.code, "prompt-file-non-utf8")

    def test_prompt_sources_cannot_be_combined(self) -> None:
        args = cli.parser().parse_args(["--prompt", "one", "--prompt-file", "two"])
        with self.assertRaises(cli.CodexCliError) as raised:
            cli.load_prompt(args)
        self.assertEqual(raised.exception.code, "prompt-source-conflict")

    def test_explicit_executable_path_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "codex-target"
            target.write_text("#!/bin/sh\n", encoding="utf-8")
            target.chmod(0o700)
            link = root / "codex-link"
            link.symlink_to(target)
            with self.assertRaises(cli.CodexCliError) as raised:
                cli.resolve_executable(str(link))
        self.assertEqual(raised.exception.code, "codex-executable-unavailable")

    def test_explicit_relative_executable_is_absolute_before_child_cd(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / "launcher" / "tools" / "codex"
            executable.parent.mkdir(parents=True)
            executable.write_text("#!/bin/sh\n", encoding="utf-8")
            executable.chmod(0o700)
            relative = str(executable.relative_to(Path.cwd())) if executable.is_relative_to(Path.cwd()) else os.path.relpath(executable, Path.cwd())
            resolved = cli.resolve_executable(relative)
        self.assertEqual(Path(resolved), executable.resolve())

    def test_dot_relative_and_path_relative_executables_are_absolute(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / "codex"
            executable.write_text("#!/bin/sh\n", encoding="utf-8")
            executable.chmod(0o700)
            previous_directory = Path.cwd()
            os.chdir(root)
            try:
                self.assertEqual(Path(cli.resolve_executable("./codex")), executable.resolve())
                with mock.patch.object(cli.shutil, "which", return_value="./codex"):
                    self.assertEqual(Path(cli.resolve_executable("codex")), executable.resolve())
            finally:
                os.chdir(previous_directory)

    def test_output_path_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.txt"
            link = root / "output.txt"
            link.symlink_to(target)
            with self.assertRaises(cli.CodexCliError) as raised:
                cli.pin_output_path(str(link))
        self.assertEqual(raised.exception.code, "output-symlink")

    def test_output_parent_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = root / "output"
            parent.mkdir()
            outside = root / "outside"
            outside.mkdir()
            target = cli.pin_output_path(str(parent / "result.txt"))
            assert target is not None
            try:
                parent.rename(root / "original-output")
                parent.symlink_to(outside, target_is_directory=True)
                with self.assertRaises(cli.CodexCliError) as raised:
                    cli.write_regular_output(target, "result")
                self.assertEqual(raised.exception.code, "output-parent-changed")
                self.assertFalse((outside / "result.txt").exists())
            finally:
                target.close()

    def test_output_final_symlink_created_after_pin_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root / "outside.txt"
            target = cli.pin_output_path(str(root / "result.txt"))
            assert target is not None
            try:
                target.path.symlink_to(outside)
                with self.assertRaises(cli.CodexCliError) as raised:
                    cli.write_regular_output(target, "result")
                self.assertEqual(raised.exception.code, "output-symlink")
                self.assertFalse(outside.exists())
            finally:
                target.close()

    def test_output_is_launcher_owned_and_keeps_delegated_sandbox(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = cli.parser().parse_args(
                [
                    "--prompt",
                    "complete prompt",
                    "--output",
                    str(Path(directory) / "result.txt"),
                    "--sandbox",
                    "read-only",
                ]
            )
            with mock.patch.object(cli, "resolve_executable", return_value="/fake/codex"):
                cli.build_invocation(args)

    def test_failed_task_preserves_existing_output(self) -> None:
        class FailedProcess:
            def __init__(self) -> None:
                self.stdin = io.StringIO()
                self.returncode = 1

            def poll(self) -> int:
                return self.returncode

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output_path = root / "result.txt"
            output_path.write_text("previous result", encoding="utf-8")
            args = cli.parser().parse_args(
                [
                    "--codex-bin",
                    "codex",
                    "--prompt",
                    "complete prompt",
                    "--cd",
                    directory,
                    "--output",
                    str(output_path),
                ]
            )
            with (
                mock.patch.object(cli, "resolve_executable", return_value="/fake/codex"),
                mock.patch.object(cli.subprocess, "Popen", return_value=FailedProcess()),
            ):
                code = cli.run_task(args, "complete prompt")
            self.assertEqual(code, 1)
            self.assertEqual(output_path.read_text(encoding="utf-8"), "previous result")

    def test_success_without_final_answer_is_a_structured_failure(self) -> None:
        class EmptyProcess:
            def __init__(self) -> None:
                self.stdin = io.StringIO()
                self.returncode = 0

            def poll(self) -> int:
                return self.returncode

        with tempfile.TemporaryDirectory() as directory:
            args = cli.parser().parse_args(
                [
                    "--codex-bin",
                    "codex",
                    "--prompt",
                    "complete prompt",
                    "--cd",
                    directory,
                ]
            )
            with (
                mock.patch.object(cli, "resolve_executable", return_value="/fake/codex"),
                mock.patch.object(cli.subprocess, "Popen", return_value=EmptyProcess()),
            ):
                with self.assertRaises(cli.CodexCliError) as raised:
                    cli.run_task(args, "complete prompt")
        self.assertEqual(raised.exception.code, "codex-empty-result")

    def test_json_argument_errors_are_structured(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = cli.main(["--json", "--model", "invalid", "--prompt", "prompt"])
        self.assertEqual(code, 2)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_code"], "argument-invalid")
        self.assertEqual(stderr.getvalue(), "")

    def test_nonfinite_heartbeat_is_rejected_as_structured_error(self) -> None:
        for value in ("nan", "inf", "-inf"):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = cli.main(["--json", f"--heartbeat-seconds={value}", "--prompt", "prompt"])
            self.assertEqual(code, 2)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["error_code"], "heartbeat-invalid")
            self.assertEqual(stderr.getvalue(), "")

    def test_json_version_is_structured(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(["--json", "--version"])
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "version")

    def test_temp_directory_failure_is_structured(self) -> None:
        stdout = io.StringIO()
        with (
            mock.patch.object(
                cli.tempfile,
                "TemporaryDirectory",
                side_effect=OSError("no temporary directory"),
            ),
            contextlib.redirect_stdout(stdout),
        ):
            code = cli.main(["--json", "--prompt", "complete prompt"])
        self.assertEqual(code, 2)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["error_code"], "codex-temp-unavailable")

    def test_run_task_passes_prompt_and_reports_result(self) -> None:
        captured: dict[str, str] = {}

        class FakeStdin:
            def write(self, prompt: str) -> int:
                captured["prompt"] = prompt
                return len(prompt)

            def close(self) -> None:
                return None

        class FakeProcess:
            def __init__(self, command: list[str], stdout: Any, stderr: Any) -> None:
                self.stdin = FakeStdin()
                self.returncode = 0
                stdout.write("stdout fallback\n")
                stderr.write("codex warning\n")
                last_message_index = command.index("--output-last-message") + 1
                Path(command[last_message_index]).write_text(
                    "final answer\n",
                    encoding="utf-8",
                )

            def poll(self) -> int:
                return self.returncode

            def wait(self, timeout: float | None = None) -> int:
                return self.returncode

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "result.txt"
            args = cli.parser().parse_args(
                [
                    "--json",
                    "--codex-bin",
                    "codex",
                    "--prompt",
                    "Full prompt\nwith unicode: è",
                    "--cd",
                    directory,
                    "--output",
                    str(output_path),
                ]
            )
            with (
                mock.patch.object(cli, "resolve_executable", return_value="/fake/codex"),
                mock.patch.object(
                    cli.subprocess,
                    "Popen",
                    side_effect=lambda command, **kwargs: FakeProcess(
                        command,
                        kwargs["stdout"],
                        kwargs["stderr"],
                    ),
                ),
            ):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    code = cli.run_task(args, args.prompt)

            self.assertEqual(code, 0)
            self.assertEqual(captured["prompt"], args.prompt)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["final_output"], "final answer\n")
            self.assertEqual(payload["stderr"], "codex warning\n")
            self.assertEqual(
                output_path.read_text(encoding="utf-8"),
                "final answer\n",
            )

    def test_broken_pipe_does_not_escape_stdin_close(self) -> None:
        class BrokenPipeStream:
            def write(self, prompt: str) -> None:
                raise BrokenPipeError

            def close(self) -> None:
                raise BrokenPipeError

        process = mock.Mock()
        process.stdin = BrokenPipeStream()
        with self.assertRaises(cli.CodexCliError) as raised:
            cli.send_prompt(process, "complete prompt")
        self.assertEqual(raised.exception.code, "prompt-transport-failed")

    def test_command_uses_exact_model_effort_and_ephemeral_exec(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = cli.parser().parse_args(
                [
                    "--codex-bin",
                    "codex",
                    "--model",
                    "terra",
                    "--task-profile",
                    "extreme",
                    "--sandbox",
                    "read-only",
                    "--prompt",
                    "complete prompt",
                    "--cd",
                    directory,
                ]
            )
            with mock.patch.object(cli, "resolve_executable", return_value="/fake/codex"):
                invocation = cli.build_invocation(
                    args,
                    output_last_message="/tmp/last-message.json",
                )
        self.assertEqual(invocation.resolution.model_id, "gpt-5.6-terra")
        self.assertEqual(invocation.resolution.reasoning_effort, "ultra")
        self.assertEqual(
            invocation.command[:9],
            [
                "/fake/codex",
                "--ask-for-approval",
                "never",
                "--model",
                "gpt-5.6-terra",
                "--config",
                'model_reasoning_effort="ultra"',
                "--sandbox",
                "read-only",
            ],
        )
        self.assertIn("exec", invocation.command)
        self.assertIn("--ephemeral", invocation.command)
        self.assertIn("--output-last-message", invocation.command)

    def test_dry_run_never_calls_codex(self) -> None:
        with mock.patch.object(cli, "resolve_executable", return_value="/fake/codex"):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = cli.main(
                    [
                        "--json",
                        "--dry-run",
                        "--model",
                        "luna",
                        "--task-profile",
                        "extreme",
                        "--prompt",
                        "full prompt",
                    ]
                )
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["model"], "luna")
        self.assertEqual(payload["reasoning_effort"], "max")
        self.assertEqual(payload["reasoning_adjustment"], "task-profile-ultra-capped-at-max")

    def test_doctor_is_read_only_and_reports_matrix(self) -> None:
        args = cli.parser().parse_args(["--json", "doctor"])
        with (
            mock.patch.object(cli, "resolve_executable", return_value="/fake/codex"),
            mock.patch.object(
                cli,
                "codex_version",
                return_value=(True, "codex-cli 0.146.0", None, "warning"),
            ),
        ):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = cli.doctor(args)
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["default_model"], "sol")
        self.assertEqual(payload["default_task_profile_by_model"]["terra"], "complex")
        self.assertEqual(payload["default_task_profile_by_model"]["luna"], "critical")
        self.assertIn("ultra", payload["models"]["sol"]["reasoning_efforts"])
        self.assertNotIn("ultra", payload["models"]["luna"]["reasoning_efforts"])
        self.assertEqual(payload["models"]["terra"]["default_reasoning_effort"], "high")
        self.assertEqual(payload["models"]["terra"]["default_task_profile"], "complex")
        self.assertEqual(payload["models"]["luna"]["default_reasoning_effort"], "max")
        self.assertEqual(payload["codex"]["stderr"], "warning")
        self.assertEqual(
            payload["task_profile_effort_by_model"]["luna"]["standard"],
            "max",
        )
        self.assertEqual(
            payload["task_profile_effort_by_model"]["terra"]["complex"],
            "high",
        )


if __name__ == "__main__":
    unittest.main()
