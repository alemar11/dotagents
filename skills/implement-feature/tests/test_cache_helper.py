from __future__ import annotations

import argparse
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
            "schema_version": "1.0.0",
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
                    "repository": claim["repositories"][0],
                    "source_state": "ready-for-agent",
                    "source_fingerprint": hashlib.sha256(
                        b"feature-spec-fixture"
                    ).hexdigest(),
                    "planned_done_ref": f"{claim['sources'][0]}#done",
                    "tracker_backend": "github",
                    "target_branch": "codex/typed-run-state",
                    "allowed_paths": ["skills/implement-feature/"],
                    "dependency_ids": [],
                    "requires_domain_closeout": False,
                    "task_model": "gpt-5.6-sol",
                    "task_thinking": "xhigh",
                    "thinking_reason": "contract-sensitive state transition work",
                    "task_goal_objective_fingerprint": self.task_goal_fingerprint,
                }
            ],
        }

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
        goal_completion: str | None = None,
        model: str = "gpt-5.6-sol",
        reasoning_effort: str = "xhigh",
        goal_fingerprint: str | None = None,
        pr: dict | None = None,
    ) -> dict:
        return {
            "type": "task-observed",
            "task_key": self.task_key,
            "task_ref": "app-task://worker-232",
            "checkout": str(REPOSITORY),
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
            "goal_completion_evidence_ref": goal_completion,
            "state": state,
            "outcome": (
                "pull-request-ready-for-merge-but-not-merged"
                if state == "merge-ready"
                else None
            ),
            "attention_reason": None,
            "summary_ref": "app-task://worker-232/summary",
            "pr": pr,
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
                self.task_event(state="created"),
                self.task_event(state="implementing"),
            ]
        )

    def direct_event(self, state: dict, event: dict, now: datetime) -> None:
        changed = CACHE_RUNTIME.apply_event(state, event, now)
        self.assertTrue(changed)

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
        repository = self.registration["sources"][0]["repository"]
        self.apply(
            [
                {
                    "type": "revision-observed",
                    "task_key": self.task_key,
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
        return self.state()["tasks"][0]["revision"]

    def pr_for(self, revision: dict) -> dict:
        assert self.registration is not None
        return {
            "repository": self.registration["sources"][0]["repository"],
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

    def start_clean_review(self, revision: dict) -> None:
        request_ref = "github-review://233/request-1"
        self.apply(
            [
                {
                    "type": "review-wait-started",
                    "task_key": self.task_key,
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
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                    "wait_invoked_at": review["wait_started_at"],
                    "provider_timeout": 1800,
                },
                {
                    "type": "review-observed",
                    "task_key": self.task_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
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
        for gate in sorted(CACHE_RUNTIME.STATIC_GATES):
            events.append(
                {
                    "type": "gate-observed",
                    "task_key": self.task_key,
                    "gate": gate,
                    "state": "passed",
                    "revision_key": None,
                    "evidence_ref": f"proof://{gate}",
                }
            )
        for gate in sorted(CACHE_RUNTIME.REVISION_GATES - {"terminal", "domain-closeout"}):
            events.append(
                {
                    "type": "gate-observed",
                    "task_key": self.task_key,
                    "gate": gate,
                    "state": "passed",
                    "revision_key": revision["revision_key"],
                    "evidence_ref": f"proof://{gate}/{revision['revision_key']}",
                }
            )
        events.append(
            {
                "type": "gate-observed",
                "task_key": self.task_key,
                "gate": "terminal",
                "state": "passed",
                "revision_key": revision["revision_key"],
                "evidence_ref": f"proof://terminal/{revision['revision_key']}",
            }
        )
        self.apply(events)

    def make_terminal_state(self) -> dict:
        self.bootstrap_active_task()
        revision = self.observe_revision()
        self.apply([self.task_event(state="draft-pr", pr=self.pr_for(revision))])
        self.start_clean_review(revision)
        self.apply(
            [
                {
                    "type": "source-moved",
                    "task_key": self.task_key,
                    "from_ref": self.source_ref,
                    "to_ref": f"{self.source_ref}#done",
                    "source_fingerprint": self.state()["sources"][0]["fingerprint"],
                    "evidence_ref": "github://issue-232/closed",
                }
            ]
        )
        self.pass_terminal_gates(revision)
        self.apply(
            [
                self.task_event(
                    state="checking-mergeability",
                    goal_state="complete",
                    goal_completion="app-task://worker-232/goal-complete",
                    pr=self.pr_for(revision),
                ),
                self.task_event(
                    state="merge-ready",
                    goal_state="complete",
                    goal_completion="app-task://worker-232/goal-complete",
                    pr=self.pr_for(revision),
                ),
                {
                    "type": "external-handoff-recorded",
                    "task_key": self.task_key,
                    "handoff_kind": "pull-request-ready",
                    "evidence_ref": "https://github.com/example/dotagents/pull/233",
                    "next_action": "Human may merge after final inspection.",
                },
                {
                    "type": "portfolio-goal-completed",
                    "goal_evidence_ref": "app-task://root-a/goal",
                    "completion_evidence_ref": "app-task://root-a/goal-complete",
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

    def test_doctor_is_v3_offline_and_read_only(self) -> None:
        before = self.snapshot_tree(self.home)
        version = self.run_cache("--version").stdout.strip()
        doctor = parse_result(self.run_cache("--json", "doctor"))

        self.assertEqual(version, "3.0.0")
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

    def test_title_profile_and_goal_evidence_are_safety_gates(self) -> None:
        self.acquire()
        self.create()
        objective_fingerprint = self.state()["portfolio"]["objective_fingerprint"]

        wrong_title = self.apply(
            [
                {
                    "type": "root-title-observed",
                    "title": "Feature Controller",
                    "evidence_ref": "app-task://root-a/title",
                }
            ],
            check=False,
        )
        self.error(wrong_title, "invalid-input")
        early_goal = self.apply(
            [
                {
                    "type": "portfolio-goal-activated",
                    "goal_evidence_ref": "app-task://root-a/goal",
                    "objective_fingerprint": objective_fingerprint,
                }
            ],
            check=False,
        )
        self.error(early_goal, "state-conflict")
        self.assertEqual(self.state()["generation"], 1)

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
        wrong_profile = self.apply(
            [self.task_event(state="created", model="gpt-5.6-terra")], check=False
        )
        self.error(wrong_profile, "state-conflict")
        no_title_evidence = self.apply(
            [
                self.task_event(state="created", title_evidence=None),
                self.task_event(state="implementing", title_evidence=None),
            ],
            check=False,
        )
        self.error(no_title_evidence, "state-conflict")
        wrong_goal = self.apply(
            [
                self.task_event(
                    state="created", goal_fingerprint=hashlib.sha256(b"other").hexdigest()
                )
            ],
            check=False,
        )
        self.error(wrong_goal, "state-conflict")
        self.assertEqual(self.state()["tasks"][0]["state"], "pending")

        self.apply(
            [self.task_event(state="created"), self.task_event(state="implementing")]
        )
        premature_completion = self.apply(
            [
                self.task_event(
                    state="implementing",
                    goal_state="complete",
                    goal_completion="app-task://worker-232/goal-complete",
                )
            ],
            check=False,
        )
        error = self.error(premature_completion, "state-conflict")
        self.assertIn("missing-current-revision", error["details"]["blockers"])
        self.assertEqual(self.state()["tasks"][0]["goal_state"], "active")

    def test_new_revision_invalidates_current_gate_and_review_evidence(self) -> None:
        self.bootstrap_active_task()
        first = self.observe_revision()
        self.start_clean_review(first)
        self.apply(
            [
                {
                    "type": "gate-observed",
                    "task_key": self.task_key,
                    "gate": "scope-acceptance",
                    "state": "passed",
                    "revision_key": first["revision_key"],
                    "evidence_ref": "proof://scope/first",
                }
            ]
        )

        second = self.observe_revision(head="c" * 40, merge_base="d" * 40)
        projection = parse_result(self.read_projection("status"))
        task = projection["tasks"][0]
        self.assertNotEqual(second["revision_key"], first["revision_key"])
        self.assertNotIn("scope-acceptance", task["gates"])
        self.assertIn("missing-current-review", task["terminal_blockers"])
        self.assertEqual(projection["due_reviews"], [])
        raw = self.state()
        self.assertEqual(raw["reviews"][0]["revision_key"], first["revision_key"])
        self.assertEqual(raw["gates"][0]["revision_key"], first["revision_key"])

    def test_review_wait_is_exactly_30_minutes_with_remaining_timeout(self) -> None:
        self.bootstrap_active_task()
        revision = self.observe_revision()
        request_ref = "github-review://233/request-remaining"
        self.apply(
            [
                {
                    "type": "review-wait-started",
                    "task_key": self.task_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                }
            ]
        )
        review = self.state()["reviews"][0]
        started = datetime.fromisoformat(review["wait_started_at"].replace("Z", "+00:00"))
        deadline = datetime.fromisoformat(review["wait_deadline"].replace("Z", "+00:00"))
        self.assertEqual(deadline - started, timedelta(minutes=30))

        observed_too_early = self.apply(
            [
                {
                    "type": "review-observed",
                    "task_key": self.task_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                    "provider_state": "clean",
                    "observation_fingerprint": hashlib.sha256(b"early").hexdigest(),
                    "disposition": "accepted",
                    "evidence_ref": "github-review://233/early",
                }
            ],
            check=False,
        )
        self.error(observed_too_early, "state-conflict")

        invoked = started + timedelta(seconds=7)
        invoked_text = invoked.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        wrong_remaining = self.apply(
            [
                {
                    "type": "review-wait-invoked",
                    "task_key": self.task_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                    "wait_invoked_at": invoked_text,
                    "provider_timeout": 1792,
                }
            ],
            check=False,
        )
        self.error(wrong_remaining, "invalid-input")
        applied = parse_result(
            self.apply(
                [
                    {
                        "type": "review-wait-invoked",
                        "task_key": self.task_key,
                        "revision_key": revision["revision_key"],
                        "request_ref": request_ref,
                        "wait_invoked_at": invoked_text,
                        "provider_timeout": 1793,
                    }
                ]
            )
        )
        self.assertEqual(applied["mutation_state"], "applied")
        self.assertEqual(self.state()["reviews"][0]["provider_timeout"], 1793)

    def test_review_monitoring_pauses_and_rearms_without_a_second_waiter(self) -> None:
        state, revision = self.prepare_review_polling_state()
        request_ref = "github-review://233/request-monitoring"
        started = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        deadline = started + timedelta(minutes=30)
        self.direct_event(
            state,
            {
                "type": "review-wait-started",
                "task_key": self.task_key,
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
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
                "wait_invoked_at": "20260718T120000Z",
                "provider_timeout": 1800,
            },
            started,
        )
        self.direct_event(
            state,
            {
                "type": "review-observed",
                "task_key": self.task_key,
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
                "provider_state": "waiting",
                "observation_fingerprint": hashlib.sha256(b"pending-1").hexdigest(),
                "disposition": "pending",
                "evidence_ref": "github-review://233/pending-1",
            },
            deadline,
        )
        self.direct_event(
            state,
            {
                "type": "review-monitoring-scheduled",
                "task_key": self.task_key,
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
                "pause_evidence_ref": "app-task://worker-232/goal-paused-1",
            },
            deadline,
        )
        review = state["reviews"][0]
        first_due = deadline + timedelta(minutes=30)
        self.assertEqual(review["due_at"], "2026-07-18T13:00:00Z")
        self.assertEqual(review["monitoring_cycle"], 1)
        self.assertEqual(state["tasks"][0]["state"], "review-monitoring")
        self.assertEqual(state["tasks"][0]["goal_state"], "paused")

        self.direct_event(
            state,
            {
                "type": "portfolio-goal-paused",
                "goal_evidence_ref": "app-task://root-a/goal",
                "pause_evidence_ref": "app-task://root-a/goal-paused-1",
                "heartbeat_id": "heartbeat-review-1",
                "target_thread_id": "app-task://root-a",
                "due_at": "2026-07-18T13:00:00Z",
            },
            deadline,
        )
        self.assertEqual(state["goal"]["state"], "paused")
        self.assertEqual(state["monitoring"]["state"], "armed")

        with self.assertRaises(CACHE_RUNTIME.CacheError) as early_worker:
            CACHE_RUNTIME.apply_event(
                state,
                {
                    "type": "review-monitoring-resumed",
                    "task_key": self.task_key,
                    "revision_key": revision["revision_key"],
                    "request_ref": request_ref,
                    "resume_evidence_ref": "app-task://worker-232/goal-resumed-early",
                },
                deadline,
            )
        self.assertEqual(early_worker.exception.code, "state-conflict")

        self.direct_event(
            state,
            {
                "type": "portfolio-goal-resumed",
                "goal_evidence_ref": "app-task://root-a/goal",
                "heartbeat_id": "heartbeat-review-1",
                "resume_evidence_ref": "automation://heartbeat-review-1/consumed",
            },
            first_due,
        )
        self.direct_event(
            state,
            {
                "type": "review-monitoring-resumed",
                "task_key": self.task_key,
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
                "resume_evidence_ref": "app-task://worker-232/goal-resumed-1",
            },
            first_due,
        )
        self.direct_event(
            state,
            {
                "type": "review-observed",
                "task_key": self.task_key,
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
                "provider_state": "waiting",
                "observation_fingerprint": hashlib.sha256(b"pending-2").hexdigest(),
                "disposition": "pending",
                "evidence_ref": "github-review://233/pending-2",
            },
            first_due,
        )
        self.direct_event(
            state,
            {
                "type": "review-monitoring-scheduled",
                "task_key": self.task_key,
                "revision_key": revision["revision_key"],
                "request_ref": request_ref,
                "pause_evidence_ref": "app-task://worker-232/goal-paused-2",
            },
            first_due,
        )
        self.assertEqual(review["monitoring_cycle"], 2)
        self.assertEqual(review["due_at"], "2026-07-18T13:30:00Z")
        self.assertEqual(review["wait_deadline"], "2026-07-18T12:30:00Z")
        self.assertEqual(review["wait_invoked_at"], "20260718T120000Z")
        self.assertEqual(review["provider_timeout"], 1800)

    def test_portfolio_goal_pause_rejects_runnable_controller_work(self) -> None:
        self.bootstrap_active_task()
        state = self.state()
        with self.assertRaises(CACHE_RUNTIME.CacheError) as raised:
            CACHE_RUNTIME.apply_event(
                state,
                {
                    "type": "portfolio-goal-paused",
                    "goal_evidence_ref": "app-task://root-a/goal",
                    "pause_evidence_ref": "app-task://root-a/goal-paused",
                    "heartbeat_id": "heartbeat-review",
                    "target_thread_id": "app-task://root-a",
                    "due_at": "20260718T130000Z",
                },
                datetime(2026, 7, 18, 12, 30, tzinfo=timezone.utc),
            )
        self.assertEqual(raised.exception.code, "state-conflict")
        self.assertIn("controller-action-required", raised.exception.details["blockers"][0])

    def test_terminal_and_goal_transitions_require_ordered_current_proof(self) -> None:
        self.bootstrap_active_task()
        revision = self.observe_revision()
        self.apply([self.task_event(state="draft-pr", pr=self.pr_for(revision))])
        self.start_clean_review(revision)

        early_terminal = self.apply(
            [
                {
                    "type": "gate-observed",
                    "task_key": self.task_key,
                    "gate": "terminal",
                    "state": "passed",
                    "revision_key": revision["revision_key"],
                    "evidence_ref": "proof://terminal/early",
                }
            ],
            check=False,
        )
        error = self.error(early_terminal, "state-conflict")
        self.assertIn("full-validation", error["details"]["gates"])
        early_goal = self.apply(
            [
                self.task_event(
                    state="checking-mergeability",
                    goal_state="complete",
                    goal_completion="app-task://worker-232/goal-complete",
                    pr=self.pr_for(revision),
                )
            ],
            check=False,
        )
        self.error(early_goal, "state-conflict")

        self.pass_terminal_gates(revision)
        merge_before_goal = self.apply(
            [self.task_event(state="merge-ready", pr=self.pr_for(revision))],
            check=False,
        )
        error = self.error(merge_before_goal, "state-conflict")
        self.assertIn("task-goal-not-complete", error["details"]["blockers"])
        portfolio_before_task = self.apply(
            [
                {
                    "type": "portfolio-goal-completed",
                    "goal_evidence_ref": "app-task://root-a/goal",
                    "completion_evidence_ref": "app-task://root-a/goal-complete",
                }
            ],
            check=False,
        )
        self.error(portfolio_before_task, "state-conflict")

        self.apply(
            [
                self.task_event(
                    state="checking-mergeability",
                    goal_state="complete",
                    goal_completion="app-task://worker-232/goal-complete",
                    pr=self.pr_for(revision),
                ),
                self.task_event(
                    state="merge-ready",
                    goal_state="complete",
                    goal_completion="app-task://worker-232/goal-complete",
                    pr=self.pr_for(revision),
                ),
                {
                    "type": "external-handoff-recorded",
                    "task_key": self.task_key,
                    "handoff_kind": "pull-request-ready",
                    "evidence_ref": "https://github.com/example/dotagents/pull/233",
                    "next_action": "Human may merge after final inspection.",
                },
                {
                    "type": "portfolio-goal-completed",
                    "goal_evidence_ref": "app-task://root-a/goal",
                    "completion_evidence_ref": "app-task://root-a/goal-complete",
                },
            ]
        )
        terminal = parse_result(self.read_projection("terminal"))
        self.assertTrue(terminal["eligible"])
        self.assertEqual(terminal["blockers"], [])

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
        release = self.release(reason="terminal", evidence="fixture://terminal-proof")
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
                "fixture://terminal-proof",
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
        self.assertEqual(metadata["evidence_ref"], "fixture://terminal-proof")
        verified = parse_result(self.run_cache("--json", "archive", "verify"))
        self.assertEqual(verified["archives"][0]["archive_id"], archived["archive_id"])

    def test_corrupt_v2_archive_fails_verification_and_is_preserved(self) -> None:
        self.make_terminal_state()
        self.release(reason="terminal", evidence="fixture://terminal-corrupt")
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
                "fixture://terminal-corrupt",
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
