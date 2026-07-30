from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
COMMAND = SKILL_ROOT / "scripts" / "pi-delegate"
METADATA = SKILL_ROOT / "agents" / "openai.yaml"


class PiDelegateTests(unittest.TestCase):
    def invoke(
        self,
        *args: str,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        stdin: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(COMMAND), *args],
            cwd=str(cwd or SKILL_ROOT),
            env=env,
            input=stdin,
            text=True,
            capture_output=True,
            check=False,
        )

    def fake_environment(
        self,
        root: Path,
        *,
        model_available: bool = True,
        run_exit_code: int = 0,
    ) -> tuple[dict[str, str], Path]:
        fake_pi = root / "pi"
        log_path = root / "pi-args.json"
        model_row = (
            "zai-coding-cn  glm-5.2  1M  131.1K  yes  no"
            if model_available
            else "zai-coding-cn  glm-5.1  200K  131.1K  yes  no"
        )
        fake_pi.write_text(
            textwrap.dedent(
                f"""\
                #!{sys.executable}
                import json
                import os
                import sys

                args = sys.argv[1:]
                if "--version" in args:
                    print("0.82.1")
                    raise SystemExit(0)
                if "--list-models" in args:
                    print("provider model context max-out thinking images")
                    print({model_row!r})
                    raise SystemExit(0)
                with open(os.environ["FAKE_PI_LOG"], "w", encoding="utf-8") as handle:
                    json.dump(args, handle)
                print("Pi completed the delegated task.")
                raise SystemExit({run_exit_code})
                """
            ),
            encoding="utf-8",
        )
        fake_pi.chmod(0o755)
        env = dict(os.environ)
        env["PATH"] = f"{root}{os.pathsep}{env.get('PATH', '')}"
        env["FAKE_PI_LOG"] = str(log_path)
        return env, log_path

    def test_public_help_version_and_manual_only_metadata(self) -> None:
        version = self.invoke("--version")
        self.assertEqual(version.returncode, 0, version.stderr)
        self.assertEqual(version.stdout.strip(), "pi-delegate 0.2.0")

        help_result = self.invoke("--help")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("doctor", help_result.stdout)
        self.assertIn("run", help_result.stdout)
        self.assertIn("zai-coding-cn/glm-5.2", help_result.stdout)

        run_help = self.invoke("run", "--help")
        self.assertEqual(run_help.returncode, 0, run_help.stderr)
        self.assertIn("--thinking-level", run_help.stdout)
        self.assertIn("--session-id", run_help.stdout)
        self.assertIn("--task-file", run_help.stdout)

        metadata = METADATA.read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: false", metadata)

    def test_doctor_reports_missing_pi_without_installing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ)
            env["PATH"] = tmp
            result = self.invoke("--json", "doctor", env=env)

        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ready"])
        self.assertEqual(
            payload["install_command"],
            "npm install -g --ignore-scripts @earendil-works/pi-coding-agent",
        )
        pi_check = next(check for check in payload["checks"] if check["name"] == "pi")
        self.assertFalse(pi_check["ok"])

    def test_doctor_validates_exact_fixed_model_offline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, _ = self.fake_environment(root)
            result = self.invoke("--json", "doctor", cwd=root, env=env)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ready"])
        self.assertEqual(payload["model"], "zai-coding-cn/glm-5.2")
        self.assertEqual(payload["pi_version"], "0.82.1")

    def test_doctor_rejects_catalog_without_exact_provider_model_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, _ = self.fake_environment(root, model_available=False)
            result = self.invoke("--json", "doctor", cwd=root, env=env)

        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ready"])
        self.assertIn("setup_hint", payload)

    def test_run_pins_model_thinking_session_and_current_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project with spaces"
            project.mkdir()
            env, log_path = self.fake_environment(root)
            result = self.invoke(
                "--json",
                "run",
                "--thinking-level",
                "high",
                "--session-id",
                "codex-pi-test",
                "--name",
                "Fix parser",
                "Edit the parser and run tests.",
                cwd=project,
                env=env,
            )

            recorded_args = json.loads(log_path.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["model"], "zai-coding-cn/glm-5.2")
        self.assertEqual(payload["thinking_level"], "high")
        self.assertEqual(payload["session_id"], "codex-pi-test")
        self.assertEqual(payload["project_root"], str(project.resolve()))
        self.assertEqual(payload["final_response"], "Pi completed the delegated task.")
        self.assertIn("--approve", recorded_args)
        self.assertNotIn("--no-approve", recorded_args)
        self.assertEqual(
            recorded_args[recorded_args.index("--model") + 1],
            "zai-coding-cn/glm-5.2",
        )
        self.assertEqual(recorded_args[recorded_args.index("--thinking") + 1], "high")

    def test_run_defaults_to_medium_and_generates_session_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, log_path = self.fake_environment(root)
            task_file = root / "task prompt.txt"
            task_file.write_text("Implement the bounded change.", encoding="utf-8")
            result = self.invoke(
                "--json",
                "run",
                "--task-file",
                str(task_file),
                cwd=root,
                env=env,
            )
            recorded_args = json.loads(log_path.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertRegex(payload["session_id"], r"^codex-pi-[0-9a-f]{32}$")
        self.assertEqual(payload["thinking_level"], "medium")
        self.assertEqual(recorded_args[recorded_args.index("--thinking") + 1], "medium")

    def test_run_accepts_every_pi_thinking_level(self) -> None:
        levels = ("off", "minimal", "low", "medium", "high", "xhigh", "max")
        for level in levels:
            with self.subTest(level=level), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                env, log_path = self.fake_environment(root)
                result = self.invoke(
                    "--json",
                    "run",
                    "--thinking-level",
                    level,
                    "Implement the bounded change.",
                    cwd=root,
                    env=env,
                )
                recorded_args = json.loads(log_path.read_text(encoding="utf-8"))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["thinking_level"], level)
            self.assertEqual(recorded_args[recorded_args.index("--thinking") + 1], level)

    def test_run_returns_stable_error_for_pi_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, _ = self.fake_environment(root, run_exit_code=7)
            result = self.invoke(
                "--json",
                "run",
                "--thinking-level",
                "high",
                "Try the implementation.",
                cwd=root,
                env=env,
            )

        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "pi_failed")
        self.assertEqual(payload["error"]["exit_code"], 7)

    def test_run_rejects_invalid_session_and_ambiguous_task_sources(self) -> None:
        invalid = self.invoke(
            "--json",
            "run",
            "--thinking-level",
            "high",
            "--session-id",
            "../escape",
            "Task",
        )
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("session ID", invalid.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, _ = self.fake_environment(root)
            task_file = root / "task.txt"
            task_file.write_text("Task from file", encoding="utf-8")
            ambiguous = self.invoke(
                "--json",
                "run",
                "--thinking-level",
                "medium",
                "--task-file",
                str(task_file),
                "Task argument",
                cwd=root,
                env=env,
            )

        self.assertEqual(ambiguous.returncode, 2)
        payload = json.loads(ambiguous.stdout)
        self.assertEqual(payload["error"]["code"], "ambiguous_task")


if __name__ == "__main__":
    unittest.main()
