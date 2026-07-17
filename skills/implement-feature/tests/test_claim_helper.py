from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts/active-root-claim"
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
        self.claim_root = (
            self.base
            / ".cache/dotagents/skills/implement-feature/claims"
        )
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
        self.ledger.write_text("# fixture ledger\n")
        self.adoption_index = 0
        self.env = os.environ.copy()
        self.env["HOME"] = str(self.base)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def acquire_args(
        self,
        root_id: str,
        repository: Path,
        source: str,
        ledger: Path | None = None,
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
            "--repository",
            str(repository),
            "--source",
            source,
            "--ledger-ref",
            str(ledger or self.ledger),
        ]

    def make_stale(self, claim: dict[str, object]) -> None:
        claim["heartbeat_at"] = "2000-01-01T00:00:00Z"
        path = self.claim_root / f"{claim['root_id']}.json"
        path.write_text(json.dumps(claim, indent=2, sort_keys=True) + "\n")

    def write_unsupported_claim(
        self, claim: dict[str, object], schema_version: str
    ) -> Path:
        unsupported = dict(claim)
        unsupported["schema_version"] = schema_version
        path = self.claim_root / f"{unsupported['root_id']}.json"
        path.write_text(json.dumps(unsupported, indent=2, sort_keys=True) + "\n")
        return path

    def make_task_adoption(
        self,
        claim: dict[str, object],
        termination_evidence: str,
        *,
        recorded: bool = True,
    ) -> Path:
        self.adoption_index += 1
        checkouts = []
        for item in claim["repository_checkouts"]:
            checkout = Path(item["checkout"])
            top_level = subprocess.run(
                ["git", "-C", str(checkout), "rev-parse", "--show-toplevel"],
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()
            branch = subprocess.run(
                ["git", "-C", str(checkout), "branch", "--show-current"],
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()
            baseline = subprocess.run(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"],
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()
            checkouts.append(
                {
                    "repository": item["git_common_dir"],
                    "checkout": str(checkout.resolve()),
                    "target_branch_name": branch,
                    "git_top_level": str(Path(top_level).resolve()),
                    "baseline_revision": baseline,
                    "isolation_evidence_ref": f"isolation-{claim['root_id']}",
                }
            )
        specs = []
        task_policy = CLAIM_RUNTIME.load_task_model_policy()
        for index, source in enumerate(claim["sources"], start=1):
            source_recorded = recorded and index == 1
            specs.append(
                {
                    "source_spec_ref": source,
                    "task_state": "recorded" if source_recorded else "no-task",
                    "task_ref": (
                        f"task-{claim['root_id']}-{index}" if source_recorded else "none"
                    ),
                    "task_model": task_policy["model"],
                    "task_thinking": task_policy["thinking_default"],
                    "thinking_reason": "default-high-fixture",
                    "goal_evidence_ref": (
                        f"goal-{claim['root_id']}-{index}" if source_recorded else "none"
                    ),
                    "managed_checkouts": checkouts if source_recorded else [],
                    "evidence_ref": f"task-state-{claim['root_id']}-{index}",
                }
            )
        value = {
            "root_id": claim["root_id"],
            "claim_fingerprint": claim["fingerprint"],
            "task_termination_evidence": termination_evidence,
            "specs": specs,
        }
        path = self.base / f"adoption-{claim['root_id']}-{self.adoption_index}.json"
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        return path

    def takeover_args(
        self,
        root_id: str,
        claims: list[dict[str, object]],
        adoptions: list[Path],
        terminations: list[str],
        *,
        ledger: Path | None = None,
    ) -> list[str]:
        args = [
            "claim",
            "takeover",
            "--root-id",
            root_id,
            "--ledger-ref",
            str(ledger or self.ledger),
            "--takeover-permission",
            "granted-by-authorized-user",
            "--takeover-reason",
            "verified-stale",
            "--evidence",
            f"prepared-takeover-{root_id}",
        ]
        repositories: dict[str, str] = {}
        sources: set[str] = set()
        for claim in claims:
            for checkout in claim["repository_checkouts"]:
                repositories[checkout["git_common_dir"]] = checkout["checkout"]
            sources.update(claim["sources"])
        for checkout in repositories.values():
            args.extend(["--repository", checkout])
        for source in sorted(sources):
            args.extend(["--source", source])
        for claim, adoption, termination in zip(
            claims, adoptions, terminations, strict=True
        ):
            root = claim["root_id"]
            args.extend(
                [
                    "--expected-root-id",
                    root,
                    "--expected-claim-fingerprint",
                    f"{root}={claim['fingerprint']}",
                    "--expected-claim-heartbeat",
                    f"{root}={claim['heartbeat_at']}",
                    "--expected-task-termination",
                    f"{root}={termination}",
                    "--expected-task-adoption",
                    f"{root}={adoption}",
                ]
            )
        return args

    def test_doctor_is_read_only_and_versioned(self) -> None:
        self.assertEqual(run_claim("--version", env=self.env).stdout.strip(), "7.0.0")
        self.assertNotRegex(TOOL.read_text(), r"os\.environ\.get\(.+CLAIM_ROOT")
        self.assertNotIn("--adapter", run_claim("claim", "acquire", "--help", env=self.env).stdout)
        takeover_help = run_claim("claim", "takeover", "--help", env=self.env).stdout
        self.assertIn("--takeover-permission", takeover_help)
        self.assertIn("--expected-task-termination", takeover_help)
        self.assertIn("--expected-task-adoption", takeover_help)
        self.assertNotIn("--takeover-policy", takeover_help)
        self.assertIn(
            "recover-takeover", run_claim("claim", "--help", env=self.env).stdout
        )
        self.assertNotIn(
            "retire-legacy", run_claim("claim", "--help", env=self.env).stdout
        )
        doctor = json.loads(run_claim("--json", "doctor", env=self.env).stdout)
        self.assertTrue(doctor["ok"])
        self.assertTrue(doctor["offline"])
        self.assertTrue(doctor["git"]["available"])
        self.assertTrue(doctor["task_model_policy"]["available"])
        self.assertEqual(
            doctor["task_model_policy"]["profile"]["model"], "gpt-5.6-sol"
        )
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
                "--release-reason",
                "terminal",
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
            "--release-reason",
            "terminal",
            "--evidence",
            "fixture-terminal",
            env=self.env,
        )
        released_value = json.loads(released.stdout)
        self.assertEqual(released_value["state"], "released")
        receipt = released_value["release_receipt"]
        self.assertEqual(receipt["root_id"], "root-a")
        self.assertEqual(receipt["ledger_ref"], str(self.ledger.resolve()))
        self.assertEqual(receipt["release_reason"], "terminal")
        self.assertTrue(Path(released_value["release_receipt_ref"]).is_file())
        repeated_release = json.loads(
            run_claim(
                "--json",
                "claim",
                "release",
                "--root-id",
                "root-a",
                "--expected-fingerprint",
                acquired["fingerprint"],
                "--release-reason",
                "terminal",
                "--evidence",
                "fixture-terminal",
                env=self.env,
            ).stdout
        )
        self.assertEqual(repeated_release["state"], "already-released")

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

    def test_pre_register_claim_can_release_to_durable_handoff(self) -> None:
        missing_ledger = self.base / "not-registered.md"
        acquired = json.loads(
            run_claim(
                *self.acquire_args(
                    "root-a", self.repo, "spec-1", ledger=missing_ledger
                ),
                env=self.env,
            ).stdout
        )["claim"]

        released = json.loads(
            run_claim(
                "--json",
                "claim",
                "release",
                "--root-id",
                "root-a",
                "--expected-fingerprint",
                acquired["fingerprint"],
                "--release-reason",
                "durable-handoff",
                "--evidence",
                "pre-register-failure",
                env=self.env,
            ).stdout
        )

        self.assertEqual(released["state"], "released")
        self.assertIsNone(released["release_receipt"]["ledger_sha256"])
        self.assertIsNone(released["release_receipt"]["ledger_size_bytes"])
        status = json.loads(
            run_claim("--json", "claim", "status", env=self.env).stdout
        )
        self.assertEqual(status["claims"], [])
        receipt_path = Path(released["release_receipt_ref"])
        self.assertTrue(receipt_path.is_file())
        run_claim(
            *self.acquire_args(
                "root-a", self.repo, "spec-1", ledger=missing_ledger
            ),
            env=self.env,
        )
        self.assertFalse(receipt_path.exists())

    def test_receipt_cleanup_failure_does_not_persist_new_claim(self) -> None:
        receipt_root = self.claim_root / "releases"
        receipt_root.mkdir(parents=True)
        (self.claim_root / ".lock").touch()
        (receipt_root / f"root-a--{'0' * 64}.json").write_text("not-json\n")

        acquired = run_claim(
            *self.acquire_args("root-a", self.repo, "spec-1"),
            env=self.env,
            check=False,
        )

        self.assertEqual(acquired.returncode, 4)
        self.assertFalse((self.claim_root / "root-a.json").exists())

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
            *self.acquire_args("root-b", linked, "spec-2"),
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
        self.assertEqual(acquired["claim"]["schema_version"], "5.0.0")
        self.assertNotIn("execution_adapter", acquired["claim"])

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
        adoption = self.make_task_adoption(
            first["claim"], "app-task-terminal-fixture"
        )

        takeover = json.loads(
            run_claim(
                "--json",
                "claim",
                "takeover",
                "--root-id",
                "root-c",
                "--repository",
                str(self.repo),
                "--source",
                first["claim"]["sources"][0],
                "--ledger-ref",
                str(self.ledger),
                "--expected-root-id",
                "root-a",
                "--takeover-permission",
                "granted-by-authorized-user",
                "--takeover-reason",
                "verified-stale",
                "--expected-claim-fingerprint",
                f"root-a={first['claim']['fingerprint']}",
                "--expected-claim-heartbeat",
                f"root-a={first['claim']['heartbeat_at']}",
                "--expected-task-termination",
                "root-a=app-task-terminal-fixture",
                "--expected-task-adoption",
                f"root-a={adoption}",
                "--evidence",
                "verified-stale-root-a",
                env=self.env,
            ).stdout
        )
        self.assertEqual(takeover["claim"]["replaced_root_ids"], ["root-a"])
        takeover_evidence = takeover["claim"]["takeover_evidence"]
        self.assertEqual(
            takeover_evidence["stale_claim_takeover_permission"],
            "granted-by-authorized-user",
        )
        self.assertEqual(
            takeover_evidence["replaced_claims"][0]["task_termination_evidence"],
            "app-task-terminal-fixture",
        )
        self.assertEqual(
            takeover_evidence["replaced_claims"][0]["claim_snapshot"]["ledger_ref"],
            first["claim"]["ledger_ref"],
        )
        self.assertEqual(
            takeover_evidence["replaced_claims"][0]["task_adoption"]["specs"][0]["task_ref"],
            "task-root-a-1",
        )
        self.assertNotIn(
            "existing_orchestrator_session_takeover_policy", takeover_evidence
        )
        status = json.loads(run_claim("--json", "claim", "status", env=self.env).stdout)
        self.assertEqual(
            sorted(claim["root_id"] for claim in status["claims"]),
            ["root-b", "root-c"],
        )

    def test_takeover_rejects_partial_multi_repository_root_scope(self) -> None:
        first_args = self.acquire_args("root-a", self.repo, "spec-1")
        source_a = first_args[first_args.index("--source") + 1]
        second_args = self.acquire_args("unused", self.other_repo, "spec-2")
        source_b = second_args[second_args.index("--source") + 1]
        first_args.extend(
            ["--repository", str(self.other_repo), "--source", source_b]
        )
        first = json.loads(run_claim(*first_args, env=self.env).stdout)["claim"]
        self.make_stale(first)
        adoption = self.make_task_adoption(
            first, "all-original-tasks-stopped-and-resumable"
        )

        partial = run_claim(
            "--json",
            "claim",
            "takeover",
            "--root-id",
            "root-b",
            "--repository",
            str(self.repo),
            "--source",
            source_a,
            "--ledger-ref",
            str(self.ledger),
            "--expected-root-id",
            "root-a",
            "--takeover-permission",
            "granted-by-authorized-user",
            "--takeover-reason",
            "verified-stale",
            "--expected-claim-fingerprint",
            f"root-a={first['fingerprint']}",
            "--expected-claim-heartbeat",
            f"root-a={first['heartbeat_at']}",
            "--expected-task-termination",
            "root-a=all-original-tasks-stopped-and-resumable",
            "--expected-task-adoption",
            f"root-a={adoption}",
            "--evidence",
            "verified-stale-root-a",
            env=self.env,
            check=False,
        )
        self.assertEqual(partial.returncode, 4)
        error = json.loads(partial.stdout)["error"]
        self.assertIn("complete replaced-root scope", error["message"])
        uncovered = error["details"]["uncovered_scopes"]
        self.assertEqual(len(uncovered), 1)
        self.assertEqual(uncovered[0]["root_id"], "root-a")
        self.assertIn(source_b, uncovered[0]["sources"])

        status = json.loads(
            run_claim(
                "--json", "claim", "status", "--root-id", "root-a", env=self.env
            ).stdout
        )
        self.assertEqual(status["state"], "active")
        self.assertEqual(len(status["claim"]["repositories"]), 2)

        complete = json.loads(
            run_claim(
                "--json",
                "claim",
                "takeover",
                "--root-id",
                "root-b",
                "--repository",
                str(self.repo),
                "--repository",
                str(self.other_repo),
                "--source",
                source_a,
                "--source",
                source_b,
                "--ledger-ref",
                str(self.ledger),
                "--expected-root-id",
                "root-a",
                "--takeover-permission",
                "granted-by-authorized-user",
                "--takeover-reason",
                "verified-stale",
                "--expected-claim-fingerprint",
                f"root-a={first['fingerprint']}",
                "--expected-claim-heartbeat",
                f"root-a={first['heartbeat_at']}",
                "--expected-task-termination",
                "root-a=all-original-tasks-stopped-and-resumable",
                "--expected-task-adoption",
                f"root-a={adoption}",
                "--evidence",
                "verified-stale-root-a",
                env=self.env,
            ).stdout
        )
        self.assertEqual(complete["state"], "acquired")
        self.assertEqual(len(complete["claim"]["repositories"]), 2)

    def test_takeover_rejects_unverified_claim_snapshot(self) -> None:
        first = json.loads(run_claim(*self.acquire_args("root-a", self.repo, "spec-1"), env=self.env).stdout)
        self.make_stale(first["claim"])
        adoption = self.make_task_adoption(
            first["claim"], "app-task-terminal-fixture"
        )
        result = run_claim(
            "--json",
            "claim",
            "takeover",
            "--root-id",
            "root-b",
            "--repository",
            str(self.repo),
            "--source",
            first["claim"]["sources"][0],
            "--ledger-ref",
            str(self.ledger),
            "--expected-root-id",
            "root-a",
            "--takeover-permission",
            "granted-by-authorized-user",
            "--takeover-reason",
            "verified-stale",
            "--expected-claim-fingerprint",
            f"root-a={'0' * 64}",
            "--expected-claim-heartbeat",
            f"root-a={first['claim']['heartbeat_at']}",
            "--expected-task-termination",
            "root-a=app-task-terminal-fixture",
            "--expected-task-adoption",
            f"root-a={adoption}",
            "--evidence",
            "verified-stale-root-a",
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 4)
        self.assertIn("stale", json.loads(result.stdout)["error"]["message"])

    def test_takeover_rejects_freshly_heartbeating_claim(self) -> None:
        first = json.loads(run_claim(*self.acquire_args("root-a", self.repo, "spec-1"), env=self.env).stdout)
        adoption = self.make_task_adoption(
            first["claim"], "app-task-terminal-fixture"
        )
        result = run_claim(
            "--json",
            "claim",
            "takeover",
            "--root-id",
            "root-b",
            "--repository",
            str(self.repo),
            "--source",
            first["claim"]["sources"][0],
            "--ledger-ref",
            str(self.ledger),
            "--expected-root-id",
            "root-a",
            "--takeover-permission",
            "granted-by-authorized-user",
            "--takeover-reason",
            "verified-stale",
            "--expected-claim-fingerprint",
            f"root-a={first['claim']['fingerprint']}",
            "--expected-claim-heartbeat",
            f"root-a={first['claim']['heartbeat_at']}",
            "--expected-task-termination",
            "root-a=app-task-terminal-fixture",
            "--expected-task-adoption",
            f"root-a={adoption}",
            "--evidence",
            "fixture-stale-review",
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 4)
        self.assertIn("stale threshold", json.loads(result.stdout)["error"]["message"])

    def test_takeover_requires_task_termination_evidence_for_every_root(self) -> None:
        first = json.loads(
            run_claim(*self.acquire_args("root-a", self.repo, "spec-1"), env=self.env).stdout
        )
        self.make_stale(first["claim"])
        result = run_claim(
            "--json",
            "claim",
            "takeover",
            "--root-id",
            "root-b",
            "--repository",
            str(self.repo),
            "--source",
            first["claim"]["sources"][0],
            "--ledger-ref",
            str(self.ledger),
            "--expected-root-id",
            "root-a",
            "--takeover-permission",
            "granted-by-authorized-user",
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
        self.assertEqual(result.returncode, 2)
        self.assertIn("--expected-task-termination", result.stderr)

    def test_takeover_rejects_duplicate_task_ref_across_replaced_roots(self) -> None:
        claim_a = json.loads(
            run_claim(
                *self.acquire_args("root-a", self.repo, "spec-1", self.base / "ledger-a.md"),
                env=self.env,
            ).stdout
        )["claim"]
        claim_b = json.loads(
            run_claim(
                *self.acquire_args(
                    "root-b", self.other_repo, "spec-2", self.base / "ledger-b.md"
                ),
                env=self.env,
            ).stdout
        )["claim"]
        for claim in (claim_a, claim_b):
            self.make_stale(claim)
        terminations = ["root-a-stopped", "root-b-stopped"]
        adoption_a = self.make_task_adoption(claim_a, terminations[0])
        adoption_b = self.make_task_adoption(claim_b, terminations[1])
        adoption_b_value = json.loads(adoption_b.read_text())
        adoption_b_value["specs"][0]["task_ref"] = json.loads(
            adoption_a.read_text()
        )["specs"][0]["task_ref"]
        adoption_b.write_text(json.dumps(adoption_b_value, indent=2, sort_keys=True) + "\n")

        result = run_claim(
            "--json",
            *self.takeover_args(
                "root-c",
                [claim_a, claim_b],
                [adoption_a, adoption_b],
                terminations,
                ledger=self.base / "ledger-c.md",
            ),
            env=self.env,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        error = json.loads(result.stdout)["error"]
        self.assertIn("task ref is owned by multiple", error["message"])
        self.assertEqual(
            sorted(owner["root_id"] for owner in error["details"]["owners"]),
            ["root-a", "root-b"],
        )
        self.assertFalse((self.claim_root / "root-c.takeover").exists())
        self.assertFalse((self.claim_root / "root-c.json").exists())

    def test_takeover_rejects_task_profile_outside_canonical_policy(self) -> None:
        claim = json.loads(
            run_claim(
                *self.acquire_args("root-a", self.repo, "spec-1"), env=self.env
            ).stdout
        )["claim"]
        self.make_stale(claim)
        termination = "root-a-stopped"
        adoption = self.make_task_adoption(claim, termination)
        adoption_value = json.loads(adoption.read_text())
        adoption_value["specs"][0]["task_thinking"] = "ultra"
        adoption.write_text(
            json.dumps(adoption_value, indent=2, sort_keys=True) + "\n"
        )

        result = run_claim(
            "--json",
            *self.takeover_args("root-b", [claim], [adoption], [termination]),
            env=self.env,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "task_thinking is invalid",
            json.loads(result.stdout)["error"]["message"],
        )
        self.assertFalse((self.claim_root / "root-b.takeover").exists())

    def test_takeover_rejects_duplicate_checkout_across_specs(self) -> None:
        acquire = self.acquire_args(
            "root-a", self.repo, "spec-1", self.base / "ledger-a.md"
        )
        second = self.acquire_args("unused", self.repo, "spec-2")
        second_source = second[second.index("--source") + 1]
        acquire.extend(["--source", second_source])
        claim = json.loads(run_claim(*acquire, env=self.env).stdout)["claim"]
        self.make_stale(claim)
        termination = "root-a-stopped"
        adoption = self.make_task_adoption(claim, termination)
        adoption_value = json.loads(adoption.read_text())
        first_spec, second_spec = adoption_value["specs"]
        self.assertEqual(second_spec["task_state"], "no-task")
        second_spec.update(
            {
                "task_state": "recorded",
                "task_ref": "task-root-a-2",
                "task_model": first_spec["task_model"],
                "task_thinking": first_spec["task_thinking"],
                "thinking_reason": "default-high-fixture-2",
                "goal_evidence_ref": "goal-root-a-2",
                "managed_checkouts": json.loads(
                    json.dumps(first_spec["managed_checkouts"])
                ),
            }
        )
        adoption.write_text(json.dumps(adoption_value, indent=2, sort_keys=True) + "\n")

        result = run_claim(
            "--json",
            *self.takeover_args(
                "root-b",
                [claim],
                [adoption],
                [termination],
                ledger=self.base / "ledger-b.md",
            ),
            env=self.env,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        error = json.loads(result.stdout)["error"]
        self.assertIn("managed checkout is owned by multiple", error["message"])
        self.assertEqual(len(error["details"]["owners"]), 2)
        self.assertFalse((self.claim_root / "root-b.takeover").exists())
        self.assertFalse((self.claim_root / "root-b.json").exists())

    def test_takeover_rejects_checkout_target_branch_mismatch(self) -> None:
        claim = json.loads(
            run_claim(
                *self.acquire_args("root-a", self.repo, "spec-1"), env=self.env
            ).stdout
        )["claim"]
        self.make_stale(claim)
        termination = "root-a-stopped"
        adoption = self.make_task_adoption(claim, termination)
        adoption_value = json.loads(adoption.read_text())
        adoption_value["specs"][0]["managed_checkouts"][0][
            "target_branch_name"
        ] = "different-valid-branch"
        adoption.write_text(json.dumps(adoption_value, indent=2, sort_keys=True) + "\n")

        result = run_claim(
            "--json",
            *self.takeover_args("root-b", [claim], [adoption], [termination]),
            env=self.env,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("target branch mismatch", json.loads(result.stdout)["error"]["message"])
        self.assertFalse((self.claim_root / "root-b.takeover").exists())

    def test_takeover_rejects_nonexistent_checkout_baseline_commit(self) -> None:
        claim = json.loads(
            run_claim(
                *self.acquire_args("root-a", self.repo, "spec-1"), env=self.env
            ).stdout
        )["claim"]
        self.make_stale(claim)
        termination = "root-a-stopped"
        adoption = self.make_task_adoption(claim, termination)
        adoption_value = json.loads(adoption.read_text())
        adoption_value["specs"][0]["managed_checkouts"][0][
            "baseline_revision"
        ] = "f" * 40
        adoption.write_text(json.dumps(adoption_value, indent=2, sort_keys=True) + "\n")

        result = run_claim(
            "--json",
            *self.takeover_args("root-b", [claim], [adoption], [termination]),
            env=self.env,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "baseline revision is not a commit",
            json.loads(result.stdout)["error"]["message"],
        )
        self.assertFalse((self.claim_root / "root-b.takeover").exists())

    def test_takeover_prepare_write_failure_preserves_prior_claims(self) -> None:
        old_ledger = self.base / "old-ledger.md"
        claim = json.loads(
            run_claim(
                *self.acquire_args("root-a", self.repo, "spec-1", old_ledger),
                env=self.env,
            ).stdout
        )["claim"]
        self.make_stale(claim)
        termination = "root-a-stopped-and-resumable"
        adoption = self.make_task_adoption(claim, termination)
        args = CLAIM_RUNTIME.build_parser().parse_args(
            self.takeover_args(
                "root-b", [claim], [adoption], [termination], ledger=self.base / "new-ledger.md"
            )
        )

        with mock.patch.object(CLAIM_RUNTIME, "claim_root", return_value=self.claim_root):
            with mock.patch.object(
                CLAIM_RUNTIME,
                "write_takeover_transaction",
                side_effect=OSError("first journal write failed"),
            ):
                with self.assertRaises(CLAIM_RUNTIME.ClaimError) as failure:
                    CLAIM_RUNTIME.takeover(args)

        self.assertEqual(failure.exception.code, "state-conflict")
        self.assertTrue((self.claim_root / "root-a.json").is_file())
        self.assertFalse((self.claim_root / "root-b.json").exists())
        self.assertFalse((self.claim_root / "root-b.takeover").exists())

    def test_status_rejects_non_object_nested_candidate_without_traceback(self) -> None:
        self.claim_root.mkdir(parents=True)
        (self.claim_root / ".lock").touch()
        transaction = {
            "schema_version": CLAIM_RUNTIME.TAKEOVER_TRANSACTION_SCHEMA_VERSION,
            "transaction_id": "a" * 32,
            "candidate_claim": 7,
            "replaced_claims": [],
            "prepared_at": "2026-07-16T00:00:00Z",
        }
        transaction["fingerprint"] = CLAIM_RUNTIME.takeover_transaction_fingerprint(
            transaction
        )
        (self.claim_root / "root-b.takeover").write_text(
            json.dumps(transaction, indent=2, sort_keys=True) + "\n"
        )

        result = run_claim(
            "--json", "claim", "status", env=self.env, check=False
        )

        self.assertEqual(result.returncode, 4)
        self.assertEqual(json.loads(result.stdout)["error"]["code"], "state-conflict")
        self.assertNotIn("Traceback", result.stderr)

    def test_partial_deletion_recovers_idempotently_from_prepared_journal(self) -> None:
        claim_a = json.loads(
            run_claim(
                *self.acquire_args(
                    "root-a", self.repo, "spec-1", self.base / "ledger-a.md"
                ),
                env=self.env,
            ).stdout
        )["claim"]
        claim_b = json.loads(
            run_claim(
                *self.acquire_args(
                    "root-b", self.other_repo, "spec-2", self.base / "ledger-b.md"
                ),
                env=self.env,
            ).stdout
        )["claim"]
        for claim in (claim_a, claim_b):
            self.make_stale(claim)
        terminations = ["root-a-stopped", "root-b-stopped"]
        adoptions = [
            self.make_task_adoption(claim_a, terminations[0]),
            self.make_task_adoption(claim_b, terminations[1]),
        ]
        args = CLAIM_RUNTIME.build_parser().parse_args(
            self.takeover_args(
                "root-c",
                [claim_a, claim_b],
                adoptions,
                terminations,
                ledger=self.base / "ledger-c.md",
            )
        )
        real_delete = CLAIM_RUNTIME.delete_replaced_claim
        deletions = 0

        def crash_after_first_delete(path: Path) -> None:
            nonlocal deletions
            real_delete(path)
            deletions += 1
            if deletions == 1:
                raise OSError("crash among replaced-claim deletions")

        with mock.patch.object(CLAIM_RUNTIME, "claim_root", return_value=self.claim_root):
            with mock.patch.object(
                CLAIM_RUNTIME,
                "delete_replaced_claim",
                side_effect=crash_after_first_delete,
            ):
                with self.assertRaises(CLAIM_RUNTIME.ClaimError) as failure:
                    CLAIM_RUNTIME.takeover(args)
        self.assertEqual(failure.exception.code, "takeover-pending")
        self.assertEqual(
            sorted(path.name for path in self.claim_root.glob("*.json")),
            ["root-b.json"],
        )

        prepared = json.loads(
            run_claim(
                "--json", "claim", "status", "--root-id", "root-c", env=self.env
            ).stdout
        )
        self.assertEqual(prepared["state"], "takeover-prepared")
        transaction_id = prepared["transaction"]["transaction_id"]
        for replaced_root in ("root-a", "root-b"):
            replaced_status = json.loads(
                run_claim(
                    "--json",
                    "claim",
                    "status",
                    "--root-id",
                    replaced_root,
                    env=self.env,
                ).stdout
            )
            self.assertEqual(replaced_status["state"], "takeover-prepared")
            self.assertEqual(replaced_status["queried_root_id"], replaced_root)
            self.assertEqual(replaced_status["candidate_root_id"], "root-c")
            self.assertEqual(
                replaced_status["transaction"]["transaction_id"], transaction_id
            )
        recovered = json.loads(
            run_claim(
                "--json",
                "claim",
                "recover-takeover",
                "--root-id",
                "root-c",
                "--expected-transaction-id",
                transaction_id,
                env=self.env,
            ).stdout
        )
        self.assertEqual(recovered["state"], "recovered")
        self.assertEqual(
            [
                item["claim_snapshot"]["ledger_ref"]
                for item in recovered["claim"]["takeover_evidence"]["replaced_claims"]
            ],
            [
                str((self.base / "ledger-a.md").resolve()),
                str((self.base / "ledger-b.md").resolve()),
            ],
        )
        repeated = json.loads(
            run_claim(
                "--json",
                "claim",
                "recover-takeover",
                "--root-id",
                "root-c",
                "--expected-transaction-id",
                transaction_id,
                env=self.env,
            ).stdout
        )
        self.assertEqual(repeated["state"], "already-finalized")

    def test_crash_after_candidate_write_recovers_journal_cleanup(self) -> None:
        claim = json.loads(
            run_claim(
                *self.acquire_args(
                    "root-a", self.repo, "spec-1", self.base / "ledger-a.md"
                ),
                env=self.env,
            ).stdout
        )["claim"]
        self.make_stale(claim)
        termination = "root-a-stopped"
        adoption = self.make_task_adoption(claim, termination)
        args = CLAIM_RUNTIME.build_parser().parse_args(
            self.takeover_args(
                "root-b",
                [claim],
                [adoption],
                [termination],
                ledger=self.base / "ledger-b.md",
            )
        )
        with mock.patch.object(CLAIM_RUNTIME, "claim_root", return_value=self.claim_root):
            with mock.patch.object(
                CLAIM_RUNTIME,
                "delete_takeover_transaction",
                side_effect=OSError("crash before journal cleanup"),
            ):
                with self.assertRaises(CLAIM_RUNTIME.ClaimError):
                    CLAIM_RUNTIME.takeover(args)

        self.assertTrue((self.claim_root / "root-b.json").is_file())
        prepared = json.loads(
            run_claim(
                "--json", "claim", "status", "--root-id", "root-b", env=self.env
            ).stdout
        )
        transaction_id = prepared["transaction"]["transaction_id"]
        recovered = json.loads(
            run_claim(
                "--json",
                "claim",
                "recover-takeover",
                "--root-id",
                "root-b",
                "--expected-transaction-id",
                transaction_id,
                env=self.env,
            ).stdout
        )
        self.assertEqual(recovered["state"], "recovered")
        self.assertFalse((self.claim_root / "root-b.takeover").exists())

    def test_immediate_recovery_uses_embedded_adoption_without_new_ledger(self) -> None:
        old_ledger = self.base / "ledger-old.md"
        new_ledger = self.base / "ledger-new.md"
        claim = json.loads(
            run_claim(
                *self.acquire_args("root-a", self.repo, "spec-1", old_ledger),
                env=self.env,
            ).stdout
        )["claim"]
        self.make_stale(claim)
        termination = "root-a-stopped"
        adoption = self.make_task_adoption(claim, termination)
        takeover = json.loads(
            run_claim(
                "--json",
                *self.takeover_args(
                    "root-b", [claim], [adoption], [termination], ledger=new_ledger
                ),
                env=self.env,
            ).stdout
        )
        self.assertFalse(new_ledger.exists())
        embedded = takeover["claim"]["takeover_evidence"]["replaced_claims"][0]
        self.assertEqual(
            embedded["claim_snapshot"]["ledger_ref"], str(old_ledger.resolve())
        )
        embedded_spec = embedded["task_adoption"]["specs"][0]
        self.assertEqual(embedded_spec["task_ref"], "task-root-a-1")
        self.assertEqual(embedded_spec["task_model"], "gpt-5.6-sol")
        self.assertEqual(embedded_spec["task_thinking"], "high")
        self.assertEqual(embedded_spec["thinking_reason"], "default-high-fixture")
        recovered = json.loads(
            run_claim(
                "--json",
                "claim",
                "recover-takeover",
                "--root-id",
                "root-b",
                "--expected-transaction-id",
                takeover["transaction_id"],
                env=self.env,
            ).stdout
        )
        self.assertEqual(recovered["state"], "already-finalized")
        self.assertEqual(
            recovered["claim"]["takeover_evidence"]["replaced_claims"][0][
                "task_adoption"
            ],
            embedded["task_adoption"],
        )

    def test_takeover_preserves_resolved_profile_for_no_task_spec(self) -> None:
        acquire = self.acquire_args(
            "root-a", self.repo, "spec-1", self.base / "ledger-old.md"
        )
        second = self.acquire_args("unused", self.repo, "spec-2")
        acquire.extend(["--source", second[second.index("--source") + 1]])
        claim = json.loads(run_claim(*acquire, env=self.env).stdout)["claim"]
        self.make_stale(claim)
        termination = "root-a-stopped"
        adoption = self.make_task_adoption(claim, termination)

        takeover = json.loads(
            run_claim(
                "--json",
                *self.takeover_args(
                    "root-b", [claim], [adoption], [termination]
                ),
                env=self.env,
            ).stdout
        )

        specs = takeover["claim"]["takeover_evidence"]["replaced_claims"][0][
            "task_adoption"
        ]["specs"]
        no_task = next(spec for spec in specs if spec["task_state"] == "no-task")
        self.assertEqual(no_task["task_ref"], "none")
        self.assertEqual(no_task["task_model"], "gpt-5.6-sol")
        self.assertEqual(no_task["task_thinking"], "high")
        self.assertEqual(no_task["thinking_reason"], "default-high-fixture")
        self.assertEqual(no_task["goal_evidence_ref"], "none")
        self.assertEqual(no_task["managed_checkouts"], [])

    def test_recovery_rejects_changed_replaced_snapshot_and_keeps_journal(self) -> None:
        claim = json.loads(
            run_claim(*self.acquire_args("root-a", self.repo, "spec-1"), env=self.env).stdout
        )["claim"]
        self.make_stale(claim)
        termination = "root-a-stopped"
        adoption = self.make_task_adoption(claim, termination)
        args = CLAIM_RUNTIME.build_parser().parse_args(
            self.takeover_args("root-b", [claim], [adoption], [termination])
        )
        with mock.patch.object(CLAIM_RUNTIME, "claim_root", return_value=self.claim_root):
            with mock.patch.object(
                CLAIM_RUNTIME,
                "delete_replaced_claim",
                side_effect=OSError("crash before first deletion"),
            ):
                with self.assertRaises(CLAIM_RUNTIME.ClaimError):
                    CLAIM_RUNTIME.takeover(args)

        prepared = json.loads(
            run_claim(
                "--json", "claim", "status", "--root-id", "root-b", env=self.env
            ).stdout
        )
        claim["heartbeat_at"] = "1999-01-01T00:00:00Z"
        (self.claim_root / "root-a.json").write_text(
            json.dumps(claim, indent=2, sort_keys=True) + "\n"
        )
        recovery = run_claim(
            "--json",
            "claim",
            "recover-takeover",
            "--root-id",
            "root-b",
            "--expected-transaction-id",
            prepared["transaction"]["transaction_id"],
            env=self.env,
            check=False,
        )
        self.assertEqual(recovery.returncode, 4)
        self.assertIn("changed after takeover preparation", recovery.stdout)
        self.assertTrue((self.claim_root / "root-a.json").is_file())
        self.assertTrue((self.claim_root / "root-b.takeover").is_file())
        self.assertFalse((self.claim_root / "root-b.json").exists())
        blocked = run_claim(
            *self.acquire_args("root-c", self.repo, "spec-3"),
            env=self.env,
            check=False,
        )
        self.assertEqual(blocked.returncode, 4)
        self.assertIn("changed after takeover preparation", blocked.stdout)

    def test_previous_claim_schemas_fail_closed_without_mutation(self) -> None:
        for schema_version in ("3.0.0", "4.0.0"):
            with self.subTest(schema_version=schema_version):
                if self.claim_root.exists():
                    for path in self.claim_root.iterdir():
                        if path.name != ".lock":
                            path.unlink()
                acquired = json.loads(
                    run_claim(
                        *self.acquire_args("root-a", self.repo, "spec-1"),
                        env=self.env,
                    ).stdout
                )["claim"]
                path = self.write_unsupported_claim(acquired, schema_version)
                before = path.read_bytes()

                for command in (
                    ("--json", "claim", "status"),
                    (*self.acquire_args("root-b", self.other_repo, "spec-2"),),
                ):
                    blocked = run_claim(*command, env=self.env, check=False)
                    self.assertEqual(blocked.returncode, 4)
                    error = json.loads(blocked.stdout)["error"]
                    self.assertEqual(error["code"], "state-conflict")
                    self.assertIn("unsupported claim schema", error["message"])
                    self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
