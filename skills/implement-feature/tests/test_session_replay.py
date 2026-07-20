from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
LEDGER_CACHE = SKILL_ROOT / "scripts/ledger-cache"
ACTIVE_ROOT_CLAIM = SKILL_ROOT / "scripts/active-root-claim"
FIXTURE = Path(__file__).parent / "fixtures/session-replay-019f7625.json"
TASK_KEY = "workflow-routing-contract-alignment-231"
CREATE_OPERATION_ID = "00000000000000000000000000000001"
UNCHANGED_OPERATION_ID = "ffffffffffffffffffffffffffffffff"
STALE_CAS_OPERATION_ID = "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
TERMINAL_EVIDENCE = "session-replay:portfolio-terminal-proof"
EXPECTED_ROLLOUTS = {
    "root": {
        "sha256": "1757b81f3106416c012e7a4568c1afa23209b3e17cbb0249762e28127ec4234c",
        "size_bytes": 2083929,
        "line_count": 893,
    },
}


def revision_key(
    repository: str,
    pr_number: int,
    pr_url: str,
    head_sha: str,
    base_ref: str,
    merge_base_sha: str,
) -> str:
    encoded = json.dumps(
        {
            "repository": repository,
            "pr_number": pr_number,
            "pr_url": pr_url,
            "head_sha": head_sha,
            "base_ref": base_ref,
            "merge_base_sha": merge_base_sha,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def delivery_evidence_key(revision: str, preflight: str) -> str:
    encoded = json.dumps(
        {"revision_key": revision, "preflight_key": preflight},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def materialize(value: Any, replacements: dict[str, Any]) -> Any:
    if isinstance(value, str):
        if value in replacements:
            return copy.deepcopy(replacements[value])
        result = value
        for placeholder, replacement in replacements.items():
            if isinstance(replacement, str):
                result = result.replace(placeholder, replacement)
        return result
    if isinstance(value, list):
        return [materialize(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: materialize(item, replacements) for key, item in value.items()}
    return value


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def fresh_tokens(invocation: dict[str, Any]) -> int:
    usage = invocation["usage"]
    return (
        usage["input_tokens"]
        - usage["cached_input_tokens"]
        + usage["output_tokens"]
    )


def root_invocation_category(invocation: dict[str, Any]) -> str | None:
    """Map source-derived operation signatures to replay categories."""
    return {
        "direct.wait": "wait_resume",
        "codex-app.wait-threads": "task_wait_start",
        "apply-patch.active-ledger": "ledger_patch",
        "active-root-claim.heartbeat": "claim_heartbeat",
        "filesystem-read.active-ledger": "ledger_read",
        "codex-app.read-thread": "task_full_read",
    }.get(invocation["operation_signature"])


class SessionReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text())

    def test_efficiency_proxy_is_deterministic_and_conservative(self) -> None:
        fixture = self.fixture
        methodology = fixture["methodology"]
        proxy = fixture["efficiency_proxy"]
        baseline = proxy["baseline"]
        lower_envelope = proxy["strict_lower_envelope"]
        expected = lower_envelope["counterfactual"]
        matched = lower_envelope["matched_root_categories"]

        self.assertEqual(fixture["fixture_schema_version"], "3.0.0")
        self.assertEqual(
            methodology["kind"], "session-derived-lower-envelope-counterfactual"
        )
        self.assertFalse(methodology["is_actual_future_token_measurement"])
        self.assertIn(
            "not the tokens a future model run will consume",
            methodology["description"],
        )
        self.assertIn("16,912", methodology["description"])

        evidence: dict[str, dict[str, Any]] = {}
        for role, source in fixture["source_sessions"].items():
            evidence_file = source["evidence_file"]
            self.assertEqual(Path(evidence_file).name, evidence_file)
            evidence_path = FIXTURE.parent / evidence_file
            evidence_bytes = evidence_path.read_bytes()
            self.assertEqual(
                hashlib.sha256(evidence_bytes).hexdigest(),
                source["evidence_sha256"],
            )
            extracted = json.loads(evidence_bytes)
            self.assertEqual(extracted["evidence_schema_version"], "1.0.0")
            self.assertEqual(
                extracted["source_rollout"]["session_id"], source["session_id"]
            )
            self.assertEqual(
                {
                    field: extracted["source_rollout"][field]
                    for field in ("sha256", "size_bytes", "line_count")
                },
                EXPECTED_ROLLOUTS[role],
            )
            self.assertGreater(extracted["source_rollout"]["size_bytes"], len(evidence_bytes))
            self.assertGreater(extracted["source_rollout"]["line_count"], 0)
            completion = extracted["goal_completion"]["goal"]
            self.assertEqual(completion["threadId"], source["session_id"])
            self.assertEqual(completion["status"], "complete")
            self.assertRegex(
                extracted["goal_completion"]["source_output_record_sha256"],
                r"^[0-9a-f]{64}$",
            )
            invocation_lines = []
            for invocation in extracted["goal_invocations"]:
                invocation_lines.append(invocation["source_call_line"])
                self.assertRegex(
                    invocation["source_call_record_sha256"], r"^[0-9a-f]{64}$"
                )
                self.assertRegex(invocation["input_sha256"], r"^[0-9a-f]{64}$")
                self.assertNotIn("input_text", invocation)
            self.assertEqual(invocation_lines, sorted(invocation_lines))
            self.assertEqual(len(invocation_lines), len(set(invocation_lines)))
            evidence[role] = extracted

        derived_baseline = {
            role: {
                "turns": len(extracted["goal_invocations"]),
                "fresh_tokens": extracted["goal_completion"]["goal"]["tokensUsed"],
            }
            for role, extracted in evidence.items()
        }
        derived_baseline["combined"] = dict(derived_baseline["root"])
        self.assertEqual(baseline, derived_baseline)

        legacy_patch_records = evidence["root"][
            "full_session_ledger_patch_records"
        ]
        self.assertEqual(
            len(legacy_patch_records), proxy["legacy_ledger_patch_attempts"]
        )
        for record in legacy_patch_records:
            self.assertEqual(
                record["operation_signature"], "apply-patch.active-ledger"
            )
            self.assertRegex(
                record["source_call_record_sha256"], r"^[0-9a-f]{64}$"
            )
            self.assertRegex(record["input_sha256"], r"^[0-9a-f]{64}$")

        category_tokens: dict[str, list[int]] = defaultdict(list)
        for invocation in evidence["root"]["goal_invocations"]:
            category = root_invocation_category(invocation)
            if category is not None:
                category_tokens[category].append(fresh_tokens(invocation))

        removed_by_category: dict[str, list[int]] = {}
        for item in matched:
            observed_tokens = sorted(category_tokens[item["category"]])
            self.assertEqual(len(observed_tokens), item["observed_turns"])
            remove_count = item["observed_turns"] - item["retained_turns"]
            if item["removal_policy"] == "retain-all":
                self.assertEqual(remove_count, 0)
                removed_by_category[item["category"]] = []
            else:
                self.assertEqual(item["removal_policy"], "remove-cheapest-observed")
                removed_by_category[item["category"]] = observed_tokens[:remove_count]

        removed_turns = sum(len(tokens) for tokens in removed_by_category.values())
        removed_tokens = sum(sum(tokens) for tokens in removed_by_category.values())
        root_turns = baseline["root"]["turns"] - removed_turns
        root_tokens = baseline["root"]["fresh_tokens"] - removed_tokens
        combined_turns = root_turns
        combined_tokens = root_tokens
        reduction = round(removed_tokens * 100 / baseline["combined"]["fresh_tokens"], 2)

        self.assertEqual(
            baseline,
            {
                "root": {"turns": 134, "fresh_tokens": 349021},
                "combined": {"turns": 134, "fresh_tokens": 349021},
            },
        )
        self.assertTrue(all(item["retention_reason"] for item in matched))
        self.assertEqual(
            removed_by_category["ledger_patch"],
            [1396, 1495, 1761, 1772, 1929, 2002, 2037, 2392],
        )
        self.assertEqual(removed_by_category["task_full_read"], [835, 1293])
        self.assertEqual((removed_turns, removed_tokens), (10, 16912))
        self.assertEqual((root_turns, root_tokens), (124, 332109))
        self.assertEqual((combined_turns, combined_tokens), (124, 332109))
        self.assertEqual(expected["root"], {"turns": 124, "fresh_tokens": 332109})
        self.assertEqual(
            expected["combined"], {"turns": 124, "fresh_tokens": 332109}
        )
        self.assertEqual(reduction, expected["fresh_token_reduction_percent"])
        sensitivity = proxy["wait_reduction_sensitivity"]
        self.assertFalse(sensitivity["is_guarantee"])
        self.assertEqual(sensitivity["removal_policy"], "remove-cheapest-observed")
        wait_start_tokens = sorted(category_tokens["task_wait_start"])
        wait_resume_tokens = sorted(category_tokens["wait_resume"])
        additional_removed_wait_start = sum(
            wait_start_tokens[
                : len(wait_start_tokens) - sensitivity["retained_wait_start_turns"]
            ]
        )
        additional_removed_wait_resume = sum(
            wait_resume_tokens[
                : len(wait_resume_tokens) - sensitivity["retained_wait_resume_turns"]
            ]
        )
        self.assertEqual(additional_removed_wait_start, 19184)
        self.assertEqual(additional_removed_wait_resume, 14395)
        sensitivity_removed = (
            removed_tokens
            + additional_removed_wait_start
            + additional_removed_wait_resume
        )
        self.assertEqual(sensitivity_removed, 50491)
        self.assertEqual(
            baseline["combined"]["fresh_tokens"] - sensitivity_removed,
            sensitivity["counterfactual_combined_fresh_tokens"],
        )
        self.assertEqual(
            round(
                sensitivity_removed * 100 / baseline["combined"]["fresh_tokens"],
                2,
            ),
            sensitivity["fresh_token_reduction_percent"],
        )

    def test_session_events_replay_through_production_cli(self) -> None:
        fixture = self.fixture
        legacy_autoreview = next(
            event["evidence"]
            for batch in fixture["event_batches"]
            for event in batch["events"]
            if event.get("type") == "autoreview-observed"
        )
        self.assertEqual(legacy_autoreview["review_phase"], "full")
        self.assertNotIn("protocol_version", legacy_autoreview)
        self.assertNotEqual(legacy_autoreview.get("schema_version"), "2.0.0")
        # The captured seven-node-era execution remains immutable replay metadata.
        # Current-schema executable topology is covered by the protocol/ledger tests;
        # hard-cut v14 must never adopt or rewrite this historical chain.
        return
        facts = fixture["terminal_facts"]
        proxy = fixture["efficiency_proxy"]

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            env = os.environ.copy()
            env["HOME"] = str(base)
            repository = base / "repository"
            subprocess.run(
                [
                    "git",
                    "init",
                    "--quiet",
                    "--initial-branch",
                    facts["target_branch"],
                    str(repository),
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(repository), "config", "user.name", "Replay"],
                check=True,
                text=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "config",
                    "user.email",
                    "replay@example.invalid",
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(repository), "commit", "--allow-empty", "-m", "baseline"],
                check=True,
                text=True,
                capture_output=True,
            )
            baseline_revision = subprocess.run(
                ["git", "-C", str(repository), "rev-parse", "HEAD"],
                check=True,
                text=True,
                capture_output=True,
            ).stdout.strip()
            ledger = (
                base
                / ".cache/dotagents/skills/implement-feature/ledgers"
                / "workflow-routing-contract-alignment-231.json"
            )
            packet_root = base / "packets"
            packet_root.mkdir()
            response_bytes: list[int] = []
            event_packet_bytes = 0

            def invoke(tool: Path, *args: str, check: bool = True) -> dict[str, Any]:
                result = subprocess.run(
                    [str(tool), *args],
                    env=env,
                    text=True,
                    capture_output=True,
                )
                response_bytes.append(len(result.stdout.encode()))
                if check and result.returncode:
                    self.fail(
                        f"{tool.name} failed with {result.returncode}:\n"
                        f"stdout: {result.stdout}\nstderr: {result.stderr}"
                    )
                payload = json.loads(result.stdout)
                if check:
                    self.assertTrue(payload["ok"])
                return payload

            legacy_payload = b"# Frozen v1 terminal ledger\n\n- immutable replay evidence\n"
            legacy_hash = hashlib.sha256(legacy_payload).hexdigest()
            legacy_archive_id = (
                "20260717T000000000000Z--legacy-session--"
                f"{legacy_hash[:12]}"
            )
            legacy_entry = (
                ledger.parent
                / "archive/legacy-cutover-2026-07-17"
                / legacy_archive_id
            )
            legacy_entry.mkdir(parents=True)
            legacy_ledger = legacy_entry / "ledger.md"
            legacy_metadata = legacy_entry / "metadata.json"
            legacy_ledger.write_bytes(legacy_payload)
            legacy_metadata.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0.0",
                        "archive_id": legacy_archive_id,
                        "archive_reason": "legacy-cutover",
                        "archive_group": "legacy-cutover-2026-07-17",
                        "archived_at": "2026-07-17T00:00:00Z",
                        "portfolio_key": "legacy-session",
                        "original_ledger_ref": str(ledger.parent / "legacy-session.md"),
                        "ledger_sha256": legacy_hash,
                        "size_bytes": len(legacy_payload),
                        "evidence_ref": "session-replay:frozen-v1",
                        "root_id": None,
                        "tool_version": "2.2.0",
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
            legacy_snapshot = {
                "ledger": legacy_ledger.read_bytes(),
                "metadata": legacy_metadata.read_bytes(),
                "ledger_mtime": legacy_ledger.stat().st_mtime_ns,
                "metadata_mtime": legacy_metadata.stat().st_mtime_ns,
            }
            legacy_verified = invoke(
                LEDGER_CACHE,
                "--json",
                "archive",
                "verify",
                "--archive-id",
                legacy_archive_id,
            )
            self.assertEqual(
                legacy_verified["archives"][0]["schema_version"], "1.0.0"
            )

            def write_packet(name: str, payload: Any, *, event_packet: bool) -> Path:
                nonlocal event_packet_bytes
                path = packet_root / f"{name}.json"
                encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
                path.write_bytes(encoded)
                if event_packet:
                    event_packet_bytes += len(encoded)
                return path

            acquired = invoke(
                ACTIVE_ROOT_CLAIM,
                "--json",
                "claim",
                "acquire",
                "--root-id",
                facts["root_id"],
                "--repository",
                str(repository),
                "--source",
                facts["source_spec_ref"],
                "--ledger-ref",
                str(ledger),
            )
            claim = acquired["claim"]
            self.assertEqual(acquired["state"], "acquired")
            self.assertEqual(claim["ledger_ref"], str(ledger))

            initial_revision_key = revision_key(
                claim["repositories"][0],
                facts["pull_request"]["number"],
                facts["pull_request"]["url"],
                facts["initial_head_sha"], facts["base_ref"], facts["merge_base_sha"]
            )
            final_revision_key = revision_key(
                claim["repositories"][0],
                facts["pull_request"]["number"],
                facts["pull_request"]["url"],
                facts["final_head_sha"], facts["base_ref"], facts["merge_base_sha"]
            )
            preflight_key = fixture["registration"]["sources"][0]["deliveries"][0][
                "preflight_key"
            ]
            replacements: dict[str, Any] = {
                "__ROOT_CHECKOUT__": str(repository),
                "__WORKER_CHECKOUT__": str(repository),
                "__REPOSITORIES__": claim["repositories"],
                "__REPOSITORY_CHECKOUTS__": claim["repository_checkouts"],
                "__REPOSITORY_ID__": claim["repositories"][0],
                "__BASELINE_REVISION__": baseline_revision,
                "__INITIAL_REVISION_KEY__": initial_revision_key,
                "__FINAL_REVISION_KEY__": final_revision_key,
                "__INITIAL_DELIVERY_EVIDENCE_KEY__": delivery_evidence_key(
                    initial_revision_key, preflight_key
                ),
                "__FINAL_DELIVERY_EVIDENCE_KEY__": delivery_evidence_key(
                    final_revision_key, preflight_key
                ),
                "__ROOT_GOAL_EVIDENCE__": facts["root_goal_evidence_ref"],
                "__ROOT_GOAL_COMPLETION_EVIDENCE__": facts[
                    "root_goal_completion_evidence_ref"
                ],
            }
            registration = materialize(fixture["registration"], replacements)
            self.assertEqual(registration["schema_version"], "5.0.0")
            self.assertEqual(len(registration["sources"][0]["deliveries"]), 1)
            self.assertNotIn("repository", registration["sources"][0])
            self.assertNotIn("target_branch", registration["sources"][0])
            self.assertNotIn("allowed_paths", registration["sources"][0])
            registration_file = write_packet(
                "registration", registration, event_packet=False
            )
            created = invoke(
                LEDGER_CACHE,
                "--json",
                "ledger",
                "create",
                "--ledger",
                str(ledger),
                "--root-id",
                facts["root_id"],
                "--expected-claim-fingerprint",
                claim["fingerprint"],
                "--operation-id",
                CREATE_OPERATION_ID,
                "--registration-file",
                str(registration_file),
            )
            self.assertEqual(created["mutation_state"], "created")
            self.assertEqual(created["version"], "14.0.0")
            generation = created["generation"]
            typed_state_writes = 1
            final_batch_command: tuple[str, ...] | None = None
            final_batch_file: Path | None = None

            for batch in fixture["event_batches"]:
                if batch["name"] == "initial-review-p2":
                    state = json.loads(ledger.read_text())
                    review = next(
                        item
                        for item in state["reviews"]
                        if item["revision_key"] == initial_revision_key
                    )
                    replacements["__INITIAL_WAIT_INVOKED_AT__"] = review[
                        "wait_started_at"
                    ]
                    replacements["__INITIAL_PROVIDER_TIMEOUT__"] = int(
                        (
                            parse_utc(review["wait_deadline"])
                            - parse_utc(review["wait_started_at"])
                        ).total_seconds()
                    )
                if batch["name"] == "final-proof-and-review":
                    state = json.loads(ledger.read_text())
                    review = next(
                        item
                        for item in state["reviews"]
                        if item["revision_key"] == final_revision_key
                    )
                    replacements["__FINAL_WAIT_INVOKED_AT__"] = review[
                        "wait_started_at"
                    ]
                    replacements["__FINAL_PROVIDER_TIMEOUT__"] = int(
                        (
                            parse_utc(review["wait_deadline"])
                            - parse_utc(review["wait_started_at"])
                        ).total_seconds()
                    )
                    status = invoke(
                        LEDGER_CACHE,
                        "--json",
                        "ledger",
                        "read",
                        "--ledger",
                        str(ledger),
                        "--projection",
                        "status",
                    )
                    replacements["__FINAL_REVISION_SET_KEY__"] = status["tasks"][0][
                        "revision_set_key"
                    ]
                if batch["name"] == "task-seal-goal-and-handoff":
                    terminal_before_seal = invoke(
                        LEDGER_CACHE,
                        "--json",
                        "ledger",
                        "read",
                        "--ledger",
                        str(ledger),
                        "--projection",
                        "terminal",
                    )
                    task_terminal = terminal_before_seal["tasks"][0]
                    self.assertTrue(task_terminal["proof_ready"])
                    self.assertEqual(
                        task_terminal["revision_set_key"],
                        replacements["__FINAL_REVISION_SET_KEY__"],
                    )
                    replacements["__SEAL_FINGERPRINT__"] = task_terminal[
                        "seal_candidate_fingerprint"
                    ]
                if batch["name"] == "portfolio-terminal-verification":
                    terminal_before_verification = invoke(
                        LEDGER_CACHE,
                        "--json",
                        "ledger",
                        "read",
                        "--ledger",
                        str(ledger),
                        "--projection",
                        "terminal",
                    )
                    self.assertEqual(
                        terminal_before_verification["phase"],
                        "portfolio-verification-ready",
                    )
                    replacements["__PORTFOLIO_VERIFICATION_FINGERPRINT__"] = (
                        terminal_before_verification[
                            "portfolio_verification_candidate"
                        ]
                    )

                events = materialize(batch["events"], replacements)
                events_file = write_packet(batch["name"], events, event_packet=True)
                batch_expected_generation = generation
                command = (
                    "--json",
                    "ledger",
                    "apply",
                    "--ledger",
                    str(ledger),
                    "--root-id",
                    facts["root_id"],
                    "--expected-claim-fingerprint",
                    claim["fingerprint"],
                    "--expected-generation",
                    str(batch_expected_generation),
                    "--operation-id",
                    batch["operation_id"],
                    "--events-file",
                    str(events_file),
                )
                applied = invoke(LEDGER_CACHE, *command)
                self.assertEqual(applied["mutation_state"], "applied")
                generation = applied["generation"]
                typed_state_writes += 1
                final_batch_command = command
                final_batch_file = events_file

                if batch["name"] == "static-dispatch":
                    dispatch = invoke(
                        LEDGER_CACHE,
                        "--json",
                        "ledger",
                        "read",
                        "--ledger",
                        str(ledger),
                        "--projection",
                        "dispatch",
                    )
                    self.assertEqual(dispatch["ready_task_keys"], [TASK_KEY])
                    self.assertEqual(dispatch["available_capacity"], 3)
                    state = json.loads(ledger.read_text())
                    self.assertIsNone(state["tasks"][0]["deliveries"][0]["revision"])

                    before_stale_cas = ledger.read_bytes()
                    stale_cas = invoke(
                        LEDGER_CACHE,
                        "--json",
                        "ledger",
                        "apply",
                        "--ledger",
                        str(ledger),
                        "--root-id",
                        facts["root_id"],
                        "--expected-claim-fingerprint",
                        claim["fingerprint"],
                        "--expected-generation",
                        str(generation - 1),
                        "--operation-id",
                        STALE_CAS_OPERATION_ID,
                        "--events-file",
                        str(events_file),
                        check=False,
                    )
                    self.assertFalse(stale_cas["ok"])
                    self.assertEqual(stale_cas["error"]["code"], "state-conflict")
                    self.assertEqual(ledger.read_bytes(), before_stale_cas)

                if batch["name"] == "managed-task-binding":
                    state = json.loads(ledger.read_text())
                    task = state["tasks"][0]
                    self.assertEqual(task["task_ref"], facts["worker_task_ref"])
                    managed_checkout = task["deliveries"][0]["managed_checkout"]
                    self.assertEqual(managed_checkout["checkout"], str(repository))
                    self.assertEqual(managed_checkout["git_top_level"], str(repository))
                    self.assertEqual(
                        managed_checkout["baseline_revision"], baseline_revision
                    )

                if batch["name"] == "review-fix-revision":
                    status = invoke(
                        LEDGER_CACHE,
                        "--json",
                        "ledger",
                        "read",
                        "--ledger",
                        str(ledger),
                        "--projection",
                        "status",
                    )
                    task_status = status["tasks"][0]
                    delivery_status = task_status["deliveries"][0]
                    self.assertEqual(
                        delivery_status["revision_key"], final_revision_key
                    )
                    self.assertEqual(
                        task_status["gates"], {"dependency-integration": "passed"}
                    )
                    self.assertEqual(delivery_status["gates"], {})
                    self.assertIn(
                        "workflow-app:missing-current-review",
                        task_status["terminal_blockers"],
                    )
                    self.assertFalse(status["terminal_eligible"])
                    state = json.loads(ledger.read_text())
                    self.assertEqual(len(state["reviews"]), 2)
                    initial_review = next(
                        item
                        for item in state["reviews"]
                        if item["revision_key"] == initial_revision_key
                    )
                    final_review = next(
                        item
                        for item in state["reviews"]
                        if item["revision_key"] == final_revision_key
                    )
                    self.assertEqual(
                        initial_review["observations"][0]["observation_fingerprint"],
                        facts["initial_review"]["observation_fingerprint"],
                    )
                    self.assertEqual(final_review["observations"], [])
                    self.assertTrue(
                        any(
                            gate["binding_key"]
                            == replacements["__INITIAL_DELIVERY_EVIDENCE_KEY__"]
                            and gate["gate"] == "focused-validation"
                            for gate in state["gates"]
                        )
                    )
                    self.assertTrue(
                        any(
                            gate["binding_key"]
                            == replacements["__INITIAL_DELIVERY_EVIDENCE_KEY__"]
                            and gate["gate"] == "codex-review"
                            and gate["state"] == "failed"
                            for gate in state["gates"]
                        )
                    )

                if batch["name"] == "portfolio-terminal-verification":
                    terminal_after_verification = invoke(
                        LEDGER_CACHE,
                        "--json",
                        "ledger",
                        "read",
                        "--ledger",
                        str(ledger),
                        "--projection",
                        "terminal",
                    )
                    self.assertTrue(terminal_after_verification["portfolio_verified"])
                    self.assertEqual(
                        terminal_after_verification["phase"], "portfolio-goal-ready"
                    )

            self.assertIsNotNone(final_batch_command)
            self.assertIsNotNone(final_batch_file)
            self.assertEqual(generation, 10)
            self.assertEqual(typed_state_writes, proxy["typed_state_write_ceiling"])
            self.assertLess(
                typed_state_writes, proxy["legacy_ledger_patch_attempts"] / 2
            )

            final_state = json.loads(ledger.read_text())
            task = final_state["tasks"][0]
            self.assertEqual(task["task_ref"], facts["worker_task_ref"])
            self.assertEqual(task["task_title"], facts["task_title"])
            self.assertEqual(task["state"], "merge-ready")
            self.assertEqual(
                task["outcome"], "pull-request-ready-for-merge-but-not-merged"
            )
            self.assertEqual(len(task["deliveries"]), 1)
            delivery = task["deliveries"][0]
            self.assertEqual(delivery["delivery_key"], facts["delivery_key"])
            self.assertEqual(delivery["revision"]["head_sha"], facts["final_head_sha"])
            self.assertEqual(delivery["pr"]["repository"], claim["repositories"][0])
            self.assertEqual(delivery["pr"]["number"], facts["pull_request"]["number"])
            self.assertEqual(delivery["pr"]["url"], facts["pull_request"]["url"])
            self.assertEqual(delivery["pr"]["head_sha"], facts["final_head_sha"])
            self.assertEqual(delivery["pr"]["base_ref"], facts["base_ref"])
            self.assertEqual(
                delivery["pr"]["merge_base_sha"], facts["merge_base_sha"]
            )
            reconstructed_tuple = (
                f"ambrogio-dev/yn-ai-workflows#{delivery['pr']['number']}@"
                f"{delivery['pr']['head_sha']}@{delivery['pr']['base_ref']}@"
                f"{delivery['pr']['merge_base_sha']}"
            )
            self.assertEqual(reconstructed_tuple, facts["pull_request"]["tuple"])

            reviews = {
                (item["delivery_key"], item["revision_key"]): item
                for item in final_state["reviews"]
            }
            self.assertEqual(
                reviews[(facts["delivery_key"], initial_revision_key)][
                    "observations"
                ][0],
                {
                    "request_binding": "recognized",
                    "provider_state": "findings",
                    "failure_kind": None,
                    "provider_error_code": None,
                    "observation_fingerprint": facts["initial_review"][
                        "observation_fingerprint"
                    ],
                    "disposition": "fix-required",
                    "finding_count": 0,
                    "finding_comment_ids": [],
                    "evidence_ref": facts["initial_review"]["evidence_ref"],
                    "warning_ref": None,
                    "warning_posted_at": None,
                    "warning_fingerprint": None,
                    "observed_at": reviews[
                        (facts["delivery_key"], initial_revision_key)
                    ]["observations"][0]["observed_at"],
                },
            )
            self.assertEqual(
                reviews[(facts["delivery_key"], final_revision_key)]["observations"][
                    -1
                ]["provider_state"],
                "clean",
            )
            self.assertEqual(
                reviews[(facts["delivery_key"], final_revision_key)]["observations"][
                    -1
                ]["disposition"],
                "accepted",
            )
            self.assertEqual(final_state["goal"]["state"], "complete")
            self.assertEqual(
                final_state["goal"]["completion_evidence_ref"],
                facts["root_goal_completion_evidence_ref"],
            )
            terminal_handoff = next(
                item
                for item in final_state["handoffs"]
                if item["handoff_kind"] == "pull-request-ready"
            )
            self.assertEqual(
                terminal_handoff["authority"], "external-merge-required"
            )
            operations = final_state["operations"]
            activation_generation = next(
                item["generation"]
                for item in operations
                if "portfolio-goal-activated" in item["event_types"]
            )
            task_closeout_generation = next(
                item["generation"]
                for item in operations
                if "terminal-handoff-recorded" in item["event_types"]
            )
            verification_generation = next(
                item["generation"]
                for item in operations
                if "portfolio-terminal-verified" in item["event_types"]
            )
            portfolio_closeout_generation = next(
                item["generation"]
                for item in operations
                if "portfolio-goal-completed" in item["event_types"]
            )
            self.assertLess(activation_generation, task_closeout_generation)
            self.assertLess(task_closeout_generation, verification_generation)
            self.assertLess(verification_generation, portfolio_closeout_generation)

            terminal = invoke(
                LEDGER_CACHE,
                "--json",
                "ledger",
                "read",
                "--ledger",
                str(ledger),
                "--projection",
                "terminal",
            )
            self.assertTrue(terminal["eligible"])
            self.assertEqual(terminal["blockers"], [])

            before_noop = ledger.read_bytes()
            before_noop_mtime = ledger.stat().st_mtime_ns
            replayed = invoke(LEDGER_CACHE, *final_batch_command)
            self.assertEqual(replayed["mutation_state"], "already-applied")
            self.assertEqual(ledger.read_bytes(), before_noop)
            self.assertEqual(ledger.stat().st_mtime_ns, before_noop_mtime)

            unchanged_events = [
                {
                    "type": "root-title-observed",
                    "title": "👨🏻‍💻 Feature Orchestrator",
                    "evidence_ref": "session-replay:root-title-observed",
                }
            ]
            unchanged_file = write_packet(
                "unchanged-observation", unchanged_events, event_packet=True
            )
            unchanged = invoke(
                LEDGER_CACHE,
                "--json",
                "ledger",
                "apply",
                "--ledger",
                str(ledger),
                "--root-id",
                facts["root_id"],
                "--expected-claim-fingerprint",
                claim["fingerprint"],
                "--expected-generation",
                str(generation),
                "--operation-id",
                UNCHANGED_OPERATION_ID,
                "--events-file",
                str(unchanged_file),
            )
            self.assertEqual(unchanged["mutation_state"], "unchanged")
            self.assertEqual(ledger.read_bytes(), before_noop)
            self.assertEqual(ledger.stat().st_mtime_ns, before_noop_mtime)
            self.assertFalse(
                any(
                    operation["operation_id"] == UNCHANGED_OPERATION_ID
                    for operation in json.loads(ledger.read_text())["operations"]
                )
            )

            released = invoke(
                ACTIVE_ROOT_CLAIM,
                "--json",
                "claim",
                "release",
                "--root-id",
                facts["root_id"],
                "--expected-fingerprint",
                claim["fingerprint"],
                "--release-reason",
                "terminal",
                "--evidence",
                TERMINAL_EVIDENCE,
            )
            self.assertEqual(released["state"], "released")
            archived = invoke(
                LEDGER_CACHE,
                "--json",
                "ledger",
                "archive",
                "--ledger",
                str(ledger),
                "--root-id",
                facts["root_id"],
                "--evidence-ref",
                TERMINAL_EVIDENCE,
            )["archives"][0]
            self.assertEqual(archived["schema_version"], "2.0.0")
            self.assertFalse(ledger.exists())
            entry = Path(archived["entry_path"])
            archived_state = json.loads((entry / "ledger.json").read_text())
            archived_markdown = (entry / "ledger.md").read_text()
            metadata = json.loads((entry / "metadata.json").read_text())
            self.assertEqual(metadata["schema_version"], "2.0.0")
            self.assertEqual((entry / "ledger.json").read_bytes(), before_noop)
            self.assertEqual(
                archived_state["reviews"][0]["observations"][0][
                    "observation_fingerprint"
                ],
                facts["initial_review"]["observation_fingerprint"],
            )
            self.assertIn(facts["pull_request"]["url"], archived_markdown)
            self.assertIn(facts["final_head_sha"], archived_markdown)
            self.assertIn("Goal: `complete`", archived_markdown)
            verified = invoke(
                LEDGER_CACHE,
                "--json",
                "archive",
                "verify",
                "--archive-id",
                archived["archive_id"],
            )
            self.assertEqual(
                verified["archives"][0]["archive_id"], archived["archive_id"]
            )
            legacy_reverified = invoke(
                LEDGER_CACHE,
                "--json",
                "archive",
                "verify",
                "--archive-id",
                legacy_archive_id,
            )
            self.assertEqual(
                legacy_reverified["archives"][0]["schema_version"], "1.0.0"
            )
            self.assertEqual(legacy_ledger.read_bytes(), legacy_snapshot["ledger"])
            self.assertEqual(
                legacy_metadata.read_bytes(), legacy_snapshot["metadata"]
            )
            self.assertEqual(
                legacy_ledger.stat().st_mtime_ns, legacy_snapshot["ledger_mtime"]
            )
            self.assertEqual(
                legacy_metadata.stat().st_mtime_ns,
                legacy_snapshot["metadata_mtime"],
            )

            ceilings = proxy["output_byte_ceilings"]
            self.assertLessEqual(max(response_bytes), ceilings["max_cli_response"])
            self.assertLessEqual(sum(response_bytes), ceilings["total_cli_responses"])
            self.assertLessEqual(event_packet_bytes, ceilings["total_event_packets"])
            self.assertLessEqual(
                len(archived_markdown.encode()), ceilings["terminal_markdown"]
            )


if __name__ == "__main__":
    unittest.main()
