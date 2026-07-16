from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import subprocess
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts/orchestrator-claim"
LOADER = importlib.machinery.SourceFileLoader("claim_helper_runtime", str(TOOL))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
CLAIM_RUNTIME = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(CLAIM_RUNTIME)


def run_claim(*args: str, env: dict[str, str], check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([str(TOOL), *args], env=env, text=True, capture_output=True)
    if check and result.returncode:
        raise AssertionError(f"claim helper failed: {result.stdout}\n{result.stderr}")
    return result


class AtomicClaimHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.claim_root = self.base / "claims"
        self.repo = self.base / "repo"
        self.other_repo = self.base / "other-repo"
        for repository in (self.repo, self.other_repo):
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.test"], check=True)
            subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
            (repository / "README.md").write_text("base\n")
            subprocess.run(["git", "-C", str(repository), "add", "README.md"], check=True)
            subprocess.run(["git", "-C", str(repository), "commit", "-qm", "base"], check=True)
        self.ledger = self.base / "ledger.md"
        self.env = os.environ.copy()
        self.env["CODEX_ORCHESTRATOR_CLAIM_ROOT"] = str(self.claim_root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def acquire_args(
        self,
        root_id: str,
        repository: Path,
        source: str,
        adapter: str = "codex-app-task",
    ) -> list[str]:
        if not source.startswith("git:") and "://" not in source:
            common = subprocess.run(
                ["git", "-C", str(repository), "rev-parse", "--git-common-dir"],
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()
            common_path = Path(common)
            if not common_path.is_absolute():
                common_path = repository / common_path
            source = f"git:{common_path.resolve()}::ref:{source}"
        return [
            "--json",
            "claim",
            "acquire",
            "--root-id",
            root_id,
            "--adapter",
            adapter,
            "--repository",
            str(repository),
            "--source",
            source,
            "--ledger-ref",
            str(self.ledger),
        ]

    def make_stale(self, claim: dict[str, object]) -> None:
        claim["heartbeat_at"] = "2000-01-01T00:00:00Z"
        path = self.claim_root / f"{claim['root_id']}.json"
        path.write_text(json.dumps(claim, indent=2, sort_keys=True) + "\n")

    def test_doctor_is_read_only_and_versioned(self) -> None:
        self.assertEqual(run_claim("--version", env=self.env).stdout.strip(), "1.0.0")
        doctor = json.loads(run_claim("--json", "doctor", env=self.env).stdout)
        self.assertTrue(doctor["ok"])
        self.assertTrue(doctor["offline"])
        self.assertTrue(doctor["git"]["available"])
        self.assertFalse(doctor["claim_root_exists"])
        self.assertFalse(self.claim_root.exists())

    def test_competing_roots_have_exactly_one_winner(self) -> None:
        commands = [
            [str(TOOL), *self.acquire_args("root-a", self.repo, "spec-1")],
            [str(TOOL), *self.acquire_args("root-b", self.repo, "spec-2")],
        ]
        processes = [
            subprocess.Popen(command, env=self.env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for command in commands
        ]
        results = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=10)
            results.append((process.returncode, json.loads(stdout), stderr))

        self.assertEqual(sorted(result[0] for result in results), [0, 4])
        winner = next(result[1]["claim"]["root_id"] for result in results if result[0] == 0)
        loser = next(result[1]["error"] for result in results if result[0] == 4)
        self.assertEqual(loser["code"], "state-conflict")
        self.assertIn(winner, loser["details"]["root_ids"])

        status = json.loads(run_claim("--json", "claim", "status", env=self.env).stdout)
        self.assertEqual([claim["root_id"] for claim in status["claims"]], [winner])
        released = json.loads(
            run_claim(
                "--json",
                "claim",
                "release",
                "--root-id",
                winner,
                "--expected-fingerprint",
                next(
                    result[1]["claim"]["fingerprint"]
                    for result in results
                    if result[0] == 0
                ),
                "--evidence",
                "fixture-terminal",
                env=self.env,
            ).stdout
        )
        self.assertEqual(released["state"], "released")

    def test_heartbeat_and_release_require_current_fingerprint(self) -> None:
        acquired = json.loads(
            run_claim(*self.acquire_args("root-a", self.repo, "spec-1"), env=self.env).stdout
        )["claim"]
        repeated = json.loads(
            run_claim(*self.acquire_args("root-a", self.repo, "spec-1"), env=self.env).stdout
        )
        self.assertEqual(repeated["state"], "already-owned")
        self.assertEqual(repeated["claim"]["fingerprint"], acquired["fingerprint"])
        wrong = "0" * 64
        heartbeat = run_claim(
            "--json",
            "claim",
            "heartbeat",
            "--root-id",
            "root-a",
            "--expected-fingerprint",
            wrong,
            env=self.env,
            check=False,
        )
        self.assertEqual(heartbeat.returncode, 4)
        released = run_claim(
            "--json",
            "claim",
            "release",
            "--root-id",
            "root-a",
            "--expected-fingerprint",
            acquired["fingerprint"],
            "--evidence",
            "fixture-terminal",
            env=self.env,
        )
        self.assertEqual(json.loads(released.stdout)["state"], "released")

        reacquired = json.loads(
            run_claim(*self.acquire_args("root-a", self.repo, "spec-1"), env=self.env).stdout
        )["claim"]
        self.assertNotEqual(reacquired["fingerprint"], acquired["fingerprint"])
        stale_heartbeat = run_claim(
            "--json",
            "claim",
            "heartbeat",
            "--root-id",
            "root-a",
            "--expected-fingerprint",
            acquired["fingerprint"],
            env=self.env,
            check=False,
        )
        self.assertEqual(stale_heartbeat.returncode, 4)

    def test_linked_worktrees_share_one_repository_identity(self) -> None:
        linked = self.base / "repo-linked"
        subprocess.run(
            ["git", "-C", str(self.repo), "worktree", "add", "-qb", "linked", str(linked), "HEAD"],
            check=True,
        )
        acquired = json.loads(
            run_claim(*self.acquire_args("root-a", self.repo, "spec-1"), env=self.env).stdout
        )
        result = run_claim(
            *self.acquire_args("root-b", linked, "spec-2", "codex-cli-session"),
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 4)
        error = json.loads(result.stdout)["error"]
        self.assertEqual(error["details"]["root_ids"], ["root-a"])
        self.assertEqual(
            acquired["claim"]["repositories"],
            [str((self.repo / ".git").resolve())],
        )
        self.assertEqual(
            acquired["claim"]["repository_checkouts"][0]["checkout"],
            str(self.repo.resolve()),
        )

    def test_bare_repository_local_source_ref_is_rejected(self) -> None:
        for source in ("#1", "planning/features/demo/SPEC.md"):
            with self.subTest(source=source):
                args = self.acquire_args("root-a", self.repo, source)
                args[args.index("--source") + 1] = source
                result = run_claim(*args, env=self.env, check=False)
                self.assertEqual(result.returncode, 2)
                self.assertIn("Git-identity-qualified", json.loads(result.stdout)["error"]["message"])

    def test_nonoverlapping_claims_and_exact_takeover(self) -> None:
        first = json.loads(run_claim(*self.acquire_args("root-a", self.repo, "spec-1"), env=self.env).stdout)
        second = json.loads(
            run_claim(*self.acquire_args("root-b", self.other_repo, "spec-2"), env=self.env).stdout
        )
        self.assertEqual(first["state"], "acquired")
        self.assertEqual(second["state"], "acquired")
        self.make_stale(first["claim"])

        takeover = json.loads(
            run_claim(
                "--json",
                "claim",
                "takeover",
                "--root-id",
                "root-c",
                "--adapter",
                "codex-app-task",
                "--repository",
                str(self.repo),
                "--source",
                first["claim"]["sources"][0],
                "--ledger-ref",
                str(self.ledger),
                "--expected-root-id",
                "root-a",
                "--takeover-policy",
                "takeover-authorized",
                "--takeover-reason",
                "verified-stale",
                "--expected-claim-fingerprint",
                f"root-a={first['claim']['fingerprint']}",
                "--expected-claim-heartbeat",
                f"root-a={first['claim']['heartbeat_at']}",
                "--evidence",
                "verified-stale-root-a",
                env=self.env,
            ).stdout
        )
        self.assertEqual(takeover["claim"]["replaced_root_ids"], ["root-a"])
        status = json.loads(run_claim("--json", "claim", "status", env=self.env).stdout)
        self.assertEqual(
            sorted(claim["root_id"] for claim in status["claims"]),
            ["root-b", "root-c"],
        )

    def test_takeover_rejects_unverified_claim_snapshot(self) -> None:
        first = json.loads(run_claim(*self.acquire_args("root-a", self.repo, "spec-1"), env=self.env).stdout)
        self.make_stale(first["claim"])
        result = run_claim(
            "--json",
            "claim",
            "takeover",
            "--root-id",
            "root-b",
            "--adapter",
            "codex-app-task",
            "--repository",
            str(self.repo),
            "--source",
            first["claim"]["sources"][0],
            "--ledger-ref",
            str(self.ledger),
            "--expected-root-id",
            "root-a",
            "--takeover-policy",
            "takeover-authorized",
            "--takeover-reason",
            "verified-stale",
            "--expected-claim-fingerprint",
            f"root-a={'0' * 64}",
            "--expected-claim-heartbeat",
            f"root-a={first['claim']['heartbeat_at']}",
            "--evidence",
            "verified-stale-root-a",
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 4)
        self.assertIn("stale", json.loads(result.stdout)["error"]["message"])

    def test_takeover_rejects_freshly_heartbeating_claim(self) -> None:
        first = json.loads(run_claim(*self.acquire_args("root-a", self.repo, "spec-1"), env=self.env).stdout)
        result = run_claim(
            "--json",
            "claim",
            "takeover",
            "--root-id",
            "root-b",
            "--adapter",
            "codex-app-task",
            "--repository",
            str(self.repo),
            "--source",
            first["claim"]["sources"][0],
            "--ledger-ref",
            str(self.ledger),
            "--expected-root-id",
            "root-a",
            "--takeover-policy",
            "takeover-authorized",
            "--takeover-reason",
            "verified-stale",
            "--expected-claim-fingerprint",
            f"root-a={first['claim']['fingerprint']}",
            "--expected-claim-heartbeat",
            f"root-a={first['claim']['heartbeat_at']}",
            "--evidence",
            "fixture-stale-review",
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 4)
        self.assertIn("stale threshold", json.loads(result.stdout)["error"]["message"])

    def test_ownership_lease_blocks_takeover_until_mutation_finishes(self) -> None:
        first = json.loads(run_claim(*self.acquire_args("root-a", self.repo, "spec-1"), env=self.env).stdout)
        self.make_stale(first["claim"])
        entered = threading.Event()
        release = threading.Event()
        errors: list[Exception] = []

        def hold_lease() -> None:
            try:
                with CLAIM_RUNTIME.ownership_lease("root-a", first["claim"]["fingerprint"]):
                    entered.set()
                    release.wait(timeout=5)
            except Exception as exc:  # pragma: no cover - surfaced below
                errors.append(exc)
                entered.set()

        with mock.patch.dict(os.environ, self.env, clear=True):
            thread = threading.Thread(target=hold_lease)
            thread.start()
            self.assertTrue(entered.wait(timeout=5))
            command = [
                str(TOOL),
                "--json",
                "claim",
                "takeover",
                "--root-id",
                "root-b",
                "--adapter",
                "codex-cli-session",
                "--repository",
                str(self.repo),
                "--source",
                first["claim"]["sources"][0],
                "--ledger-ref",
                str(self.ledger),
                "--expected-root-id",
                "root-a",
                "--takeover-policy",
                "takeover-authorized",
                "--takeover-reason",
                "verified-stale",
                "--expected-claim-fingerprint",
                f"root-a={first['claim']['fingerprint']}",
                "--expected-claim-heartbeat",
                f"root-a={first['claim']['heartbeat_at']}",
                "--evidence",
                "fixture-terminal",
            ]
            process = subprocess.Popen(command, env=self.env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(0.1)
            self.assertIsNone(process.poll())
            release.set()
            stdout, stderr = process.communicate(timeout=5)
            thread.join(timeout=5)
        self.assertEqual(errors, [])
        self.assertEqual(process.returncode, 0, stderr)
        self.assertEqual(json.loads(stdout)["claim"]["root_id"], "root-b")

    def test_ownership_lease_does_not_swallow_mutation_file_errors(self) -> None:
        acquired = json.loads(
            run_claim(*self.acquire_args("root-a", self.repo, "spec-1"), env=self.env).stdout
        )["claim"]
        with mock.patch.dict(os.environ, self.env, clear=True):
            with self.assertRaises(FileNotFoundError):
                with CLAIM_RUNTIME.ownership_lease("root-a", acquired["fingerprint"]):
                    raise FileNotFoundError("fixture protected mutation")


if __name__ == "__main__":
    unittest.main()
