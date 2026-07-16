from __future__ import annotations

import contextlib
import json
import importlib.machinery
import os
import shutil
import signal
import stat
import subprocess
import tempfile
import time
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/codex-session"
CLAIM_TOOL = ROOT.parent / "codex-orchestrator/scripts/orchestrator-claim"
RUNTIME = importlib.machinery.SourceFileLoader("codex_session_runtime", str(SCRIPT)).load_module()


def run(*args: str, env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT), *args],
        text=True,
        capture_output=True,
        env=env,
        check=check,
    )


class CliOrchestratorContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.cache = self.base / "cache"
        self.workspace = self.base / "workspace"
        self.workspace.mkdir()
        self.repo = self.workspace / "repo"
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "test@example.test"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "Test"], check=True)
        (self.repo / "README.md").write_text("base\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "base"], check=True)
        self.prompt = self.base / "prompt.md"
        self.prompt.write_text("Return a structured report.\n")
        self.schema = ROOT / "assets/worker-output-schema.json"
        self.ledger = self.base / "ledger.md"
        self.ledger.write_text("# ledger\n")
        self.manifest = self.base / "manifest.json"
        self.manifest.write_text(
            json.dumps(
                {
                    "schema_version": "1.0.0",
                    "run_id": "run-a",
                    "root_cwd": str(self.workspace),
                    "worktree_root": str(self.workspace / ".worktrees" / "run-a"),
                    "ledger_path": str(self.ledger),
                    "feature_specs": [
                        {
                            "spec_id": "spec-a",
                            "spec_ref": "#1",
                            "spec_title": "Spec A",
                            "prompt_path": str(self.prompt),
                            "output_schema_path": str(self.schema),
                            "repositories": [
                                {
                                    "repo_id": "repo",
                                    "source_path": str(self.repo),
                                    "base_ref": "HEAD",
                                    "target_branch": "feature/spec-a",
                                }
                            ],
                        }
                    ],
                }
            )
        )
        self.env = os.environ.copy()
        self.env["CODEX_CLI_ORCHESTRATOR_CACHE"] = str(self.cache)
        self.env["CODEX_ORCHESTRATOR_CLAIM_ROOT"] = str(self.base / "claims")

    def tearDown(self) -> None:
        subprocess.run(["tmux", "kill-session", "-t", self.tmux_session("run-a")], capture_output=True)
        self.temporary.cleanup()

    def tmux_session(self, run_id: str) -> str:
        with mock.patch.dict(os.environ, {"CODEX_CLI_ORCHESTRATOR_CACHE": str(self.cache)}):
            return RUNTIME.tmux_session(run_id)

    def test_shipped_artifact_and_doctor(self) -> None:
        self.assertEqual(run("--version").stdout.strip(), "0.5.0")
        doctor = json.loads(run("--json", "doctor").stdout)
        self.assertTrue(doctor["ok"])
        self.assertTrue(doctor["offline"])
        self.assertFalse(doctor["auth_required"])
        self.assertTrue(doctor["claim_helper"]["available"])
        self.assertTrue(doctor["tools"]["ps"]["available"])
        self.assertNotIn("core/merge-authorization.md", doctor["shared_core"]["files"])
        self.assertFalse(self.cache.exists(), "doctor must not create runtime state")

    def test_create_prepare_status_and_safe_cleanup(self) -> None:
        created = json.loads(run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env).stdout)
        self.assertEqual(created["state"], "created")
        self.assertTrue(created["atomic_claim"]["root_id"].startswith("cli-run-a-"))
        run_state = json.loads((self.cache / "run-a" / "status.json").read_text())
        self.assertEqual(run_state["atomic_claim_root_id"], created["atomic_claim"]["root_id"])
        prepared = json.loads(run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=self.env).stdout)
        self.assertEqual(prepared["state"], "prepared")
        worktree = Path(prepared["worktrees"][0]["path"])
        self.assertTrue(worktree.is_dir())
        (worktree / "change.txt").write_text("dirty\n")
        failed = run(
            "--json", "spec", "cleanup", "--run-id", "run-a", "--spec-id", "spec-a",
            "--disposition", "abandoned", env=self.env, check=False,
        )
        self.assertEqual(failed.returncode, 6)
        self.assertEqual(json.loads(failed.stdout)["error"]["code"], "unsafe-cleanup")

    def test_run_create_blocks_before_state_when_app_claim_overlaps(self) -> None:
        app_claim = subprocess.run(
            [
                str(CLAIM_TOOL),
                "--json",
                "claim",
                "acquire",
                "--root-id",
                "app-root",
                "--adapter",
                "codex-app-task",
                "--repository",
                str(self.repo),
                "--source",
                "https://example.test/specs/app-spec",
                "--ledger-ref",
                str(self.ledger),
            ],
            env=self.env,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(json.loads(app_claim.stdout)["state"], "acquired")
        result = run(
            "--json",
            "run",
            "create",
            "--manifest",
            str(self.manifest),
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 4)
        self.assertEqual(json.loads(result.stdout)["error"]["code"], "state-conflict")
        self.assertFalse((self.cache / "run-a").exists())

    def test_concurrent_run_create_has_one_claim_owner(self) -> None:
        command = [str(SCRIPT), "--json", "run", "create", "--manifest", str(self.manifest)]
        processes = [
            subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env)
            for _ in range(2)
        ]
        results = [process.communicate() + (process.returncode,) for process in processes]
        self.assertEqual(sorted(result[2] for result in results), [0, 4])
        winner = json.loads(next(stdout for stdout, _stderr, code in results if code == 0))
        run_state = json.loads((self.cache / "run-a" / "status.json").read_text())
        self.assertEqual(run_state["atomic_claim_root_id"], winner["atomic_claim"]["root_id"])
        status = subprocess.run(
            [str(CLAIM_TOOL), "--json", "claim", "status"],
            env=self.env,
            text=True,
            capture_output=True,
            check=True,
        )
        claims = json.loads(status.stdout)["claims"]
        self.assertEqual([claim["root_id"] for claim in claims], [run_state["atomic_claim_root_id"]])

    def test_same_run_id_nonoverlapping_creators_cannot_delete_winner(self) -> None:
        second_repo = self.workspace / "repo-two"
        subprocess.run(["git", "init", "-q", str(second_repo)], check=True)
        subprocess.run(["git", "-C", str(second_repo), "config", "user.email", "test@example.test"], check=True)
        subprocess.run(["git", "-C", str(second_repo), "config", "user.name", "Test"], check=True)
        (second_repo / "README.md").write_text("base\n")
        subprocess.run(["git", "-C", str(second_repo), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(second_repo), "commit", "-qm", "base"], check=True)
        alternate_value = json.loads(self.manifest.read_text())
        alternate_spec = alternate_value["feature_specs"][0]
        alternate_spec["spec_id"] = "spec-b"
        alternate_spec["spec_ref"] = "#2"
        alternate_spec["spec_title"] = "Spec B"
        alternate_spec["repositories"][0].update(
            {
                "repo_id": "repo-two",
                "source_path": str(second_repo),
                "target_branch": "feature/spec-b",
            }
        )
        alternate = self.base / "alternate-manifest.json"
        alternate.write_text(json.dumps(alternate_value))
        commands = [
            [str(SCRIPT), "--json", "run", "create", "--manifest", str(path)]
            for path in (self.manifest, alternate)
        ]
        processes = [
            subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env)
            for command in commands
        ]
        results = [process.communicate() + (process.returncode,) for process in processes]
        self.assertEqual(sorted(result[2] for result in results), [0, 4])
        stored = json.loads((self.cache / "run-a" / "manifest.json").read_text())
        self.assertIn(stored["feature_specs"][0]["spec_id"], {"spec-a", "spec-b"})
        self.assertEqual(json.loads((self.cache / "run-a" / "status.json").read_text())["state"], "created")
        claims = subprocess.run(
            [str(CLAIM_TOOL), "--json", "claim", "status"],
            env=self.env,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(len(json.loads(claims.stdout)["claims"]), 1)

    def test_same_local_spec_ref_in_independent_repositories_does_not_conflict(self) -> None:
        second_repo = self.workspace / "repo-two"
        subprocess.run(["git", "init", "-q", str(second_repo)], check=True)
        subprocess.run(["git", "-C", str(second_repo), "config", "user.email", "test@example.test"], check=True)
        subprocess.run(["git", "-C", str(second_repo), "config", "user.name", "Test"], check=True)
        (second_repo / "README.md").write_text("base\n")
        subprocess.run(["git", "-C", str(second_repo), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(second_repo), "commit", "-qm", "base"], check=True)
        alternate_value = json.loads(self.manifest.read_text())
        alternate_value["run_id"] = "run-b"
        alternate_value["worktree_root"] = str(self.workspace / ".worktrees" / "run-b")
        alternate_spec = alternate_value["feature_specs"][0]
        alternate_spec["spec_id"] = "spec-b"
        alternate_spec["repositories"][0].update(
            {"repo_id": "repo-two", "source_path": str(second_repo), "target_branch": "feature/spec-b"}
        )
        alternate = self.base / "alternate-run-manifest.json"
        alternate.write_text(json.dumps(alternate_value))
        first = json.loads(run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env).stdout)
        second = json.loads(run("--json", "run", "create", "--manifest", str(alternate), env=self.env).stdout)
        self.assertEqual(first["state"], "created")
        self.assertEqual(second["state"], "created")
        claims = subprocess.run(
            [str(CLAIM_TOOL), "--json", "claim", "status"],
            env=self.env,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(len(json.loads(claims.stdout)["claims"]), 2)

    def test_same_repo_relative_spec_ref_in_independent_repositories_does_not_conflict(self) -> None:
        first_value = json.loads(self.manifest.read_text())
        first_value["feature_specs"][0]["spec_ref"] = "planning/features/demo/SPEC.md"
        self.manifest.write_text(json.dumps(first_value))
        second_repo = self.workspace / "repo-two"
        subprocess.run(["git", "init", "-q", str(second_repo)], check=True)
        subprocess.run(["git", "-C", str(second_repo), "config", "user.email", "test@example.test"], check=True)
        subprocess.run(["git", "-C", str(second_repo), "config", "user.name", "Test"], check=True)
        (second_repo / "README.md").write_text("base\n")
        subprocess.run(["git", "-C", str(second_repo), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(second_repo), "commit", "-qm", "base"], check=True)
        alternate_value = json.loads(json.dumps(first_value))
        alternate_value["run_id"] = "run-b"
        alternate_value["worktree_root"] = str(self.workspace / ".worktrees" / "run-b")
        alternate_spec = alternate_value["feature_specs"][0]
        alternate_spec["spec_id"] = "spec-b"
        alternate_spec["repositories"][0].update(
            {"repo_id": "repo-two", "source_path": str(second_repo), "target_branch": "feature/spec-b"}
        )
        alternate = self.base / "relative-ref-run-manifest.json"
        alternate.write_text(json.dumps(alternate_value))
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        result = run("--json", "run", "create", "--manifest", str(alternate), env=self.env)
        self.assertEqual(json.loads(result.stdout)["state"], "created")

    def test_same_global_spec_ref_in_independent_repositories_conflicts(self) -> None:
        second_repo = self.workspace / "repo-two"
        subprocess.run(["git", "init", "-q", str(second_repo)], check=True)
        subprocess.run(["git", "-C", str(second_repo), "config", "user.email", "test@example.test"], check=True)
        subprocess.run(["git", "-C", str(second_repo), "config", "user.name", "Test"], check=True)
        (second_repo / "README.md").write_text("base\n")
        subprocess.run(["git", "-C", str(second_repo), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(second_repo), "commit", "-qm", "base"], check=True)
        durable_ref = "https://github.com/example/specs/issues/1"
        first_value = json.loads(self.manifest.read_text())
        first_value["feature_specs"][0]["spec_ref"] = durable_ref
        self.manifest.write_text(json.dumps(first_value))
        alternate_value = json.loads(json.dumps(first_value))
        alternate_value["run_id"] = "run-b"
        alternate_value["worktree_root"] = str(self.workspace / ".worktrees" / "run-b")
        alternate_spec = alternate_value["feature_specs"][0]
        alternate_spec["spec_id"] = "spec-b"
        alternate_spec["repositories"][0].update(
            {"repo_id": "repo-two", "source_path": str(second_repo), "target_branch": "feature/spec-b"}
        )
        alternate = self.base / "global-ref-manifest.json"
        alternate.write_text(json.dumps(alternate_value))
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        result = run(
            "--json", "run", "create", "--manifest", str(alternate), env=self.env, check=False
        )
        self.assertEqual(result.returncode, 4)
        self.assertFalse((self.cache / "run-b").exists())

    def test_concurrent_prepare_creates_one_worktree(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        command = [
            str(SCRIPT),
            "--json",
            "spec",
            "prepare",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
        ]
        processes = [
            subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env)
            for _ in range(2)
        ]
        results = [process.communicate() + (process.returncode,) for process in processes]
        self.assertEqual(sorted(result[2] for result in results), [0, 4])
        status = json.loads((self.cache / "run-a" / "specs" / "spec-a" / "status.json").read_text())
        self.assertEqual(status["state"], "prepared")
        worktree = self.workspace / ".worktrees" / "run-a" / "spec-a" / "repo"
        registered = subprocess.run(
            ["git", "-C", str(self.repo), "worktree", "list", "--porcelain"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        self.assertEqual(registered.count(f"worktree {worktree.resolve()}"), 1)

    def test_run_status_advances_claim_heartbeat(self) -> None:
        created = json.loads(run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env).stdout)
        root_id = created["atomic_claim"]["root_id"]
        before = created["atomic_claim"]["heartbeat_at"]
        time.sleep(0.01)
        run("--json", "run", "status", "--run-id", "run-a", env=self.env)
        observed = subprocess.run(
            [str(CLAIM_TOOL), "--json", "claim", "status", "--root-id", root_id],
            env=self.env,
            text=True,
            capture_output=True,
            check=True,
        )
        after = json.loads(observed.stdout)["claim"]["heartbeat_at"]
        self.assertGreater(after, before)

    def test_lost_claim_blocks_prepare_before_worktree_mutation(self) -> None:
        created = json.loads(run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env).stdout)
        subprocess.run(
            [
                str(CLAIM_TOOL),
                "--json",
                "claim",
                "release",
                "--root-id",
                created["atomic_claim"]["root_id"],
                "--expected-fingerprint",
                created["atomic_claim"]["fingerprint"],
                "--evidence",
                "fixture-simulated-ownership-loss",
            ],
            env=self.env,
            text=True,
            capture_output=True,
            check=True,
        )
        result = run(
            "--json",
            "spec",
            "prepare",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 3)
        self.assertEqual(json.loads(result.stdout)["error"]["code"], "not-found")
        self.assertFalse((self.workspace / ".worktrees" / "run-a").exists())

    def test_lost_claim_blocks_cleanup_before_worktree_mutation(self) -> None:
        created = json.loads(run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env).stdout)
        prepared = json.loads(
            run(
                "--json",
                "spec",
                "prepare",
                "--run-id",
                "run-a",
                "--spec-id",
                "spec-a",
                env=self.env,
            ).stdout
        )
        worktree = Path(prepared["worktrees"][0]["path"])
        (self.cache / "run-a" / "specs" / "spec-a" / "status.json").write_text(
            json.dumps({"state": "succeeded"})
        )
        subprocess.run(
            [
                str(CLAIM_TOOL),
                "--json",
                "claim",
                "release",
                "--root-id",
                created["atomic_claim"]["root_id"],
                "--expected-fingerprint",
                created["atomic_claim"]["fingerprint"],
                "--evidence",
                "fixture-simulated-ownership-loss",
            ],
            env=self.env,
            text=True,
            capture_output=True,
            check=True,
        )
        result = run(
            "--json",
            "spec",
            "cleanup",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            "--disposition",
            "integrated",
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 3)
        self.assertTrue(worktree.is_dir())

    def test_lost_claim_preserves_prior_final_artifact(self) -> None:
        created = json.loads(run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env).stdout)
        run(
            "--json",
            "spec",
            "prepare",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
        )
        directory = self.cache / "run-a" / "specs" / "spec-a"
        final = directory / "final.json"
        final.write_text("prior-final-evidence\n")
        subprocess.run(
            [
                str(CLAIM_TOOL),
                "--json",
                "claim",
                "release",
                "--root-id",
                created["atomic_claim"]["root_id"],
                "--expected-fingerprint",
                created["atomic_claim"]["fingerprint"],
                "--evidence",
                "fixture-simulated-ownership-loss",
            ],
            env=self.env,
            text=True,
            capture_output=True,
            check=True,
        )
        result = run(
            "_launch",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            "--cache-root",
            str(self.cache),
            "--claim-root",
            str(self.base / "claims"),
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 3)
        self.assertEqual(final.read_text(), "prior-final-evidence\n")

    def test_terminal_publication_stops_when_claim_is_lost(self) -> None:
        fake_bin = self.base / "terminal-bin"
        fake_bin.mkdir()
        fake_codex = fake_bin / "codex"
        fake_codex.write_text(
            "#!/bin/sh\n"
            "last=''\n"
            "while [ \"$#\" -gt 0 ]; do\n"
            "  if [ \"$1\" = '--output-last-message' ]; then shift; last=$1; fi\n"
            "  shift\n"
            "done\n"
            "printf '%s\\n' '{\"result_status\":\"ready\",\"summary\":\"ok\",\"changed_files\":[],\"validation\":[{\"command\":\"test\",\"result\":\"passed\",\"evidence\":\"ok\"}],\"generated_artifacts\":[],\"internal_subagents\":[],\"risks\":[],\"blockers\":[],\"recommended_root_action\":\"inspect\"}' > \"$last\"\n"
            "echo '{\"type\":\"thread.started\",\"thread_id\":\"99999999-9999-4999-8999-999999999999\"}'\n"
            "exit 0\n"
        )
        fake_codex.chmod(fake_codex.stat().st_mode | stat.S_IXUSR)
        env = self.env.copy()
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        run("--json", "run", "create", "--manifest", str(self.manifest), env=env)
        run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=env)
        directory = self.cache / "run-a" / "specs" / "spec-a"
        ownership_lost = RUNTIME.CliError("state-conflict", "fixture ownership lost", 4)
        lost_lease = mock.MagicMock()
        lost_lease.__enter__.side_effect = ownership_lost
        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch.object(RUNTIME, "run_claim_lease", side_effect=[nullcontext(), lost_lease]),
        ):
            result = RUNTIME.internal_launch("run-a", "spec-a", False)
        self.assertEqual(result, 4)
        self.assertTrue((directory / "final.json").is_file())
        self.assertFalse((directory / "codex_session_id").exists())
        self.assertFalse((directory / "exit_code").exists())
        status = json.loads((directory / "status.json").read_text())
        self.assertEqual(status["state"], "running")
        self.assertEqual(status["worker_group_model"], "persistent-anchor-v1")
        self.assertFalse(
            RUNTIME.process_group_live(status["worker_pgid"], status["worker_leader_started_at"])
        )

    def test_terminal_publication_proves_descendant_process_group_dead(self) -> None:
        fake_bin = self.base / "terminal-descendant-bin"
        fake_bin.mkdir()
        fake_codex = fake_bin / "codex"
        pgid_file = self.base / "terminal-descendant-pgid"
        report = {
            "result_status": "ready",
            "summary": "ok",
            "changed_files": [],
            "validation": [{"command": "test", "result": "passed", "evidence": "ok"}],
            "generated_artifacts": [],
            "internal_subagents": [],
            "risks": [],
            "blockers": [],
            "recommended_root_action": "inspect",
        }
        fake_codex.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, subprocess, sys\n"
            "args = sys.argv[1:]\n"
            "last = args[args.index('--output-last-message') + 1]\n"
            "subprocess.Popen(['sleep', '30'])\n"
            f"open({str(pgid_file)!r}, 'w').write(str(os.getpgrp()))\n"
            f"open(last, 'w').write(json.dumps({report!r}))\n"
            "print(json.dumps({'type':'thread.started','thread_id':'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'}))\n"
        )
        fake_codex.chmod(fake_codex.stat().st_mode | stat.S_IXUSR)
        env = self.env.copy()
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        run("--json", "run", "create", "--manifest", str(self.manifest), env=env)
        run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=env)
        with mock.patch.dict(os.environ, env, clear=True):
            result = RUNTIME.internal_launch("run-a", "spec-a", False)
        self.assertEqual(result, 0)
        self.assertTrue(pgid_file.is_file())
        self.assertFalse(RUNTIME.process_group_live(int(pgid_file.read_text())))
        status = json.loads((self.cache / "run-a" / "specs" / "spec-a" / "status.json").read_text())
        self.assertEqual(status["state"], "succeeded")
        self.assertFalse(status["worker_process_live"])

    def test_claim_loss_terminates_entire_worker_process_group(self) -> None:
        fake_bin = self.base / "claim-loss-bin"
        fake_bin.mkdir()
        fake_codex = fake_bin / "codex"
        worker_pgid_file = self.base / "claim-loss-worker-pgid"
        fake_codex.write_text(
            "#!/bin/sh\n"
            "sleep 30 &\n"
            f"/bin/ps -o pgid= -p $$ | /usr/bin/tr -d ' ' > \"{worker_pgid_file}\"\n"
            "wait\n"
        )
        fake_codex.chmod(fake_codex.stat().st_mode | stat.S_IXUSR)
        env = self.env.copy()
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        run("--json", "run", "create", "--manifest", str(self.manifest), env=env)
        run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=env)
        ownership_lost = RUNTIME.CliError("state-conflict", "fixture ownership lost", 4)

        def lose_ownership(_run_id: str) -> None:
            deadline = time.monotonic() + 2
            while not worker_pgid_file.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            raise ownership_lost

        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch.object(RUNTIME, "CLAIM_HEARTBEAT_SECONDS", 0.05),
            mock.patch.object(RUNTIME, "heartbeat_run_claim", side_effect=lose_ownership),
        ):
            result = RUNTIME.internal_launch("run-a", "spec-a", False)
        self.assertEqual(result, 4)
        self.assertTrue(worker_pgid_file.is_file())
        self.assertFalse(RUNTIME.process_group_live(int(worker_pgid_file.read_text().strip())))

    def test_failed_run_creation_rolls_back_and_can_retry(self) -> None:
        with mock.patch.dict(os.environ, self.env, clear=True):
            with mock.patch.object(RUNTIME, "write_json", side_effect=OSError("fixture write failure")):
                with self.assertRaises(OSError):
                    RUNTIME.create_run(self.manifest)
            self.assertFalse((self.cache / "run-a").exists())
            claims = subprocess.run(
                [str(CLAIM_TOOL), "--json", "claim", "status"],
                env=self.env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(json.loads(claims.stdout)["claims"], [])
            retried = RUNTIME.create_run(self.manifest)
        self.assertEqual(retried["state"], "created")

    def test_run_cleanup_recovers_after_claim_was_released(self) -> None:
        created = json.loads(run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env).stdout)
        (self.cache / "run-a" / "specs" / "spec-a" / "status.json").write_text(
            json.dumps({"state": "cleaned", "disposition": "integrated"})
        )
        claim = created["atomic_claim"]
        (self.cache / "run-a" / "status.json").write_text(
            json.dumps(
                {
                    "state": "releasing",
                    "atomic_claim_root_id": claim["root_id"],
                    "atomic_claim_fingerprint": claim["fingerprint"],
                }
            )
        )
        subprocess.run(
            [
                str(CLAIM_TOOL),
                "--json",
                "claim",
                "release",
                "--root-id",
                claim["root_id"],
                "--expected-fingerprint",
                claim["fingerprint"],
                "--evidence",
                "fixture-release-before-final-checkpoint",
            ],
            env=self.env,
            text=True,
            capture_output=True,
            check=True,
        )
        recovered = json.loads(
            run("--json", "run", "cleanup", "--run-id", "run-a", env=self.env).stdout
        )
        self.assertEqual(recovered["state"], "cleaned")
        self.assertEqual(recovered["atomic_claim"]["state"], "already-released")
        persisted = json.loads((self.cache / "run-a" / "status.json").read_text())
        self.assertEqual(persisted["atomic_claim_state"], "released")

    def test_rejects_noncanonical_or_overlapping_manifest(self) -> None:
        value = json.loads(self.manifest.read_text())
        value["unknown_option"] = True
        self.manifest.write_text(json.dumps(value))
        result = run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["error"]["code"], "invalid-input")

    def test_rejects_noncanonical_worker_output_schema(self) -> None:
        custom_schema = self.base / "custom-schema.json"
        custom_schema.write_text(json.dumps({"type": "object"}))
        value = json.loads(self.manifest.read_text())
        value["feature_specs"][0]["output_schema_path"] = str(custom_schema)
        self.manifest.write_text(json.dumps(value))
        result = run(
            "--json", "run", "create", "--manifest", str(self.manifest),
            env=self.env, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("shipped worker-output-schema.json", json.loads(result.stdout)["error"]["message"])

    def test_rejects_same_branch_through_linked_source_checkout(self) -> None:
        linked = self.workspace / "repo-linked"
        subprocess.run(
            ["git", "-C", str(self.repo), "worktree", "add", "-qb", "linked-source", str(linked), "HEAD"],
            check=True,
        )
        value = json.loads(self.manifest.read_text())
        second = json.loads(json.dumps(value["feature_specs"][0]))
        second["spec_id"] = "spec-b"
        second["spec_ref"] = "#2"
        second["spec_title"] = "Spec B"
        second["repositories"][0]["source_path"] = str(linked)
        value["feature_specs"].append(second)
        self.manifest.write_text(json.dumps(value))
        result = run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("target branch is shared", json.loads(result.stdout)["error"]["message"])

    def test_rejects_worktree_root_outside_workspace(self) -> None:
        value = json.loads(self.manifest.read_text())
        value["worktree_root"] = str(self.base / "outside")
        self.manifest.write_text(json.dumps(value))
        result = run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("strict descendant", json.loads(result.stdout)["error"]["message"])

    def test_cached_manifest_is_canonical_and_revalidated(self) -> None:
        workspace_link = self.base / "workspace-link"
        workspace_link.symlink_to(self.workspace, target_is_directory=True)
        value = json.loads(self.manifest.read_text())
        value["root_cwd"] = str(workspace_link)
        value["worktree_root"] = str(workspace_link / ".worktrees" / "run-a")
        self.manifest.write_text(json.dumps(value))
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        stored_path = self.cache / "run-a" / "manifest.json"
        stored = json.loads(stored_path.read_text())
        self.assertEqual(stored["root_cwd"], str(self.workspace.resolve()))
        stored["worktree_root"] = str(self.base / "tampered-outside")
        stored_path.write_text(json.dumps(stored))
        result = run(
            "--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a",
            env=self.env, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("strict descendant", json.loads(result.stdout)["error"]["message"])

    def test_existing_worktree_path_must_match_source_and_branch(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        path = self.workspace / ".worktrees" / "run-a" / "spec-a" / "repo"
        path.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(path)], check=True)
        result = run(
            "--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a",
            env=self.env, check=False,
        )
        self.assertEqual(result.returncode, 4)
        self.assertIn("identity does not match", json.loads(result.stdout)["error"]["message"])

    def test_launch_revalidates_prepared_branch(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        prepared = json.loads(run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=self.env).stdout)
        worktree = prepared["worktrees"][0]["path"]
        subprocess.run(["git", "-C", worktree, "switch", "-qc", "wrong-branch"], check=True)
        result = run(
            "--json", "spec", "start", "--run-id", "run-a", "--spec-id", "spec-a",
            env=self.env, check=False,
        )
        self.assertEqual(result.returncode, 4)
        self.assertIn("identity does not match", json.loads(result.stdout)["error"]["message"])

    def test_multi_repo_cleanup_preflights_before_removal(self) -> None:
        second = self.workspace / "repo-two"
        subprocess.run(["git", "init", "-q", str(second)], check=True)
        subprocess.run(["git", "-C", str(second), "config", "user.email", "test@example.test"], check=True)
        subprocess.run(["git", "-C", str(second), "config", "user.name", "Test"], check=True)
        (second / "README.md").write_text("base\n")
        subprocess.run(["git", "-C", str(second), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(second), "commit", "-qm", "base"], check=True)
        value = json.loads(self.manifest.read_text())
        value["feature_specs"][0]["repositories"].append(
            {
                "repo_id": "repo-two",
                "source_path": str(second),
                "base_ref": "HEAD",
                "target_branch": "feature/spec-a",
            }
        )
        self.manifest.write_text(json.dumps(value))
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        prepared = json.loads(run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=self.env).stdout)
        first = Path(prepared["worktrees"][0]["path"])
        second_worktree = Path(prepared["worktrees"][1]["path"])
        (second_worktree / "dirty.txt").write_text("dirty\n")
        (self.cache / "run-a" / "specs" / "spec-a" / "status.json").write_text(json.dumps({"state": "succeeded"}))
        result = run(
            "--json", "spec", "cleanup", "--run-id", "run-a", "--spec-id", "spec-a",
            "--disposition", "integrated", env=self.env, check=False,
        )
        self.assertEqual(result.returncode, 6)
        self.assertTrue(first.is_dir(), "first worktree must remain after a later dirty preflight")

    def test_prepared_spec_can_be_abandoned_before_launch(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        prepared = json.loads(
            run(
                "--json",
                "spec",
                "prepare",
                "--run-id",
                "run-a",
                "--spec-id",
                "spec-a",
                env=self.env,
            ).stdout
        )
        worktree = Path(prepared["worktrees"][0]["path"])
        cleaned = json.loads(
            run(
                "--json",
                "spec",
                "cleanup",
                "--run-id",
                "run-a",
                "--spec-id",
                "spec-a",
                "--disposition",
                "abandoned",
                env=self.env,
            ).stdout
        )
        self.assertEqual(cleaned["state"], "cleaned")
        self.assertFalse(worktree.exists())

    def test_partial_prepare_failure_can_be_abandoned(self) -> None:
        second = self.workspace / "repo-two"
        subprocess.run(["git", "init", "-q", str(second)], check=True)
        subprocess.run(["git", "-C", str(second), "config", "user.email", "test@example.test"], check=True)
        subprocess.run(["git", "-C", str(second), "config", "user.name", "Test"], check=True)
        (second / "README.md").write_text("base\n")
        subprocess.run(["git", "-C", str(second), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(second), "commit", "-qm", "base"], check=True)
        value = json.loads(self.manifest.read_text())
        value["feature_specs"][0]["repositories"].append(
            {
                "repo_id": "repo-two",
                "source_path": str(second),
                "base_ref": "HEAD",
                "target_branch": "feature/spec-a",
            }
        )
        self.manifest.write_text(json.dumps(value))
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        invalid_second_path = self.workspace / ".worktrees" / "run-a" / "spec-a" / "repo-two"
        invalid_second_path.mkdir(parents=True)
        result = run(
            "--json",
            "spec",
            "prepare",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 4)
        status_path = self.cache / "run-a" / "specs" / "spec-a" / "status.json"
        status = json.loads(status_path.read_text())
        self.assertEqual(status["state"], "prepare-failed")
        self.assertEqual(status["prepared_repo_ids"], ["repo"])
        first_worktree = self.workspace / ".worktrees" / "run-a" / "spec-a" / "repo"
        self.assertTrue(first_worktree.is_dir())
        cleaned = json.loads(
            run(
                "--json",
                "spec",
                "cleanup",
                "--run-id",
                "run-a",
                "--spec-id",
                "spec-a",
                "--disposition",
                "abandoned",
                env=self.env,
            ).stdout
        )
        self.assertEqual(cleaned["removed"], [str(first_worktree.resolve())])
        self.assertFalse(first_worktree.exists())
        self.assertTrue(invalid_second_path.is_dir())
        run("--json", "run", "cleanup", "--run-id", "run-a", env=self.env)

    def test_cleanup_recovers_after_removal_before_state_update(self) -> None:
        second = self.workspace / "repo-two"
        subprocess.run(["git", "init", "-q", str(second)], check=True)
        subprocess.run(["git", "-C", str(second), "config", "user.email", "test@example.test"], check=True)
        subprocess.run(["git", "-C", str(second), "config", "user.name", "Test"], check=True)
        (second / "README.md").write_text("base\n")
        subprocess.run(["git", "-C", str(second), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(second), "commit", "-qm", "base"], check=True)
        value = json.loads(self.manifest.read_text())
        value["feature_specs"][0]["repositories"].append(
            {
                "repo_id": "repo-two",
                "source_path": str(second),
                "base_ref": "HEAD",
                "target_branch": "feature/spec-a",
            }
        )
        self.manifest.write_text(json.dumps(value))
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        prepared = json.loads(run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=self.env).stdout)
        first = Path(prepared["worktrees"][0]["path"])
        second_worktree = Path(prepared["worktrees"][1]["path"])
        subprocess.run(["git", "-C", str(self.repo), "worktree", "remove", str(first)], check=True)
        status_path = self.cache / "run-a" / "specs" / "spec-a" / "status.json"
        status_path.write_text(
            json.dumps(
                {
                    "state": "cleaning",
                    "disposition": "integrated",
                    "cleanup_repo_ids": ["repo", "repo-two"],
                    "pending_repo_ids": ["repo", "repo-two"],
                    "removed_worktrees": [],
                    "removing_repo_id": "repo",
                }
            )
        )
        recovered = json.loads(
            run(
                "--json", "spec", "cleanup", "--run-id", "run-a", "--spec-id", "spec-a",
                "--disposition", "integrated", env=self.env,
            ).stdout
        )
        self.assertEqual(recovered["state"], "cleaned")
        self.assertFalse(second_worktree.exists())
        self.assertEqual(len(recovered["removed"]), 2)

    def test_cleanup_recovery_rejects_disposition_change(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        prepared = json.loads(run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=self.env).stdout)
        worktree = Path(prepared["worktrees"][0]["path"])
        status_path = self.cache / "run-a" / "specs" / "spec-a" / "status.json"
        status_path.write_text(
            json.dumps(
                {
                    "state": "cleaning",
                    "disposition": "integrated",
                    "cleanup_repo_ids": ["repo"],
                    "pending_repo_ids": ["repo"],
                    "removed_worktrees": [],
                }
            )
        )
        result = run(
            "--json", "spec", "cleanup", "--run-id", "run-a", "--spec-id", "spec-a",
            "--disposition", "abandoned", env=self.env, check=False,
        )
        self.assertEqual(result.returncode, 6)
        self.assertIn("cannot change", json.loads(result.stdout)["error"]["message"])
        self.assertTrue(worktree.is_dir())

    def test_cleanup_recovers_empty_pending_final_checkpoint(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        prepared = json.loads(run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=self.env).stdout)
        worktree = Path(prepared["worktrees"][0]["path"])
        subprocess.run(["git", "-C", str(self.repo), "worktree", "remove", str(worktree)], check=True)
        status_path = self.cache / "run-a" / "specs" / "spec-a" / "status.json"
        status_path.write_text(
            json.dumps(
                {
                    "state": "cleaning",
                    "disposition": "integrated",
                    "cleanup_repo_ids": ["repo"],
                    "pending_repo_ids": [],
                    "removed_worktrees": [str(worktree)],
                }
            )
        )
        recovered = json.loads(
            run(
                "--json", "spec", "cleanup", "--run-id", "run-a", "--spec-id", "spec-a",
                "--disposition", "integrated", env=self.env,
            ).stdout
        )
        self.assertEqual(recovered["state"], "cleaned")
        self.assertEqual(recovered["removed"], [str(worktree)])

    def test_nonterminal_feature_spec_cap_is_three(self) -> None:
        value = json.loads(self.manifest.read_text())
        template = value["feature_specs"][0]
        value["feature_specs"] = []
        for index in range(1, 5):
            spec = json.loads(json.dumps(template))
            spec["spec_id"] = f"spec-{index}"
            spec["spec_ref"] = f"#{index}"
            spec["spec_title"] = f"Spec {index}"
            spec["repositories"][0]["target_branch"] = f"feature/spec-{index}"
            value["feature_specs"].append(spec)
        self.manifest.write_text(json.dumps(value))
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-4", env=self.env)
        for index in range(1, 4):
            status = self.cache / "run-a" / "specs" / f"spec-{index}" / "status.json"
            status.write_text(json.dumps({"state": "succeeded"}))
        fourth = self.cache / "run-a" / "specs" / "spec-4" / "status.json"
        fourth.write_text(json.dumps({"state": "prepared"}))
        result = run(
            "--json", "spec", "start", "--run-id", "run-a", "--spec-id", "spec-4",
            env=self.env, check=False,
        )
        self.assertEqual(result.returncode, 4)
        self.assertIn("three Feature Spec executions", json.loads(result.stdout)["error"]["message"])

    def test_dead_window_and_run_failure_are_not_complete(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        status_path = self.cache / "run-a" / "specs" / "spec-a" / "status.json"
        status_path.write_text(json.dumps({"state": "running"}))
        stopped = json.loads(run("--json", "spec", "status", "--run-id", "run-a", "--spec-id", "spec-a", env=self.env).stdout)
        self.assertEqual(stopped["state"], "stopped")
        self.assertEqual(stopped["recovery_reason"], "tmux-window-not-live")
        blocked = json.loads(run("--json", "run", "status", "--run-id", "run-a", env=self.env).stdout)
        self.assertEqual(blocked["state"], "blocked")
        status_path.write_text(json.dumps({"state": "cleaned", "disposition": "integrated"}))
        complete = json.loads(run("--json", "run", "status", "--run-id", "run-a", env=self.env).stdout)
        self.assertEqual(complete["state"], "complete")

    def test_stop_failure_keeps_running_state_retryable(self) -> None:
        writes: list[dict[str, object]] = []
        failed = subprocess.CompletedProcess(["tmux"], 1, "", "kill failed")
        with (
            mock.patch.object(RUNTIME, "run_lock", return_value=nullcontext()),
            mock.patch.object(RUNTIME, "heartbeat_run_claim"),
            mock.patch.object(RUNTIME, "run_claim_lease", return_value=nullcontext()),
            mock.patch.object(RUNTIME, "read_status", return_value={"state": "running", "tmux_live": True}),
            mock.patch.object(RUNTIME, "command", return_value=failed),
            mock.patch.object(RUNTIME, "has_tmux_target", return_value=True),
            mock.patch.object(RUNTIME, "write_json", side_effect=lambda _path, value: writes.append(value)),
        ):
            with self.assertRaises(RUNTIME.CliError) as raised:
                RUNTIME.stop_spec("run-a", "spec-a")
        self.assertEqual(raised.exception.code, "state-conflict")
        self.assertEqual(writes[-1]["state"], "running")
        self.assertEqual(writes[-1]["reason"], "tmux-stop-failed")

    def test_required_process_group_termination_outlives_soft_deadline(self) -> None:
        members = [
            {"pid": 4242, "started_at": "Wed Jul 15 11:00:00 2026"},
            {"pid": 4243, "started_at": "Wed Jul 15 11:00:01 2026"},
        ]
        with (
            mock.patch.object(
                RUNTIME,
                "persistent_anchor_snapshot",
                side_effect=[("matching-anchor", members), ("matching-anchor", members)],
            ),
            mock.patch.object(RUNTIME, "process_group_live", return_value=False),
            mock.patch.object(RUNTIME.time, "monotonic", side_effect=[0, 6]),
            mock.patch.object(RUNTIME.time, "sleep"),
            mock.patch.object(RUNTIME.os, "killpg") as killpg,
        ):
            terminated = RUNTIME.terminate_anchored_process_group(
                4242,
                leader_started_at="Wed Jul 15 11:00:00 2026",
                require_death=True,
            )
        self.assertTrue(terminated)
        self.assertEqual(
            [call.args[1] for call in killpg.call_args_list],
            [signal.SIGTERM, signal.SIGKILL],
        )

    def test_worker_anchor_reserves_pgid_after_codex_child_exits(self) -> None:
        control = self.base / "anchor-control.json"
        events = self.base / "anchor-events.jsonl"
        stderr = self.base / "anchor-stderr.log"
        config = self.base / "anchor-config.json"
        config.write_text(
            json.dumps(
                {
                    "args": ["/bin/sh", "-c", "exit 0"],
                    "cwd": str(self.base),
                    "prompt": str(self.prompt),
                    "events": str(events),
                    "stderr": str(stderr),
                    "control": str(control),
                }
            )
        )
        anchor = subprocess.Popen(
            [str(SCRIPT), "_worker_anchor", "--config", str(config)],
            start_new_session=True,
        )
        try:
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                if control.is_file() and json.loads(control.read_text()).get("state") == "exited":
                    break
                time.sleep(0.01)
            self.assertEqual(json.loads(control.read_text())["state"], "exited")
            self.assertIsNone(anchor.poll(), "the persistent group leader must outlive the Codex child")
            started_at = RUNTIME.process_started_at(anchor.pid)
            self.assertEqual(
                RUNTIME.persistent_anchor_snapshot(anchor.pid, started_at)[0],
                "matching-anchor",
            )
        finally:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(anchor.pid, signal.SIGKILL)
            anchor.wait(timeout=2)

    def test_reused_process_group_id_is_not_treated_as_the_worker(self) -> None:
        with mock.patch.object(
            RUNTIME,
            "process_group_members",
            return_value=[{"pid": 4242, "started_at": "Wed Jul 15 12:00:00 2026"}],
        ):
            self.assertFalse(
                RUNTIME.process_group_live(4242, "Wed Jul 15 11:00:00 2026")
            )

    def test_stop_refuses_unverifiable_legacy_process_group(self) -> None:
        with (
            mock.patch.object(RUNTIME, "run_lock", return_value=nullcontext()),
            mock.patch.object(RUNTIME, "run_claim_lease", return_value=nullcontext()),
            mock.patch.object(
                RUNTIME,
                "read_status",
                return_value={
                    "state": "running",
                    "tmux_live": True,
                    "worker_pgid": 4242,
                    "worker_process_live": True,
                    "worker_process_identity": "unverifiable",
                },
            ),
            mock.patch.object(RUNTIME, "command") as command_mock,
            mock.patch.object(RUNTIME.os, "killpg") as killpg,
        ):
            with self.assertRaises(RUNTIME.CliError) as raised:
                RUNTIME.stop_spec("run-a", "spec-a")
        self.assertEqual(raised.exception.code, "state-conflict")
        command_mock.assert_not_called()
        killpg.assert_not_called()

    def test_long_tmux_identifiers_have_hash_suffixes(self) -> None:
        prefix = "a" * 80
        self.assertNotEqual(RUNTIME.tmux_session(prefix + "x"), RUNTIME.tmux_session(prefix + "y"))
        self.assertNotEqual(RUNTIME.tmux_window(prefix + "x"), RUNTIME.tmux_window(prefix + "y"))
        self.assertLessEqual(len(RUNTIME.tmux_session(prefix)), 64)
        self.assertLessEqual(len(RUNTIME.tmux_window(prefix)), 64)

    def test_tmux_session_identity_includes_run_store(self) -> None:
        with mock.patch.dict(os.environ, {"CODEX_CLI_ORCHESTRATOR_CACHE": str(self.base / "cache-a")}):
            first = RUNTIME.tmux_session("same-run")
        with mock.patch.dict(os.environ, {"CODEX_CLI_ORCHESTRATOR_CACHE": str(self.base / "cache-b")}):
            second = RUNTIME.tmux_session("same-run")
        self.assertNotEqual(first, second)

    def test_cli_docs_exclude_visible_app_task_surface(self) -> None:
        files = [ROOT / "SKILL.md", ROOT / "agents/openai.yaml"]
        files.extend((ROOT / "references").glob("*.md"))
        text = "\n".join(path.read_text() for path in files).lower()
        for token in ("create_thread", "read_thread", "visible_app_task_permission", "task-owned goal"):
            self.assertNotIn(token, text)
        self.assertIn("tmux", text)
        self.assertIn("codex exec", text)
        self.assertIn("root alone owns", text)
        skill = (ROOT / "SKILL.md").read_text()
        self.assertIn("core/options.md", skill)
        self.assertNotIn("- `options.md` for common authority", skill)
        before_dispatch = skill.split("Before dispatch, load", 1)[1].split(
            "## Post-Conclusion Merge Authorization", 1
        )[0]
        post_conclusion = skill.split("## Post-Conclusion Merge Authorization", 1)[1].split(
            "## Controller Loop", 1
        )[0]
        self.assertNotIn("merge-authorization.md", before_dispatch)
        self.assertIn("merge-authorization.md", post_conclusion)
        self.assertIn("only after the selected delivery target", post_conclusion)
        self.assertNotIn("tmux send-keys", (ROOT / "scripts/codex-session").read_text())
        self.assertTrue((ROOT / "assets/worker-output-schema.json").is_file())

    @unittest.skipUnless(shutil.which("tmux"), "tmux is required")
    def test_tmux_worker_produces_structured_artifacts(self) -> None:
        fake_bin = self.base / "bin"
        fake_bin.mkdir()
        fake_codex = fake_bin / "codex"
        cwd_evidence = self.base / "codex-cwd"
        fake_codex.write_text(
            "#!/bin/sh\n"
            f"pwd > \"{cwd_evidence}\"\n"
            "last=''\n"
            "while [ \"$#\" -gt 0 ]; do\n"
            "  if [ \"$1\" = '--output-last-message' ]; then shift; last=$1; fi\n"
            "  shift\n"
            "done\n"
            "printf '%s\\n' '{\"result_status\":\"ready\",\"summary\":\"ok\",\"changed_files\":[],\"validation\":[{\"command\":\"test\",\"result\":\"passed\",\"evidence\":\"ok\"}],\"generated_artifacts\":[],\"internal_subagents\":[],\"risks\":[],\"blockers\":[],\"recommended_root_action\":\"inspect\"}' > \"$last\"\n"
            "echo '{\"type\":\"thread.started\",\"thread_id\":\"11111111-1111-4111-8111-111111111111\"}'\n"
            "exit 0\n"
        )
        fake_codex.chmod(fake_codex.stat().st_mode | stat.S_IXUSR)
        env = self.env.copy()
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        run("--json", "run", "create", "--manifest", str(self.manifest), env=env)
        run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=env)
        started = json.loads(run("--json", "spec", "start", "--run-id", "run-a", "--spec-id", "spec-a", env=env).stdout)
        self.assertIn(started["state"], {"running", "succeeded"})
        status = {}
        for _ in range(40):
            time.sleep(0.05)
            status = json.loads(run("--json", "spec", "status", "--run-id", "run-a", "--spec-id", "spec-a", env=env).stdout)
            if status["state"] == "succeeded":
                break
        self.assertEqual(status["state"], "succeeded")
        self.assertEqual(status["codex_session_id"], "11111111-1111-4111-8111-111111111111")
        self.assertTrue(Path(status["artifacts"]["events.jsonl"]).is_file())
        self.assertTrue(Path(status["artifacts"]["exit_code"]).is_file())
        self.assertEqual(
            Path(cwd_evidence.read_text().strip()).resolve(),
            (self.workspace / ".worktrees" / "run-a" / "spec-a" / "repo").resolve(),
        )
        run(
            "--json", "spec", "cleanup", "--run-id", "run-a", "--spec-id", "spec-a",
            "--disposition", "integrated", env=env,
        )
        cleaned = json.loads(run("--json", "run", "cleanup", "--run-id", "run-a", env=env).stdout)
        self.assertEqual(cleaned["state"], "cleaned")

    @unittest.skipUnless(shutil.which("tmux"), "tmux is required")
    def test_stop_terminates_detached_codex_process_group(self) -> None:
        fake_bin = self.base / "stop-bin"
        fake_bin.mkdir()
        fake_codex = fake_bin / "codex"
        pid_file = self.base / "codex-worker-pid"
        fake_codex.write_text(
            "#!/bin/sh\n"
            f"echo $$ > \"{pid_file}\"\n"
            "trap 'exit 0' TERM INT HUP\n"
            "while :; do sleep 1; done\n"
        )
        fake_codex.chmod(fake_codex.stat().st_mode | stat.S_IXUSR)
        env = self.env.copy()
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        run("--json", "run", "create", "--manifest", str(self.manifest), env=env)
        run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=env)
        run("--json", "spec", "start", "--run-id", "run-a", "--spec-id", "spec-a", env=env)
        observed = {}
        for _ in range(100):
            time.sleep(0.05)
            observed = json.loads(
                run("--json", "spec", "status", "--run-id", "run-a", "--spec-id", "spec-a", env=env).stdout
            )
            if observed.get("worker_pgid") and pid_file.exists():
                break
        self.assertTrue(observed.get("worker_process_live"))
        worker_pid = int(pid_file.read_text().strip())
        stopped = json.loads(
            run("--json", "spec", "stop", "--run-id", "run-a", "--spec-id", "spec-a", env=env).stdout
        )
        self.assertEqual(stopped["state"], "stopped")
        with self.assertRaises(ProcessLookupError):
            os.kill(worker_pid, 0)
        run(
            "--json",
            "spec",
            "cleanup",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            "--disposition",
            "abandoned",
            env=env,
        )

    @unittest.skipUnless(shutil.which("tmux"), "tmux is required")
    def test_zero_exit_without_final_report_fails_supervision(self) -> None:
        fake_bin = self.base / "bin"
        fake_bin.mkdir()
        fake_codex = fake_bin / "codex"
        fake_codex.write_text(
            "#!/bin/sh\n"
            "echo '{\"type\":\"thread.started\",\"thread_id\":\"22222222-2222-4222-8222-222222222222\"}'\n"
            "exit 0\n"
        )
        fake_codex.chmod(fake_codex.stat().st_mode | stat.S_IXUSR)
        env = self.env.copy()
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        run("--json", "run", "create", "--manifest", str(self.manifest), env=env)
        run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=env)
        run("--json", "spec", "start", "--run-id", "run-a", "--spec-id", "spec-a", env=env)
        status = {}
        for _ in range(40):
            time.sleep(0.05)
            status = json.loads(run("--json", "spec", "status", "--run-id", "run-a", "--spec-id", "spec-a", env=env).stdout)
            if status["state"] == "failed":
                break
        self.assertEqual(status["state"], "failed")
        self.assertEqual(status["artifact_error"], "final-report-missing")
        self.assertEqual(status["process_returncode"], 0)
        self.assertEqual(status["returncode"], 5)
        self.assertEqual(Path(status["artifacts"]["exit_code"]).read_text().strip(), "5")

    def test_resume_recovers_session_id_from_events(self) -> None:
        fake_bin = self.base / "bin"
        fake_bin.mkdir()
        fake_codex = fake_bin / "codex"
        fake_codex.write_text(
            "#!/bin/sh\n"
            "last=''\n"
            "while [ \"$#\" -gt 0 ]; do\n"
            "  if [ \"$1\" = '--output-last-message' ]; then shift; last=$1; fi\n"
            "  shift\n"
            "done\n"
            "printf '%s\\n' '{\"result_status\":\"ready\",\"summary\":\"resumed\",\"changed_files\":[],\"validation\":[{\"command\":\"test\",\"result\":\"passed\",\"evidence\":\"ok\"}],\"generated_artifacts\":[],\"internal_subagents\":[],\"risks\":[],\"blockers\":[],\"recommended_root_action\":\"inspect\"}' > \"$last\"\n"
            "exit 0\n"
        )
        fake_codex.chmod(fake_codex.stat().st_mode | stat.S_IXUSR)
        env = self.env.copy()
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        run("--json", "run", "create", "--manifest", str(self.manifest), env=env)
        run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=env)
        directory = self.cache / "run-a" / "specs" / "spec-a"
        (directory / "status.json").write_text(json.dumps({"state": "running"}))
        recovered_session_id = "33333333-3333-4333-8333-333333333333"
        (directory / "events.jsonl").write_text(
            json.dumps({"type": "thread.started", "thread_id": recovered_session_id}) + "\n"
        )
        result = run(
            "_launch", "--run-id", "run-a", "--spec-id", "spec-a",
            "--cache-root", str(self.cache), "--claim-root", str(self.base / "claims"),
            "--resume", env=env, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((directory / "codex_session_id").read_text().strip(), recovered_session_id)
        self.assertEqual(json.loads((directory / "status.json").read_text())["state"], "succeeded")

    def test_resume_without_session_id_is_rejected(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        run(
            "--json",
            "spec",
            "prepare",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
        )
        directory = self.cache / "run-a" / "specs" / "spec-a"
        (directory / "status.json").write_text(json.dumps({"state": "running"}))
        result = run(
            "--json",
            "spec",
            "resume",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 4)
        error = json.loads(result.stdout)["error"]
        self.assertEqual(error["code"], "state-conflict")
        self.assertIn("recorded Codex session UUID", error["message"])
        self.assertFalse((directory / "codex_session_id").exists())

    def test_resume_with_malformed_canonical_session_id_is_rejected(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        run(
            "--json",
            "spec",
            "prepare",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
        )
        directory = self.cache / "run-a" / "specs" / "spec-a"
        (directory / "status.json").write_text(json.dumps({"state": "running"}))
        (directory / "codex_session_id").write_text("truncated-session-id\n")
        (directory / "events.jsonl").write_text(
            '{"type":"thread.started","thread_id":"77777777-7777-4777-8777-777777777777"}\n'
        )
        result = run(
            "--json",
            "spec",
            "resume",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 4)
        error = json.loads(result.stdout)["error"]
        self.assertEqual(error["code"], "state-conflict")
        self.assertIn("malformed canonical Codex session UUID", error["message"])

    def test_resume_with_noncanonical_session_id_is_rejected(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        run(
            "--json",
            "spec",
            "prepare",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
        )
        directory = self.cache / "run-a" / "specs" / "spec-a"
        (directory / "status.json").write_text(json.dumps({"state": "running"}))
        (directory / "codex_session_id").write_text(
            "AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA\n"
        )
        result = run(
            "--json",
            "spec",
            "resume",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 4)
        error = json.loads(result.stdout)["error"]
        self.assertEqual(error["code"], "state-conflict")
        self.assertIn("noncanonical canonical Codex session UUID", error["message"])

    def test_resume_with_malformed_event_session_id_is_rejected(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        run(
            "--json",
            "spec",
            "prepare",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
        )
        directory = self.cache / "run-a" / "specs" / "spec-a"
        (directory / "status.json").write_text(json.dumps({"state": "running"}))
        (directory / "events.jsonl").write_text(
            '{"type":"thread.started","thread_id":"truncated-session-id"}\n'
        )
        result = run(
            "--json",
            "spec",
            "resume",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 4)
        error = json.loads(result.stdout)["error"]
        self.assertEqual(error["code"], "state-conflict")
        self.assertIn("malformed Codex session UUID in events", error["message"])

    def test_resume_with_malformed_json_and_valid_uuid_is_rejected(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        run(
            "--json",
            "spec",
            "prepare",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
        )
        directory = self.cache / "run-a" / "specs" / "spec-a"
        (directory / "status.json").write_text(json.dumps({"state": "running"}))
        (directory / "events.jsonl").write_text(
            '{"type":"thread.started"\n'
            '{"type":"thread.started","thread_id":"88888888-8888-4888-8888-888888888888"}\n'
        )
        result = run(
            "--json",
            "spec",
            "resume",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 4)
        error = json.loads(result.stdout)["error"]
        self.assertEqual(error["code"], "state-conflict")
        self.assertIn("malformed JSON in Codex session events", error["message"])

    def test_valid_canonical_session_id_precedes_historical_events(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        run(
            "--json",
            "spec",
            "prepare",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
        )
        directory = self.cache / "run-a" / "specs" / "spec-a"
        (directory / "status.json").write_text(json.dumps({"state": "running"}))
        canonical_id = "44444444-4444-4444-8444-444444444444"
        (directory / "codex_session_id").write_text(canonical_id + "\n")
        (directory / "events.jsonl").write_text(
            '{"type":"thread.started"\n'
            '{"type":"thread.started","thread_id":"55555555-5555-4555-8555-555555555555"}\n'
        )
        self.assertEqual(RUNTIME.recover_session_id(directory), canonical_id)

    def test_resume_with_conflicting_recovery_event_ids_is_rejected(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        run(
            "--json",
            "spec",
            "prepare",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
        )
        directory = self.cache / "run-a" / "specs" / "spec-a"
        (directory / "status.json").write_text(json.dumps({"state": "running"}))
        (directory / "events.jsonl").write_text(
            '{"type":"thread.started","thread_id":"44444444-4444-4444-8444-444444444444"}\n'
            '{"type":"thread.started","thread_id":"55555555-5555-4555-8555-555555555555"}\n'
        )
        result = run(
            "--json",
            "spec",
            "resume",
            "--run-id",
            "run-a",
            "--spec-id",
            "spec-a",
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 4)
        error = json.loads(result.stdout)["error"]
        self.assertEqual(error["code"], "state-conflict")
        self.assertIn("conflicting Codex session UUIDs in events", error["message"])

    def test_blocked_report_cannot_complete_as_integrated(self) -> None:
        fake_bin = self.base / "bin"
        fake_bin.mkdir()
        fake_codex = fake_bin / "codex"
        fake_codex.write_text(
            "#!/bin/sh\n"
            "last=''\n"
            "while [ \"$#\" -gt 0 ]; do\n"
            "  if [ \"$1\" = '--output-last-message' ]; then shift; last=$1; fi\n"
            "  shift\n"
            "done\n"
            "printf '%s\\n' '{\"result_status\":\"blocked\",\"summary\":\"blocked\",\"changed_files\":[],\"validation\":[],\"generated_artifacts\":[],\"internal_subagents\":[],\"risks\":[],\"blockers\":[\"missing authority\"],\"recommended_root_action\":\"resolve blocker\"}' > \"$last\"\n"
            "echo '{\"type\":\"thread.started\",\"thread_id\":\"66666666-6666-4666-8666-666666666666\"}'\n"
            "exit 0\n"
        )
        fake_codex.chmod(fake_codex.stat().st_mode | stat.S_IXUSR)
        env = self.env.copy()
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        run("--json", "run", "create", "--manifest", str(self.manifest), env=env)
        run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=env)
        directory = self.cache / "run-a" / "specs" / "spec-a"
        (directory / "status.json").write_text(json.dumps({"state": "running"}))
        result = run(
            "_launch", "--run-id", "run-a", "--spec-id", "spec-a",
            "--cache-root", str(self.cache), "--claim-root", str(self.base / "claims"),
            env=env, check=False,
        )
        self.assertEqual(result.returncode, 4)
        status = json.loads((directory / "status.json").read_text())
        self.assertEqual(status["state"], "failed")
        self.assertEqual(status["worker_result_status"], "blocked")
        integrated = run(
            "--json", "spec", "cleanup", "--run-id", "run-a", "--spec-id", "spec-a",
            "--disposition", "integrated", env=env, check=False,
        )
        self.assertEqual(integrated.returncode, 6)
        abandoned = json.loads(
            run(
                "--json", "spec", "cleanup", "--run-id", "run-a", "--spec-id", "spec-a",
                "--disposition", "abandoned", env=env,
            ).stdout
        )
        self.assertEqual(abandoned["state"], "cleaned")

    def test_codex_spawn_failure_writes_terminal_artifacts(self) -> None:
        run("--json", "run", "create", "--manifest", str(self.manifest), env=self.env)
        run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=self.env)
        directory = self.cache / "run-a" / "specs" / "spec-a"
        (directory / "status.json").write_text(json.dumps({"state": "running"}))
        tool_bin = self.base / "spawn-tools"
        tool_bin.mkdir()
        (tool_bin / "python3").symlink_to(shutil.which("python3"))
        (tool_bin / "git").symlink_to(shutil.which("git"))
        (tool_bin / "ps").symlink_to(shutil.which("ps"))
        env = self.env.copy()
        env["PATH"] = str(tool_bin)
        result = run(
            "_launch", "--run-id", "run-a", "--spec-id", "spec-a",
            "--cache-root", str(self.cache), "--claim-root", str(self.base / "claims"),
            env=env, check=False,
        )
        self.assertEqual(result.returncode, 5, result.stderr)
        status = json.loads((directory / "status.json").read_text())
        self.assertEqual(status["state"], "failed")
        self.assertEqual(status["reason"], "codex-spawn-failed")
        self.assertEqual((directory / "exit_code").read_text().strip(), "5")
        self.assertIn("codex spawn failed", (directory / "stderr.log").read_text())

    def test_anchor_handshake_failure_proves_group_dead_before_terminal_status(self) -> None:
        fake_bin = self.base / "handshake-bin"
        fake_bin.mkdir()
        fake_codex = fake_bin / "codex"
        fake_codex.write_text("#!/bin/sh\nwhile :; do sleep 1; done\n")
        fake_codex.chmod(fake_codex.stat().st_mode | stat.S_IXUSR)
        env = self.env.copy()
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        run("--json", "run", "create", "--manifest", str(self.manifest), env=env)
        run("--json", "spec", "prepare", "--run-id", "run-a", "--spec-id", "spec-a", env=env)
        directory = self.cache / "run-a" / "specs" / "spec-a"
        (directory / "status.json").write_text(json.dumps({"state": "running"}))
        observed: dict[str, object] = {}
        bootstrap_status: dict[str, object] = {}
        original_cleanup = RUNTIME.cleanup_started_anchor

        def capture_cleanup(anchor: subprocess.Popen[object], started_at: str | None) -> bool:
            observed["pgid"] = anchor.pid
            observed["started_at"] = started_at
            cleaned = original_cleanup(anchor, started_at)
            observed["cleaned"] = cleaned
            return cleaned

        def fail_after_observing_bootstrap(*_args: object, **_kwargs: object) -> dict[str, object]:
            bootstrap_status.update(json.loads((directory / "status.json").read_text()))
            raise OSError("fixture timeout")

        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch.object(RUNTIME, "wait_for_anchor_handshake", side_effect=fail_after_observing_bootstrap),
            mock.patch.object(RUNTIME, "cleanup_started_anchor", side_effect=capture_cleanup),
        ):
            result = RUNTIME.internal_launch("run-a", "spec-a", False)
        self.assertEqual(result, 5)
        self.assertEqual(bootstrap_status["worker_group_model"], "persistent-anchor-v1")
        self.assertEqual(bootstrap_status["worker_bootstrap_phase"], "awaiting-child-handshake")
        self.assertIsInstance(bootstrap_status["worker_leader_started_at"], str)
        self.assertTrue(observed["cleaned"])
        self.assertFalse(RUNTIME.process_group_live(observed["pgid"], observed["started_at"]))
        status = json.loads((directory / "status.json").read_text())
        self.assertEqual(status["state"], "failed")
        self.assertEqual(status["reason"], "codex-spawn-failed")


if __name__ == "__main__":
    unittest.main()
