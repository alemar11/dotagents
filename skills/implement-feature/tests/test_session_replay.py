from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
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
TERMINAL_EVIDENCE = "session-replay-019f7625-terminal"


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


class SessionReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text())

    def test_efficiency_proxy_is_deterministic_and_conservative(self) -> None:
        fixture = self.fixture
        methodology = fixture["methodology"]
        proxy = fixture["efficiency_proxy"]
        baseline = proxy["baseline"]
        expected = proxy["counterfactual"]
        removed = proxy["removed_root_categories"]

        self.assertEqual(methodology["kind"], "deterministic-conservative-proxy")
        self.assertFalse(methodology["is_actual_future_token_measurement"])
        self.assertIn("not the tokens a future model run will consume", methodology["description"])
        self.assertEqual(
            fixture["source_sessions"]["root"]["sha256"],
            "1757b81f3106416c012e7a4568c1afa23209b3e17cbb0249762e28127ec4234c",
        )
        self.assertEqual(
            fixture["source_sessions"]["worker"]["sha256"],
            "30a21f8062274ec05a3b18bece526a8b1c6e498692894d60abc7fb89977b055f",
        )
        for source in fixture["source_sessions"].values():
            self.assertRegex(source["sha256"], r"^[0-9a-f]{64}$")

        removed_turns = sum(item["turns"] for item in removed)
        removed_tokens = sum(item["fresh_tokens"] for item in removed)
        root_turns = baseline["root"]["turns"] - removed_turns
        root_tokens = baseline["root"]["fresh_tokens"] - removed_tokens
        combined_turns = root_turns + baseline["worker"]["turns"]
        combined_tokens = root_tokens + baseline["worker"]["fresh_tokens"]
        reduction = round(removed_tokens * 100 / baseline["combined"]["fresh_tokens"], 2)
        root_worker_ratio = round(
            root_tokens * 100 / baseline["worker"]["fresh_tokens"], 2
        )

        self.assertEqual(
            baseline,
            {
                "root": {"turns": 134, "fresh_tokens": 349021},
                "worker": {"turns": 172, "fresh_tokens": 408675},
                "combined": {"turns": 306, "fresh_tokens": 757696},
            },
        )
        self.assertEqual((removed_turns, removed_tokens), (105, 265640))
        self.assertEqual((root_turns, root_tokens), (29, 83381))
        self.assertEqual((combined_turns, combined_tokens), (201, 492056))
        self.assertEqual(expected["root"], {"turns": 29, "fresh_tokens": 83381})
        self.assertEqual(
            expected["combined"], {"turns": 201, "fresh_tokens": 492056}
        )
        self.assertEqual(reduction, expected["fresh_token_reduction_percent"])
        self.assertEqual(
            root_worker_ratio, expected["root_to_worker_fresh_token_percent"]
        )

    def test_session_events_replay_through_production_cli(self) -> None:
        fixture = self.fixture
        facts = fixture["terminal_facts"]
        proxy = fixture["efficiency_proxy"]

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            env = os.environ.copy()
            env["HOME"] = str(base)
            repository = base / "repository"
            subprocess.run(
                ["git", "init", "--quiet", str(repository)],
                check=True,
                text=True,
                capture_output=True,
            )
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
            replacements: dict[str, Any] = {
                "__ROOT_CHECKOUT__": str(repository),
                "__WORKER_CHECKOUT__": str(repository),
                "__REPOSITORIES__": claim["repositories"],
                "__REPOSITORY_CHECKOUTS__": claim["repository_checkouts"],
                "__REPOSITORY_ID__": claim["repositories"][0],
                "__INITIAL_REVISION_KEY__": initial_revision_key,
                "__FINAL_REVISION_KEY__": final_revision_key,
            }
            registration = materialize(fixture["registration"], replacements)
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
                if batch["name"] == "final-review-and-terminal-gate":
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
                    self.assertEqual(task_status["revision_key"], final_revision_key)
                    self.assertEqual(
                        set(task_status["gates"]),
                        {"dependency-integration", "pr-preflight"},
                    )
                    self.assertIn("missing-current-review", task_status["terminal_blockers"])
                    self.assertFalse(status["terminal_eligible"])
                    state = json.loads(ledger.read_text())
                    self.assertEqual(len(state["reviews"]), 1)
                    self.assertEqual(
                        state["reviews"][0]["observations"][0]["observation_fingerprint"],
                        facts["initial_review"]["observation_fingerprint"],
                    )
                    self.assertTrue(
                        any(
                            gate["revision_key"] == initial_revision_key
                            and gate["gate"] == "focused-validation"
                            for gate in state["gates"]
                        )
                    )

            self.assertIsNotNone(final_batch_command)
            self.assertIsNotNone(final_batch_file)
            self.assertEqual(generation, 9)
            self.assertEqual(typed_state_writes, proxy["typed_state_write_ceiling"])
            self.assertLess(
                typed_state_writes, proxy["legacy_ledger_patch_attempts"] / 2
            )

            final_state = json.loads(ledger.read_text())
            task = final_state["tasks"][0]
            self.assertEqual(task["task_ref"], facts["worker_task_ref"])
            self.assertEqual(task["task_title"], facts["task_title"])
            self.assertEqual(task["goal_state"], "complete")
            self.assertEqual(task["state"], "merge-ready")
            self.assertEqual(
                task["outcome"], "pull-request-ready-for-merge-but-not-merged"
            )
            self.assertEqual(task["revision"]["head_sha"], facts["final_head_sha"])
            self.assertEqual(task["pr"]["number"], facts["pull_request"]["number"])
            self.assertEqual(task["pr"]["url"], facts["pull_request"]["url"])
            self.assertEqual(task["pr"]["head_sha"], facts["final_head_sha"])
            self.assertEqual(task["pr"]["base_ref"], facts["base_ref"])
            self.assertEqual(task["pr"]["merge_base_sha"], facts["merge_base_sha"])
            reconstructed_tuple = (
                f"ambrogio-dev/yn-ai-workflows#{task['pr']['number']}@"
                f"{task['pr']['head_sha']}@{task['pr']['base_ref']}@"
                f"{task['pr']['merge_base_sha']}"
            )
            self.assertEqual(reconstructed_tuple, facts["pull_request"]["tuple"])

            reviews = {item["revision_key"]: item for item in final_state["reviews"]}
            self.assertEqual(
                reviews[initial_revision_key]["observations"][0],
                {
                    "provider_state": "findings",
                    "observation_fingerprint": facts["initial_review"][
                        "observation_fingerprint"
                    ],
                    "disposition": "fix-required",
                    "evidence_ref": facts["initial_review"]["evidence_ref"],
                    "observed_at": reviews[initial_revision_key]["observations"][0][
                        "observed_at"
                    ],
                },
            )
            self.assertEqual(
                reviews[final_revision_key]["observations"][-1]["provider_state"],
                "clean",
            )
            self.assertEqual(
                reviews[final_revision_key]["observations"][-1]["disposition"],
                "accepted",
            )
            self.assertEqual(final_state["goal"]["state"], "complete")
            operations = final_state["operations"]
            activation_generation = next(
                item["generation"]
                for item in operations
                if "portfolio-goal-activated" in item["event_types"]
            )
            task_closeout_generation = max(
                item["generation"]
                for item in operations
                if "task-observed" in item["event_types"]
            )
            portfolio_closeout_generation = next(
                item["generation"]
                for item in operations
                if "portfolio-goal-completed" in item["event_types"]
            )
            self.assertLess(activation_generation, task_closeout_generation)
            self.assertLess(task_closeout_generation, portfolio_closeout_generation)

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

            ceilings = proxy["output_byte_ceilings"]
            self.assertLessEqual(max(response_bytes), ceilings["max_cli_response"])
            self.assertLessEqual(sum(response_bytes), ceilings["total_cli_responses"])
            self.assertLessEqual(event_packet_bytes, ceilings["total_event_packets"])
            self.assertLessEqual(
                len(archived_markdown.encode()), ceilings["terminal_markdown"]
            )


if __name__ == "__main__":
    unittest.main()
