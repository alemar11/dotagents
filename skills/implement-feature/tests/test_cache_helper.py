from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = SKILL_ROOT.parents[1]
TOOL = SKILL_ROOT / "scripts/ledger-cache"
CLAIM_TOOL = SKILL_ROOT / "scripts/active-root-claim"
LOADER = importlib.machinery.SourceFileLoader("ledger_cache_runtime", str(TOOL))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
CACHE_RUNTIME = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(CACHE_RUNTIME)


def run_tool(
    tool: Path,
    *args: str,
    env: dict[str, str],
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(tool), *args],
        env=env,
        text=True,
        capture_output=True,
    )
    if check and result.returncode:
        raise AssertionError(
            f"{tool.name} failed ({result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result


def parse_result(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)


class LedgerCacheV3Tests(unittest.TestCase):
    source_ref = "https://github.com/example/dotagents/issues/232"
    task_key = "spec-232"
    task_title = "Implement Feature Spec 232"
    task_goal_objective = "Implement Feature Spec 232 exactly"

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.home_patch = mock.patch.dict(os.environ, {"HOME": str(self.home)})
        self.home_patch.start()
        self.addCleanup(self.home_patch.stop)
        self.cache_root = self.home / ".cache/dotagents/skills/implement-feature"
        self.claim_root = self.cache_root / "claims"
        self.ledger_root = self.cache_root / "ledgers"
        self.archive_root = self.ledger_root / "archive"
        self.packet_root = self.home / "packets"
        self.env = os.environ.copy()
        self.env["HOME"] = str(self.home)
        self.packet_index = 0
        self.operation_index = 0
        self.ledger = self.ledger_root / "portfolio-232.json"
        self.claim: dict | None = None
        self.registration: dict | None = None
        self.task_goal_fingerprint = hashlib.sha256(
            self.task_goal_objective.encode()
        ).hexdigest()

    def run_cache(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return run_tool(TOOL, *args, env=self.env, check=check)

    def run_claim(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return run_tool(CLAIM_TOOL, *args, env=self.env, check=check)

    def write_packet(self, value: object, stem: str) -> Path:
        self.packet_root.mkdir(parents=True, exist_ok=True)
        self.packet_index += 1
        path = self.packet_root / f"{self.packet_index:03d}-{stem}.json"
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        return path

    def next_operation_id(self) -> str:
        self.operation_index += 1
        return f"{self.operation_index:032x}"

    def acquire(
        self,
        *,
        ledger: Path | None = None,
        root_id: str = "root-a",
        source_ref: str | None = None,
    ) -> dict:
        ledger = ledger or self.ledger
        result = self.run_claim(
            "--json",
            "claim",
            "acquire",
            "--root-id",
            root_id,
            "--repository",
            str(REPOSITORY),
            "--source",
            source_ref or self.source_ref,
            "--ledger-ref",
            str(ledger),
        )
        self.claim = parse_result(result)["claim"]
        return self.claim

    def release(
        self,
        *,
        reason: str,
        evidence: str,
        root_id: str = "root-a",
    ) -> dict:
        assert self.claim is not None
        return parse_result(
            self.run_claim(
                "--json",
                "claim",
                "release",
                "--root-id",
                root_id,
                "--expected-fingerprint",
                self.claim["fingerprint"],
                "--release-reason",
                reason,
                "--evidence",
                evidence,
            )
        )

    def registration_for(self, claim: dict | None = None) -> dict:
        claim = claim or self.claim
        assert claim is not None
        objective = "Implement the registered Feature Spec portfolio"
        return {
            "schema_version": "2.0.0",
            "root_task_ref": "app-task://root-a",
            "root_checkout": str(REPOSITORY),
            "objective": objective,
            "objective_fingerprint": hashlib.sha256(objective.encode()).hexdigest(),
            "permission_evidence_ref": "user-message://authorized-visible-tasks",
            "repositories": claim["repositories"],
            "repository_checkouts": claim["repository_checkouts"],
            "sources": [
                {
                    "task_key": self.task_key,
                    "source_id": claim["sources"][0],
                    "source_spec_ref": claim["sources"][0],
                    "feature_spec_title": "Feature Spec: Typed Run State",
                    "feature_slug": "typed-run-state",
                    "source_state": "ready-for-agent",
                    "source_fingerprint": hashlib.sha256(
                        b"feature-spec-fixture"
                    ).hexdigest(),
                    "planned_done_ref": f"{claim['sources'][0]}#done",
                    "tracker_backend": "github",
                    "tracker_repository": claim["repositories"][0],
                    "deliveries": [
                        {
                            "delivery_key": "dotagents",
                            "repository": claim["repositories"][0],
                            "target_branch": "main",
                            "allowed_paths": ["skills/implement-feature/"],
                        }
                    ],
                    "dependency_ids": [],
                    "requires_domain_closeout": False,
                    "task_model": "gpt-5.6-sol",
                    "task_thinking": "xhigh",
                    "thinking_reason": "contract-sensitive state transition work",
                    "task_goal_objective_fingerprint": self.task_goal_fingerprint,
                }
            ],
        }

    def install_takeover_evidence(
        self,
        claim: dict,
        specs: list[dict],
        *,
        old_root_id: str = "root-old",
        termination_evidence: str = "app-task://old/terminated",
    ) -> dict:
        snapshot = copy.deepcopy(claim)
        snapshot["root_id"] = old_root_id
        snapshot["fingerprint"] = CACHE_RUNTIME.claim_fingerprint(snapshot)
        adoption = {
            "root_id": old_root_id,
            "claim_fingerprint": snapshot["fingerprint"],
            "task_termination_evidence": termination_evidence,
            "specs": specs,
        }
        evidence = {
            "stale_claim_takeover_permission": "granted-by-authorized-user",
            "takeover_reason": "verified-stale",
            "evidence": f"takeover://verified-stale/{old_root_id}",
            "transaction_id": "a" * 32,
            "replaced_claims": [
                {
                    "claim_snapshot": snapshot,
                    "task_termination_evidence": termination_evidence,
                    "task_adoption": adoption,
                }
            ],
        }
        evidence["evidence_fingerprint"] = CACHE_RUNTIME.request_fingerprint(evidence)
        claim["replaced_root_ids"] = [old_root_id]
        claim["takeover_evidence"] = evidence
        claim["fingerprint"] = CACHE_RUNTIME.claim_fingerprint(claim)
        claim_path = self.claim_root / f"{claim['root_id']}.json"
        claim_path.write_text(json.dumps(claim, indent=2, sort_keys=True) + "\n")
        self.claim = claim
        return claim

    def create(
        self,
        *,
        registration: dict | None = None,
        operation_id: str | None = None,
        check: bool = True,
        ledger: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        assert self.claim is not None
        ledger = ledger or self.ledger
        registration = registration or self.registration_for()
        self.registration = registration
        packet = self.write_packet(registration, "registration")
        return self.run_cache(
            "--json",
            "ledger",
            "create",
            "--ledger",
            str(ledger),
            "--root-id",
            self.claim["root_id"],
            "--expected-claim-fingerprint",
            self.claim["fingerprint"],
            "--operation-id",
            operation_id or self.next_operation_id(),
            "--registration-file",
            str(packet),
            check=check,
        )

    def apply_command(
        self,
        events: list[dict],
        *,
        expected_generation: int,
        operation_id: str,
    ) -> tuple[str, ...]:
        assert self.claim is not None
        packet = self.write_packet(events, "events")
        return (
            "--json",
            "ledger",
            "apply",
            "--ledger",
            str(self.ledger),
            "--root-id",
            self.claim["root_id"],
            "--expected-claim-fingerprint",
            self.claim["fingerprint"],
            "--expected-generation",
            str(expected_generation),
            "--operation-id",
            operation_id,
            "--events-file",
            str(packet),
        )

    def apply(
        self,
        events: list[dict],
        *,
        expected_generation: int | None = None,
        operation_id: str | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        generation = expected_generation or self.state()["generation"]
        command = self.apply_command(
            events,
            expected_generation=generation,
            operation_id=operation_id or self.next_operation_id(),
        )
        return self.run_cache(*command, check=check)

    def state(self) -> dict:
        return json.loads(self.ledger.read_text())

    def read_projection(self, projection: str) -> subprocess.CompletedProcess[str]:
        return self.run_cache(
            "--json",
            "ledger",
            "read",
            "--ledger",
            str(self.ledger),
            "--projection",
            projection,
        )

    def error(self, result: subprocess.CompletedProcess[str], code: str) -> dict:
        self.assertNotEqual(result.returncode, 0)
        payload = parse_result(result)
        self.assertEqual(payload["error"]["code"], code)
        return payload["error"]

    def task_event(
        self,
        *,
        state: str,
        goal_state: str = "active",
        title_evidence: str | None = "app-task://worker/title",
        model: str = "gpt-5.6-sol",
        reasoning_effort: str = "xhigh",
        goal_fingerprint: str | None = None,
    ) -> dict:
        return {
            "type": "task-observed",
            "task_key": self.task_key,
            "model": model,
            "reasoning_effort": reasoning_effort,
            "thinking_reason": "contract-sensitive state transition work",
            "task_title": self.task_title,
            "task_title_evidence_ref": title_evidence,
            "goal_objective_fingerprint": goal_fingerprint
            or self.task_goal_fingerprint,
            "goal_state": goal_state,
            "goal_evidence_ref": (
                "app-task://worker-232/goal" if goal_state != "pending" else None
            ),
            "state": state,
            "outcome": (
                "pull-request-ready-for-merge-but-not-merged"
                if state == "merge-ready"
                else None
            ),
            "attention_reason": None,
            "summary_ref": "app-task://worker-232/summary",
        }

    def checkout_event(self) -> dict:
        assert self.registration is not None
        delivery = self.registration["sources"][0]["deliveries"][0]
        return {
            "type": "managed-checkouts-observed",
            "task_key": self.task_key,
            "task_ref": "app-task://worker-232",
            "managed_checkouts": [
                {
                    "delivery_key": delivery["delivery_key"],
                    "repository": delivery["repository"],
                    "target_branch": delivery["target_branch"],
                    "checkout": str(REPOSITORY),
                    "git_top_level": str(REPOSITORY),
                    "baseline_revision": subprocess.run(
                        ["git", "-C", str(REPOSITORY), "rev-parse", "HEAD"],
                        text=True,
                        capture_output=True,
                        check=True,
                    ).stdout.strip(),
                    "isolation_evidence_ref": "app-task://worker-232/worktree",
                }
            ],
            "evidence_ref": "app-task://worker-232/checkout-map",
        }

    def bootstrap_active_task(self) -> None:
        self.acquire()
        self.create()
        state = self.state()
        objective_fingerprint = state["portfolio"]["objective_fingerprint"]
        self.apply(
            [
                {
                    "type": "root-title-observed",
                    "title": "👨🏻‍💻 Feature Orchestrator",
                    "evidence_ref": "app-task://root-a/title",
                },
                {
                    "type": "portfolio-goal-activated",
                    "goal_evidence_ref": "app-task://root-a/goal",
                    "objective_fingerprint": objective_fingerprint,
                },
                self.checkout_event(),
                self.task_event(state="created"),
                self.task_event(state="implementing"),
            ]
        )

    def direct_event(self, state: dict, event: dict, now: datetime) -> None:
        changed = CACHE_RUNTIME.apply_event(state, event, now)
        self.assertTrue(changed)

    def add_synthetic_delivery(self, state: dict) -> dict:
        task = state["tasks"][0]
        first = task["deliveries"][0]
        second = copy.deepcopy(first)
        repository = f"{first['repository']}-docs"
        head = "c" * 40
        merge_base = "d" * 40
        pr_url = "https://github.com/example/docs/pull/234"
        second.update(
            {
                "delivery_key": "docs",
                "repository": repository,
                "revision": {
                    "head_sha": head,
                    "base_ref": "main",
                    "merge_base_sha": merge_base,
                    "repository": repository,
                    "pr_number": 234,
                    "pr_url": pr_url,
                    "revision_key": CACHE_RUNTIME.revision_key(
                        repository, 234, pr_url, head, "main", merge_base
                    ),
                    "evidence_ref": "git://revision/docs",
                    "observed_at": "2026-07-18T11:00:00Z",
                },
                "pr": None,
                "committed": False,
                "published": False,
                "observation_evidence_ref": "git://revision/docs",
            }
        )
        if second["managed_checkout"] is not None:
            second["managed_checkout"] = {
                **second["managed_checkout"],
                "checkout": str(self.home / "docs-checkout"),
                "git_top_level": str(self.home / "docs-checkout"),
                "isolation_evidence_ref": "app-task://worker-232/docs-worktree",
            }
        task["deliveries"].append(second)
        state["portfolio"]["repositories"] = sorted(
            [*state["portfolio"]["repositories"], repository]
        )
        return second

    def prepare_review_polling_state(self) -> tuple[dict, dict]:
        self.bootstrap_active_task()
        revision = self.observe_revision()
        self.apply([self.task_event(state="review-polling")])
        return self.state(), revision

    def observe_revision(
        self,
        *,
        head: str = "a" * 40,
        merge_base: str = "b" * 40,
    ) -> dict:
        assert self.registration is not None
        repository = self.registration["sources"][0]["deliveries"][0]["repository"]
        self.apply(
            [
                {
                    "type": "revision-observed",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "head_sha": head,
                    "base_ref": "main",
                    "merge_base_sha": merge_base,
                    "repository": repository,
                    "pr_number": 233,
                    "pr_url": "https://github.com/example/dotagents/pull/233",
                    "evidence_ref": f"git://revision/{head}",
                }
            ]
        )
        return self.state()["tasks"][0]["deliveries"][0]["revision"]

    def pr_for(self, revision: dict) -> dict:
        assert self.registration is not None
        return {
            "repository": self.registration["sources"][0]["deliveries"][0]["repository"],
            "number": 233,
            "url": "https://github.com/example/dotagents/pull/233",
            "state": "open",
            "is_draft": False,
            "head_sha": revision["head_sha"],
            "base_ref": revision["base_ref"],
            "merge_base_sha": revision["merge_base_sha"],
            "mergeable": True,
            "merge_state": "clean",
            "closing_refs": [self.source_ref],
        }

    def observe_delivery(self, revision: dict, *, ready: bool = True) -> None:
        pr = self.pr_for(revision)
        if not ready:
            pr["is_draft"] = True
            pr["mergeable"] = False
            pr["merge_state"] = "blocked"
        self.apply(
            [
                {
                    "type": "delivery-observed",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "revision_key": revision["revision_key"],
                    "pr": pr,
                    "committed": True,
                    "published": True,
                    "evidence_ref": "gitstack://delivery/233",
                }
            ]
        )

    def start_clean_review(self, revision: dict) -> None:
        request_ref = "github-review://233/request-1"
        self.apply(
            [
                {
                    "type": "review-wait-started",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                }
            ]
        )
        review = self.state()["reviews"][-1]
        self.apply(
            [
                {
                    "type": "review-wait-invoked",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                    "wait_invoked_at": review["wait_started_at"],
                    "provider_timeout": 1800,
                },
                {
                    "type": "review-observed",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                    "monitoring_cycle": 0,
                    "provider_state": "clean",
                    "observation_fingerprint": hashlib.sha256(
                        b"clean-review"
                    ).hexdigest(),
                    "disposition": "accepted",
                    "evidence_ref": "github-review://233/clean",
                },
            ]
        )

    def pass_terminal_gates(self, revision: dict) -> None:
        events = []
        revision_set = CACHE_RUNTIME.current_revision_set_key(self.state()["tasks"][0])
        for gate in sorted(CACHE_RUNTIME.TASK_STATIC_GATES):
            events.append(
                {
                    "type": "gate-observed",
                    "task_key": self.task_key,
                    "delivery_key": None,
                    "gate": gate,
                    "state": "passed",
                    "binding_key": None,
                    "evidence_ref": f"proof://{gate}",
                }
            )
        for gate in sorted(CACHE_RUNTIME.DELIVERY_STATIC_GATES):
            events.append(
                {
                    "type": "gate-observed",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "gate": gate,
                    "state": "passed",
                    "binding_key": None,
                    "evidence_ref": f"proof://{gate}",
                }
            )
        for gate in sorted(CACHE_RUNTIME.TASK_REVISION_SET_GATES - {"domain-closeout"}):
            events.append(
                {
                    "type": "gate-observed",
                    "task_key": self.task_key,
                    "delivery_key": None,
                    "gate": gate,
                    "state": "passed",
                    "binding_key": revision_set,
                    "evidence_ref": f"proof://{gate}/{revision_set}",
                }
            )
        for gate in sorted(CACHE_RUNTIME.DELIVERY_REVISION_GATES):
            events.append(
                {
                    "type": "gate-observed",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "gate": gate,
                    "state": "passed",
                    "binding_key": revision["revision_key"],
                    "evidence_ref": f"proof://{gate}/{revision['revision_key']}",
                }
            )
        self.apply(events)

    def make_terminal_sealed_state(self) -> dict:
        self.bootstrap_active_task()
        revision = self.observe_revision()
        self.observe_delivery(revision)
        self.apply([self.task_event(state="draft-pr")])
        self.start_clean_review(revision)
        self.pass_terminal_gates(revision)
        seal = parse_result(self.read_projection("terminal"))["tasks"][0]
        seal_fingerprint = seal["seal_candidate_fingerprint"]
        revision_set = seal["revision_set_key"]
        self.apply(
            [
                {
                    "type": "task-terminal-sealed",
                    "task_key": self.task_key,
                    "revision_set_key": revision_set,
                    "seal_fingerprint": seal_fingerprint,
                    "evidence_ref": "proof://seal/232",
                }
            ]
        )
        return self.state()

    def make_terminal_state(self) -> dict:
        sealed = self.make_terminal_sealed_state()
        seal_fingerprint = sealed["tasks"][0]["seal"]["seal_fingerprint"]
        self.apply(
            [
                {
                    "type": "task-goal-completed",
                    "task_key": self.task_key,
                    "seal_fingerprint": seal_fingerprint,
                    "goal_evidence_ref": "app-task://worker-232/goal",
                    "completion_evidence_ref": "app-task://worker-232/goal-complete",
                },
                {
                    "type": "terminal-handoff-recorded",
                    "task_key": self.task_key,
                    "seal_fingerprint": seal_fingerprint,
                    "handoff_kind": "pull-request-ready",
                    "authority": "external-merge-required",
                    "evidence_ref": "https://github.com/example/dotagents/pull/233",
                    "next_action": "Human may merge after final inspection.",
                },
            ]
        )
        verification = parse_result(self.read_projection("terminal"))[
            "portfolio_verification_candidate"
        ]
        self.apply(
            [
                {
                    "type": "portfolio-terminal-verified",
                    "verification_fingerprint": verification,
                    "evidence_ref": "proof://portfolio-terminal/232",
                },
                {
                    "type": "portfolio-goal-completed",
                    "goal_evidence_ref": "app-task://root-a/goal",
                    "completion_evidence_ref": "app-task://root-a/goal-complete",
                    "verification_fingerprint": verification,
                },
            ]
        )
        terminal = parse_result(self.read_projection("terminal"))
        self.assertTrue(terminal["eligible"])
        return self.state()

    def make_legacy_archive(
        self,
        name: str,
        body: bytes,
        *,
        archived_at: datetime | None = None,
    ) -> dict:
        archived_at = archived_at or datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.ledger_root.mkdir(parents=True, exist_ok=True)
        source = self.ledger_root / f"{name}.md"
        source.write_bytes(body)
        digest = hashlib.sha256(body).hexdigest()
        archive_id = (
            f"{CACHE_RUNTIME.compact_timestamp(archived_at)}--{name}--{digest[:12]}"
        )
        metadata = {
            "schema_version": "1.0.0",
            "archive_id": archive_id,
            "archive_reason": "legacy-cutover",
            "archive_group": CACHE_RUNTIME.RETAINED_LEGACY_GROUP,
            "archived_at": CACHE_RUNTIME.format_timestamp(archived_at),
            "portfolio_key": name,
            "original_ledger_ref": str(source.resolve()),
            "ledger_sha256": digest,
            "size_bytes": len(body),
            "evidence_ref": "fixture://legacy-cutover",
            "root_id": None,
            "tool_version": "2.0.0",
        }
        entry = self.archive_root / CACHE_RUNTIME.RETAINED_LEGACY_GROUP / archive_id
        entry.mkdir(parents=True)
        (entry / "ledger.md").write_bytes(body)
        (entry / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n"
        )
        source.unlink()
        return CACHE_RUNTIME.validate_archive_entry(entry, verify_hash=True)

    def snapshot_tree(self, root: Path) -> dict[str, bytes | None]:
        if not root.exists():
            return {}
        snapshot: dict[str, bytes | None] = {}
        for path in sorted(root.rglob("*")):
            relative = str(path.relative_to(root))
            snapshot[relative] = path.read_bytes() if path.is_file() else None
        return snapshot

    def test_doctor_is_v4_offline_and_read_only(self) -> None:
        before = self.snapshot_tree(self.home)
        version = self.run_cache("--version").stdout.strip()
        doctor = parse_result(self.run_cache("--json", "doctor"))

        self.assertEqual(version, "4.0.0")
        self.assertTrue(doctor["ok"])
        self.assertTrue(doctor["offline"])
        self.assertEqual(doctor["active_ledgers"], [])
        self.assertEqual(doctor["archive_count"], 0)
        self.assertEqual(before, self.snapshot_tree(self.home))
        self.assertFalse(self.cache_root.exists())

    def test_create_rejects_unknown_fields_and_claim_mismatches_then_succeeds(self) -> None:
        claim = self.acquire()
        registration = self.registration_for(claim)

        mismatched = json.loads(json.dumps(registration))
        mismatched["repositories"] = ["/not/the/claimed/repository"]
        conflict = self.create(registration=mismatched, check=False)
        self.error(conflict, "state-conflict")
        self.assertFalse(self.ledger.exists())

        unknown = json.loads(json.dumps(registration))
        unknown["compatibility_mode"] = "legacy"
        rejected = self.create(registration=unknown, check=False)
        error = self.error(rejected, "invalid-input")
        self.assertEqual(error["details"]["unknown"], ["compatibility_mode"])
        self.assertFalse(self.ledger.exists())

        created = parse_result(self.create(registration=registration))
        self.assertEqual(created["mutation_state"], "created")
        self.assertEqual(created["generation"], 1)
        state = self.state()
        self.assertEqual(state["portfolio"]["repositories"], claim["repositories"])
        self.assertEqual(state["claim"]["fingerprint"], claim["fingerprint"])
        self.assertEqual(len(state["operations"]), 1)

    def test_active_paths_require_direct_json_and_reject_markdown(self) -> None:
        outside = self.home / "outside.json"
        result = self.run_claim(
            "--json",
            "claim",
            "acquire",
            "--root-id",
            "root-a",
            "--repository",
            str(REPOSITORY),
            "--source",
            self.source_ref,
            "--ledger-ref",
            str(outside),
            check=False,
        )
        self.error(result, "invalid-input")

        markdown = self.ledger_root / "portfolio-232.md"
        result = self.run_claim(
            "--json",
            "claim",
            "acquire",
            "--root-id",
            "root-a",
            "--repository",
            str(REPOSITORY),
            "--source",
            self.source_ref,
            "--ledger-ref",
            str(markdown),
            check=False,
        )
        self.error(result, "invalid-input")

        self.acquire(ledger=self.ledger)
        self.ledger_root.mkdir(parents=True, exist_ok=True)
        markdown.write_text("# stale active ledger\n")
        result = self.create(check=False)
        error = self.error(result, "unsupported-active-ledger")
        self.assertEqual(
            error["details"]["ledger"],
            os.path.abspath(os.fspath(markdown)),
        )
        self.assertFalse(self.ledger.exists())

    def test_apply_is_cas_idempotent_strict_and_does_not_record_noops(self) -> None:
        self.acquire()
        self.create()
        event = {
            "type": "root-title-observed",
            "title": "👨🏻‍💻 Feature Orchestrator",
            "evidence_ref": "app-task://root-a/title",
        }
        operation_id = self.next_operation_id()
        command = self.apply_command(
            [event], expected_generation=1, operation_id=operation_id
        )
        first = parse_result(self.run_cache(*command))
        replay = parse_result(self.run_cache(*command))
        self.assertEqual(first["mutation_state"], "applied")
        self.assertEqual(replay["mutation_state"], "already-applied")
        self.assertEqual(first["generation"], 2)
        self.assertEqual(replay["content_fingerprint"], first["content_fingerprint"])

        changed_packet = self.write_packet(
            [{**event, "evidence_ref": "app-task://root-a/other-title-proof"}],
            "changed-replay",
        )
        reused = self.run_cache(
            "--json",
            "ledger",
            "apply",
            "--ledger",
            str(self.ledger),
            "--root-id",
            "root-a",
            "--expected-claim-fingerprint",
            self.claim["fingerprint"],
            "--expected-generation",
            "2",
            "--operation-id",
            operation_id,
            "--events-file",
            str(changed_packet),
            check=False,
        )
        self.error(reused, "state-conflict")

        stale = self.apply(
            [event],
            expected_generation=1,
            operation_id=self.next_operation_id(),
            check=False,
        )
        self.error(stale, "state-conflict")

        unchanged = parse_result(
            self.apply([event], expected_generation=2, operation_id=self.next_operation_id())
        )
        self.assertEqual(unchanged["mutation_state"], "unchanged")
        self.assertEqual(unchanged["generation"], 2)
        self.assertEqual(len(self.state()["operations"]), 2)

        malformed = self.apply(
            [{**event, "legacy_note": "not allowed"}], check=False
        )
        error = self.error(malformed, "invalid-input")
        self.assertEqual(error["details"]["unknown"], ["legacy_note"])
        unsupported = self.apply(
            [{"type": "markdown-row-patched"}], check=False
        )
        self.error(unsupported, "invalid-input")
        self.assertEqual(self.state()["generation"], 2)

    def test_static_delivery_gates_make_dispatch_reachable_before_revision(self) -> None:
        self.acquire()
        self.create()
        self.apply(
            [
                {
                    "type": "gate-observed",
                    "task_key": self.task_key,
                    "delivery_key": None,
                    "gate": "dependency-integration",
                    "state": "passed",
                    "binding_key": None,
                    "evidence_ref": "proof://dependency-integration",
                },
                {
                    "type": "gate-observed",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "gate": "pr-preflight",
                    "state": "passed",
                    "binding_key": None,
                    "evidence_ref": "proof://pr-preflight/dotagents",
                },
            ]
        )
        task = self.state()["tasks"][0]
        self.assertIsNone(task["deliveries"][0]["revision"])
        dispatch = parse_result(self.read_projection("dispatch"))
        self.assertEqual(dispatch["ready_task_keys"], [])
        objective_fingerprint = self.state()["portfolio"]["objective_fingerprint"]
        self.apply(
            [
                {
                    "type": "root-title-observed",
                    "title": "👨🏻‍💻 Feature Orchestrator",
                    "evidence_ref": "app-task://root-a/title",
                },
                {
                    "type": "portfolio-goal-activated",
                    "goal_evidence_ref": "app-task://root-a/goal",
                    "objective_fingerprint": objective_fingerprint,
                },
            ]
        )
        dispatch = parse_result(self.read_projection("dispatch"))
        self.assertEqual(dispatch["ready_task_keys"], [self.task_key])

    def test_registration_represents_multiple_repository_deliveries_and_rejects_singular_v2(self) -> None:
        second = self.home / "second-repository"
        second.mkdir()
        subprocess.run(["git", "init", "-b", "main", str(second)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(second), "config", "user.email", "fixture@example.com"], check=True)
        subprocess.run(["git", "-C", str(second), "config", "user.name", "Fixture"], check=True)
        (second / "README.md").write_text("fixture\n")
        subprocess.run(["git", "-C", str(second), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(second), "commit", "-m", "fixture"], check=True, capture_output=True)
        claim = parse_result(
            self.run_claim(
                "--json", "claim", "acquire",
                "--root-id", "root-a",
                "--repository", str(REPOSITORY),
                "--repository", str(second),
                "--source", self.source_ref,
                "--ledger-ref", str(self.ledger),
            )
        )["claim"]
        self.claim = claim
        registration = self.registration_for(claim)
        registration["sources"][0]["deliveries"] = [
            {
                "delivery_key": f"delivery-{index}",
                "repository": repository,
                "target_branch": "main",
                "allowed_paths": ["src/"],
            }
            for index, repository in enumerate(claim["repositories"], start=1)
        ]
        registration["sources"][0]["tracker_repository"] = claim["repositories"][0]
        self.create(registration=registration)
        self.assertEqual(len(self.state()["tasks"][0]["deliveries"]), 2)

        old_shape = self.registration_for(claim)
        source = old_shape["sources"][0]
        source["repository"] = source["deliveries"][0]["repository"]
        source["target_branch"] = source["deliveries"][0]["target_branch"]
        source["allowed_paths"] = source["deliveries"][0]["allowed_paths"]
        del source["deliveries"]
        del source["tracker_repository"]
        with self.assertRaises(CACHE_RUNTIME.CacheError):
            CACHE_RUNTIME.validate_registration(old_shape, claim, self.ledger)

    def test_managed_checkout_map_and_task_profile_are_immutable_safety_gates(self) -> None:
        self.acquire()
        self.create()
        objective_fingerprint = self.state()["portfolio"]["objective_fingerprint"]
        self.apply(
            [
                {
                    "type": "root-title-observed",
                    "title": "👨🏻‍💻 Feature Orchestrator",
                    "evidence_ref": "app-task://root-a/title",
                },
                {
                    "type": "portfolio-goal-activated",
                    "goal_evidence_ref": "app-task://root-a/goal",
                    "objective_fingerprint": objective_fingerprint,
                },
            ]
        )
        before_checkout = self.apply([self.task_event(state="created")], check=False)
        self.error(before_checkout, "state-conflict")
        self.apply([self.checkout_event(), self.task_event(state="created")])
        wrong_profile = self.apply(
            [self.task_event(state="implementing", model="gpt-5.6-terra")], check=False
        )
        self.error(wrong_profile, "state-conflict")
        changed_checkout = self.checkout_event()
        changed_checkout["managed_checkouts"][0]["baseline_revision"] = "0" * 40
        rejected = self.apply([changed_checkout], check=False)
        self.error(rejected, "invalid-input")

    def test_worker_task_ref_cannot_collide_with_root_task_ref(self) -> None:
        self.acquire()
        self.create()
        collision = self.checkout_event()
        collision["task_ref"] = "app-task://root-a"
        rejected = self.apply([collision], check=False)
        self.error(rejected, "state-conflict")

        corrupt = self.state()
        corrupt["tasks"][0]["task_ref"] = corrupt["portfolio"]["root_task_ref"]
        CACHE_RUNTIME.seal_state_fingerprint(corrupt)
        with self.assertRaises(CACHE_RUNTIME.CacheError) as invalid:
            CACHE_RUNTIME.validate_state(corrupt, self.ledger)
        self.assertEqual(invalid.exception.code, "integrity-failure")

    def test_revision_and_review_evidence_are_delivery_scoped_and_invalidated(self) -> None:
        self.bootstrap_active_task()
        first = self.observe_revision()
        self.observe_delivery(first)
        self.start_clean_review(first)
        revision_set = CACHE_RUNTIME.current_revision_set_key(self.state()["tasks"][0])
        self.apply(
            [
                {
                    "type": "gate-observed",
                    "task_key": self.task_key,
                    "delivery_key": None,
                    "gate": "scope-acceptance",
                    "state": "passed",
                    "binding_key": revision_set,
                    "evidence_ref": "proof://scope/first",
                }
            ]
        )
        second = self.observe_revision(head="c" * 40, merge_base="d" * 40)
        projection = parse_result(self.read_projection("status"))
        task = projection["tasks"][0]
        self.assertNotEqual(second["revision_key"], first["revision_key"])
        self.assertNotIn("scope-acceptance", task["gates"])
        self.assertIn("dotagents:missing-current-review", task["terminal_blockers"])
        self.assertEqual(projection["due_reviews"], [])

    def test_review_monitoring_pause_resume_is_reachable_and_cycle_bound(self) -> None:
        self.bootstrap_active_task()
        revision = self.observe_revision()
        self.observe_delivery(revision)
        self.apply([self.task_event(state="review-polling")])
        state = self.state()
        started = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        request_ref = "github-review://233/request-monitoring"
        self.direct_event(
            state,
            {
                "type": "review-wait-started",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
            },
            started,
        )
        with self.assertRaises(CACHE_RUNTIME.CacheError) as before_start:
            CACHE_RUNTIME.apply_event(
                state,
                {
                    "type": "review-wait-invoked",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                    "wait_invoked_at": "2026-07-18T11:59:59Z",
                    "provider_timeout": 1801,
                },
                started,
            )
        self.assertEqual(before_start.exception.code, "invalid-input")
        self.direct_event(
            state,
            {
                "type": "review-wait-invoked",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
                "wait_invoked_at": "2026-07-18T12:00:00Z",
                "provider_timeout": 1800,
            },
            started,
        )
        deadline = started + timedelta(minutes=30)
        self.direct_event(
            state,
            {
                "type": "review-observed",
                "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                    "monitoring_cycle": 0,
                    "provider_state": "waiting",
                    "observation_fingerprint": hashlib.sha256(b"pending").hexdigest(),
                "disposition": "pending",
                "evidence_ref": "github-review://233/pending",
            },
            deadline,
        )
        self.direct_event(
            state,
            {
                "type": "review-monitoring-scheduled",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
            },
            deadline,
        )
        due_at = state["reviews"][0]["due_at"]
        schedule_fingerprint = CACHE_RUNTIME.task_monitoring_schedule_fingerprint(
            state, state["tasks"][0]
        )
        assert schedule_fingerprint is not None
        self.direct_event(
            state,
            {
                "type": "task-monitoring-paused",
                "task_key": self.task_key,
                "schedule_fingerprint": schedule_fingerprint,
                "pause_evidence_ref": "app-task://worker-232/goal-paused",
            },
            deadline,
        )
        active_root_state = copy.deepcopy(state)
        other = copy.deepcopy(active_root_state["tasks"][0])
        other.update(
            {
                "task_key": "spec-other",
                "source_id": "https://github.com/example/dotagents/issues/999",
                "source_spec_ref": "https://github.com/example/dotagents/issues/999",
                "task_ref": "app-task://worker-999",
                "state": "implementing",
                "goal_state": "active",
                "monitoring_schedule_fingerprint": None,
            }
        )
        active_root_state["tasks"].append(other)
        self.assertIn(
            "spec-other:controller-action-required",
            CACHE_RUNTIME.portfolio_pause_blockers(active_root_state, deadline),
        )
        due_while_root_active = CACHE_RUNTIME.parse_timestamp(due_at, "due_at")
        self.direct_event(
            active_root_state,
            {
                "type": "task-monitoring-resumed",
                "task_key": self.task_key,
                "schedule_fingerprint": schedule_fingerprint,
                "resume_reason": "due-review",
                "resume_evidence_ref": "app-task://worker-232/root-still-active",
            },
            due_while_root_active,
        )
        self.assertEqual(active_root_state["goal"]["state"], "active")
        self.assertEqual(active_root_state["monitoring"]["state"], "inactive")
        self.assertEqual(CACHE_RUNTIME.portfolio_pause_blockers(state, deadline), [])
        self.direct_event(
            state,
            {
                "type": "portfolio-goal-paused",
                "goal_evidence_ref": "app-task://root-a/goal",
                "pause_evidence_ref": "app-task://root-a/goal-paused",
                "heartbeat_id": "heartbeat-review",
                "target_thread_id": "app-task://root-a",
                "due_at": due_at,
            },
            deadline,
        )
        self.assertEqual(state["goal"]["state"], "paused")
        self.assertEqual(state["handoffs"], [])

        due = CACHE_RUNTIME.parse_timestamp(due_at, "due_at")
        self.direct_event(
            state,
            {
                "type": "portfolio-goal-resumed",
                "goal_evidence_ref": "app-task://root-a/goal",
                "heartbeat_id": "heartbeat-review",
                "resume_evidence_ref": "app-task://root-a/goal-resumed",
            },
            due,
        )
        self.direct_event(
            state,
            {
                "type": "task-monitoring-resumed",
                "task_key": self.task_key,
                "schedule_fingerprint": schedule_fingerprint,
                "resume_reason": "due-review",
                "resume_evidence_ref": "app-task://worker-232/goal-resumed",
            },
            due,
        )
        repeated_fingerprint = hashlib.sha256(b"pending").hexdigest()
        self.direct_event(
            state,
            {
                "type": "review-observed",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
                "monitoring_cycle": 1,
                "provider_state": "waiting",
                "observation_fingerprint": repeated_fingerprint,
                "disposition": "pending",
                "evidence_ref": "github-review://233/pending",
            },
            due,
        )
        delayed_apply = due + timedelta(minutes=5)
        self.direct_event(
            state,
            {
                "type": "review-monitoring-scheduled",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
            },
            delayed_apply,
        )
        review = state["reviews"][0]
        self.assertEqual(len(review["observations"]), 2)
        self.assertEqual(
            review["due_at"],
            CACHE_RUNTIME.format_timestamp(due + timedelta(minutes=30)),
        )

    def test_review_wait_uses_zero_for_exact_deadline_and_rejects_invalid_timeout(self) -> None:
        self.bootstrap_active_task()
        revision = self.observe_revision()
        self.observe_delivery(revision)
        self.apply([self.task_event(state="review-polling")])
        state = self.state()
        started = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        request_ref = "github-review://233/exact-deadline"
        self.direct_event(
            state,
            {
                "type": "review-wait-started",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
            },
            started,
        )
        deadline = started + timedelta(minutes=30)
        for invalid_timeout in (-1, False):
            with self.subTest(provider_timeout=invalid_timeout):
                with self.assertRaises(CACHE_RUNTIME.CacheError) as invalid:
                    CACHE_RUNTIME.apply_event(
                        state,
                        {
                            "type": "review-wait-invoked",
                            "task_key": self.task_key,
                            "delivery_key": "dotagents",
                            "revision_key": revision["revision_key"],
                            "request_ref": request_ref,
                            "wait_invoked_at": CACHE_RUNTIME.format_timestamp(deadline),
                            "provider_timeout": invalid_timeout,
                        },
                        deadline,
                    )
                self.assertEqual(invalid.exception.code, "invalid-input")
        with self.assertRaises(CACHE_RUNTIME.CacheError) as future:
            CACHE_RUNTIME.apply_event(
                state,
                {
                    "type": "review-wait-invoked",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                    "wait_invoked_at": CACHE_RUNTIME.format_timestamp(deadline),
                    "provider_timeout": 0,
                },
                deadline - timedelta(seconds=1),
            )
        self.assertEqual(future.exception.code, "invalid-input")
        self.direct_event(
            state,
            {
                "type": "review-wait-invoked",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
                "wait_invoked_at": CACHE_RUNTIME.format_timestamp(deadline),
                "provider_timeout": 0,
            },
            deadline,
        )
        self.direct_event(
            state,
            {
                "type": "review-observed",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
                "monitoring_cycle": 0,
                "provider_state": "clean",
                "observation_fingerprint": hashlib.sha256(b"clean-at-deadline").hexdigest(),
                "disposition": "accepted",
                "evidence_ref": "github-review://233/clean-at-deadline",
            },
            deadline,
        )

    def test_review_wait_expired_before_launch_uses_zero_and_schedules_from_observation(self) -> None:
        self.bootstrap_active_task()
        revision = self.observe_revision()
        self.observe_delivery(revision)
        self.apply([self.task_event(state="review-polling")])
        state = self.state()
        started = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        request_ref = "github-review://233/expired-before-launch"
        self.direct_event(
            state,
            {
                "type": "review-wait-started",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
            },
            started,
        )
        observed_at = started + timedelta(minutes=35)
        self.direct_event(
            state,
            {
                "type": "review-wait-invoked",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
                "wait_invoked_at": CACHE_RUNTIME.format_timestamp(observed_at),
                "provider_timeout": 0,
            },
            observed_at,
        )
        self.direct_event(
            state,
            {
                "type": "review-observed",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
                "monitoring_cycle": 0,
                "provider_state": "waiting",
                "observation_fingerprint": hashlib.sha256(b"late-pending").hexdigest(),
                "disposition": "pending",
                "evidence_ref": "github-review://233/late-pending",
            },
            observed_at,
        )
        self.direct_event(
            state,
            {
                "type": "review-monitoring-scheduled",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
            },
            observed_at,
        )
        self.assertEqual(
            state["reviews"][0]["due_at"],
            CACHE_RUNTIME.format_timestamp(observed_at + timedelta(minutes=30)),
        )

    def test_task_monitoring_epoch_resumes_all_due_deliveries_once(self) -> None:
        self.bootstrap_active_task()
        first_revision = self.observe_revision()
        self.observe_delivery(first_revision)
        self.apply([self.task_event(state="review-polling")])
        state = self.state()
        second = self.add_synthetic_delivery(state)
        revisions = {
            "dotagents": first_revision,
            "docs": second["revision"],
        }
        started = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        for delivery_key, revision in revisions.items():
            request_ref = f"github-review://{delivery_key}/pending"
            self.direct_event(
                state,
                {
                    "type": "review-wait-started",
                    "task_key": self.task_key,
                    "delivery_key": delivery_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                },
                started,
            )
            self.direct_event(
                state,
                {
                    "type": "review-wait-invoked",
                    "task_key": self.task_key,
                    "delivery_key": delivery_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                    "wait_invoked_at": CACHE_RUNTIME.format_timestamp(started),
                    "provider_timeout": 1800,
                },
                started,
            )
        deadline = started + timedelta(minutes=30)
        for delivery_key, revision in revisions.items():
            request_ref = f"github-review://{delivery_key}/pending"
            self.direct_event(
                state,
                {
                    "type": "review-observed",
                    "task_key": self.task_key,
                    "delivery_key": delivery_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                    "monitoring_cycle": 0,
                    "provider_state": "waiting",
                    "observation_fingerprint": hashlib.sha256(
                        f"pending-{delivery_key}".encode()
                    ).hexdigest(),
                    "disposition": "pending",
                    "evidence_ref": f"github-review://{delivery_key}/observation",
                },
                deadline,
            )
            self.direct_event(
                state,
                {
                    "type": "review-monitoring-scheduled",
                    "task_key": self.task_key,
                    "delivery_key": delivery_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                },
                deadline,
            )
        self.assertEqual(state["tasks"][0]["state"], "review-polling")
        schedule_fingerprint = CACHE_RUNTIME.task_monitoring_schedule_fingerprint(
            state, state["tasks"][0]
        )
        assert schedule_fingerprint is not None
        self.direct_event(
            state,
            {
                "type": "task-monitoring-paused",
                "task_key": self.task_key,
                "schedule_fingerprint": schedule_fingerprint,
                "pause_evidence_ref": "app-task://worker-232/multi-paused",
            },
            deadline,
        )
        due_at = state["reviews"][0]["due_at"]
        self.direct_event(
            state,
            {
                "type": "portfolio-goal-paused",
                "goal_evidence_ref": "app-task://root-a/goal",
                "pause_evidence_ref": "app-task://root-a/multi-paused",
                "heartbeat_id": "heartbeat-multi",
                "target_thread_id": "app-task://root-a",
                "due_at": due_at,
            },
            deadline,
        )
        due = CACHE_RUNTIME.parse_timestamp(due_at, "due_at")
        self.direct_event(
            state,
            {
                "type": "portfolio-goal-resumed",
                "goal_evidence_ref": "app-task://root-a/goal",
                "heartbeat_id": "heartbeat-multi",
                "resume_evidence_ref": "app-task://root-a/multi-resumed",
            },
            due,
        )
        self.direct_event(
            state,
            {
                "type": "task-monitoring-resumed",
                "task_key": self.task_key,
                "schedule_fingerprint": schedule_fingerprint,
                "resume_reason": "due-review",
                "resume_evidence_ref": "app-task://worker-232/multi-resumed",
            },
            due,
        )
        self.assertEqual(
            {review["delivery_key"] for review in state["reviews"] if review["monitoring_state"] == "checking"},
            {"dotagents", "docs"},
        )
        for delivery_key, provider_state, disposition in (
            ("dotagents", "clean", "accepted"),
            ("docs", "waiting", "pending"),
        ):
            revision = revisions[delivery_key]
            self.direct_event(
                state,
                {
                    "type": "review-observed",
                    "task_key": self.task_key,
                    "delivery_key": delivery_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": f"github-review://{delivery_key}/pending",
                    "monitoring_cycle": 1,
                    "provider_state": provider_state,
                    "observation_fingerprint": hashlib.sha256(
                        f"cycle-1-{delivery_key}".encode()
                    ).hexdigest(),
                    "disposition": disposition,
                    "evidence_ref": f"github-review://{delivery_key}/cycle-1",
                },
                due,
            )
        self.direct_event(
            state,
            {
                "type": "review-monitoring-scheduled",
                "task_key": self.task_key,
                "delivery_key": "docs",
                "revision_key": revisions["docs"]["revision_key"],
                "request_ref": "github-review://docs/pending",
            },
            due,
        )
        next_fingerprint = CACHE_RUNTIME.task_monitoring_schedule_fingerprint(
            state, state["tasks"][0]
        )
        assert next_fingerprint is not None
        self.direct_event(
            state,
            {
                "type": "task-monitoring-paused",
                "task_key": self.task_key,
                "schedule_fingerprint": next_fingerprint,
                "pause_evidence_ref": "app-task://worker-232/clean-plus-pending-paused",
            },
            due,
        )
        self.assertEqual(state["tasks"][0]["state"], "review-monitoring")

    def test_controller_resume_makes_replaced_revision_schedule_inert(self) -> None:
        self.bootstrap_active_task()
        first_revision = self.observe_revision()
        self.observe_delivery(first_revision)
        self.apply([self.task_event(state="review-polling")])
        state = self.state()
        second = self.add_synthetic_delivery(state)
        starts = {
            "dotagents": datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc),
            "docs": datetime(2026, 7, 18, 12, 0, 0, 100000, tzinfo=timezone.utc),
        }
        revisions = {"dotagents": first_revision, "docs": second["revision"]}
        for delivery_key, revision in revisions.items():
            started = starts[delivery_key]
            request_ref = f"github-review://{delivery_key}/stale"
            self.direct_event(
                state,
                {
                    "type": "review-wait-started",
                    "task_key": self.task_key,
                    "delivery_key": delivery_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                },
                started,
            )
            self.direct_event(
                state,
                {
                    "type": "review-wait-invoked",
                    "task_key": self.task_key,
                    "delivery_key": delivery_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                    "wait_invoked_at": CACHE_RUNTIME.format_timestamp(started),
                    "provider_timeout": 1800,
                },
                started,
            )
            observed_at = started + timedelta(minutes=30)
            self.direct_event(
                state,
                {
                    "type": "review-observed",
                    "task_key": self.task_key,
                    "delivery_key": delivery_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                    "monitoring_cycle": 0,
                    "provider_state": "waiting",
                    "observation_fingerprint": hashlib.sha256(
                        f"stale-{delivery_key}".encode()
                    ).hexdigest(),
                    "disposition": "pending",
                    "evidence_ref": f"github-review://{delivery_key}/stale-observation",
                },
                observed_at,
            )
            self.direct_event(
                state,
                {
                    "type": "review-monitoring-scheduled",
                    "task_key": self.task_key,
                    "delivery_key": delivery_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                },
                observed_at,
            )
        now = starts["docs"] + timedelta(minutes=30)
        schedule_fingerprint = CACHE_RUNTIME.task_monitoring_schedule_fingerprint(
            state, state["tasks"][0]
        )
        assert schedule_fingerprint is not None
        self.direct_event(
            state,
            {
                "type": "task-monitoring-paused",
                "task_key": self.task_key,
                "schedule_fingerprint": schedule_fingerprint,
                "pause_evidence_ref": "app-task://worker-232/controller-paused",
            },
            now,
        )
        scheduled = CACHE_RUNTIME.current_scheduled_reviews(state)
        self.assertEqual(scheduled[0][1]["delivery_key"], "dotagents")
        earliest_due = scheduled[0][2]["due_at"]
        self.direct_event(
            state,
            {
                "type": "portfolio-goal-paused",
                "goal_evidence_ref": "app-task://root-a/goal",
                "pause_evidence_ref": "app-task://root-a/controller-paused",
                "heartbeat_id": "heartbeat-controller",
                "target_thread_id": "app-task://root-a",
                "due_at": earliest_due,
            },
            now,
        )
        early = now + timedelta(minutes=5)
        self.direct_event(
            state,
            {
                "type": "portfolio-goal-resumed",
                "goal_evidence_ref": "app-task://root-a/goal",
                "heartbeat_id": "heartbeat-controller",
                "resume_evidence_ref": "app-task://root-a/controller-resumed",
            },
            early,
        )
        self.direct_event(
            state,
            {
                "type": "task-monitoring-resumed",
                "task_key": self.task_key,
                "schedule_fingerprint": schedule_fingerprint,
                "resume_reason": "controller-action",
                "resume_evidence_ref": "app-task://worker-232/controller-resumed",
            },
            early,
        )
        repository = state["tasks"][0]["deliveries"][0]["repository"]
        self.direct_event(
            state,
            {
                "type": "revision-observed",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "head_sha": "e" * 40,
                "base_ref": "main",
                "merge_base_sha": "f" * 40,
                "repository": repository,
                "pr_number": 233,
                "pr_url": "https://github.com/example/dotagents/pull/233",
                "evidence_ref": "git://revision/replaced",
            },
            early,
        )
        self.assertEqual(
            [delivery["delivery_key"] for _, delivery, _ in CACHE_RUNTIME.current_scheduled_reviews(state)],
            ["docs"],
        )
        current_fingerprint = CACHE_RUNTIME.task_monitoring_schedule_fingerprint(
            state, state["tasks"][0]
        )
        assert current_fingerprint is not None
        docs_due = CACHE_RUNTIME.parse_timestamp(
            CACHE_RUNTIME.current_scheduled_reviews(state)[0][2]["due_at"],
            "due_at",
        )
        self.direct_event(
            state,
            {
                "type": "task-monitoring-resumed",
                "task_key": self.task_key,
                "schedule_fingerprint": current_fingerprint,
                "resume_reason": "due-review",
                "resume_evidence_ref": "app-task://worker-232/already-active",
            },
            docs_due,
        )
        self.assertEqual(
            next(review for review in state["reviews"] if review["delivery_key"] == "docs")[
                "monitoring_state"
            ],
            "checking",
        )

    def test_staged_closeout_and_post_terminal_drift_preserve_completed_goals(self) -> None:
        state = self.make_terminal_state()
        terminal = parse_result(self.read_projection("terminal"))
        self.assertTrue(terminal["archive_ready"])
        self.assertEqual(terminal["phase"], "archive-ready")
        task = state["tasks"][0]
        goal_evidence = state["goal"]["completion_evidence_ref"]
        self.apply(
            [
                {
                    "type": "post-terminal-drift-recorded",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "seal_fingerprint": task["seal"]["seal_fingerprint"],
                    "drift_fingerprint": hashlib.sha256(b"head-drift").hexdigest(),
                    "reason": "The PR head changed after terminal verification.",
                    "evidence_ref": "git://post-terminal-drift/233",
                }
            ]
        )
        drifted = parse_result(self.read_projection("terminal"))
        self.assertEqual(drifted["phase"], "drifted")
        self.assertFalse(drifted["archive_ready"])
        self.assertEqual(self.state()["goal"]["state"], "complete")
        self.assertEqual(self.state()["goal"]["completion_evidence_ref"], goal_evidence)

    def test_sealed_task_rejects_all_ordinary_mutations_and_repeated_seal(self) -> None:
        sealed = self.make_terminal_sealed_state()
        now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        ordinary_events = {
            "managed-checkouts-observed",
            "task-observed",
            "revision-observed",
            "delivery-observed",
            "source-moved",
            "review-wait-started",
            "review-wait-invoked",
            "review-observed",
            "review-monitoring-scheduled",
            "task-monitoring-paused",
            "task-monitoring-resumed",
            "gate-observed",
            "task-terminal-sealed",
        }
        for event_type in sorted(ordinary_events):
            with self.subTest(event_type=event_type):
                candidate = copy.deepcopy(sealed)
                with self.assertRaises(CACHE_RUNTIME.CacheError) as rejected:
                    CACHE_RUNTIME.apply_event(
                        candidate,
                        {"type": event_type, "task_key": self.task_key},
                        now,
                    )
                self.assertEqual(rejected.exception.code, "state-conflict")
                self.assertEqual(candidate, sealed)

    def test_post_terminal_drift_is_recordable_at_every_post_seal_stage(self) -> None:
        sealed = self.make_terminal_sealed_state()
        seal_fingerprint = sealed["tasks"][0]["seal"]["seal_fingerprint"]
        now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        stages = [("terminal-sealed", copy.deepcopy(sealed))]

        worker_complete = copy.deepcopy(sealed)
        CACHE_RUNTIME.apply_event(
            worker_complete,
            {
                "type": "task-goal-completed",
                "task_key": self.task_key,
                "seal_fingerprint": seal_fingerprint,
                "goal_evidence_ref": "app-task://worker-232/goal",
                "completion_evidence_ref": "app-task://worker-232/goal-complete",
            },
            now,
        )
        stages.append(("worker-goal-complete", copy.deepcopy(worker_complete)))

        handed_off = copy.deepcopy(worker_complete)
        CACHE_RUNTIME.apply_event(
            handed_off,
            {
                "type": "terminal-handoff-recorded",
                "task_key": self.task_key,
                "seal_fingerprint": seal_fingerprint,
                "handoff_kind": "pull-request-ready",
                "authority": "external-merge-required",
                "evidence_ref": "https://github.com/example/dotagents/pull/233",
                "next_action": "Human may merge after final inspection.",
            },
            now,
        )
        stages.append(("terminal-handoff", copy.deepcopy(handed_off)))

        verified = copy.deepcopy(handed_off)
        verification = CACHE_RUNTIME.portfolio_verification_candidate(verified)
        self.assertIsNotNone(verification)
        CACHE_RUNTIME.apply_event(
            verified,
            {
                "type": "portfolio-terminal-verified",
                "verification_fingerprint": verification,
                "evidence_ref": "proof://portfolio-terminal/232",
            },
            now,
        )
        stages.append(("portfolio-verified", copy.deepcopy(verified)))

        root_complete = copy.deepcopy(verified)
        CACHE_RUNTIME.apply_event(
            root_complete,
            {
                "type": "portfolio-goal-completed",
                "goal_evidence_ref": "app-task://root-a/goal",
                "completion_evidence_ref": "app-task://root-a/goal-complete",
                "verification_fingerprint": verification,
            },
            now,
        )
        stages.append(("portfolio-goal-complete", root_complete))

        for stage_name, stage in stages:
            with self.subTest(stage=stage_name):
                task_goal_before = (
                    stage["tasks"][0]["goal_state"],
                    stage["tasks"][0]["goal_completion_evidence_ref"],
                )
                root_goal_before = (
                    stage["goal"]["state"],
                    stage["goal"]["completion_evidence_ref"],
                )
                changed = CACHE_RUNTIME.apply_event(
                    stage,
                    {
                        "type": "post-terminal-drift-recorded",
                        "task_key": self.task_key,
                        "delivery_key": "dotagents",
                        "seal_fingerprint": seal_fingerprint,
                        "drift_fingerprint": hashlib.sha256(
                            f"head-drift-{stage_name}".encode()
                        ).hexdigest(),
                        "reason": f"The PR head changed during {stage_name}.",
                        "evidence_ref": f"git://post-terminal-drift/{stage_name}",
                    },
                    now,
                )
                self.assertTrue(changed)
                self.assertEqual(
                    (
                        stage["tasks"][0]["goal_state"],
                        stage["tasks"][0]["goal_completion_evidence_ref"],
                    ),
                    task_goal_before,
                )
                self.assertEqual(
                    (stage["goal"]["state"], stage["goal"]["completion_evidence_ref"]),
                    root_goal_before,
                )
                terminal = CACHE_RUNTIME.terminal_projection(stage)
                self.assertEqual(terminal["phase"], "drifted")
                self.assertFalse(terminal["archive_ready"])
                CACHE_RUNTIME.seal_state_fingerprint(stage)
                CACHE_RUNTIME.validate_state(stage, self.ledger)

    def test_pre_completion_drift_preserves_goal_fact_but_blocks_terminal_handoff(self) -> None:
        state = self.make_terminal_sealed_state()
        seal_fingerprint = state["tasks"][0]["seal"]["seal_fingerprint"]
        now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        CACHE_RUNTIME.apply_event(
            state,
            {
                "type": "post-terminal-drift-recorded",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "seal_fingerprint": seal_fingerprint,
                "drift_fingerprint": hashlib.sha256(b"pre-completion-drift").hexdigest(),
                "reason": "The PR head changed before Goal completion was recorded.",
                "evidence_ref": "git://post-terminal-drift/pre-completion",
            },
            now,
        )
        CACHE_RUNTIME.apply_event(
            state,
            {
                "type": "task-goal-completed",
                "task_key": self.task_key,
                "seal_fingerprint": seal_fingerprint,
                "goal_evidence_ref": "app-task://worker-232/goal",
                "completion_evidence_ref": "app-task://worker-232/goal-complete",
            },
            now,
        )
        self.assertEqual(state["tasks"][0]["goal_state"], "complete")
        self.assertIsNotNone(state["tasks"][0]["post_terminal_drift"])
        with self.assertRaises(CACHE_RUNTIME.CacheError) as rejected:
            CACHE_RUNTIME.apply_event(
                state,
                {
                    "type": "terminal-handoff-recorded",
                    "task_key": self.task_key,
                    "seal_fingerprint": seal_fingerprint,
                    "handoff_kind": "pull-request-ready",
                    "authority": "external-merge-required",
                    "evidence_ref": "https://github.com/example/dotagents/pull/233",
                    "next_action": "Human may merge after final inspection.",
                },
                now,
            )
        self.assertEqual(rejected.exception.code, "state-conflict")
        self.assertEqual(state["tasks"][0]["goal_state"], "complete")

    def test_local_source_move_is_proof_gated_and_marks_tracker_delivery_dirty(self) -> None:
        self.acquire()
        registration = self.registration_for()
        registration["sources"][0]["tracker_backend"] = "local"
        registration["sources"][0]["planned_done_ref"] = "planning/features/typed-run-state/issues/done/232.md"
        registration["sources"][0]["source_spec_ref"] = self.source_ref
        self.create(registration=registration)
        objective_fingerprint = self.state()["portfolio"]["objective_fingerprint"]
        self.apply(
            [
                {"type": "root-title-observed", "title": "👨🏻‍💻 Feature Orchestrator", "evidence_ref": "app-task://root-a/title"},
                {"type": "portfolio-goal-activated", "goal_evidence_ref": "app-task://root-a/goal", "objective_fingerprint": objective_fingerprint},
                self.checkout_event(),
                self.task_event(state="created"),
                self.task_event(state="implementing"),
            ]
        )
        revision = self.observe_revision()
        self.observe_delivery(revision)
        self.start_clean_review(revision)
        self.pass_terminal_gates(revision)
        revision_set = CACHE_RUNTIME.current_revision_set_key(self.state()["tasks"][0])
        self.apply(
            [
                {
                    "type": "source-moved",
                    "task_key": self.task_key,
                    "from_ref": self.source_ref,
                    "to_ref": registration["sources"][0]["planned_done_ref"],
                    "source_fingerprint": self.state()["sources"][0]["fingerprint"],
                    "tracker_repository": registration["sources"][0]["tracker_repository"],
                    "revision_set_key": revision_set,
                    "evidence_ref": "git://move-local-source/232",
                }
            ]
        )
        delivery = self.state()["tasks"][0]["deliveries"][0]
        self.assertEqual(delivery["tracker_dirty_after_revision_key"], revision["revision_key"])
        self.assertIsNone(parse_result(self.read_projection("terminal"))["tasks"][0]["seal_candidate_fingerprint"])

    def test_takeover_create_derives_recorded_adoption_from_live_claim(self) -> None:
        claim = self.acquire()
        snapshot = copy.deepcopy(claim)
        snapshot["root_id"] = "root-old"
        snapshot["fingerprint"] = CACHE_RUNTIME.claim_fingerprint(snapshot)
        checkout = {
            "repository": claim["repositories"][0],
            "checkout": str(REPOSITORY),
            "target_branch_name": "main",
            "git_top_level": str(REPOSITORY),
            "baseline_revision": subprocess.run(
                ["git", "-C", str(REPOSITORY), "rev-parse", "HEAD"],
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip(),
            "isolation_evidence_ref": "takeover://checkout",
        }
        claim["replaced_root_ids"] = ["root-old"]
        adoption = {
            "root_id": "root-old",
            "claim_fingerprint": snapshot["fingerprint"],
            "task_termination_evidence": "app-task://old/terminated",
            "specs": [
                {
                    "source_spec_ref": self.source_ref,
                    "task_state": "recorded",
                    "task_ref": "app-task://old-worker",
                    "task_model": "gpt-5.6-sol",
                    "task_thinking": "xhigh",
                    "thinking_reason": "contract-sensitive state transition work",
                    "goal_evidence_ref": "app-task://old-worker/goal",
                    "managed_checkouts": [checkout],
                    "evidence_ref": "takeover://task-adoption",
                }
            ],
        }
        evidence = {
            "stale_claim_takeover_permission": "granted-by-authorized-user",
            "takeover_reason": "verified-stale",
            "evidence": "takeover://verified-stale/root-old",
            "transaction_id": "a" * 32,
            "replaced_claims": [
                {
                    "claim_snapshot": snapshot,
                    "task_termination_evidence": "app-task://old/terminated",
                    "task_adoption": adoption,
                }
            ],
        }
        evidence["evidence_fingerprint"] = CACHE_RUNTIME.request_fingerprint(evidence)
        claim["takeover_evidence"] = evidence
        claim["fingerprint"] = CACHE_RUNTIME.claim_fingerprint(claim)
        claim_path = self.claim_root / "root-a.json"
        claim_path.write_text(json.dumps(claim, indent=2, sort_keys=True) + "\n")
        self.claim = claim
        created = parse_result(self.create())
        self.assertEqual(created["mutation_state"], "created")
        task = self.state()["tasks"][0]
        self.assertEqual(task["adoption"]["origin_root_id"], "root-old")
        self.assertEqual(task["task_ref"], "app-task://old-worker")
        self.assertEqual(task["goal_state"], "active")
        self.assertEqual(task["goal_evidence_ref"], "app-task://old-worker/goal")
        self.assertIsNotNone(task["deliveries"][0]["managed_checkout"])

    def test_takeover_adoptions_bind_by_source_id_and_are_consumed_once(self) -> None:
        second_source = "https://github.com/example/dotagents/issues/234"
        claim = parse_result(
            self.run_claim(
                "--json",
                "claim",
                "acquire",
                "--root-id",
                "root-a",
                "--repository",
                str(REPOSITORY),
                "--source",
                self.source_ref,
                "--source",
                second_source,
                "--ledger-ref",
                str(self.ledger),
            )
        )["claim"]
        specs = [
            {
                "source_spec_ref": source_id,
                "task_state": "no-task",
                "task_ref": "none",
                "task_model": "gpt-5.6-sol",
                "task_thinking": "xhigh",
                "thinking_reason": "contract-sensitive state transition work",
                "goal_evidence_ref": "none",
                "managed_checkouts": [],
                "evidence_ref": f"takeover://adoption/{index}",
            }
            for index, source_id in enumerate(claim["sources"], start=1)
        ]
        self.install_takeover_evidence(claim, specs)

        registration = self.registration_for(claim)
        first = registration["sources"][0]
        first["source_spec_ref"] = claim["sources"][0]
        first["planned_done_ref"] = claim["sources"][0]
        second = copy.deepcopy(first)
        second.update(
            {
                "task_key": "spec-234",
                "source_id": claim["sources"][1],
                # Deliberately share the authored ref. Canonical source_id must
                # still select and consume the second embedded adoption.
                "source_spec_ref": claim["sources"][0],
                "planned_done_ref": claim["sources"][0],
                "feature_spec_title": "Feature Spec: Typed Run State Two",
                "feature_slug": "typed-run-state-two",
                "source_fingerprint": hashlib.sha256(b"feature-spec-two").hexdigest(),
            }
        )
        registration["sources"].append(second)
        created = parse_result(self.create(registration=registration))
        self.assertEqual(created["mutation_state"], "created")
        evidence_by_source = {
            task["source_id"]: task["adoption"]["evidence_ref"]
            for task in self.state()["tasks"]
        }
        self.assertEqual(
            evidence_by_source,
            {
                claim["sources"][0]: "takeover://adoption/1",
                claim["sources"][1]: "takeover://adoption/2",
            },
        )

    def test_takeover_evidence_tampering_is_rejected_even_with_core_claim_fingerprint(self) -> None:
        claim = self.acquire()
        specs = [
            {
                "source_spec_ref": claim["sources"][0],
                "task_state": "no-task",
                "task_ref": "none",
                "task_model": "gpt-5.6-sol",
                "task_thinking": "xhigh",
                "thinking_reason": "contract-sensitive state transition work",
                "goal_evidence_ref": "none",
                "managed_checkouts": [],
                "evidence_ref": "takeover://adoption/1",
            }
        ]
        valid = copy.deepcopy(self.install_takeover_evidence(claim, specs))
        claim_path = self.claim_root / "root-a.json"

        fingerprint_tamper = copy.deepcopy(valid)
        fingerprint_tamper["takeover_evidence"]["replaced_claims"][0][
            "task_adoption"
        ]["specs"][0]["evidence_ref"] = "takeover://tampered"
        self.assertIsNotNone(
            CACHE_RUNTIME.claim_artifact_error(claim_path, fingerprint_tamper)
        )

        semantic_tamper = copy.deepcopy(valid)
        semantic_tamper["takeover_evidence"]["replaced_claims"][0][
            "task_termination_evidence"
        ] = "app-task://different/termination"
        evidence = semantic_tamper["takeover_evidence"]
        del evidence["evidence_fingerprint"]
        evidence["evidence_fingerprint"] = CACHE_RUNTIME.request_fingerprint(evidence)
        self.assertEqual(semantic_tamper["fingerprint"], valid["fingerprint"])
        self.assertIsNotNone(
            CACHE_RUNTIME.claim_artifact_error(claim_path, semantic_tamper)
        )
        claim_path.write_text(json.dumps(semantic_tamper, indent=2, sort_keys=True) + "\n")
        self.claim = semantic_tamper
        rejected = self.create(check=False)
        self.error(rejected, "state-conflict")
        self.assertFalse(self.ledger.exists())

    def test_takeover_create_reverifies_adopted_checkout_git_identity(self) -> None:
        claim = self.acquire()
        missing_checkout = self.home / "removed-worker-checkout"
        specs = [
            {
                "source_spec_ref": claim["sources"][0],
                "task_state": "recorded",
                "task_ref": "app-task://old-worker",
                "task_model": "gpt-5.6-sol",
                "task_thinking": "xhigh",
                "thinking_reason": "contract-sensitive state transition work",
                "goal_evidence_ref": "app-task://old-worker/goal",
                "managed_checkouts": [
                    {
                        "repository": claim["repositories"][0],
                        "checkout": str(missing_checkout),
                        "target_branch_name": "main",
                        "git_top_level": str(missing_checkout),
                        "baseline_revision": "a" * 40,
                        "isolation_evidence_ref": "takeover://removed-checkout",
                    }
                ],
                "evidence_ref": "takeover://adoption/1",
            }
        ]
        self.install_takeover_evidence(claim, specs)
        rejected = self.create(check=False)
        self.error(rejected, "invalid-input")
        self.assertFalse(self.ledger.exists())

    def test_non_takeover_create_initializes_no_task_adoption_without_goal_evidence(self) -> None:
        self.acquire()
        self.create()
        task = self.state()["tasks"][0]
        self.assertEqual(task["adoption"]["task_state"], "no-task")
        self.assertIsNone(task["task_ref"])
        self.assertEqual(task["goal_state"], "pending")
        self.assertIsNone(task["goal_evidence_ref"])

    def test_bounds_path_normalization_and_missing_lock_fail_closed(self) -> None:
        self.acquire()
        registration = self.registration_for()
        registration["sources"][0]["deliveries"][0]["allowed_paths"] = [
            "skills/../skills/implement-feature"
        ]
        rejected = self.create(registration=registration, check=False)
        self.error(rejected, "invalid-input")

        oversized = self.registration_for()
        oversized["objective"] = "x" * CACHE_RUNTIME.MAX_PACKET_BYTES
        oversized["objective_fingerprint"] = hashlib.sha256(
            oversized["objective"].encode()
        ).hexdigest()
        packet_rejected = self.create(registration=oversized, check=False)
        self.error(packet_rejected, "invalid-input")

        self.create(registration=self.registration_for())
        too_many = [
            {
                "type": "root-title-observed",
                "title": "👨🏻‍💻 Feature Orchestrator",
                "evidence_ref": "app-task://root-a/title",
            }
        ] * (CACHE_RUNTIME.MAX_EVENTS_PER_BATCH + 1)
        bounded = self.apply(too_many, check=False)
        self.error(bounded, "invalid-input")
        (self.claim_root / ".lock").unlink()
        locked = self.apply(
            [
                {
                    "type": "root-title-observed",
                    "title": "👨🏻‍💻 Feature Orchestrator",
                    "evidence_ref": "app-task://root-a/title",
                }
            ],
            check=False,
        )
        self.error(locked, "state-conflict")

    def test_symlinked_archive_root_is_rejected_without_touching_target(self) -> None:
        self.ledger_root.mkdir(parents=True)
        target = self.home / "archive-target"
        target.mkdir()
        marker = target / "preserve.txt"
        marker.write_text("preserve\n")
        self.archive_root.symlink_to(target, target_is_directory=True)

        doctor = self.run_cache("--json", "doctor", check=False)

        self.error(doctor, "state-conflict")
        self.assertEqual(marker.read_text(), "preserve\n")
        self.assertEqual(list(target.iterdir()), [marker])

    def test_projections_and_markdown_are_deterministic_and_bounded(self) -> None:
        self.bootstrap_active_task()
        for projection in ("status", "dispatch", "recovery", "terminal"):
            first = self.read_projection(projection).stdout
            second = self.read_projection(projection).stdout
            self.assertEqual(first, second)
            payload = json.loads(first)
            self.assertNotIn("operations", payload)
            self.assertNotIn("reviews", payload)

        state = self.state()
        first_markdown = CACHE_RUNTIME.render_markdown(state)
        second_markdown = CACHE_RUNTIME.render_markdown(state)
        self.assertEqual(first_markdown, second_markdown)
        self.assertIn("# Implement Feature Terminal Run State", first_markdown)
        self.assertNotIn("Wave Report", first_markdown)
        self.assertNotIn("Recovery Packet", first_markdown)

    def test_terminal_archive_v2_preserves_exact_state_and_projection(self) -> None:
        state = self.make_terminal_state()
        state_bytes = self.ledger.read_bytes()
        expected_markdown = CACHE_RUNTIME.render_markdown(state).encode()
        release = self.release(
            reason="terminal", evidence="proof://portfolio-terminal/232"
        )
        receipt_path = Path(release["release_receipt_ref"])
        receipt = release["release_receipt"]
        self.assertEqual(receipt["ledger_sha256"], hashlib.sha256(state_bytes).hexdigest())
        self.assertEqual(receipt["ledger_size_bytes"], len(state_bytes))

        archived = parse_result(
            self.run_cache(
                "--json",
                "ledger",
                "archive",
                "--ledger",
                str(self.ledger),
                "--root-id",
                "root-a",
                "--evidence-ref",
                "proof://portfolio-terminal/232",
            )
        )["archives"][0]
        entry = Path(archived["entry_path"])
        self.assertFalse(self.ledger.exists())
        self.assertFalse(receipt_path.exists())
        self.assertEqual(
            {path.name for path in entry.iterdir()},
            {"ledger.json", "ledger.md", "metadata.json"},
        )
        self.assertEqual((entry / "ledger.json").read_bytes(), state_bytes)
        self.assertEqual((entry / "ledger.md").read_bytes(), expected_markdown)
        metadata = json.loads((entry / "metadata.json").read_text())
        self.assertEqual(metadata["schema_version"], "2.0.0")
        self.assertEqual(metadata["state_sha256"], hashlib.sha256(state_bytes).hexdigest())
        self.assertEqual(metadata["state_size_bytes"], len(state_bytes))
        self.assertEqual(
            metadata["markdown_sha256"], hashlib.sha256(expected_markdown).hexdigest()
        )
        self.assertEqual(metadata["markdown_size_bytes"], len(expected_markdown))
        self.assertEqual(metadata["root_id"], "root-a")
        self.assertEqual(
            metadata["evidence_ref"], "proof://portfolio-terminal/232"
        )
        verified = parse_result(self.run_cache("--json", "archive", "verify"))
        self.assertEqual(verified["archives"][0]["archive_id"], archived["archive_id"])

    def test_corrupt_v2_archive_fails_verification_and_is_preserved(self) -> None:
        self.make_terminal_state()
        self.release(reason="terminal", evidence="proof://portfolio-terminal/232")
        archived = parse_result(
            self.run_cache(
                "--json",
                "ledger",
                "archive",
                "--ledger",
                str(self.ledger),
                "--root-id",
                "root-a",
                "--evidence-ref",
                "proof://portfolio-terminal/232",
            )
        )["archives"][0]
        entry = Path(archived["entry_path"])
        markdown = entry / "ledger.md"
        original = markdown.read_bytes()
        markdown.write_bytes(b"X" + original[1:])

        verified = self.run_cache("--json", "archive", "verify", check=False)
        error = self.error(verified, "integrity-failure")
        self.assertEqual(len(error["details"]["invalid"]), 1)
        doctor = parse_result(self.run_cache("--json", "doctor", check=False))
        self.assertFalse(doctor["ok"])
        self.assertTrue(entry.exists())
        self.assertEqual(markdown.read_bytes(), b"X" + original[1:])

    def test_doctor_flags_unsupported_active_markdown_without_mutating_it(self) -> None:
        self.ledger_root.mkdir(parents=True)
        markdown = self.ledger_root / "retired-active.md"
        markdown.write_bytes(b"# retired active ledger\n")
        before = self.snapshot_tree(self.cache_root)

        doctor = parse_result(self.run_cache("--json", "doctor", check=False))

        self.assertFalse(doctor["ok"])
        self.assertEqual(doctor["unsupported_active_ledgers"], [str(markdown)])
        self.assertIn(
            "one or more unsupported active Markdown ledgers exist",
            doctor["warnings"],
        )
        self.assertEqual(before, self.snapshot_tree(self.cache_root))

    def test_legacy_v1_archives_remain_byte_identical_and_verifiable(self) -> None:
        alpha = "# alpha\n\nπ and null: \x00\n".encode()
        beta = "# beta\n\nline endings stay exact\r\n".encode()
        first = self.make_legacy_archive("alpha", alpha)
        second = self.make_legacy_archive("beta", beta)

        self.assertEqual(Path(first["ledger_path"]).read_bytes(), alpha)
        self.assertEqual(Path(second["ledger_path"]).read_bytes(), beta)
        verified = parse_result(self.run_cache("--json", "archive", "verify"))
        self.assertEqual(len(verified["archives"]), 2)
        self.assertTrue(
            all(item["schema_version"] == "1.0.0" for item in verified["archives"])
        )

    def test_legacy_prune_is_age_bounded_and_preserves_corrupt_entries(self) -> None:
        fixed_now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        good_body = b"good legacy bytes\n"
        good = self.make_legacy_archive(
            "good-old",
            good_body,
            archived_at=fixed_now - timedelta(days=180),
        )
        corrupt = self.make_legacy_archive(
            "corrupt-old",
            b"corrupt legacy bytes\n",
            archived_at=fixed_now - timedelta(days=181),
        )
        corrupt_path = Path(corrupt["ledger_path"])
        corrupt_path.write_bytes(b"X" + corrupt_path.read_bytes()[1:])
        args = argparse.Namespace(older_than_days=180, apply=False)

        with mock.patch.object(CACHE_RUNTIME, "utc_now", return_value=fixed_now):
            preview = CACHE_RUNTIME.prune_archives(args)
        self.assertEqual(preview["eligible"], [good["archive_id"]])
        self.assertEqual(len(preview["protected"]), 1)
        self.assertEqual(Path(good["ledger_path"]).read_bytes(), good_body)

        args.apply = True
        with mock.patch.object(CACHE_RUNTIME, "utc_now", return_value=fixed_now):
            applied = CACHE_RUNTIME.prune_archives(args)
        self.assertEqual(applied["deleted"], [good["archive_id"]])
        self.assertFalse(Path(good["entry_path"]).exists())
        self.assertTrue(Path(corrupt["entry_path"]).exists())
        self.assertEqual(corrupt_path.read_bytes()[0:1], b"X")

    def test_legacy_prune_rejects_new_claim_reference_and_expires_normally(self) -> None:
        fixed_now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        archive = self.make_legacy_archive(
            "claimed-old",
            b"claimed legacy bytes\n",
            archived_at=fixed_now - timedelta(days=181),
        )
        original = Path(archive["original_ledger_ref"])
        rejected = self.run_claim(
            "--json",
            "claim",
            "acquire",
            "--root-id",
            "root-a",
            "--repository",
            str(REPOSITORY),
            "--source",
            "https://github.com/example/dotagents/issues/999",
            "--ledger-ref",
            str(original),
            check=False,
        )
        self.error(rejected, "invalid-input")
        args = argparse.Namespace(older_than_days=180, apply=True)

        with mock.patch.object(CACHE_RUNTIME, "utc_now", return_value=fixed_now):
            result = CACHE_RUNTIME.prune_archives(args)

        self.assertEqual(result["eligible"], [archive["archive_id"]])
        self.assertEqual(result["deleted"], [archive["archive_id"]])
        self.assertEqual(result["protected"], [])
        self.assertFalse(Path(archive["entry_path"]).exists())

    def test_doctor_never_repairs_or_deletes_cold_archive_state(self) -> None:
        self.make_legacy_archive("doctor-cold", b"cold archive evidence\n")
        interrupted = self.archive_root / ".tmp-fixture"
        interrupted.mkdir()
        (interrupted / "partial.bin").write_bytes(b"partial")
        before = self.snapshot_tree(self.cache_root)

        doctor = parse_result(self.run_cache("--json", "doctor", check=False))

        self.assertFalse(doctor["ok"])
        self.assertEqual(doctor["archive_count"], 1)
        self.assertEqual(doctor["temporary"], [str(interrupted)])
        self.assertEqual(before, self.snapshot_tree(self.cache_root))
        self.assertFalse(self.claim_root.exists())


if __name__ == "__main__":
    unittest.main()
