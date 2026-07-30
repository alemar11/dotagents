from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import textwrap
import time
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
        event_delay: float = 0,
        event_mode: str = "valid",
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
                import signal
                import subprocess
                import sys
                import time

                args = sys.argv[1:]
                if "--version" in args:
                    print("0.82.1")
                    raise SystemExit(0)
                if "--list-models" in args:
                    print("provider model context max-out thinking images")
                    print({model_row!r})
                    raise SystemExit(0)
                task = sys.stdin.read()
                with open(os.environ["FAKE_PI_LOG"], "w", encoding="utf-8") as handle:
                    json.dump({{"args": args, "task": task}}, handle)
                mode = {event_mode!r}
                if mode == "invalid":
                    print("not-json", flush=True)
                    raise SystemExit({run_exit_code})
                if mode == "stderr-secret":
                    print("sensitive provider diagnostic", file=sys.stderr, flush=True)
                session_id = (
                    "resumed-pi-session"
                    if "--continue" in args
                    else args[args.index("--session-id") + 1]
                )
                message = {{
                    "role": "assistant",
                    "content": [{{"type": "text", "text": "Pi completed the delegated task."}}],
                }}
                print(json.dumps({{
                    "type": "session",
                    "version": 3,
                    "id": session_id,
                    "timestamp": "2026-07-30T00:00:00Z",
                    "cwd": os.getcwd(),
                }}), flush=True)
                print(json.dumps({{"type": "agent_start"}}), flush=True)
                if mode == "hang-with-child":
                    subprocess.Popen([
                        sys.executable,
                        "-c",
                        (
                            "import pathlib,sys,time; "
                            "time.sleep(2); "
                            "pathlib.Path(sys.argv[1]).write_text('survived', encoding='utf-8')"
                        ),
                        os.environ["FAKE_PI_CHILD_MARKER"],
                    ])
                    while True:
                        time.sleep(60)
                if mode == "hang":
                    while True:
                        time.sleep(60)
                if mode == "self-sigkill":
                    os.kill(os.getpid(), signal.SIGKILL)
                time.sleep({event_delay})
                print(json.dumps({{
                    "type": "tool_execution_start",
                    "toolCallId": "tool-1",
                    "toolName": "read",
                    "args": {{"path": "secret-source.txt"}},
                }}), flush=True)
                print(json.dumps({{
                    "type": "tool_execution_end",
                    "toolCallId": "tool-1",
                    "toolName": "read",
                    "result": {{"content": "sensitive tool output"}},
                    "isError": False,
                }}), flush=True)
                if mode != "missing-response":
                    print(json.dumps({{
                        "type": "message_end",
                        "message": message,
                    }}), flush=True)
                if mode != "missing-end":
                    messages = [] if mode == "missing-response" else [message]
                    print(json.dumps({{
                        "type": "agent_end",
                        "messages": messages,
                    }}), flush=True)
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
        self.assertEqual(version.stdout.strip(), "pi-delegate 0.3.1")

        help_result = self.invoke("--help")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("doctor", help_result.stdout)
        self.assertIn("run", help_result.stdout)
        self.assertIn("zai-coding-cn/glm-5.2", help_result.stdout)
        self.assertIn("bounded task", help_result.stdout)
        self.assertNotIn("coding task", help_result.stdout)

        run_help = self.invoke("run", "--help")
        self.assertEqual(run_help.returncode, 0, run_help.stderr)
        self.assertIn("--thinking-level", run_help.stdout)
        self.assertIn("--session-id", run_help.stdout)
        self.assertIn("--task-file", run_help.stdout)
        self.assertIn("--progress", run_help.stdout)
        self.assertIn("--heartbeat-seconds", run_help.stdout)
        self.assertIn("--timeout", run_help.stdout)
        self.assertIn("--resume-last", run_help.stdout)
        self.assertNotIn("--data-scope", run_help.stdout)
        self.assertIn("Delegated task", run_help.stdout)
        self.assertNotIn("Delegated coding task", run_help.stdout)

        metadata = METADATA.read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertIn("Delegate bounded tasks", metadata)
        self.assertNotIn("delegate coding work", metadata)

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

            recorded = json.loads(log_path.read_text(encoding="utf-8"))
            recorded_args = recorded["args"]

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["model"], "zai-coding-cn/glm-5.2")
        self.assertEqual(payload["thinking_level"], "high")
        self.assertEqual(payload["session_id"], "codex-pi-test")
        self.assertEqual(payload["project_root"], str(project.resolve()))
        self.assertEqual(payload["timeout_seconds"], 1800)
        self.assertIsNone(payload["signal"])
        self.assertEqual(payload["final_response"], "Pi completed the delegated task.")
        self.assertIn("--approve", recorded_args)
        self.assertNotIn("--no-approve", recorded_args)
        self.assertEqual(recorded_args[recorded_args.index("--mode") + 1], "json")
        self.assertEqual(
            recorded_args[recorded_args.index("--model") + 1],
            "zai-coding-cn/glm-5.2",
        )
        self.assertEqual(recorded_args[recorded_args.index("--thinking") + 1], "high")
        self.assertEqual(recorded["task"], "Edit the parser and run tests.")
        self.assertNotIn(recorded["task"], recorded_args)

    def test_run_defaults_to_medium_and_generates_session_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, log_path = self.fake_environment(root)
            task_file = root / "task prompt.txt"
            task = (
                "Explicitly invoke $maintainer and preserve `literal code`, "
                "\"double quotes\", and 'single quotes'."
            )
            task_file.write_text(task, encoding="utf-8")
            result = self.invoke(
                "--json",
                "run",
                "--task-file",
                str(task_file),
                cwd=root,
                env=env,
            )
            recorded = json.loads(log_path.read_text(encoding="utf-8"))
            recorded_args = recorded["args"]

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertRegex(payload["session_id"], r"^codex-pi-[0-9a-f]{32}$")
        self.assertEqual(payload["thinking_level"], "medium")
        self.assertEqual(recorded_args[recorded_args.index("--thinking") + 1], "medium")
        self.assertEqual(recorded["task"], task)

    def test_run_accepts_read_only_research_task_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, log_path = self.fake_environment(root)
            task = (
                "Research firsthand GitHub issues and discussions. Stay read-only, "
                "cite primary sources, and do not edit files."
            )
            result = self.invoke("--json", "run", task, cwd=root, env=env)
            recorded = json.loads(log_path.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(recorded["task"], task)
        self.assertNotIn(task, recorded["args"])

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
                recorded = json.loads(log_path.read_text(encoding="utf-8"))
                recorded_args = recorded["args"]

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["thinking_level"], level)
            self.assertEqual(recorded_args[recorded_args.index("--thinking") + 1], level)

    def test_resume_last_uses_continue_and_reports_actual_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, log_path = self.fake_environment(root)
            result = self.invoke(
                "--json",
                "run",
                "--resume-last",
                "Apply the bounded follow-up.",
                cwd=root,
                env=env,
            )
            recorded = json.loads(log_path.read_text(encoding="utf-8"))
            recorded_args = recorded["args"]

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["session_id"], "resumed-pi-session")
        self.assertIn("--continue", recorded_args)
        self.assertNotIn("--session-id", recorded_args)
        self.assertEqual(recorded["task"], "Apply the bounded follow-up.")

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
        self.assertEqual(payload["status"], "failed")
        self.assertEqual(payload["error"]["code"], "pi_failed")
        self.assertEqual(payload["error"]["exit_code"], 7)

    def test_raw_pi_stderr_is_suppressed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, _ = self.fake_environment(root, event_mode="stderr-secret")
            result = self.invoke(
                "--json",
                "run",
                "Inspect the project.",
                cwd=root,
                env=env,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("sensitive provider diagnostic", result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["suppressed_diagnostic_lines"], 1)

    def test_progress_streams_before_exit_and_redacts_event_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, _ = self.fake_environment(root, event_delay=0.5)
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(COMMAND),
                    "--json",
                    "run",
                    "--progress",
                    "--name",
                    "Streaming audit",
                    "Inspect the project.",
                ],
                cwd=str(root),
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            assert process.stderr is not None
            first_progress = json.loads(process.stderr.readline())
            self.assertEqual(first_progress["event"], "process_started")
            self.assertEqual(first_progress["name"], "Streaming audit")
            self.assertIsNone(process.poll())
            stdout, remaining_stderr = process.communicate(timeout=5)

        self.assertEqual(process.returncode, 0)
        final_payload = json.loads(stdout)
        self.assertTrue(final_payload["progress_enabled"])
        progress = [first_progress]
        progress.extend(
            json.loads(line)
            for line in remaining_stderr.splitlines()
            if line.strip()
        )
        events = [item["event"] for item in progress]
        self.assertIn("tool_started", events)
        self.assertIn("tool_finished", events)
        self.assertIn("agent_end", events)
        serialized = json.dumps(progress)
        self.assertNotIn("secret-source.txt", serialized)
        self.assertNotIn("sensitive tool output", serialized)
        self.assertNotIn("Pi completed the delegated task.", serialized)
        self.assertEqual(progress[-1]["event"], "process_finished")
        self.assertEqual(progress[-1]["status"], "completed")

    def test_progress_heartbeats_while_pi_is_quiet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, _ = self.fake_environment(root, event_delay=1.2)
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(COMMAND),
                    "--json",
                    "run",
                    "--progress",
                    "--heartbeat-seconds",
                    "1",
                    "Inspect the project.",
                ],
                cwd=str(root),
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            assert process.stderr is not None
            seen_heartbeat = False
            while True:
                progress = json.loads(process.stderr.readline())
                if progress["event"] == "heartbeat":
                    seen_heartbeat = True
                    self.assertIsNone(process.poll())
                    break
            stdout, _ = process.communicate(timeout=5)

        self.assertTrue(seen_heartbeat)
        self.assertTrue(json.loads(stdout)["ok"])

    def test_overlapping_sessions_have_independent_progress_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, _ = self.fake_environment(root, event_delay=0.5)
            processes: list[subprocess.Popen[str]] = []
            progress_records: list[dict[str, object]] = []
            for index in range(2):
                process_env = dict(env)
                process_env["FAKE_PI_LOG"] = str(root / f"pi-args-{index}.json")
                process = subprocess.Popen(
                    [
                        sys.executable,
                        str(COMMAND),
                        "--json",
                        "run",
                        "--progress",
                        "--name",
                        f"Concurrent task {index}",
                        "Inspect a disjoint scope.",
                    ],
                    cwd=str(root),
                    env=process_env,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                processes.append(process)

            for process in processes:
                assert process.stderr is not None
                progress_records.append(json.loads(process.stderr.readline()))

            self.assertTrue(all(process.poll() is None for process in processes))
            final_payloads = []
            for process in processes:
                stdout, _ = process.communicate(timeout=5)
                self.assertEqual(process.returncode, 0)
                final_payloads.append(json.loads(stdout))

        self.assertEqual(
            {record["name"] for record in progress_records},
            {"Concurrent task 0", "Concurrent task 1"},
        )
        self.assertEqual(
            len({record["session_id"] for record in progress_records}),
            2,
        )
        self.assertEqual(
            {payload["session_id"] for payload in final_payloads},
            {record["session_id"] for record in progress_records},
        )

    @unittest.skipUnless(os.name == "posix", "process-group behavior is POSIX-specific")
    def test_timeout_kills_the_complete_process_group(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, _ = self.fake_environment(root, event_mode="hang-with-child")
            marker = root / "child-survived.txt"
            env["FAKE_PI_CHILD_MARKER"] = str(marker)
            result = self.invoke(
                "--json",
                "run",
                "--timeout",
                "1s",
                "Run until the controller timeout.",
                cwd=root,
                env=env,
            )
            time.sleep(2.2)

        self.assertEqual(result.returncode, 1, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "timeout")
        self.assertEqual(payload["error"]["code"], "pi_timeout")
        self.assertEqual(payload["error"]["exit_code"], 124)
        self.assertEqual(payload["signal"], "SIGTERM")
        self.assertFalse(marker.exists(), "a Pi descendant survived the timeout")

    @unittest.skipUnless(os.name == "posix", "signal behavior is POSIX-specific")
    def test_controller_signal_reports_aborted_and_terminates_pi(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, _ = self.fake_environment(root, event_mode="hang")
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(COMMAND),
                    "--json",
                    "run",
                    "--progress",
                    "Wait for cancellation.",
                ],
                cwd=str(root),
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            assert process.stderr is not None
            json.loads(process.stderr.readline())
            process.send_signal(signal.SIGTERM)
            stdout, stderr = process.communicate(timeout=8)

        self.assertEqual(process.returncode, 1, stderr)
        payload = json.loads(stdout)
        self.assertEqual(payload["status"], "aborted")
        self.assertEqual(payload["signal"], "SIGTERM")
        self.assertEqual(payload["error"]["code"], "pi_aborted")

    @unittest.skipUnless(os.name == "posix", "signal behavior is POSIX-specific")
    def test_sigkill_is_reported_as_probable_host_kill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env, _ = self.fake_environment(root, event_mode="self-sigkill")
            result = self.invoke(
                "--json",
                "run",
                "Trigger a simulated host kill.",
                cwd=root,
                env=env,
            )

        self.assertEqual(result.returncode, 1, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "failed")
        self.assertEqual(payload["signal"], "SIGKILL")
        self.assertEqual(payload["error"]["code"], "host_killed")

    def test_invalid_or_incomplete_pi_event_stream_fails_closed(self) -> None:
        for event_mode in ("invalid", "missing-end", "missing-response"):
            with self.subTest(event_mode=event_mode), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                env, _ = self.fake_environment(root, event_mode=event_mode)
                result = self.invoke(
                    "--json",
                    "run",
                    "Inspect the project.",
                    cwd=root,
                    env=env,
                )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["code"], "pi_protocol_error")

    def test_run_rejects_invalid_session_and_ambiguous_task_sources(self) -> None:
        for timeout in ("0s", "soon", "1.5s"):
            with self.subTest(timeout=timeout):
                invalid_timeout = self.invoke(
                    "--json",
                    "run",
                    "--timeout",
                    timeout,
                    "Task",
                )
                self.assertEqual(invalid_timeout.returncode, 2)
                self.assertIn("timeout", invalid_timeout.stderr)

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

        conflicting_resume = self.invoke(
            "--json",
            "run",
            "--session-id",
            "known-session",
            "--resume-last",
            "Task",
        )
        self.assertEqual(conflicting_resume.returncode, 2)
        self.assertIn("not allowed with argument", conflicting_resume.stderr)

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
