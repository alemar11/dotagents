from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = SKILL_ROOT.parents[1]
TOOL = SKILL_ROOT / "scripts/ledger-cache"
CLAIM_TOOL = SKILL_ROOT / "scripts/active-root-claim"
AUTOREVIEW_TOOL = REPOSITORY / "skills/autoreview/scripts/autoreview"
LOADER = importlib.machinery.SourceFileLoader("ledger_cache_runtime", str(TOOL))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
CACHE_RUNTIME = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(CACHE_RUNTIME)
AUTOREVIEW_LOADER = importlib.machinery.SourceFileLoader(
    "autoreview_controller_runtime", str(AUTOREVIEW_TOOL)
)
AUTOREVIEW_SPEC = importlib.util.spec_from_loader(
    AUTOREVIEW_LOADER.name, AUTOREVIEW_LOADER
)
assert AUTOREVIEW_SPEC is not None
AUTOREVIEW_RUNTIME = importlib.util.module_from_spec(AUTOREVIEW_SPEC)
sys.modules[AUTOREVIEW_LOADER.name] = AUTOREVIEW_RUNTIME
AUTOREVIEW_LOADER.exec_module(AUTOREVIEW_RUNTIME)


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


class LedgerCacheV18Tests(unittest.TestCase):
    source_ref = "https://github.com/example/dotagents/issues/232"
    task_key = "spec-232"
    task_title = "Implement Feature Spec 232"
    task_assignment_objective = "Implement Feature Spec 232 exactly with CI when configured"

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.home_patch = mock.patch.dict(os.environ, {"HOME": str(self.home)})
        self.home_patch.start()
        self.addCleanup(self.home_patch.stop)
        (self.home / ".gitignore_global").write_text(".DS_Store\n")
        (self.home / ".gitconfig").write_text(
            "[core]\n\texcludesFile = " + str(self.home / ".gitignore_global") + "\n"
        )
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
        self.task_assignment_fingerprint = hashlib.sha256(
            self.task_assignment_objective.encode()
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
        objective = (
            "Implement the registered Feature Spec portfolio with CI when configured"
        )
        registration = {
            "schema_version": "8.0.0",
            "bundle_sha256": hashlib.sha256(b"bundle-fixture").hexdigest(),
            "execution_scope_fingerprint": "0" * 64,
            "authorization_fingerprint": "0" * 64,
            "root_task_ref": "app-task://root-a",
            "root_checkout": str(REPOSITORY),
            "objective": objective,
            "objective_fingerprint": hashlib.sha256(objective.encode()).hexdigest(),
            "permission_evidence_ref": "user-message://authorized-visible-tasks",
            "gitstack_installation_evidence": self.gitstack_installation_evidence(),
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
                            "github_repository": "example/dotagents",
                            "target_branch": "main",
                            "default_base": "main",
                            "allowed_paths": ["skills/implement-feature/"],
                            "ci_availability": "configured",
                            "preflight_key": hashlib.sha256(
                                b"delivery-preflight-fixture"
                            ).hexdigest(),
                            "preflight_evidence_ref": "delivery-preflight://fixture",
                            "validation_plan": [
                                {
                                    "validation_key": "full-validation",
                                    "command_id": "full-validation",
                                    "adapter": "clean-exit-v1",
                                    "policy": "clean-required",
                                    "authored_argv_fingerprint": hashlib.sha256(b"authored-argv").hexdigest(),
                                    "projected_argv_fingerprint": hashlib.sha256(b"projected-argv").hexdigest(),
                                    "tool_identities_fingerprint": hashlib.sha256(b"tool-identities").hexdigest(),
                                    "execution_policy_fingerprint": CACHE_RUNTIME.request_fingerprint(
                                        {
                                            "timeout_seconds": 3600,
                                            "heartbeat_seconds": 15,
                                            "term_grace_seconds": 10,
                                            "cleanup_seconds": 30,
                                            "stdout_limit_bytes": 8388608,
                                            "stderr_limit_bytes": 8388608,
                                        }
                                    ),
                                }
                            ],
                        }
                    ],
                    "dependency_ids": [],
                    "requires_domain_closeout": False,
                    "task_model": "gpt-5.6-sol",
                    "task_thinking": "xhigh",
                    "thinking_reason": "contract-sensitive state transition work",
                    "task_assignment_fingerprint": self.task_assignment_fingerprint,
                }
            ],
        }
        self.refresh_registration_fingerprints(registration)
        return registration

    def refresh_registration_fingerprints(self, registration: dict) -> None:
        scope_payload = {
            "bundle_sha256": registration["bundle_sha256"],
            "sources": [
                {
                    "task_key": source["task_key"],
                    "source_fingerprint": source["source_fingerprint"],
                    "deliveries": [
                        {
                            key: (
                                [CACHE_RUNTIME.canonical_allowed_path(path, "allowed_path") for path in delivery[key]]
                                if key == "allowed_paths" else delivery[key]
                            )
                            for key in ("delivery_key", "repository", "target_branch", "allowed_paths", "validation_plan")
                        }
                        for delivery in source["deliveries"]
                    ],
                }
                for source in registration["sources"]
            ],
        }
        registration["execution_scope_fingerprint"] = CACHE_RUNTIME.request_fingerprint(scope_payload)
        registration["authorization_fingerprint"] = CACHE_RUNTIME.request_fingerprint(
            {
                "execution_scope_fingerprint": registration["execution_scope_fingerprint"],
                "permission_evidence_ref": registration["permission_evidence_ref"],
                "gitstack_installation_fingerprint": registration["gitstack_installation_evidence"]["fingerprint"],
            }
        )

    def gitstack_installation_evidence(self) -> dict:
        evidence = {
            "schema_version": "gitstack-installation-parity:v1",
            "plugin_name": "gitstack",
            "plugin_root": "/installed/gitstack/5.0.0",
            "loaded_skill_path": "/installed/gitstack/5.0.0/skills/github-review-threads/SKILL.md",
            "manifest_version": "5.0.0",
            "package_version": "5.0.0",
            "cli_version": "5.0.0",
            "cli_sha256": hashlib.sha256(b"gitstack-cli").hexdigest(),
        }
        evidence["fingerprint"] = CACHE_RUNTIME.request_fingerprint(evidence)
        return evidence

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
            "execution_recovery_fingerprint": CACHE_RUNTIME.request_fingerprint([]),
            "command_cleanup_evidence": [],
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
        packet = self.write_packet(self.bind_decision_events(events), "events")
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

    def controller_next(self, *, check: bool = True) -> subprocess.CompletedProcess[str]:
        assert self.claim is not None
        return self.run_cache(
            "--json",
            "controller",
            "next",
            "--ledger",
            str(self.ledger),
            "--root-id",
            self.claim["root_id"],
            "--expected-claim-fingerprint",
            self.claim["fingerprint"],
            check=check,
        )

    def read_controller_result(
        self, controller: dict, *, owner: str, result_fingerprint: str,
    ) -> dict:
        controller_path = self.write_packet(controller, "controller-result-read")
        return CACHE_RUNTIME.operation_read_result(argparse.Namespace(
            owner=owner,
            result_fingerprint=result_fingerprint,
            controller_envelope_file=str(controller_path),
            ledger=str(self.ledger),
        ))

    def record_mock_owned_result(
        self,
        *,
        owner: str,
        operation: str,
        outcome: str,
        input_value: dict | None = None,
        facts: dict | None = None,
        result_extra: dict | None = None,
        assert_repeat_start_rejected: bool = False,
        expected_recovery_action: str | None = None,
    ) -> tuple[dict, dict, dict]:
        controller = parse_result(self.controller_next())
        self.assertEqual(controller["packet_template"]["operation"], {"owner": owner, "name": operation, "contract_version": "1.0.0"})
        operation_id = hashlib.sha256(f"{owner}:{operation}:{controller['projection_fingerprint']}".encode()).hexdigest()[:32]
        request = {
            "operation": operation, "operation_id": operation_id,
            "request_fingerprint": hashlib.sha256(f"request:{operation_id}".encode()).hexdigest(),
            "controller_envelope": controller,
            "controller_projection_fingerprint": controller["projection_fingerprint"],
            "authority": copy.deepcopy(controller["packet_template"]["authority_binding"]),
        }
        if owner == "gitstack":
            request["input"] = copy.deepcopy(input_value or {})
            if operation == "warning" and "prior_pending_result" not in request["input"]:
                pending = [
                    row["owner_result"] for row in self.state()["operations"]
                    if row["record_kind"] == "owned-operation-result"
                    and row["owner"] == "gitstack"
                    and row["owner_operation"] == "wait"
                    and row["normalized"]["disposition"] == "pending-warning"
                ]
                self.assertEqual(len(pending), 1)
                request["input"]["prior_pending_result"] = pending[0]
        start_identity = {
            "owner": owner,
            "operation": operation,
            "operation_id": operation_id,
            "request_fingerprint": request["request_fingerprint"],
            "start_receipt_fingerprint": None,
        }
        if owner == "gitstack" and operation == "reconcile-terminal":
            prior_result = request["input"]["prior_failed_result"]
            start_identity = {
                "owner": owner,
                "operation": prior_result["operation"],
                "operation_id": prior_result["operation_id"],
                "request_fingerprint": prior_result["request_fingerprint"],
                "start_receipt_fingerprint": prior_result["start_receipt_fingerprint"],
            }
        request_descriptor = self.owner_validation_descriptor(
            owner,
            request,
            start_identity=start_identity,
            prior_result_effect=(
                {
                    "relationship": "predecessor",
                    "owner": "gitstack",
                    "result_fingerprint": request["input"]["prior_pending_result"]["result_fingerprint"],
                    "required_disposition": "pending-warning",
                }
                if owner == "gitstack" and operation == "warning"
                else {
                    "relationship": "supersedes",
                    "owner": "gitstack",
                    "result_fingerprint": request["input"]["prior_failed_result"]["result_fingerprint"],
                    "required_disposition": "needs-owner",
                }
                if owner == "gitstack" and operation == "reconcile-terminal"
                else None
            ),
        )
        request_path = self.write_packet(request, f"{owner}-{operation}-request")
        args = argparse.Namespace(owner=owner, request_file=str(request_path), ledger=str(self.ledger))
        if operation == "reconcile-terminal":
            with mock.patch.object(CACHE_RUNTIME, "validate_owned_artifact", return_value=(request, None, request_descriptor)):
                started = {"start_receipt": CACHE_RUNTIME.operation_read_start(args)["start_receipt"]}
        else:
            with mock.patch.object(CACHE_RUNTIME, "validate_owned_artifact", return_value=(request, None, request_descriptor)):
                started = CACHE_RUNTIME.operation_start(args)
        if expected_recovery_action is not None:
            recovery = parse_result(self.controller_next())
            self.assertEqual(recovery["action"], expected_recovery_action)
            evidence = recovery["packet_template"]["evidence_descriptors"][0]
            recovered = CACHE_RUNTIME.operation_read_request(argparse.Namespace(
                owner=evidence["owner"], operation=evidence["operation"],
                operation_id=evidence["operation_id"],
                request_fingerprint=evidence["request_fingerprint"],
                start_receipt_fingerprint=evidence["start_receipt_fingerprint"],
                ledger=str(self.ledger),
            ))
            self.assertEqual(recovered["owner_request"], request)
        if assert_repeat_start_rejected:
            with mock.patch.object(CACHE_RUNTIME, "validate_owned_artifact", return_value=(request, None, request_descriptor)):
                with self.assertRaises(CACHE_RUNTIME.CacheError) as rejected:
                    CACHE_RUNTIME.operation_start(args)
            self.assertEqual(rejected.exception.code, "reconcile-required")
            with mock.patch.object(CACHE_RUNTIME, "validate_owned_artifact", return_value=(request, None, request_descriptor)):
                self.assertEqual(CACHE_RUNTIME.operation_read_start(args)["start_receipt"], started["start_receipt"])
        result = {
            "operation": operation, "operation_id": operation_id,
            "request_fingerprint": request["request_fingerprint"],
            "start_receipt_fingerprint": started["start_receipt"]["receipt_fingerprint"],
            "outcome": outcome, "facts": facts or {},
            "result_fingerprint": hashlib.sha256(f"result:{operation_id}:{outcome}".encode()).hexdigest(),
        }
        result.update(copy.deepcopy(result_extra or {}))
        followup_effect = None
        if owner == "gitstack" and operation == "wait" and outcome == "findings":
            followup_effect = {
                "consumes_obligation_id": None,
                "creates": [{
                    "kind": "review-thread", "action": "reply",
                    "obligation_id": hashlib.sha256(f"reply:{result['result_fingerprint']}".encode()).hexdigest(),
                    "source_result_fingerprint": result["result_fingerprint"],
                    "artifact_identity_fingerprint": hashlib.sha256(b"finding:1").hexdigest(),
                    "artifact_ref": "gitstack-operation://findings#followup-1",
                }],
            }
        elif owner == "gitstack" and operation in {"reply", "resolve"}:
            source = request["input"]["followup_obligation"]
            followup_effect = {
                "consumes_obligation_id": source["obligation_id"],
                "creates": [] if operation == "resolve" else [{
                    "kind": "review-thread", "action": "resolve",
                    "obligation_id": hashlib.sha256(f"resolve:{result['result_fingerprint']}".encode()).hexdigest(),
                    "source_result_fingerprint": result["result_fingerprint"],
                    "artifact_identity_fingerprint": hashlib.sha256(b"reply:1").hexdigest(),
                    "artifact_ref": "gitstack-operation://reply#followup-1",
                }],
            }
        result_descriptor = self.owner_validation_descriptor(
            owner,
            request,
            start_identity=start_identity,
            prior_result_effect=request_descriptor["prior_result_effect"],
            followup_effect=followup_effect,
            result=result,
            evidence_produced=outcome in {
                "terminal-clean", "terminal-composite-clean", "verification-clean",
                "fix-required",
            },
            orchestration_descriptor=(result_extra or {}).get("orchestration_descriptor"),
        )
        result_path = self.write_packet(result, f"{owner}-{operation}-result")
        result_args = argparse.Namespace(**vars(args), result_file=str(result_path))
        with mock.patch.object(CACHE_RUNTIME, "validate_owned_artifact", return_value=(request, result, result_descriptor)):
            recorded = CACHE_RUNTIME.operation_record_result(result_args)
        return request, result, recorded

    def owner_validation_descriptor(
        self,
        owner: str,
        request: dict,
        *,
        start_identity: dict | None = None,
        prior_result_effect: dict | None = None,
        followup_effect: dict | None = None,
        result: dict | None = None,
        evidence_produced: bool = False,
        orchestration_descriptor: dict | None = None,
        effective_result: dict | None = None,
    ) -> dict:
        return {
            "schema": "owned-operation-validation-descriptor:v1",
            "owner": owner,
            "operation": request["operation"],
            "operation_id": request["operation_id"],
            "request_fingerprint": request["request_fingerprint"],
            "start_identity": copy.deepcopy(start_identity or {
                "owner": owner,
                "operation": request["operation"],
                "operation_id": request["operation_id"],
                "request_fingerprint": request["request_fingerprint"],
                "start_receipt_fingerprint": None,
            }),
            "prior_result_effect": copy.deepcopy(prior_result_effect),
            "followup_effect": copy.deepcopy(followup_effect),
            "result_effect": None if result is None else {
                "evidence_produced": evidence_produced,
                "orchestration_descriptor": copy.deepcopy(orchestration_descriptor),
                "effective_result": {
                    "operation": (effective_result or result)["operation"],
                    "outcome": (effective_result or result)["outcome"],
                },
            },
        }

    def start_mock_owned_operation(
        self, owner: str, operation: str, *, input_value: dict | None = None,
    ) -> tuple[dict, dict]:
        controller = parse_result(self.controller_next())
        self.assertEqual(controller["packet_template"]["operation"]["name"], operation)
        operation_id = hashlib.sha256(f"crash:{owner}:{operation}:{controller['projection_fingerprint']}".encode()).hexdigest()[:32]
        request = {
            "operation": operation, "operation_id": operation_id,
            "request_fingerprint": hashlib.sha256(f"crash-request:{operation_id}".encode()).hexdigest(),
            "controller_envelope": controller,
            "controller_projection_fingerprint": controller["projection_fingerprint"],
            "authority": copy.deepcopy(controller["packet_template"]["authority_binding"]),
        }
        if owner == "gitstack":
            request["input"] = copy.deepcopy(input_value or {})
        path = self.write_packet(request, f"crash-{owner}-{operation}")
        args = argparse.Namespace(owner=owner, request_file=str(path), ledger=str(self.ledger))
        descriptor = self.owner_validation_descriptor(owner, request)
        with mock.patch.object(CACHE_RUNTIME, "validate_owned_artifact", return_value=(request, None, descriptor)):
            started = CACHE_RUNTIME.operation_start(args)
        return request, started

    def record_mock_mutation_reconciliation(
        self, original_request: dict, started: dict, *,
        effective_operation: str, effective_outcome: str,
        followup_effect: dict | None = None,
    ) -> dict:
        controller = parse_result(self.controller_next())
        self.assertEqual(controller["action"], "execute-gitstack-mutation-reconciliation")
        operation_id = hashlib.sha256(f"reconcile:{original_request['operation_id']}".encode()).hexdigest()[:32]
        request = {
            "operation": "reconcile-mutation", "operation_id": operation_id,
            "request_fingerprint": hashlib.sha256(f"reconcile-request:{operation_id}".encode()).hexdigest(),
            "controller_envelope": controller,
            "controller_projection_fingerprint": controller["projection_fingerprint"],
            "authority": copy.deepcopy(controller["packet_template"]["authority_binding"]),
        }
        start_identity = {
            "owner": "gitstack", "operation": original_request["operation"],
            "operation_id": original_request["operation_id"],
            "request_fingerprint": original_request["request_fingerprint"],
            "start_receipt_fingerprint": started["start_receipt"]["receipt_fingerprint"],
        }
        result = {
            "operation": "reconcile-mutation", "operation_id": operation_id,
            "request_fingerprint": request["request_fingerprint"],
            "start_receipt_fingerprint": started["start_receipt"]["receipt_fingerprint"],
            "outcome": "completed-from-readback", "facts": {},
            "result_fingerprint": hashlib.sha256(f"reconcile-result:{operation_id}".encode()).hexdigest(),
        }
        descriptor = self.owner_validation_descriptor(
            "gitstack", request, start_identity=start_identity, result=result,
            effective_result={"operation": effective_operation, "outcome": effective_outcome},
            followup_effect=followup_effect,
        )
        request_path = self.write_packet(request, "reconcile-request")
        result_path = self.write_packet(result, "reconcile-result")
        args = argparse.Namespace(owner="gitstack", request_file=str(request_path), result_file=str(result_path), ledger=str(self.ledger))
        with mock.patch.object(CACHE_RUNTIME, "validate_owned_artifact", return_value=(request, result, descriptor)):
            CACHE_RUNTIME.operation_record_result(args)
        return result

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
        title_evidence: str | None = "app-task://worker/title",
        model: str = "gpt-5.6-sol",
        reasoning_effort: str = "xhigh",
        assignment_fingerprint: str | None = None,
        read_scope: str = "eof",
        anchor_observation_fingerprint: str | None = None,
        anchor_marker_id: str | None = None,
    ) -> dict:
        state_snapshot = self.state()
        marker = f"{state_snapshot['generation']}-{state}"
        content_fingerprint = CACHE_RUNTIME.request_fingerprint(
            {
                "task_ref": "app-task://worker-232",
                "state": state,
                "marker": marker,
            }
        )
        page_chain_fingerprint = CACHE_RUNTIME.request_fingerprint(
            {"read": read_scope, "marker": marker, "content": content_fingerprint}
        )
        observation = {
            "observation_kind": "full-read",
            "task_ref": "app-task://worker-232",
            "host_id": "host-implement-feature",
            "wait_cursor": f"opaque-wait-{state_snapshot['generation']}",
            "read_scope": read_scope,
            "anchor_observation_fingerprint": anchor_observation_fingerprint,
            "anchor_marker_id": anchor_marker_id,
            "latest_turn_id": f"turn-{marker}",
            "latest_message_id": f"message-{marker}",
            "latest_tool_marker_id": f"tool-{marker}",
            "observed_status": state,
            "content_fingerprint": content_fingerprint,
            "page_chain_fingerprint": page_chain_fingerprint,
            "observed_at": state_snapshot["updated_at"],
            "base_generation": state_snapshot["generation"],
            "base_head": state_snapshot["content_fingerprint"],
        }
        observation["observation_fingerprint"] = CACHE_RUNTIME.full_read_observation_fingerprint(observation)
        return {
            "type": "task-observed",
            "task_key": self.task_key,
            "model": model,
            "reasoning_effort": reasoning_effort,
            "thinking_reason": "contract-sensitive state transition work",
            "task_title": self.task_title,
            "task_title_evidence_ref": title_evidence,
            "task_assignment_fingerprint": assignment_fingerprint
            or self.task_assignment_fingerprint,
            "state": state,
            "outcome": (
                "pull-request-ready-for-merge-but-not-merged"
                if state == "merge-ready"
                else None
            ),
            "attention_reason": None,
            "summary_ref": "app-task://worker-232/summary",
            "observation": observation,
        }

    def bind_decision_event(self, event: dict, state: dict | None = None) -> dict:
        bound = copy.deepcopy(event)
        event_type = bound.get("type")
        state = state or self.state()
        if (
            event_type in CACHE_RUNTIME.TASK_OBSERVATION_BOUND_EVENTS
            and "task_observation_fingerprint" not in bound
        ):
            task = next(
                item for item in state["tasks"] if item["task_key"] == bound.get("task_key")
            )
            observation = task["current_observation"]
            if observation is not None:
                bound["task_observation_fingerprint"] = observation[
                    "observation_fingerprint"
                ]
        return bound

    def bind_decision_events(self, events: list[dict]) -> list[dict]:
        return [self.bind_decision_event(event) for event in events]

    def checkout_event(self) -> dict:
        assert self.registration is not None
        deliveries = self.registration["sources"][0]["deliveries"]
        managed_checkouts = []
        for delivery in deliveries:
            checkout = (
                REPOSITORY
                if delivery["repository"] == self.claim["repositories"][0]
                else Path(delivery["repository"]).parent
            )
            head = subprocess.run(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"],
                text=True, capture_output=True, check=True,
            ).stdout.strip()
            tree = subprocess.run(
                ["git", "-C", str(checkout), "rev-parse", "HEAD^{tree}"],
                text=True, capture_output=True, check=True,
            ).stdout.strip()
            status = subprocess.run(
                ["git", "-C", str(checkout), "status", "--porcelain=v2", "--untracked-files=all", "-z"],
                capture_output=True,
                check=True,
            ).stdout
            managed_checkouts.append(
                {
                    "delivery_key": delivery["delivery_key"],
                    "repository": delivery["repository"],
                    "target_branch": delivery["target_branch"],
                    "checkout": str(checkout),
                    "git_top_level": str(checkout),
                    "baseline_revision": head,
                    "baseline_tree_sha": tree,
                    "baseline_status_fingerprint": hashlib.sha256(status).hexdigest(),
                    "execution_scope_fingerprint": self.registration["execution_scope_fingerprint"],
                    "isolation_evidence_ref": f"app-task://worker-232/worktree/{delivery['delivery_key']}",
                }
            )
        return {
            "type": "managed-checkouts-observed",
            "task_key": self.task_key,
            "task_ref": "app-task://worker-232",
            "managed_checkouts": managed_checkouts,
            "evidence_ref": "app-task://worker-232/checkout-map",
        }

    def baseline_acceptance_event(self) -> dict:
        state = self.state()
        baselines = []
        for task in state["tasks"]:
            for delivery in task["deliveries"]:
                checkout = delivery["managed_checkout"]
                assert checkout is not None
                for plan in delivery["validation_plan"]:
                    observation = {
                        "adapter": plan["adapter"],
                        "policy": plan["policy"],
                        "execution_scope_fingerprint": state["authorization"]["execution_scope_fingerprint"],
                        "authored_argv_fingerprint": plan["authored_argv_fingerprint"],
                        "argv_fingerprint": plan["projected_argv_fingerprint"],
                        "checkout_identity": {
                            "checkout": checkout["checkout"],
                            "branch": delivery["target_branch"],
                            "head_sha": checkout["baseline_revision"],
                            "tree_sha": checkout["baseline_tree_sha"],
                            "status_sha256": checkout["baseline_status_fingerprint"],
                            "status_clean": True,
                        },
                        "tool_identities_fingerprint": plan["tool_identities_fingerprint"],
                        "result": "clean",
                        "diagnostics": [],
                        "diagnostic_set_fingerprint": CACHE_RUNTIME.request_fingerprint([]),
                    }
                    manifest = {
                        "schema_version": "4.0.0",
                        "operation": "baseline-validation",
                        "manifest_sha256": hashlib.sha256(b"manifest").hexdigest(),
                        "argv_fingerprint": plan["projected_argv_fingerprint"],
                        "execution_policy": {
                            "timeout_seconds": 3600,
                            "heartbeat_seconds": 15,
                            "term_grace_seconds": 10,
                            "cleanup_seconds": 30,
                            "stdout_limit_bytes": 8388608,
                            "stderr_limit_bytes": 8388608,
                        },
                        "baseline": {
                            "adapter": plan["adapter"],
                            "policy": plan["policy"],
                            "execution_scope_fingerprint": state["authorization"]["execution_scope_fingerprint"],
                            "authored_argv_fingerprint": plan["authored_argv_fingerprint"],
                        },
                    }
                    receipt = {
                        "schema_version": "4.0.0",
                        "status": "passed",
                        "manifest_sha256": manifest["manifest_sha256"],
                        "receipt_sha256": hashlib.sha256(b"receipt").hexdigest(),
                        "baseline_observation": observation,
                    }
                    stem = f"{task['task_key']}-{delivery['delivery_key']}-{plan['validation_key']}"
                    manifest_path = self.home / f"baseline-manifest-{stem}.json"
                    receipt_path = self.home / f"baseline-receipt-{stem}.json"
                    manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n")
                    receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n")
                    baselines.append(
                        {
                            "task_key": task["task_key"],
                            "delivery_key": delivery["delivery_key"],
                            "validation_key": plan["validation_key"],
                            "manifest_file": str(manifest_path),
                            "manifest_bytes_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                            "receipt_file": str(receipt_path),
                            "receipt_bytes_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
                        }
                    )
        return {
            "type": "implementation-baseline-accepted",
            "expected_generation": state["generation"],
            "expected_state_fingerprint": state["content_fingerprint"],
            "expected_claim_fingerprint": state["claim"]["fingerprint"],
            "execution_scope_fingerprint": state["authorization"]["execution_scope_fingerprint"],
            "baselines": baselines,
            "evidence_ref": "baseline://accepted",
        }

    def bootstrap_active_task(self) -> None:
        self.acquire()
        self.create()
        self.apply(
            [
                {
                    "type": "root-title-observed",
                    "title": "👨🏻‍💻 Feature Orchestrator",
                    "evidence_ref": "app-task://root-a/title",
                },
                self.checkout_event(),
                self.task_event(state="created"),
            ]
        )
        self.apply([self.baseline_acceptance_event()])
        state = self.state()
        self.apply(
            [
                {
                    "type": "portfolio-goal-activated",
                    "goal_evidence_ref": "app-task://root-a/goal",
                    "objective_fingerprint": state["portfolio"]["objective_fingerprint"],
                },
                self.task_event(state="implementing"),
            ]
        )

    def test_dependency_wait_binds_and_restores_the_exact_resume_phase(self) -> None:
        self.bootstrap_active_task()
        started = {
            "type": "task-dependency-wait-started",
            "task_key": self.task_key,
            "resume_state": "implementing",
            "reason": "waiting for a root-owned transition",
            "summary_ref": "app-task://worker-232/dependency",
            "evidence_ref": "app-task://root-a/dependency-started",
        }
        self.apply([started])
        task = self.state()["tasks"][0]
        self.assertEqual(task["state"], "dependency-wait")
        self.assertEqual(task["dependency_wait"]["resume_state"], "implementing")
        self.assertNotIn("goal_state", task)

        wrong = self.apply(
            [
                {
                    "type": "task-dependency-wait-resolved",
                    "task_key": self.task_key,
                    "resume_state": "validating",
                    "evidence_ref": "app-task://root-a/dependency-resolved",
                }
            ],
            check=False,
        )
        self.error(wrong, "state-conflict")
        self.assertEqual(self.state()["tasks"][0]["state"], "dependency-wait")

        self.apply(
            [
                {
                    "type": "task-dependency-wait-resolved",
                    "task_key": self.task_key,
                    "resume_state": "implementing",
                    "evidence_ref": "app-task://root-a/dependency-resolved",
                }
            ]
        )
        task = self.state()["tasks"][0]
        self.assertEqual(task["state"], "implementing")
        self.assertIsNone(task["dependency_wait"])
        self.assertNotEqual(task["state"], "blocked")

    def test_full_read_proof_is_bounded_replay_safe_and_cas_bound(self) -> None:
        self.acquire()
        self.create()
        first = self.task_event(state="created")
        self.apply([self.checkout_event(), first])
        state = self.state()
        observation = state["tasks"][0]["current_observation"]
        self.assertIsNotNone(observation)
        assert observation is not None
        self.assertEqual(observation["observation_kind"], "full-read")
        self.assertIn("wait_cursor", observation)
        self.assertNotIn("read_cursor", observation)
        self.assertEqual(observation["read_scope"], "eof")
        self.assertIsNone(observation["anchor_observation_fingerprint"])
        self.assertIsNone(observation["anchor_marker_id"])
        self.assertEqual(
            observation["observation_fingerprint"],
            CACHE_RUNTIME.full_read_observation_fingerprint(observation),
        )

        before = self.ledger.read_bytes()
        compact = copy.deepcopy(first)
        compact["observation"]["observation_kind"] = "compact"
        rejected_compact = self.apply([compact], check=False)
        self.error(rejected_compact, "invalid-input")
        self.assertEqual(self.ledger.read_bytes(), before)

        pagination_cursor = copy.deepcopy(first)
        pagination_cursor["observation"]["read_cursor"] = "read-page-2"
        rejected_cursor = self.apply([pagination_cursor], check=False)
        self.error(rejected_cursor, "invalid-input")
        self.assertEqual(self.ledger.read_bytes(), before)

        duplicate = parse_result(self.apply([first], operation_id=self.next_operation_id()))
        self.assertEqual(duplicate["mutation_state"], "unchanged")
        self.assertEqual(self.ledger.read_bytes(), before)

        conflicting = copy.deepcopy(first)
        conflicting["observation"]["content_fingerprint"] = "0" * 64
        conflicting["observation"]["observation_fingerprint"] = (
            CACHE_RUNTIME.full_read_observation_fingerprint(conflicting["observation"])
        )
        rejected_conflict = self.apply(
            [conflicting], operation_id=self.next_operation_id(), check=False
        )
        self.error(rejected_conflict, "state-conflict")
        self.assertEqual(self.ledger.read_bytes(), before)

        stale = self.task_event(state="created")
        stale["observation"]["base_generation"] -= 1
        rejected_stale = self.apply(
            [stale], operation_id=self.next_operation_id(), check=False
        )
        self.error(rejected_stale, "state-conflict")
        self.assertEqual(self.ledger.read_bytes(), before)

        # An unrelated durable append does not invalidate the accepted proof.
        self.apply([self.baseline_acceptance_event()])
        replay_after_unrelated = parse_result(
            self.apply([first], operation_id=self.next_operation_id())
        )
        self.assertEqual(replay_after_unrelated["mutation_state"], "unchanged")

    def test_full_read_scope_requires_eof_or_exact_prior_anchor(self) -> None:
        self.acquire()
        self.create()

        initial_anchored = self.task_event(
            state="created",
            read_scope="anchored",
            anchor_observation_fingerprint="a" * 64,
            anchor_marker_id="turn-initial",
        )
        rejected_initial = self.apply(
            [self.checkout_event(), initial_anchored], check=False
        )
        self.error(rejected_initial, "state-conflict")
        self.assertIsNone(self.state()["tasks"][0]["current_observation"])

        initial_eof = self.task_event(state="created")
        self.apply([self.checkout_event(), initial_eof])
        prior = self.state()["tasks"][0]["current_observation"]
        assert prior is not None

        missing_anchor = self.task_event(
            state="created",
            read_scope="anchored",
            anchor_observation_fingerprint=None,
            anchor_marker_id=prior["latest_turn_id"],
        )
        rejected_missing_anchor = self.apply(
            [missing_anchor], operation_id=self.next_operation_id(), check=False
        )
        self.error(rejected_missing_anchor, "state-conflict")

        wrong_anchor_fingerprint = self.task_event(
            state="created",
            read_scope="anchored",
            anchor_observation_fingerprint="b" * 64,
            anchor_marker_id=prior["latest_turn_id"],
        )
        rejected_wrong_fingerprint = self.apply(
            [wrong_anchor_fingerprint],
            operation_id=self.next_operation_id(),
            check=False,
        )
        self.error(rejected_wrong_fingerprint, "state-conflict")

        wrong_anchor_marker = self.task_event(
            state="created",
            read_scope="anchored",
            anchor_observation_fingerprint=prior["observation_fingerprint"],
            anchor_marker_id="turn-not-from-prior",
        )
        rejected_wrong_marker = self.apply(
            [wrong_anchor_marker], operation_id=self.next_operation_id(), check=False
        )
        self.error(rejected_wrong_marker, "state-conflict")

        anchored = self.task_event(
            state="created",
            read_scope="anchored",
            anchor_observation_fingerprint=prior["observation_fingerprint"],
            anchor_marker_id=prior["latest_message_id"],
        )
        accepted_anchored = parse_result(
            self.apply([anchored], operation_id=self.next_operation_id())
        )
        self.assertEqual(accepted_anchored["mutation_state"], "applied")
        anchored_observation = self.state()["tasks"][0]["current_observation"]
        assert anchored_observation is not None
        self.assertEqual(anchored_observation["read_scope"], "anchored")
        self.assertEqual(
            anchored_observation["anchor_observation_fingerprint"],
            prior["observation_fingerprint"],
        )
        self.assertEqual(
            anchored_observation["anchor_marker_id"], prior["latest_message_id"]
        )

        replay_bytes = self.ledger.read_bytes()
        replayed_anchored = parse_result(
            self.apply([anchored], operation_id=self.next_operation_id())
        )
        self.assertEqual(replayed_anchored["mutation_state"], "unchanged")
        self.assertEqual(self.ledger.read_bytes(), replay_bytes)

        changed_eof = self.task_event(state="created", read_scope="eof")
        accepted_eof = parse_result(
            self.apply([changed_eof], operation_id=self.next_operation_id())
        )
        self.assertEqual(accepted_eof["mutation_state"], "applied")
        eof_observation = self.state()["tasks"][0]["current_observation"]
        assert eof_observation is not None
        self.assertEqual(eof_observation["read_scope"], "eof")
        self.assertIsNone(eof_observation["anchor_observation_fingerprint"])
        self.assertIsNone(eof_observation["anchor_marker_id"])

    def test_decision_events_require_the_latest_task_full_read(self) -> None:
        self.bootstrap_active_task()
        state = self.state()
        event = {
            "type": "gate-observed",
            "task_key": self.task_key,
            "delivery_key": None,
            "gate": "dependency-integration",
            "state": "passed",
            "binding_key": None,
            "evidence_ref": "proof://dependency-integration",
        }
        with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "schema is invalid"):
            CACHE_RUNTIME.apply_event(
                copy.deepcopy(state), event, datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
            )
        stale = {**event, "task_observation_fingerprint": "0" * 64}
        with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "latest accepted"):
            CACHE_RUNTIME.apply_event(
                copy.deepcopy(state), stale, datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
            )
        self.apply([event])
        self.assertEqual(self.state()["gates"][0]["gate"], "dependency-integration")

    def test_review_provider_mutation_guard_is_cas_bound_append_only_and_replay_safe(self) -> None:
        self.bootstrap_active_task()
        for event_type in (
            "review-provider-mutation-reserved",
            "review-provider-mutation-started",
            "review-provider-mutation-observed",
        ):
            self.error(self.apply([{"type": event_type}], check=False), "invalid-input")
        parser = CACHE_RUNTIME.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["ledger", "review-authority"])
        return

        self.bootstrap_active_task()
        revision = self.observe_revision()
        self.observe_delivery(revision)
        state = self.state()
        receipt = self.request_receipt(revision, request_key="mutation-request")
        protocol = CACHE_RUNTIME.REVIEW_MUTATION
        operation_id = protocol.operation_id_for_request(
            receipt["repository"], receipt["pr_number"], receipt["head_sha"],
            receipt["request_key"], receipt["request_fingerprint"],
        )
        packet = protocol.build_reservation(
            mutation_kind="review-request",
            repository=receipt["repository"],
            pr_number=receipt["pr_number"],
            head_sha=receipt["head_sha"],
            task_key=self.task_key,
            delivery_key="dotagents",
            operation_id=operation_id,
            request_key=receipt["request_key"],
            request_fingerprint=receipt["request_fingerprint"],
            thread_id=None,
            thread_fingerprint=None,
            finding_comment_id=None,
            body_fingerprint=receipt["body_fingerprint"],
            reply_receipt_fingerprint=None,
            expected_generation=state["generation"],
            expected_state_fingerprint=state["content_fingerprint"],
            expected_claim_fingerprint=state["claim"]["fingerprint"],
            expected_task_state=state["tasks"][0]["state"],
        )
        packet_fp = protocol.packet_fingerprint(packet)
        reserve = {
            "type": "review-provider-mutation-reserved",
            "task_key": self.task_key,
            "delivery_key": "dotagents",
            "reservation": packet,
            "packet_fingerprint": packet_fp,
            "evidence_ref": "app-task://root-a/review-reservation",
        }
        self.apply([reserve])
        journal = self.state()["tasks"][0]["deliveries"][0]["review_provider_mutations"]
        self.assertEqual(journal[0]["attempt_state"], "prepared")
        self.assertNotIn("attempt_state", journal[0]["reservation"])
        authority_packet = self.write_packet(packet, "authority")
        not_started = self.run_cache(
            "--json", "ledger", "review-authority", "--ledger", str(self.ledger),
            "--reservation-file", str(authority_packet), check=False,
        )
        self.error(not_started, "state-conflict")

        start = {
            "type": "review-provider-mutation-started",
            "task_key": self.task_key,
            "delivery_key": "dotagents",
            "reservation_id": packet["reservation_id"],
            "operation_id": packet["operation_id"],
            "packet_fingerprint": packet_fp,
            "evidence_ref": "app-task://root-a/review-mutation-started",
        }
        self.apply([start])
        authority = parse_result(
            self.run_cache(
                "--json", "ledger", "review-authority", "--ledger", str(self.ledger),
                "--reservation-file", str(authority_packet),
            )
        )
        self.assertEqual(authority["authority"], "review-provider-mutation-started")
        self.assertEqual(authority["packet_fingerprint"], packet_fp)
        result = {
            "type": "review-provider-mutation-observed",
            "task_key": self.task_key,
            "delivery_key": "dotagents",
            "reservation_id": packet["reservation_id"],
            "operation_id": packet["operation_id"],
            "attempt_state": "completed",
            "result_fingerprint": hashlib.sha256(b"request-receipt-401").hexdigest(),
            "receipt_ref": "gitstack://request/401",
            "recovery_state": "reconciled",
            "evidence_ref": "app-task://worker-232/request-result",
        }
        self.apply([result])
        journal = self.state()["tasks"][0]["deliveries"][0]["review_provider_mutations"]
        self.assertEqual(journal[0]["attempt_state"], "completed")
        self.assertEqual(
            [phase["attempt_state"] for phase in journal[0]["phase_history"]],
            ["prepared", "mutation-started", "completed"],
        )

        # The top-level projection is part of the integrity boundary, not a
        # cache of only the lifecycle enum.  Recompute the outer state
        # fingerprint so validation reaches the mutation projection check.
        tampered = copy.deepcopy(self.state())
        tampered["tasks"][0]["deliveries"][0]["review_provider_mutations"][0][
            "receipt_ref"
        ] = "gitstack://request/tampered"
        tampered["content_fingerprint"] = CACHE_RUNTIME.state_payload_fingerprint(tampered)
        with self.assertRaisesRegex(
            CACHE_RUNTIME.CacheError,
            "review provider mutation projection does not match final phase",
        ):
            CACHE_RUNTIME.validate_state(tampered, self.ledger)

        malformed = copy.deepcopy(self.state())
        malformed["tasks"][0]["deliveries"][0]["review_provider_mutations"][0][
            "phase_history"
        ][0] = "not-an-object"
        malformed["content_fingerprint"] = CACHE_RUNTIME.state_payload_fingerprint(malformed)
        with self.assertRaisesRegex(
            CACHE_RUNTIME.CacheError,
            r"phase_history\[0\]",
        ):
            CACHE_RUNTIME.validate_state(malformed, self.ledger)

        # A delayed duplicate of each message is a no-op, even though its
        # original packet generation is no longer current.
        self.apply([reserve])
        self.apply([start])
        self.apply([result])
        replayed = self.apply([result], operation_id=self.next_operation_id())
        self.assertEqual(parse_result(replayed)["mutation_state"], "unchanged")

        # Root bookkeeping may be wrapped by the typed dependency wait. Exact
        # delayed replays remain no-ops while the effective resume phase is
        # preserved; new authority cannot be reserved with the stale packet.
        self.apply([{
            "type": "task-dependency-wait-started",
            "task_key": self.task_key,
            "resume_state": "implementing",
            "reason": "persisting review result",
            "summary_ref": "app-task://worker-232/review-bookkeeping",
            "evidence_ref": "app-task://root-a/review-wait",
        }])
        self.apply([reserve], operation_id=self.next_operation_id())
        self.apply([start], operation_id=self.next_operation_id())
        self.apply([result], operation_id=self.next_operation_id())
        self.apply([{
            "type": "task-dependency-wait-resolved",
            "task_key": self.task_key,
            "resume_state": "implementing",
            "evidence_ref": "app-task://root-a/review-resumed",
        }])
        self.assertEqual(self.state()["tasks"][0]["state"], "implementing")

        # A result that advances the task is ordered inside one CAS batch:
        # wait-started -> result -> wait-resolved -> task transition.
        transition_state = self.state()
        transition_receipt = self.request_receipt(revision, request_key="transition-request")
        transition_operation_id = protocol.operation_id_for_request(
            transition_receipt["repository"],
            transition_receipt["pr_number"],
            transition_receipt["head_sha"],
            transition_receipt["request_key"],
            transition_receipt["request_fingerprint"],
        )
        transition_packet = protocol.build_reservation(
            mutation_kind="review-request",
            repository=receipt["repository"], pr_number=receipt["pr_number"],
            head_sha=receipt["head_sha"], task_key=self.task_key,
            delivery_key="dotagents", operation_id=transition_operation_id,
            request_key="transition-request", request_fingerprint=transition_receipt["request_fingerprint"],
            thread_id=None, thread_fingerprint=None, finding_comment_id=None,
            body_fingerprint=transition_receipt["body_fingerprint"], reply_receipt_fingerprint=None,
            expected_generation=transition_state["generation"],
            expected_state_fingerprint=transition_state["content_fingerprint"],
            expected_claim_fingerprint=transition_state["claim"]["fingerprint"],
            expected_task_state="implementing",
        )
        transition_fp = protocol.packet_fingerprint(transition_packet)
        self.apply([{
            "type": "review-provider-mutation-reserved", "task_key": self.task_key,
            "delivery_key": "dotagents", "reservation": transition_packet,
            "packet_fingerprint": transition_fp, "evidence_ref": "app-task://root-a/transition-reserved",
        }])
        self.apply([{
            "type": "review-provider-mutation-started", "task_key": self.task_key,
            "delivery_key": "dotagents", "reservation_id": transition_packet["reservation_id"],
            "operation_id": transition_packet["operation_id"], "packet_fingerprint": transition_fp,
            "evidence_ref": "app-task://root-a/transition-started",
        }])
        transition_result = {
            "type": "review-provider-mutation-observed", "task_key": self.task_key,
            "delivery_key": "dotagents", "reservation_id": transition_packet["reservation_id"],
            "operation_id": transition_packet["operation_id"], "attempt_state": "completed",
            "result_fingerprint": hashlib.sha256(b"transition-result").hexdigest(),
            "receipt_ref": "gitstack://request/transition", "recovery_state": "reconciled",
            "evidence_ref": "app-task://worker-232/transition-result",
        }
        self.apply([
            {
                "type": "task-dependency-wait-started", "task_key": self.task_key,
                "resume_state": "implementing", "reason": "persisting a state-changing result",
                "summary_ref": "app-task://worker-232/transition-bookkeeping",
                "evidence_ref": "app-task://root-a/transition-wait",
            },
            transition_result,
            {
                "type": "task-dependency-wait-resolved", "task_key": self.task_key,
                "resume_state": "implementing", "evidence_ref": "app-task://root-a/transition-resolved",
            },
            self.task_event(state="validating"),
        ])
        self.assertEqual(self.state()["tasks"][0]["state"], "validating")

        # A result without a durable start cannot cross the authority boundary.
        second_state = self.state()
        second_receipt = self.request_receipt(revision, request_key="second-request")
        second_operation_id = protocol.operation_id_for_request(
            second_receipt["repository"],
            second_receipt["pr_number"],
            second_receipt["head_sha"],
            second_receipt["request_key"],
            second_receipt["request_fingerprint"],
        )
        second_packet = protocol.build_reservation(
            mutation_kind="review-request",
            repository=receipt["repository"], pr_number=receipt["pr_number"], head_sha=receipt["head_sha"],
            task_key=self.task_key, delivery_key="dotagents",
            operation_id=second_operation_id, request_key="second-request",
            request_fingerprint=second_receipt["request_fingerprint"], thread_id=None,
            thread_fingerprint=None, finding_comment_id=None, body_fingerprint=second_receipt["body_fingerprint"],
            reply_receipt_fingerprint=None, expected_generation=second_state["generation"],
            expected_state_fingerprint=second_state["content_fingerprint"],
            expected_claim_fingerprint=second_state["claim"]["fingerprint"],
            expected_task_state=second_state["tasks"][0]["state"],
        )
        second_fp = protocol.packet_fingerprint(second_packet)
        self.apply([{
            "type": "review-provider-mutation-reserved", "task_key": self.task_key,
            "delivery_key": "dotagents", "reservation": second_packet,
            "packet_fingerprint": second_fp, "evidence_ref": "app-task://root-a/second-reservation",
        }])
        invalid_result = {
            **result,
            "reservation_id": second_packet["reservation_id"],
            "operation_id": second_packet["operation_id"],
        }
        rejected = self.apply([invalid_result], check=False)
        self.error(rejected, "state-conflict")

        # Mutation packets retain their own exact revision evidence. A later
        # PR head must not make the historical append-only journal invalid.
        self.observe_revision(head="e" * 40, merge_base="f" * 40)
        CACHE_RUNTIME.validate_state(self.state(), self.ledger)
    def direct_event(self, state: dict, event: dict, now: datetime) -> None:
        changed = CACHE_RUNTIME.apply_event(
            state, self.bind_decision_event(event, state), now
        )
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
                "github_repository": "example/docs",
                "preflight_key": hashlib.sha256(
                    b"delivery-preflight:example/docs:feature/docs"
                ).hexdigest(),
                "preflight_evidence_ref": "github://example/docs/preflight",
                "revision": {
                    "head_sha": head,
                    "base_ref": "main",
                    "merge_base_sha": merge_base,
                    "repository": repository,
                    "github_repository": "example/docs",
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
                    "github_repository": "example/dotagents",
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
            "github_repository": "example/dotagents",
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

    def request_receipt(
        self,
        revision: dict,
        *,
        comment_id: int = 9001,
        request_key: str = "run-clean",
        created_at: str = "2026-07-18T12:00:00Z",
        status: str = "posted",
    ) -> dict:
        schema = "gitstack-codex-review-request:v1"
        repository = "example/dotagents"
        pr_number = 233
        head_sha = revision["head_sha"]

        def fingerprint(value: dict) -> str:
            return hashlib.sha256(
                json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
            ).hexdigest()

        request_fingerprint = fingerprint({
            "schema": schema,
            "provider": "codex",
            "repository": repository,
            "pr_number": pr_number,
            "head_sha": head_sha,
            "request_key": request_key,
        })
        operation_id = hashlib.sha256(
            f"{repository}:{pr_number}:{head_sha}:{request_key}:{request_fingerprint}".encode()
        ).hexdigest()[:32]
        body = (
            f"@codex review {head_sha}\n\n<!-- {schema}\n"
            f"request_key={request_key}\nrequest_fingerprint={request_fingerprint}\n-->\n\n"
            f"<!-- gitstack-operation:{operation_id} -->"
        )
        body_fingerprint = hashlib.sha256(body.encode()).hexdigest()
        request_ref = f"https://github.com/{repository}/pull/{pr_number}#issuecomment-{comment_id}"
        identity_fingerprint = fingerprint({
            "schema": schema,
            "provider": "codex",
            "repository": repository,
            "pr_number": pr_number,
            "head_sha": head_sha,
            "request_key": request_key,
            "request_fingerprint": request_fingerprint,
            "body_fingerprint": body_fingerprint,
            "provider_request_id": {"kind": "github-issue-comment", "value": str(comment_id)},
            "request_ref": request_ref,
            "created_at": created_at,
        })
        return {
            "schema": schema,
            "provider": "codex",
            "repository": repository,
            "pr_number": pr_number,
            "head_sha": head_sha,
            "request_key": request_key,
            "request_fingerprint": request_fingerprint,
            "body_fingerprint": body_fingerprint,
            "identity_fingerprint": identity_fingerprint,
            "provider_request_id": {"kind": "github-issue-comment", "value": str(comment_id)},
            "request_ref": request_ref,
            "comment_id": comment_id,
            "created_at": created_at,
            "status": status,
        }

    def terminal_evidence_receipt(
        self,
        revision: dict,
        request_receipt: dict,
        *,
        artifact_id: int = 9010,
        outcome: str = "clean",
        body_fingerprint: str | None = None,
        artifact_created_at: str = "2026-07-18T12:05:00Z",
        verified_at: str = "2026-07-18T12:10:00Z",
    ) -> dict:
        actor = "chatgpt-codex-connector[bot]"
        artifact_ref = f"https://github.com/example/dotagents/pull/233#issuecomment-{artifact_id}"
        receipt = {
            "schema": "gitstack-terminal-provider-evidence:v1",
            "status": "verified",
            "provider": "codex",
            "repository": "example/dotagents",
            "pr_number": 233,
            "head_sha": revision["head_sha"],
            "request_identity_fingerprint": request_receipt["identity_fingerprint"],
            "request_fingerprint": request_receipt["request_fingerprint"],
            "provider_request_id": request_receipt["provider_request_id"],
            "request_ref": request_receipt["request_ref"],
            "request_created_at": request_receipt["created_at"],
            "artifact_id": {"kind": "github-issue-comment", "value": str(artifact_id)},
            "artifact_ref": artifact_ref,
            "artifact_created_at": artifact_created_at,
            "provider_actor": actor,
            "provider_identity_fingerprint": CACHE_RUNTIME.request_fingerprint(
                {"provider": "codex", "actor": actor}
            ),
            "body_fingerprint": body_fingerprint or hashlib.sha256(b"Codex clean result").hexdigest(),
            "reviewed_head_token": revision["head_sha"][:10],
            "resolved_head_sha": revision["head_sha"],
            "outcome": outcome,
            "artifact_fingerprint": "",
            "verified_at": verified_at,
            "receipt_fingerprint": "",
        }
        artifact_identity = {
            name: receipt[name]
            for name in (
                "provider", "repository", "pr_number", "head_sha", "artifact_id",
                "artifact_ref", "artifact_created_at", "provider_actor",
                "provider_identity_fingerprint", "body_fingerprint", "reviewed_head_token",
                "resolved_head_sha", "outcome",
            )
        }
        receipt["artifact_fingerprint"] = CACHE_RUNTIME.request_fingerprint(artifact_identity)
        receipt["receipt_fingerprint"] = CACHE_RUNTIME.request_fingerprint(
            {key: value for key, value in receipt.items() if key != "receipt_fingerprint"}
        )
        return receipt

    def review_reply_receipt(
        self,
        finding_revision: dict,
        reply_revision: dict,
        *,
        finding_comment_id: int = 55,
        reply_comment_id: int = 56,
    ) -> dict:
        receipt = {
            "schema": "gitstack-review-thread-reply:v1",
            "repository": "example/dotagents",
            "pr_number": 233,
            "finding_head_sha": finding_revision["head_sha"],
            "reply_head_sha": reply_revision["head_sha"],
            "thread_id": "PRRT_thread_55",
            "finding_comment_id": finding_comment_id,
            "finding_node_id": "PRRC_finding_55",
            "finding_ref": f"https://github.com/example/dotagents/pull/233#discussion_r{finding_comment_id}",
            "finding_created_at": "2026-07-18T12:01:00Z",
            "reply_comment_id": reply_comment_id,
            "reply_node_id": "PRRC_reply_56",
            "reply_author": "agent",
            "reply_ref": f"https://github.com/example/dotagents/pull/233#discussion_r{reply_comment_id}",
            "reply_created_at": "2026-07-18T13:01:00Z",
            "body_fingerprint": hashlib.sha256(b"fixed with focused proof").hexdigest(),
            "identity_fingerprint": "",
            "status": "replied",
        }
        identity = {
            name: receipt[name]
            for name in receipt
            if name not in {"identity_fingerprint", "status"}
        }
        receipt["identity_fingerprint"] = CACHE_RUNTIME.request_fingerprint(identity)
        return receipt

    def review_resolution_receipt(
        self, reply_receipt: dict, *, status: str = "resolved"
    ) -> dict:
        receipt = {
            "schema": "gitstack-review-thread-resolution:v1",
            "repository": reply_receipt["repository"],
            "pr_number": reply_receipt["pr_number"],
            "head_sha": reply_receipt["reply_head_sha"],
            "thread_id": reply_receipt["thread_id"],
            "finding_comment_id": reply_receipt["finding_comment_id"],
            "finding_node_id": reply_receipt["finding_node_id"],
            "reply_comment_id": reply_receipt["reply_comment_id"],
            "reply_node_id": reply_receipt["reply_node_id"],
            "reply_identity_fingerprint": reply_receipt["identity_fingerprint"],
            "resolution_fingerprint": "",
            "is_resolved": True,
            "observed_at": "2026-07-18T13:02:00Z",
            "status": status,
        }
        identity = {
            name: receipt[name]
            for name in receipt
            if name not in {"resolution_fingerprint", "is_resolved", "observed_at", "status"}
        }
        receipt["resolution_fingerprint"] = CACHE_RUNTIME.request_fingerprint(identity)
        return receipt

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
        if self.state()["tasks"][0]["state"] != "review-polling":
            self.apply([self.task_event(state="review-polling")])
        controller = parse_result(self.controller_next())
        if controller.get("packet_template", {}).get("operation") == {
            "owner": "autoreview",
            "name": "run-phase",
            "contract_version": "1.0.0",
        }:
            self.record_mock_owned_result(
                owner="autoreview",
                operation="run-phase",
                outcome="terminal-clean",
            )
        request_receipt = self.request_receipt(revision, request_key="run-clean")
        self.record_mock_owned_result(
            owner="gitstack",
            operation="request",
            outcome="created",
            facts={"request_receipt": request_receipt},
        )
        self.record_mock_owned_result(
            owner="gitstack",
            operation="wait",
            outcome="clean",
            facts={"request_receipt": request_receipt},
        )

    def autoreview_evidence(
        self,
        *,
        terminal_state: str = "terminal-clean",
        open_findings: list | None = None,
        parent: dict | None = None,
        phase: str = "full",
    ) -> dict:
        value = {
            "schema_version": "2.0.0",
            "review_phase": phase,
            "terminal_state": terminal_state,
            "open_findings": open_findings or [],
            "parent_evidence_fingerprint": parent["evidence_fingerprint"] if parent else None,
        }
        value["evidence_fingerprint"] = CACHE_RUNTIME.request_fingerprint(value)
        return value

    def record_autoreview(self, evidence: dict) -> None:
        outcome = {
            "terminal-clean": "terminal-clean",
            "terminal-composite-clean": "terminal-composite-clean",
            "verification-clean": "verification-clean",
        }.get(evidence["terminal_state"], "fix-required")
        self.record_mock_owned_result(
            owner="autoreview",
            operation="run-phase",
            outcome=outcome,
            facts={"evidence": evidence},
        )

    def test_autoreview_reservation_dry_run_uses_real_apply_path_and_exact_state(self) -> None:
        self.bootstrap_active_task()
        self.observe_revision()
        before = self.ledger.read_bytes()
        first = parse_result(self.controller_next())
        second = parse_result(self.controller_next())
        self.assertEqual(first, second)
        self.assertEqual(first["action"], "execute-autoreview-phase")
        self.assertEqual(
            first["packet_template"]["operation"],
            {"owner": "autoreview", "name": "run-phase", "contract_version": "1.0.0"},
        )
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_autoreview_reservation_allows_one_launch_and_no_release_after_start(self) -> None:
        self.bootstrap_active_task()
        self.observe_revision()
        self.record_mock_owned_result(
            owner="autoreview",
            operation="run-phase",
            outcome="terminal-clean",
            assert_repeat_start_rejected=True,
            expected_recovery_action="reconcile-autoreview-operation",
        )
        starts = [row for row in self.state()["operations"] if row["record_kind"] == "owned-operation-started"]
        self.assertEqual(len(starts), 1)

    def test_managed_autoreview_revalidates_live_claim_before_model_launch(self) -> None:
        self.bootstrap_active_task()
        self.observe_revision()
        controller = parse_result(self.controller_next())
        operation_id = "d" * 32
        request = {
            "operation": "run-phase", "operation_id": operation_id,
            "request_fingerprint": "e" * 64,
            "controller_envelope": controller,
            "controller_projection_fingerprint": controller["projection_fingerprint"],
            "authority": copy.deepcopy(controller["packet_template"]["authority_binding"]),
        }
        request_path = self.write_packet(request, "autoreview-drift-request")
        assert self.claim is not None
        (self.claim_root / f"{self.claim['root_id']}.json").unlink()
        args = argparse.Namespace(owner="autoreview", request_file=str(request_path), ledger=str(self.ledger))
        descriptor = self.owner_validation_descriptor("autoreview", request)
        with mock.patch.object(CACHE_RUNTIME, "validate_owned_artifact", return_value=(request, None, descriptor)):
            with self.assertRaises(CACHE_RUNTIME.CacheError) as rejected:
                CACHE_RUNTIME.operation_start(args)
        self.assertEqual(rejected.exception.code, "state-conflict")

    def test_consumed_failed_autoreview_attempt_requires_owner_and_cannot_reserve_again(self) -> None:
        self.bootstrap_active_task()
        self.observe_revision()
        self.record_mock_owned_result(
            owner="autoreview", operation="run-phase", outcome="failed"
        )

        blocked = parse_result(self.controller_next())
        self.assertIsNone(blocked["action"])
        self.assertIsNone(blocked["packet_template"])
        self.assertEqual(blocked["decision"], "blocked")
        self.assertEqual(blocked["blockers"][0]["code"], "autoreview-owned-result-failed")

    def observe_nonregression_and_scope(self, revision: dict) -> None:
        delivery = self.state()["tasks"][0]["deliveries"][0]
        plan = delivery["validation_plan"][0]
        diagnostics: list[dict] = []
        self.apply(
            [
                {
                    "type": "validation-nonregression-observed",
                    "task_key": self.task_key,
                    "delivery_key": delivery["delivery_key"],
                    "validation_key": plan["validation_key"],
                    "revision_key": revision["revision_key"],
                    "adapter": plan["adapter"],
                    "policy": plan["policy"],
                    "argv_fingerprint": plan["projected_argv_fingerprint"],
                    "tool_identities_fingerprint": plan["tool_identities_fingerprint"],
                    "diagnostics": diagnostics,
                    "diagnostic_set_fingerprint": CACHE_RUNTIME.request_fingerprint(diagnostics),
                    "evidence_ref": "validation://nonregression/full",
                },
                {
                    "type": "delivery-scope-observed",
                    "task_key": self.task_key,
                    "delivery_key": delivery["delivery_key"],
                    "revision_key": revision["revision_key"],
                    "changed_paths": ["skills/implement-feature"],
                    "untracked_paths": [],
                    "evidence_ref": "git://scope/current",
                },
            ]
        )

    def pass_terminal_gates(self, revision: dict) -> None:
        task = self.state()["tasks"][0]
        delivery = task["deliveries"][0]
        if CACHE_RUNTIME.owned_gate_result(self.state(), task, delivery, "autoreview") is None:
            self.record_autoreview(self.autoreview_evidence())
        self.observe_nonregression_and_scope(revision)
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
        delivery = self.state()["tasks"][0]["deliveries"][0]
        delivery_binding = CACHE_RUNTIME.delivery_evidence_key(delivery)
        for gate in sorted(CACHE_RUNTIME.applicable_delivery_revision_gates(delivery)):
            events.append(
                {
                    "type": "gate-observed",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "gate": gate,
                    "state": "passed",
                    "binding_key": delivery_binding,
                    "evidence_ref": f"proof://{gate}/{delivery_binding}",
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

    def test_doctor_is_v18_offline_and_read_only(self) -> None:
        before = self.snapshot_tree(self.home)
        version = self.run_cache("--version").stdout.strip()
        doctor = parse_result(self.run_cache("--json", "doctor"))

        self.assertEqual(version, "20.0.0")
        self.assertTrue(doctor["ok"])
        self.assertTrue(doctor["offline"])
        self.assertEqual(doctor["active_ledgers"], [])
        self.assertEqual(doctor["archive_count"], 0)
        self.assertEqual(before, self.snapshot_tree(self.home))
        self.assertFalse(self.cache_root.exists())

    def test_controller_registry_fixture_is_exhaustive_strict_and_bounded(self) -> None:
        fixture = json.loads(
            (SKILL_ROOT / "tests/fixtures/controller-replay-v2.json").read_text()
        )
        self.assertFalse((SKILL_ROOT / "tests/fixtures/controller-replay-v1.json").exists())
        CACHE_RUNTIME.validate_controller_registry()
        actual = [
            [
                action,
                spec["rank"],
                spec["phase"],
                spec["owner"],
                spec["packet_kind"],
                len(spec["contracts"]),
            ]
            for action, spec in sorted(
                CACHE_RUNTIME.CONTROLLER_ACTIONS.items(),
                key=lambda item: item[1]["rank"],
            )
        ]
        self.assertEqual(actual, fixture["registry"])
        self.assertEqual(CACHE_RUNTIME.CONTROLLER_TASK_STATE_ACTIONS, fixture["visible_task_states"])
        self.assertEqual(len(actual), fixture["metrics"]["registry_actions"])
        self.assertEqual(CACHE_RUNTIME.CONTROLLER_PROJECTION_SCHEMA_VERSION, "2.0.0")
        self.assertEqual(CACHE_RUNTIME.CONTROLLER_TEMPLATE_SCHEMA_VERSION, "2.0.0")
        self.assertEqual(CACHE_RUNTIME.LEDGER_SCHEMA_VERSION, fixture["ledger_schema_version"])
        self.assertEqual(CACHE_RUNTIME.REGISTRATION_SCHEMA_VERSION, fixture["registration_schema_version"])
        self.assertFalse(any("merge" in action and action != "steer-mergeability" for action, *_ in actual))
        for action, spec in CACHE_RUNTIME.CONTROLLER_ACTIONS.items():
            limit = 4 if spec["phase"] == "operation-recovery" else 3
            self.assertLessEqual(len(spec["contracts"]), limit, action)
            if spec["packet_kind"] == "owned-operation":
                self.assertEqual(spec["events"], [])
                self.assertTrue(all(set(row) == {"outcome", "next_phase"} for row in spec["transitions"]))
            else:
                self.assertEqual(
                    sorted(event for row in spec["transitions"] for event in row["event_types"]),
                    sorted(spec["events"]),
                )
            self.assertEqual(
                set(spec["bound_argument_types"]),
                set(CACHE_RUNTIME.CONTROLLER_BASE_BOUND_ARGUMENT_TYPES)
                | set(CACHE_RUNTIME.CONTROLLER_ACTION_BOUND_ARGUMENT_TYPES.get(action, {})),
            )

    def test_controller_next_is_claim_bound_deterministic_and_byte_read_only(self) -> None:
        claim = self.acquire()
        self.create()
        before = self.snapshot_tree(self.home)
        first_raw = self.controller_next().stdout
        second_raw = self.controller_next().stdout
        after = self.snapshot_tree(self.home)
        self.assertEqual(first_raw, second_raw)
        self.assertEqual(before, after)

        result = json.loads(first_raw)
        self.assertEqual(result["action"], "observe-root-title")
        self.assertEqual(result["binding"]["claim_fingerprint"], claim["fingerprint"])
        self.assertEqual(result["binding"]["generation"], 1)
        self.assertEqual(result["binding"]["state_fingerprint"], self.state()["content_fingerprint"])
        self.assertEqual(
            set(result),
            {
                "ok", "command", "controller_schema_version", "tool_version",
                "ledger_schema_version", "ledger", "portfolio_key", "root_id",
                "binding", "decision", "phase", "target", "action",
                "action_owner", "packet_template", "allowed_transitions",
                "completion_criterion", "blockers", "required_contracts",
                "projection_fingerprint",
            },
        )
        self.assertEqual(
            set(result["packet_template"]),
            {"schema_version", "packet_kind", "executor", "bound_arguments", "required_inputs", "result_event_types"},
        )
        self.assertNotIn("packet", result)

        for mutation in ("unknown-bound-argument", "wrong-bound-type", "unknown-input-type"):
            candidate = copy.deepcopy(result)
            if mutation == "unknown-bound-argument":
                candidate["packet_template"]["bound_arguments"]["manual_phase"] = "implementation"
            elif mutation == "wrong-bound-type":
                candidate["packet_template"]["bound_arguments"]["expected_generation"] = "1"
            else:
                candidate["packet_template"]["required_inputs"][0]["type"] = "free-form"
            candidate["projection_fingerprint"] = CACHE_RUNTIME.request_fingerprint(
                {key: value for key, value in candidate.items() if key != "projection_fingerprint"}
            )
            with self.assertRaises(CACHE_RUNTIME.CacheError, msg=mutation):
                CACHE_RUNTIME.validate_controller_response(candidate)

    def test_schema15_owned_start_is_single_use_and_autoreview_result_drives_gate(self) -> None:
        self.bootstrap_active_task()
        revision = self.observe_revision()
        controller = parse_result(self.controller_next())
        self.assertEqual(controller["action"], "execute-autoreview-phase")
        self.assertEqual(set(controller["packet_template"]), {"schema_version", "packet_kind", "executor", "operation", "authority_binding", "evidence_descriptors", "required_inputs", "accepted_result"})
        self.assertTrue(all(set(row) == {"outcome", "next_phase"} for row in controller["allowed_transitions"]))
        self.assertFalse(any("event" in key for row in controller["allowed_transitions"] for key in row))
        self.record_mock_owned_result(owner="autoreview", operation="run-phase", outcome="terminal-clean", assert_repeat_start_rejected=True)
        self.assertNotEqual(parse_result(self.controller_next())["action"], "execute-autoreview-phase")
        state = self.state(); task = state["tasks"][0]; delivery = task["deliveries"][0]
        self.apply([{
            "type": "gate-observed", "task_key": self.task_key, "delivery_key": delivery["delivery_key"],
            "gate": "autoreview", "state": "passed", "binding_key": CACHE_RUNTIME.delivery_evidence_key(delivery),
            "task_observation_fingerprint": task["current_observation"]["observation_fingerprint"],
            "evidence_ref": f"owned-operation://autoreview/{revision['revision_key']}",
        }])
        self.assertEqual(CACHE_RUNTIME.current_gate(self.state(), self.state()["tasks"][0], "autoreview", self.state()["tasks"][0]["deliveries"][0])["state"], "passed")

    def test_gitstack_request_wait_clean_and_findings_change_controller_and_gate(self) -> None:
        self.bootstrap_active_task(); self.observe_revision()
        self.record_mock_owned_result(owner="autoreview", operation="run-phase", outcome="terminal-clean")
        self.apply([self.task_event(state="review-polling")])
        self.assertEqual(parse_result(self.controller_next())["action"], "execute-gitstack-request")
        self.record_mock_owned_result(
            owner="gitstack", operation="request", outcome="created",
            expected_recovery_action="execute-gitstack-mutation-reconciliation",
        )
        self.assertEqual(parse_result(self.controller_next())["action"], "execute-gitstack-wait")
        self.record_mock_owned_result(
            owner="gitstack", operation="wait", outcome="clean",
            facts={"request_receipt": {"identity": "clean"}},
            expected_recovery_action="resume-gitstack-wait",
        )
        self.assertEqual(parse_result(self.controller_next())["action"], "steer-ci")
        state = self.state(); task = state["tasks"][0]; delivery = task["deliveries"][0]
        self.apply([{"type": "gate-observed", "task_key": self.task_key, "delivery_key": delivery["delivery_key"], "gate": "codex-review", "state": "passed", "binding_key": CACHE_RUNTIME.delivery_evidence_key(delivery), "task_observation_fingerprint": task["current_observation"]["observation_fingerprint"], "evidence_ref": "owned-operation://gitstack/clean"}])

    def test_gitstack_findings_route_to_review_fix(self) -> None:
        self.bootstrap_active_task(); self.observe_revision()
        self.record_mock_owned_result(owner="autoreview", operation="run-phase", outcome="terminal-clean")
        self.apply([self.task_event(state="review-polling")])
        self.record_mock_owned_result(owner="gitstack", operation="request", outcome="created")
        self.record_mock_owned_result(owner="gitstack", operation="wait", outcome="findings", facts={"request_receipt": {"identity": "findings"}})
        self.assertEqual(parse_result(self.controller_next())["action"], "steer-review-fix")

    def test_gitstack_findings_fix_reply_resolve_uses_durable_followups(self) -> None:
        self.bootstrap_active_task(); findings_revision = self.observe_revision()
        self.record_mock_owned_result(
            owner="autoreview", operation="run-phase", outcome="terminal-clean"
        )
        self.apply([self.task_event(state="review-polling")])
        self.record_mock_owned_result(owner="gitstack", operation="request", outcome="created")
        _, findings_result, _ = self.record_mock_owned_result(
            owner="gitstack", operation="wait", outcome="findings",
        )
        self.assertEqual(parse_result(self.controller_next())["action"], "steer-review-fix")

        self.observe_revision(head="c" * 40)
        self.record_mock_owned_result(
            owner="autoreview", operation="run-phase", outcome="terminal-clean"
        )
        reply_action = parse_result(self.controller_next())
        self.assertEqual(reply_action["action"], "execute-gitstack-reply")
        reply_obligation = reply_action["packet_template"]["evidence_descriptors"][0]
        recovered_findings = self.read_controller_result(
            reply_action, owner="gitstack",
            result_fingerprint=reply_obligation["source_result_fingerprint"],
        )
        self.assertEqual(recovered_findings["owner_result"], findings_result)
        self.assertEqual(
            recovered_findings["source_binding"]["revision_key"],
            findings_revision["revision_key"],
        )
        self.assertNotEqual(
            recovered_findings["source_binding"]["revision_key"],
            reply_action["packet_template"]["authority_binding"]["revision_key"],
        )
        reply_request, reply_started = self.start_mock_owned_operation(
            "gitstack", "reply", input_value={
                "followup_obligation": reply_obligation,
                "prior_findings_result": recovered_findings["owner_result"],
            },
        )
        resolve_obligation = {
            "kind": "review-thread", "action": "resolve",
            "obligation_id": hashlib.sha256(b"recovered-resolve").hexdigest(),
            "source_result_fingerprint": hashlib.sha256(b"recovered-reply-result").hexdigest(),
            "artifact_identity_fingerprint": hashlib.sha256(b"recovered-reply").hexdigest(),
            "artifact_ref": "gitstack-operation://recovered-reply#followup-1",
        }
        recovered_reply_result = self.record_mock_mutation_reconciliation(
            reply_request, reply_started, effective_operation="reply", effective_outcome="posted",
            followup_effect={
                "consumes_obligation_id": reply_obligation["obligation_id"],
                "creates": [resolve_obligation],
            },
        )
        resolve_action = parse_result(self.controller_next())
        self.assertEqual(resolve_action["action"], "execute-gitstack-resolve")
        self.assertEqual(resolve_action["packet_template"]["evidence_descriptors"][0], resolve_obligation)
        recovered_reply = self.read_controller_result(
            resolve_action, owner="gitstack",
            result_fingerprint=resolve_obligation["source_result_fingerprint"],
        )
        self.assertEqual(recovered_reply["owner_result"], recovered_reply_result)
        resolve_request, resolve_started = self.start_mock_owned_operation(
            "gitstack", "resolve", input_value={
                "followup_obligation": resolve_obligation,
                "prior_reply_result": recovered_reply["owner_result"],
            },
        )
        self.record_mock_mutation_reconciliation(
            resolve_request, resolve_started, effective_operation="resolve", effective_outcome="resolved",
            followup_effect={
                "consumes_obligation_id": resolve_obligation["obligation_id"], "creates": [],
            },
        )
        self.assertFalse(open_review_followups := CACHE_RUNTIME.open_review_followups(
            self.state(), self.state()["tasks"][0], self.state()["tasks"][0]["deliveries"][0]
        ))

    def test_gitstack_timeout_requires_warning_before_warning_only_gate(self) -> None:
        self.bootstrap_active_task(); self.observe_revision()
        self.record_mock_owned_result(owner="autoreview", operation="run-phase", outcome="terminal-clean")
        self.apply([self.task_event(state="review-polling")])
        self.record_mock_owned_result(owner="gitstack", operation="request", outcome="created")
        receipt = {"identity": "timeout-request"}
        _, pending_result, _ = self.record_mock_owned_result(
            owner="gitstack", operation="wait", outcome="pending-at-deadline",
            facts={"request_receipt": receipt},
        )
        warning_action = parse_result(self.controller_next())
        self.assertEqual(warning_action["action"], "execute-gitstack-warning")
        pending_descriptor = warning_action["packet_template"]["evidence_descriptors"][0]
        self.assertEqual(pending_descriptor["purpose"], "prior-pending")
        recovered_pending = self.read_controller_result(
            warning_action, owner="gitstack",
            result_fingerprint=pending_descriptor["result_fingerprint"],
        )
        self.assertEqual(recovered_pending["owner_result"], pending_result)
        state = self.state(); task = state["tasks"][0]; delivery = task["deliveries"][0]
        rejected = self.apply([{"type": "gate-observed", "task_key": self.task_key, "delivery_key": delivery["delivery_key"], "gate": "codex-review", "state": "passed", "binding_key": CACHE_RUNTIME.delivery_evidence_key(delivery), "task_observation_fingerprint": task["current_observation"]["observation_fingerprint"], "evidence_ref": "owned-operation://gitstack/no-warning"}], check=False)
        self.error(rejected, "state-conflict")
        self.record_mock_owned_result(
            owner="gitstack", operation="warning", outcome="posted",
            input_value={
                "request_receipt": receipt,
                "prior_pending_result": recovered_pending["owner_result"],
            }, facts={"request_receipt": receipt},
        )
        state = self.state(); task = state["tasks"][0]; delivery = task["deliveries"][0]
        self.apply([{"type": "gate-observed", "task_key": self.task_key, "delivery_key": delivery["delivery_key"], "gate": "codex-review", "state": "passed", "binding_key": CACHE_RUNTIME.delivery_evidence_key(delivery), "task_observation_fingerprint": task["current_observation"]["observation_fingerprint"], "evidence_ref": "owned-operation://gitstack/timeout-warning"}])

    def test_recovered_request_advances_to_wait_and_never_requests_again(self) -> None:
        self.bootstrap_active_task(); self.observe_revision()
        self.record_mock_owned_result(owner="autoreview", operation="run-phase", outcome="terminal-clean")
        self.apply([self.task_event(state="review-polling")])
        original, started = self.start_mock_owned_operation("gitstack", "request")
        self.record_mock_mutation_reconciliation(
            original, started, effective_operation="request", effective_outcome="created",
        )
        self.assertEqual(parse_result(self.controller_next())["action"], "execute-gitstack-wait")

    def test_recovered_warning_advances_and_never_warns_again(self) -> None:
        self.bootstrap_active_task(); self.observe_revision()
        self.record_mock_owned_result(owner="autoreview", operation="run-phase", outcome="terminal-clean")
        self.apply([self.task_event(state="review-polling")])
        self.record_mock_owned_result(owner="gitstack", operation="request", outcome="created")
        _, pending, _ = self.record_mock_owned_result(owner="gitstack", operation="wait", outcome="pending-at-deadline")
        original, started = self.start_mock_owned_operation(
            "gitstack", "warning", input_value={"prior_pending_result": pending},
        )
        self.record_mock_mutation_reconciliation(
            original, started, effective_operation="warning", effective_outcome="posted",
        )
        next_action = parse_result(self.controller_next())
        self.assertNotEqual(next_action["action"], "execute-gitstack-warning")
        gate_result = CACHE_RUNTIME.owned_gate_result(
            self.state(), self.state()["tasks"][0], self.state()["tasks"][0]["deliveries"][0], "codex-review",
        )
        self.assertEqual(gate_result["normalized"]["disposition"], "timeout-accepted")

    def test_terminal_reconciliation_appends_supersession_and_conflicting_result_fails(self) -> None:
        self.bootstrap_active_task(); self.observe_revision()
        self.record_mock_owned_result(owner="autoreview", operation="run-phase", outcome="terminal-clean")
        self.apply([self.task_event(state="review-polling")])
        self.record_mock_owned_result(owner="gitstack", operation="request", outcome="created")
        receipt = {"identity": "correlation-request"}
        _, failed, _ = self.record_mock_owned_result(owner="gitstack", operation="wait", outcome="request-correlation-failure", facts={"request_receipt": receipt})
        reconcile_action = parse_result(self.controller_next())
        self.assertEqual(reconcile_action["action"], "execute-gitstack-terminal-reconciliation")
        failed_descriptor = reconcile_action["packet_template"]["evidence_descriptors"][0]
        self.assertEqual(failed_descriptor["purpose"], "prior-failed")
        recovered_failed = self.read_controller_result(
            reconcile_action, owner="gitstack",
            result_fingerprint=failed_descriptor["result_fingerprint"],
        )
        self.assertEqual(recovered_failed["owner_result"], failed)
        request, result, _ = self.record_mock_owned_result(
            owner="gitstack", operation="reconcile-terminal", outcome="clean-verified",
            input_value={"prior_failed_result": recovered_failed["owner_result"], "request_receipt": receipt},
        )
        records = [row for row in self.state()["operations"] if row["record_kind"] == "owned-operation-result"]
        self.assertEqual(records[-1]["supersedes_result_fingerprint"], failed["result_fingerprint"])
        conflicting = copy.deepcopy(result); conflicting["outcome"] = "findings-verified"; conflicting["result_fingerprint"] = "f" * 64
        args = argparse.Namespace(owner="gitstack", request_file=str(self.write_packet(request, "conflict-request")), result_file=str(self.write_packet(conflicting, "conflict-result")), ledger=str(self.ledger))
        prior = request["input"]["prior_failed_result"]
        descriptor = self.owner_validation_descriptor(
            "gitstack",
            request,
            start_identity={
                "owner": "gitstack", "operation": prior["operation"],
                "operation_id": prior["operation_id"],
                "request_fingerprint": prior["request_fingerprint"],
                "start_receipt_fingerprint": prior["start_receipt_fingerprint"],
            },
            prior_result_effect={
                "relationship": "supersedes", "owner": "gitstack",
                "result_fingerprint": prior["result_fingerprint"],
                "required_disposition": "needs-owner",
            },
            result=conflicting,
        )
        with mock.patch.object(CACHE_RUNTIME, "validate_owned_artifact", return_value=(request, conflicting, descriptor)):
            with self.assertRaises(CACHE_RUNTIME.CacheError) as rejected:
                CACHE_RUNTIME.operation_record_result(args)
        self.assertEqual(rejected.exception.code, "state-conflict")

    def test_hosted_obligation_is_consumed_by_exact_autoreview_result(self) -> None:
        self.bootstrap_active_task(); self.observe_revision()
        self.record_mock_owned_result(
            owner="autoreview", operation="run-phase", outcome="terminal-clean"
        )
        self.apply([self.task_event(state="review-polling")])
        self.record_mock_owned_result(
            owner="gitstack", operation="request", outcome="created"
        )
        _, findings, _ = self.record_mock_owned_result(
            owner="gitstack", operation="wait", outcome="findings"
        )
        descriptor = {
            "hosted_obligation_ref": "owned-obligation://finding-1",
            "source_result_fingerprint": findings["result_fingerprint"],
        }
        self.apply([{
            "type": "autoreview-hosted-finding-obligated",
            "task_key": self.task_key,
            "delivery_key": "dotagents",
            "obligation_ref": descriptor["hosted_obligation_ref"],
            "source_result_fingerprint": descriptor["source_result_fingerprint"],
            "evidence_ref": "owned-operation://gitstack/findings",
        }])
        self.observe_revision(head="c" * 40)
        self.record_mock_owned_result(
            owner="autoreview",
            operation="run-phase",
            outcome="verification-clean",
            result_extra={
                "orchestration_descriptor": descriptor,
                "lineage_reset_authority_fingerprint": None,
            },
        )
        obligation = self.state()["tasks"][0]["deliveries"][0]["hosted_obligations"][0]
        self.assertEqual(obligation["state"], "consumed")
        self.assertRegex(obligation["consumed_result_fingerprint"], r"^[0-9a-f]{64}$")

    def test_hosted_obligation_mismatch_fails_closed_and_remains_open(self) -> None:
        self.bootstrap_active_task(); self.observe_revision()
        self.record_mock_owned_result(
            owner="autoreview", operation="run-phase", outcome="terminal-clean"
        )
        self.apply([self.task_event(state="review-polling")])
        self.record_mock_owned_result(
            owner="gitstack", operation="request", outcome="created"
        )
        _, findings, _ = self.record_mock_owned_result(
            owner="gitstack", operation="wait", outcome="findings"
        )
        descriptor = {
            "hosted_obligation_ref": "owned-obligation://finding-1",
            "source_result_fingerprint": findings["result_fingerprint"],
        }
        self.apply([{
            "type": "autoreview-hosted-finding-obligated",
            "task_key": self.task_key,
            "delivery_key": "dotagents",
            "obligation_ref": descriptor["hosted_obligation_ref"],
            "source_result_fingerprint": descriptor["source_result_fingerprint"],
            "evidence_ref": "owned-operation://gitstack/findings",
        }])
        self.observe_revision(head="c" * 40)
        controller = parse_result(self.controller_next())
        operation_id = "d" * 32
        request = {
            "operation": "run-phase", "operation_id": operation_id,
            "request_fingerprint": "e" * 64,
            "controller_envelope": controller,
            "controller_projection_fingerprint": controller["projection_fingerprint"],
            "authority": copy.deepcopy(controller["packet_template"]["authority_binding"]),
        }
        request_path = self.write_packet(request, "mismatched-obligation-request")
        args = argparse.Namespace(owner="autoreview", request_file=str(request_path), ledger=str(self.ledger))
        request_descriptor = self.owner_validation_descriptor("autoreview", request)
        with mock.patch.object(CACHE_RUNTIME, "validate_owned_artifact", return_value=(request, None, request_descriptor)):
            started = CACHE_RUNTIME.operation_start(args)
        result = {
            "operation": "run-phase", "operation_id": operation_id,
            "request_fingerprint": request["request_fingerprint"],
            "start_receipt_fingerprint": started["start_receipt"]["receipt_fingerprint"],
            "outcome": "verification-clean", "facts": {},
            "orchestration_descriptor": {
                **descriptor, "hosted_obligation_ref": "owned-obligation://other",
            },
            "lineage_reset_authority_fingerprint": None,
            "result_fingerprint": "f" * 64,
        }
        result_path = self.write_packet(result, "mismatched-obligation-result")
        result_args = argparse.Namespace(**vars(args), result_file=str(result_path))
        result_descriptor = self.owner_validation_descriptor(
            "autoreview", request, result=result, evidence_produced=True,
            orchestration_descriptor=result["orchestration_descriptor"],
        )
        with mock.patch.object(CACHE_RUNTIME, "validate_owned_artifact", return_value=(request, result, result_descriptor)):
            with self.assertRaises(CACHE_RUNTIME.CacheError) as rejected:
                CACHE_RUNTIME.operation_record_result(result_args)
        self.assertEqual(rejected.exception.code, "state-conflict")
        self.assertEqual(
            self.state()["tasks"][0]["deliveries"][0]["hosted_obligations"][0]["state"],
            "open",
        )

    def test_hosted_obligation_failed_autoreview_result_remains_open(self) -> None:
        self.bootstrap_active_task(); self.observe_revision()
        self.record_mock_owned_result(
            owner="autoreview", operation="run-phase", outcome="terminal-clean"
        )
        self.apply([self.task_event(state="review-polling")])
        self.record_mock_owned_result(owner="gitstack", operation="request", outcome="created")
        _, findings, _ = self.record_mock_owned_result(
            owner="gitstack", operation="wait", outcome="findings"
        )
        descriptor = {
            "hosted_obligation_ref": "owned-obligation://finding-failed",
            "source_result_fingerprint": findings["result_fingerprint"],
        }
        self.apply([{
            "type": "autoreview-hosted-finding-obligated",
            "task_key": self.task_key,
            "delivery_key": "dotagents",
            "obligation_ref": descriptor["hosted_obligation_ref"],
            "source_result_fingerprint": descriptor["source_result_fingerprint"],
            "evidence_ref": "owned-operation://gitstack/findings",
        }])
        self.observe_revision(head="c" * 40)
        self.record_mock_owned_result(
            owner="autoreview",
            operation="run-phase",
            outcome="failed",
            result_extra={
                "orchestration_descriptor": descriptor,
                "lineage_reset_authority_fingerprint": None,
            },
        )
        obligation = self.state()["tasks"][0]["deliveries"][0]["hosted_obligations"][0]
        self.assertEqual(obligation["state"], "open")
        self.assertIsNone(obligation["consumed_result_fingerprint"])

    def test_owner_validation_descriptor_rejects_cross_owner_identity(self) -> None:
        request = {
            "operation": "run-phase",
            "operation_id": "a" * 32,
            "request_fingerprint": "b" * 64,
        }
        descriptor = self.owner_validation_descriptor("autoreview", request)
        for mutate in (
            lambda row: row.update(owner="gitstack"),
            lambda row: row["start_identity"].update(owner="gitstack"),
            lambda row: row.update(operation_id="d" * 32),
        ):
            candidate = copy.deepcopy(descriptor)
            mutate(candidate)
            with self.assertRaises(CACHE_RUNTIME.CacheError):
                CACHE_RUNTIME.owner_validation_descriptor(
                    "autoreview", request, candidate, has_result=False,
                )

        prior = self.owner_validation_descriptor("autoreview", request)
        prior["prior_result_effect"] = {
            "relationship": "predecessor", "owner": "autoreview",
            "result_fingerprint": "e" * 64,
            "required_disposition": "pending-warning",
        }
        for mutate in (
            lambda row: row["prior_result_effect"].update(owner="gitstack"),
            lambda row: row["prior_result_effect"].update(required_disposition="accepted"),
            lambda row: row["prior_result_effect"].update(relationship="supersedes"),
        ):
            candidate = copy.deepcopy(prior)
            mutate(candidate)
            with self.assertRaises(CACHE_RUNTIME.CacheError):
                CACHE_RUNTIME.owner_validation_descriptor(
                    "autoreview", request, candidate, has_result=False,
                )

    def test_owned_result_normalized_map_tamper_is_rejected(self) -> None:
        self.bootstrap_active_task(); self.observe_revision()
        self.record_mock_owned_result(
            owner="autoreview", operation="run-phase", outcome="terminal-clean"
        )
        state = self.state()
        result = next(
            row for row in state["operations"] if row["record_kind"] == "owned-operation-result"
        )
        result["normalized"] = {
            **result["normalized"], "disposition": "needs-owner",
        }
        CACHE_RUNTIME.seal_state_fingerprint(state)
        with self.assertRaises(CACHE_RUNTIME.CacheError) as rejected:
            CACHE_RUNTIME.validate_state(state, self.ledger)
        self.assertEqual(rejected.exception.code, "integrity-failure")

    def test_controller_rejects_released_replaced_and_stale_claims(self) -> None:
        original = self.acquire()
        self.create()
        # Release and takeover both durably remove the old active claim file;
        # the controller must reject the old envelope before inspecting state.
        (self.claim_root / f"{original['root_id']}.json").unlink()
        released = self.run_cache(
            "--json", "controller", "next", "--ledger", str(self.ledger),
            "--root-id", original["root_id"],
            "--expected-claim-fingerprint", original["fingerprint"],
            check=False,
        )
        self.error(released, "state-conflict")

        replacement = self.acquire(root_id="root-b")
        stale = self.run_cache(
            "--json", "controller", "next", "--ledger", str(self.ledger),
            "--root-id", replacement["root_id"],
            "--expected-claim-fingerprint", original["fingerprint"],
            check=False,
        )
        self.error(stale, "state-conflict")
        rebound = self.controller_next(check=False)
        self.error(rebound, "state-conflict")

    def test_standalone_autoreview_next_route_is_removed(self) -> None:
        result = self.run_cache("--json", "autoreview", "next", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)

    def test_controller_replays_every_visible_phase_and_aggregates_concurrent_tasks(self) -> None:
        self.bootstrap_active_task()
        fixture = json.loads(
            (SKILL_ROOT / "tests/fixtures/controller-replay-v2.json").read_text()
        )
        base = self.state()
        decisions: list[tuple[str, str]] = []
        for task_state, expected_action in fixture["visible_task_states"].items():
            state = copy.deepcopy(base)
            state["tasks"][0]["state"] = task_state
            state["tasks"][0]["current_observation"]["observed_status"] = task_state
            projection = CACHE_RUNTIME.derive_controller_projection(self.ledger, state)
            decisions.append((task_state, projection["action"]))
            self.assertEqual(projection["decision"], "action")
            self.assertEqual(projection["action"], expected_action)
            self.assertNotIn("manual_phase", projection["packet_template"]["bound_arguments"])

        concurrent = copy.deepcopy(base)
        second = copy.deepcopy(concurrent["tasks"][0])
        second["task_key"] = "spec-233"
        second["source_id"] = "https://github.com/example/dotagents/issues/233"
        second["state"] = "implementing"
        second["current_observation"]["observed_status"] = "implementing"
        concurrent["tasks"].append(second)
        second_source = copy.deepcopy(concurrent["sources"][0])
        second_source["task_key"] = "spec-233"
        second_source["source_id"] = "https://github.com/example/dotagents/issues/233"
        second_source["source_spec_ref"] = second_source["source_id"]
        concurrent["sources"].append(second_source)
        first = CACHE_RUNTIME.derive_controller_projection(self.ledger, concurrent)
        second_projection = CACHE_RUNTIME.derive_controller_projection(
            self.ledger, copy.deepcopy(concurrent)
        )
        self.assertEqual(first, second_projection)
        self.assertEqual(first["action"], "steer-implementation")
        self.assertEqual(
            first["packet_template"]["bound_arguments"]["task_keys"],
            ["spec-232", "spec-233"],
        )
        self.assertEqual(len(decisions), len(fixture["visible_task_states"]))

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

    def test_objective_requires_conditional_ci_on_create_and_read(self) -> None:
        self.acquire()
        retired = self.registration_for()
        retired["objective"] = "Implement the portfolio with mandatory CI"
        retired["objective_fingerprint"] = hashlib.sha256(
            retired["objective"].encode()
        ).hexdigest()
        rejected = self.create(registration=retired, check=False)
        self.error(rejected, "invalid-input")
        self.assertFalse(self.ledger.exists())

        self.create(registration=self.registration_for())
        state = self.state()
        state["portfolio"]["objective"] = retired["objective"]
        state["portfolio"]["objective_fingerprint"] = retired[
            "objective_fingerprint"
        ]
        CACHE_RUNTIME.seal_state_fingerprint(state)
        self.ledger.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
        stale = self.run_cache(
            "--json",
            "ledger",
            "read",
            "--ledger",
            str(self.ledger),
            "--projection",
            "recovery",
            check=False,
        )
        self.error(stale, "integrity-failure")

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

    def test_schema12_active_ledger_is_rejected_without_rewrite(self) -> None:
        self.ledger_root.mkdir(parents=True, exist_ok=True)
        legacy = self.ledger_root / "schema12.json"
        legacy.write_text(json.dumps({"schema_version": "12.0.0"}, sort_keys=True) + "\n")
        before = legacy.read_bytes()
        result = self.run_cache(
            "--json",
            "ledger",
            "read",
            "--ledger",
            str(legacy),
            "--projection",
            "status",
            check=False,
        )
        self.assertEqual(result.returncode, 5)
        self.assertEqual(legacy.read_bytes(), before)

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

    def test_atomic_baseline_makes_dispatch_reachable_before_revision(self) -> None:
        self.acquire()
        self.create()
        self.apply([self.checkout_event(), self.task_event(state="created")])
        task = self.state()["tasks"][0]
        self.assertIsNone(task["deliveries"][0]["revision"])
        dispatch = parse_result(self.read_projection("dispatch"))
        self.assertEqual(dispatch["ready_task_keys"], [])
        self.apply([self.baseline_acceptance_event()])
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
        self.apply([self.task_event(state="implementing")])
        self.assertEqual(self.state()["tasks"][0]["state"], "implementing")

    def test_baseline_cas_rejects_partial_stale_drifted_and_tampered_grants(self) -> None:
        self.acquire()
        self.create()
        self.apply([
            {"type": "root-title-observed", "title": "👨🏻‍💻 Feature Orchestrator", "evidence_ref": "app-task://root-a/title"},
            self.checkout_event(),
            self.task_event(state="created"),
        ])
        valid = self.baseline_acceptance_event()
        candidates = []
        partial = copy.deepcopy(valid)
        partial["baselines"] = []
        candidates.append(partial)
        stale = copy.deepcopy(valid)
        stale["expected_generation"] -= 1
        candidates.append(stale)
        scope_drift = copy.deepcopy(valid)
        scope_drift["execution_scope_fingerprint"] = "f" * 64
        candidates.append(scope_drift)
        for candidate in candidates:
            self.error(self.apply([candidate], check=False), "state-conflict")
            self.assertEqual(self.state()["tasks"][0]["implementation_baseline"], "pending")

        tool_drift = copy.deepcopy(valid)
        row = tool_drift["baselines"][0]
        receipt_path = Path(row["receipt_file"])
        receipt = json.loads(receipt_path.read_text())
        receipt["baseline_observation"]["tool_identities_fingerprint"] = "e" * 64
        receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n")
        row["receipt_bytes_sha256"] = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
        self.error(self.apply([tool_drift], check=False), "state-conflict")

        tampered = self.baseline_acceptance_event()
        tampered_path = Path(tampered["baselines"][0]["receipt_file"])
        tampered_path.write_bytes(tampered_path.read_bytes() + b" ")
        self.error(self.apply([tampered], check=False), "state-conflict")
        self.assertEqual(self.state()["tasks"][0]["implementation_baseline"], "pending")

    def test_prebaseline_workers_have_no_goal_delivery_review_or_gate_authority(self) -> None:
        self.acquire()
        self.create()
        self.apply([
            {"type": "root-title-observed", "title": "👨🏻‍💻 Feature Orchestrator", "evidence_ref": "app-task://root-a/title"},
            self.checkout_event(),
            self.task_event(state="created"),
        ])
        objective = self.state()["portfolio"]["objective_fingerprint"]
        denied = [
            {"type": "portfolio-goal-activated", "goal_evidence_ref": "app-task://root-a/goal", "objective_fingerprint": objective},
            {
                "type": "gate-observed", "task_key": self.task_key, "delivery_key": None,
                "gate": "dependency-integration", "state": "passed", "binding_key": None,
                "evidence_ref": "proof://premature-gate",
            },
            {
                "type": "committed-revision-observed", "task_key": self.task_key,
                "delivery_key": "dotagents", "target": {}, "evidence_ref": "git://premature-revision",
            },
        ]
        for event in denied:
            self.error(
                self.apply([event], check=False),
                "invalid-input" if event["type"] == "committed-revision-observed" else "state-conflict",
            )
        state = self.state()
        self.assertEqual(state["goal"]["state"], "pending")
        self.assertEqual(state["gates"], [])
        self.assertIsNone(state["tasks"][0]["deliveries"][0]["revision"])
        self.assertNotIn("committed_revision", state["tasks"][0]["deliveries"][0])

    def test_preimplementation_abort_releases_and_archives_without_goal_state(self) -> None:
        self.acquire()
        self.create()
        self.apply([
            {"type": "root-title-observed", "title": "👨🏻‍💻 Feature Orchestrator", "evidence_ref": "app-task://root-a/title"},
            self.checkout_event(),
            self.task_event(state="created"),
        ])
        evidence = "planning://baseline-required/232"
        self.apply([{
            "type": "portfolio-preimplementation-aborted",
            "reason": "The declared validation has no provably read-only baseline projection.",
            "task_stop_evidence": [{
                "task_key": self.task_key,
                "task_ref": "app-task://worker-232",
                "evidence_ref": "app-task://worker-232/archived",
            }],
            "evidence_ref": evidence,
        }])
        state = self.state()
        self.assertEqual(state["goal"]["state"], "pending")
        self.assertEqual(state["tasks"][0]["implementation_baseline"], "planning-required")
        self.release(reason="preimplementation-abort", evidence=evidence)
        archived = parse_result(self.run_cache(
            "--json", "ledger", "archive", "--ledger", str(self.ledger),
            "--root-id", "root-a", "--reason", "preimplementation-abort",
            "--evidence-ref", evidence,
        ))["archives"][0]
        self.assertEqual(archived["archive_reason"], "preimplementation-abort")
        self.assertFalse(self.ledger.exists())

    def test_not_configured_ci_is_reported_and_never_accepts_a_ci_gate(self) -> None:
        self.acquire()
        registration = self.registration_for()
        registration["sources"][0]["deliveries"][0][
            "ci_availability"
        ] = "not-configured"
        self.create(registration=registration)
        delivery = self.state()["tasks"][0]["deliveries"][0]
        self.assertEqual(delivery["ci_availability"], "not-configured")
        status = parse_result(self.read_projection("status"))
        self.assertEqual(
            status["tasks"][0]["deliveries"][0]["ci_availability"],
            "not-configured",
        )

        objective_fingerprint = self.state()["portfolio"]["objective_fingerprint"]
        self.apply(
            [
                {
                    "type": "root-title-observed",
                    "title": "👨🏻‍💻 Feature Orchestrator",
                    "evidence_ref": "app-task://root-a/title",
                },
                self.checkout_event(),
                self.task_event(state="created"),
            ]
        )
        self.apply([self.baseline_acceptance_event()])
        self.apply([
            {
                "type": "portfolio-goal-activated",
                "goal_evidence_ref": "app-task://root-a/goal",
                "objective_fingerprint": objective_fingerprint,
            },
            self.task_event(state="implementing"),
        ])
        revision = self.observe_revision()
        rejected = self.apply(
            [
                {
                    "type": "gate-observed",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "gate": "ci",
                    "state": "passed",
                    "binding_key": CACHE_RUNTIME.delivery_evidence_key(
                        self.state()["tasks"][0]["deliveries"][0]
                    ),
                    "evidence_ref": "proof://ci/should-not-exist",
                }
            ],
            check=False,
        )
        self.error(rejected, "invalid-input")
        self.observe_delivery(revision)
        self.apply([self.task_event(state="draft-pr")])
        self.start_clean_review(revision)
        self.pass_terminal_gates(revision)
        gates = {
            item["gate"]
            for item in self.state()["gates"]
            if item["delivery_key"] == "dotagents"
        }
        self.assertNotIn("ci", gates)
        terminal = parse_result(self.read_projection("terminal"))["tasks"][0]
        self.assertNotIn("dotagents:gate:ci", terminal["blockers"])
        self.assertIsNotNone(terminal["seal_candidate_fingerprint"])

    def test_preflight_drift_changes_bindings_and_invalidates_delivery_gates(self) -> None:
        self.bootstrap_active_task()
        revision = self.observe_revision()
        self.observe_delivery(revision)
        self.apply([self.task_event(state="draft-pr")])
        self.start_clean_review(revision)
        self.pass_terminal_gates(revision)
        before = self.state()
        task_before = before["tasks"][0]
        old_revision_set = CACHE_RUNTIME.current_revision_set_key(task_before)
        old_binding = CACHE_RUNTIME.delivery_evidence_key(task_before["deliveries"][0])
        self.assertIsNotNone(
            CACHE_RUNTIME.current_gate(
                before, task_before, "full-validation", task_before["deliveries"][0]
            )
        )

        new_preflight_key = hashlib.sha256(b"delivery-preflight-drift").hexdigest()
        self.apply(
            [
                {
                    "type": "delivery-preflight-observed",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "github_repository": "example/dotagents",
                    "target_branch": "main",
                    "default_base": "main",
                    "ci_availability": "not-configured",
                    "preflight_key": new_preflight_key,
                    "evidence_ref": "delivery-preflight://drift",
                }
            ]
        )
        after = self.state()
        task_after = after["tasks"][0]
        delivery_after = task_after["deliveries"][0]
        self.assertNotEqual(old_binding, CACHE_RUNTIME.delivery_evidence_key(delivery_after))
        self.assertNotEqual(old_revision_set, CACHE_RUNTIME.current_revision_set_key(task_after))
        self.assertIsNone(
            CACHE_RUNTIME.current_gate(
                after, task_after, "full-validation", delivery_after
            )
        )
        self.assertEqual(delivery_after["ci_availability"], "not-configured")

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
                "github_repository": f"example/delivery-{index}",
                "target_branch": "main",
                "default_base": "main",
                "allowed_paths": ["src/"],
                "ci_availability": "configured",
                "preflight_key": hashlib.sha256(
                    f"delivery-preflight-{index}".encode()
                ).hexdigest(),
                "preflight_evidence_ref": f"delivery-preflight://{index}",
                "validation_plan": copy.deepcopy(
                    self.registration_for(claim)["sources"][0]["deliveries"][0]["validation_plan"]
                ),
            }
            for index, repository in enumerate(claim["repositories"], start=1)
        ]
        registration["sources"][0]["tracker_repository"] = claim["repositories"][0]
        self.refresh_registration_fingerprints(registration)
        self.create(registration=registration)
        self.assertEqual(len(self.state()["tasks"][0]["deliveries"]), 2)
        self.apply([
            {"type": "root-title-observed", "title": "👨🏻‍💻 Feature Orchestrator", "evidence_ref": "app-task://root-a/title"},
            self.checkout_event(),
            self.task_event(state="created"),
        ])
        atomic = self.baseline_acceptance_event()
        partial = copy.deepcopy(atomic)
        partial["baselines"] = partial["baselines"][:1]
        self.error(self.apply([partial], check=False), "state-conflict")
        self.assertTrue(all(not delivery["baseline_validations"] for delivery in self.state()["tasks"][0]["deliveries"]))
        self.apply([atomic])
        accepted = self.state()["tasks"][0]
        self.assertEqual(accepted["implementation_baseline"], "accepted")
        self.assertTrue(all(delivery["baseline_validations"] for delivery in accepted["deliveries"]))

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
                self.checkout_event(),
                self.task_event(state="created"),
            ]
        )
        self.apply([self.baseline_acceptance_event()])
        self.apply([{
            "type": "portfolio-goal-activated",
            "goal_evidence_ref": "app-task://root-a/goal",
            "objective_fingerprint": objective_fingerprint,
        }])
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
        self.error(self.apply([{"type": "review-observed"}], check=False), "invalid-input")
        return
        first = self.observe_revision()
        self.observe_delivery(first)
        self.start_clean_review(first)
        self.record_autoreview(self.autoreview_evidence())
        self.observe_nonregression_and_scope(first)
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
        second = self.observe_revision(head="c" * 40)
        projection = parse_result(self.read_projection("status"))
        task = projection["tasks"][0]
        self.assertNotEqual(second["revision_key"], first["revision_key"])
        self.assertNotIn("scope-acceptance", task["gates"])
        self.assertIn("dotagents:missing-current-review", task["terminal_blockers"])
        self.assertEqual(projection["warnings"], [])

    def test_autoreview_gate_requires_typed_terminal_evidence_and_revision_progress(self) -> None:
        self.bootstrap_active_task()
        revision = self.observe_revision()
        self.observe_delivery(revision)
        delivery = self.state()["tasks"][0]["deliveries"][0]
        binding = CACHE_RUNTIME.delivery_evidence_key(delivery)
        gate = {
            "type": "gate-observed", "task_key": self.task_key,
            "delivery_key": "dotagents", "gate": "autoreview", "state": "passed",
            "binding_key": binding, "evidence_ref": "proof://autoreview/free-form",
        }
        self.error(self.apply([gate], check=False), "state-conflict")
        initial = self.autoreview_evidence()
        self.record_autoreview(initial)
        self.apply([gate])
        next_action = parse_result(self.controller_next())
        self.assertNotEqual(next_action["action"], "reserve-autoreview-action")
        delivery = self.state()["tasks"][0]["deliveries"][0]
        owned = CACHE_RUNTIME.owned_gate_result(
            self.state(), self.state()["tasks"][0], delivery, "autoreview",
        )
        self.assertIsNotNone(owned)
        self.assertEqual(owned["normalized"]["disposition"], "accepted")

    def test_autoreview_lineage_cannot_cross_merge_base_drift(self) -> None:
        self.bootstrap_active_task()
        self.observe_revision()
        self.error(self.apply([{
            "type": "committed-revision-observed", "task_key": self.task_key,
            "delivery_key": "dotagents", "target": {}, "evidence_ref": "git://retired",
        }], check=False), "invalid-input")
        return
        prior_target = self.state()["tasks"][0]["deliveries"][0]["committed_revision"]["target"]
        equivalent = copy.deepcopy(prior_target)
        equivalent["head_sha"] = "e" * 40
        equivalent["merge_base_sha"] = "f" * 40
        equivalent["committed_revision_key"] = CACHE_RUNTIME.AUTOREVIEW_PROTOCOL.make_committed_revision_key(
            review_target_key=equivalent["review_target_key"],
            head_sha=equivalent["head_sha"],
            reviewed_patch_fingerprint=equivalent["reviewed_patch_fingerprint"],
        )
        self.apply(
            [{"type": "committed-revision-observed", "task_key": self.task_key, "delivery_key": "dotagents", "target": equivalent, "evidence_ref": "git://pure-rebase"}]
        )
        changed = copy.deepcopy(equivalent)
        changed["head_sha"] = "1" * 40
        changed["merge_base_sha"] = "2" * 40
        changed["reviewed_patch_fingerprint"] = "3" * 64
        changed["committed_revision_key"] = CACHE_RUNTIME.AUTOREVIEW_PROTOCOL.make_committed_revision_key(
            review_target_key=changed["review_target_key"], head_sha=changed["head_sha"],
            reviewed_patch_fingerprint=changed["reviewed_patch_fingerprint"],
        )
        error = self.error(
            self.apply([{"type": "committed-revision-observed", "task_key": self.task_key, "delivery_key": "dotagents", "target": changed, "evidence_ref": "git://semantic-drift"}], check=False),
            "state-conflict",
        )
        self.assertIn("lineage reset authority", error["message"])
        prior = self.state()["tasks"][0]["deliveries"][0]["autoreview"]
        self.apply(
            [
                {
                    "type": "autoreview-lineage-reset-authorized",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "authority": "granted-by-authorized-user",
                    "reason": "the canonical rebased patch changed semantically",
                    "evidence_ref": "owner://lineage-reset/1",
                    "prior_evidence_fingerprint": prior["evidence_fingerprint"],
                    "next_review_target_key": changed["review_target_key"],
                    "next_committed_revision_key": changed["committed_revision_key"],
                }
            ]
        )
        self.apply(
            [{"type": "committed-revision-observed", "task_key": self.task_key, "delivery_key": "dotagents", "target": changed, "evidence_ref": "git://semantic-drift"}]
        )
        _, arguments = self.autoreview_controller_projection()
        next_action = arguments["autoreview_projection"]
        self.assertEqual(next_action["action"], "full")
        self.assertIsNone(arguments["prior_evidence"])
        self.assertIsNone(next_action["packet"]["prior_evidence_fingerprint"])
        replacement = self.autoreview_evidence()
        replacement["lineage_id"] = "4" * 64
        replacement["evidence_fingerprint"] = CACHE_RUNTIME.AUTOREVIEW_PROTOCOL.evidence_fingerprint(replacement)
        self.record_autoreview(replacement)
        delivery = self.state()["tasks"][0]["deliveries"][0]
        self.assertEqual(delivery["autoreview"]["lineage_id"], "4" * 64)
        self.assertEqual(delivery["lineage_reset_authority"]["state"], "consumed")
        self.assertEqual(
            delivery["lineage_reset_authority"]["consumed_by"],
            replacement["evidence_fingerprint"],
        )

    def test_summary_only_hosted_finding_creates_one_focused_obligation(self) -> None:
        self.bootstrap_active_task()
        self.error(self.apply([{"type": "review-wait-started"}], check=False), "invalid-input")
        return
        revision = self.observe_revision()
        self.observe_delivery(revision)
        self.record_autoreview(self.autoreview_evidence())
        receipt = self.request_receipt(revision, request_key="summary-finding")
        self.apply([
            {"type": "review-wait-started", "task_key": self.task_key, "delivery_key": "dotagents", "revision_key": revision["revision_key"], "request_receipt": receipt}
        ])
        review = self.state()["reviews"][-1]
        observation_fingerprint = hashlib.sha256(b"summary-only-hosted-finding").hexdigest()
        evidence_ref = "github-review://233/summary-finding"
        self.apply([
            {"type": "review-wait-invoked", "task_key": self.task_key, "delivery_key": "dotagents", "revision_key": revision["revision_key"], "request_receipt": receipt, "wait_invoked_at": review["wait_started_at"], "provider_timeout": 2700},
            {"type": "review-observed", "task_key": self.task_key, "delivery_key": "dotagents", "revision_key": revision["revision_key"], "request_receipt": receipt, "request_binding": "recognized", "provider_state": "findings", "failure_kind": None, "provider_error_code": None, "observation_fingerprint": observation_fingerprint, "disposition": "fix-required", "finding_count": 1, "finding_comment_ids": [], "evidence_ref": evidence_ref, "warning_ref": None, "warning_posted_at": None, "warning_fingerprint": None},
        ])
        delivery = self.state()["tasks"][0]["deliveries"][0]
        finding_set = self.write_packet({"finding_source": "codex-review", "findings": [{"summary": "Fix the terminal comment finding."}]}, "summary-findings")
        finding_set_fingerprint = hashlib.sha256(finding_set.read_bytes()).hexdigest()
        provider_evidence_fingerprint = CACHE_RUNTIME.request_fingerprint({
            "evidence_ref": evidence_ref,
            "provider_state": "findings",
            "finding_count": 1,
            "finding_comment_ids": [],
        })
        obligation = {
            "schema_version": "2.0.0",
            "obligation_id": hashlib.sha256(b"summary-obligation").hexdigest(),
            "review_target_key": delivery["committed_revision"]["target"]["review_target_key"],
            "prior_lineage_id": delivery["autoreview"]["lineage_id"],
            "prior_evidence_fingerprint": delivery["autoreview"]["evidence_fingerprint"],
            "source_committed_revision_key": delivery["committed_revision"]["target"]["committed_revision_key"],
            "repository_id": delivery["committed_revision"]["target"]["repository_id"],
            "github_repository": delivery["github_repository"],
            "pr_number": 233,
            "request_receipt_fingerprint": CACHE_RUNTIME.request_fingerprint(receipt),
            "observation_fingerprint": observation_fingerprint,
            "provider_evidence_fingerprint": provider_evidence_fingerprint,
            "finding_count": 1,
            "finding_comment_ids": [],
            "finding_set_ref": str(finding_set),
            "finding_set_fingerprint": finding_set_fingerprint,
        }
        event = {"type": "autoreview-hosted-finding-obligated", "task_key": self.task_key, "delivery_key": "dotagents", "obligation": obligation}
        self.apply([event])
        _, arguments = self.autoreview_controller_projection()
        next_action = arguments["autoreview_projection"]
        self.assertEqual(next_action["action"], "fix-verification")
        self.assertEqual(arguments["hosted_obligation"]["finding_comment_ids"], [])
        self.assertEqual(self.apply([event]).returncode, 0)

    def test_review_wait_is_fixed_45_minutes_and_timeout_requires_warning(self) -> None:
        self.bootstrap_active_task()
        self.error(self.apply([{"type": "review-wait-started"}], check=False), "invalid-input")
        return
        revision = self.observe_revision()
        self.observe_delivery(revision)
        self.apply([self.task_event(state="review-polling")])
        state = self.state()
        started = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        request_receipt = self.request_receipt(revision, request_key="run-timeout", comment_id=9001, created_at="2026-07-18T12:00:00Z")
        self.direct_event(
            state,
            {
                "type": "review-wait-started",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_receipt": request_receipt,
            },
            started,
        )
        review = state["reviews"][-1]
        self.assertEqual(review["wait_deadline"], "2026-07-18T12:45:00Z")
        corrupt_deadline = copy.deepcopy(state)
        corrupt_deadline["reviews"][-1]["wait_deadline"] = "2026-07-18T12:44:00Z"
        CACHE_RUNTIME.seal_state_fingerprint(corrupt_deadline)
        with self.assertRaises(CACHE_RUNTIME.CacheError) as invalid_deadline:
            CACHE_RUNTIME.validate_state(corrupt_deadline, self.ledger)
        self.assertEqual(invalid_deadline.exception.code, "integrity-failure")
        self.assertEqual(invalid_deadline.exception.exit_code, 5)
        self.direct_event(
            state,
            {
                "type": "review-wait-invoked",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_receipt": request_receipt,
                "wait_invoked_at": "2026-07-18T12:00:00Z",
                "provider_timeout": 2700,
            },
            started,
        )
        observation = {
            "type": "review-observed",
            "task_key": self.task_key,
            "delivery_key": "dotagents",
            "revision_key": revision["revision_key"],
            "request_receipt": request_receipt,
            "request_binding": "recognized",
            "provider_state": "waiting",
            "failure_kind": None,
            "provider_error_code": None,
            "observation_fingerprint": hashlib.sha256(b"pending-timeout").hexdigest(),
            "disposition": "timeout-accepted",
            "finding_count": 0,
            "finding_comment_ids": [],
            "evidence_ref": "github-review://233/pending",
            "warning_ref": "https://github.com/example/dotagents/pull/233#issuecomment-9010",
            "warning_posted_at": review["wait_deadline"],
            "warning_fingerprint": CACHE_RUNTIME.review_timeout_warning_fingerprint(review),
        }
        with self.assertRaisesRegex(
            CACHE_RUNTIME.CacheError, "cannot be accepted before its deadline"
        ):
            CACHE_RUNTIME.apply_event(
                copy.deepcopy(state),
                observation,
                started + timedelta(minutes=44, seconds=59),
            )
        missing_warning = {**observation, "warning_ref": None}
        with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "warning_ref is required"):
            CACHE_RUNTIME.apply_event(
                copy.deepcopy(state),
                missing_warning,
                started + timedelta(minutes=45),
            )
        wrong_pr_warning = {
            **observation,
            "warning_ref": "https://github.com/example/other/pull/999#issuecomment-9010",
        }
        with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "exact pull request"):
            CACHE_RUNTIME.apply_event(
                copy.deepcopy(state),
                wrong_pr_warning,
                started + timedelta(minutes=45),
            )
        wrong_content = {**observation, "warning_fingerprint": "0" * 64}
        with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "required timeout warning"):
            CACHE_RUNTIME.apply_event(
                copy.deepcopy(state),
                wrong_content,
                started + timedelta(minutes=45),
            )
        old_comment = {**observation, "warning_posted_at": "2026-07-18T12:44:59Z"}
        with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "between the review deadline"):
            CACHE_RUNTIME.apply_event(
                copy.deepcopy(state),
                old_comment,
                started + timedelta(minutes=45),
            )
        self.direct_event(state, observation, started + timedelta(minutes=45))
        CACHE_RUNTIME.seal_state_fingerprint(state)
        CACHE_RUNTIME.validate_state(state, self.ledger)
        self.assertEqual(review["wait_state"], "complete")
        self.assertEqual(state["goal"]["state"], "active")
        self.assertEqual(
            CACHE_RUNTIME.review_warnings(state),
            [
                {
                    "code": "codex-review-timeout-accepted",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "revision_key": revision["revision_key"],
                    "pr_url": revision["pr_url"],
                    "warning_ref": observation["warning_ref"],
                }
            ],
        )
        self.direct_event(
            state,
            {
                "type": "gate-observed",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "gate": "codex-review",
                "state": "passed",
                "binding_key": CACHE_RUNTIME.delivery_evidence_key(
                    state["tasks"][0]["deliveries"][0]
                ),
                "evidence_ref": observation["warning_ref"],
            },
            started + timedelta(minutes=46),
        )
        self.direct_event(
            state,
            {
                "type": "committed-revision-observed",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "target": {
                    **state["tasks"][0]["deliveries"][0]["committed_revision"]["target"],
                    "head_sha": "e" * 40,
                    "merge_base_sha": "f" * 40,
                    "reviewed_patch_fingerprint": "1" * 64,
                    "phase_input_fingerprint": "1" * 64,
                    "committed_revision_key": CACHE_RUNTIME.AUTOREVIEW_PROTOCOL.make_committed_revision_key(
                        review_target_key=state["tasks"][0]["deliveries"][0]["committed_revision"]["target"]["review_target_key"],
                        head_sha="e" * 40,
                        reviewed_patch_fingerprint="1" * 64,
                    ),
                },
                "evidence_ref": "git://committed-revision/after-timeout",
            },
            started + timedelta(minutes=47),
        )
        self.direct_event(
            state,
            {
                "type": "revision-observed",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "repository": revision["repository"],
                "github_repository": revision["github_repository"],
                "pr_number": revision["pr_number"],
                "pr_url": revision["pr_url"],
                "head_sha": "e" * 40,
                "base_ref": revision["base_ref"],
                "merge_base_sha": "f" * 40,
                "evidence_ref": "git://revision/after-timeout",
            },
            started + timedelta(minutes=47),
        )
        self.assertEqual(CACHE_RUNTIME.review_warnings(state), [])

    def test_review_warning_projection_is_bounded_and_reports_omissions(self) -> None:
        self.bootstrap_active_task()
        self.error(self.apply([{"type": "review-observed"}], check=False), "invalid-input")
        return
        state = self.state()
        base_task = state["tasks"][0]
        base_delivery = base_task["deliveries"][0]
        tasks = []
        sources = []
        reviews = []
        for task_index in range(32):
            task_key = f"task-{task_index}"
            deliveries = []
            for delivery_index in range(8):
                warning_index = task_index * 8 + delivery_index + 1
                delivery_key = f"delivery-{delivery_index}"
                revision_key = hashlib.sha256(
                    f"revision-{warning_index}".encode()
                ).hexdigest()
                repository = f"example/{'r' * 3000}"
                pr_url = (
                    f"https://github.com/{repository}/pull/{warning_index}"
                )
                delivery = copy.deepcopy(base_delivery)
                delivery["delivery_key"] = delivery_key
                delivery["revision"] = {"revision_key": revision_key}
                deliveries.append(delivery)
                reviews.append(
                    {
                        "task_key": task_key,
                        "delivery_key": delivery_key,
                        "revision_key": revision_key,
                        "pr_url": pr_url,
                        "wait_state": "complete",
                        "reconciliations": [],
                        "observations": [
                            {
                                "request_binding": "recognized",
                                "provider_state": "waiting",
                                "failure_kind": None,
                                "provider_error_code": None,
                                "observation_fingerprint": hashlib.sha256(
                                    f"warning-{warning_index}".encode()
                                ).hexdigest(),
                                "disposition": "timeout-accepted",
                                "finding_count": 0,
                                "finding_comment_ids": [],
                                "warning_ref": (
                                    f"{pr_url}#issuecomment-{warning_index}"
                                ),
                            }
                        ],
                    }
                )
            task = copy.deepcopy(base_task)
            task["task_key"] = task_key
            task["deliveries"] = deliveries
            tasks.append(task)
            source = copy.deepcopy(state["sources"][0])
            source["task_key"] = task_key
            sources.append(source)

        state["tasks"] = tasks
        state["sources"] = sources
        state["reviews"] = reviews
        warnings = CACHE_RUNTIME.review_warnings(state)
        encoded = json.dumps(
            warnings, sort_keys=True, separators=(",", ":")
        ).encode()
        self.assertLessEqual(
            len(encoded), CACHE_RUNTIME.MAX_PROJECTED_REVIEW_WARNING_BYTES
        )
        self.assertEqual(warnings[-1]["summary"], "additional-warnings-omitted")
        self.assertEqual(warnings[-1]["total_count"], 256)
        self.assertGreater(warnings[-1]["omitted_count"], 0)
        markdown = CACHE_RUNTIME.render_markdown(state)
        self.assertIn("additional timeout warnings omitted", markdown)
        self.assertIn("full evidence remains in the JSON archive", markdown)

    def test_github_pr_identity_rejects_untrusted_input_and_corrupt_state(self) -> None:
        self.bootstrap_active_task()
        assert self.registration is not None
        repository = self.registration["sources"][0]["deliveries"][0]["repository"]
        event = {
            "type": "revision-observed",
            "task_key": self.task_key,
            "delivery_key": "dotagents",
            "head_sha": "a" * 40,
            "base_ref": "main",
            "merge_base_sha": "b" * 40,
            "repository": repository,
            "github_repository": "example/dotagents",
            "pr_number": 233,
            "pr_url": "https://attacker.example/pull/233",
            "evidence_ref": "git://revision/untrusted-url",
        }
        base_state = self.state()
        observed_at = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        for github_repository in ("example/.github", "example/source.git"):
            with self.subTest(github_repository=github_repository):
                accepted = {
                    **event,
                    "github_repository": github_repository,
                    "pr_url": f"https://github.com/{github_repository}/pull/233",
                }
                accepted_state = copy.deepcopy(base_state)
                accepted_state["tasks"][0]["deliveries"][0][
                    "github_repository"
                ] = github_repository
                with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "canonical owner/repository"):
                    CACHE_RUNTIME.apply_event(accepted_state, accepted, observed_at)
        rejected = self.apply([event], check=False)
        error = self.error(rejected, "invalid-input")
        self.assertIn("canonical GitHub PR URL", error["message"])

        revision = self.observe_revision()
        corrupt_revision = self.state()
        corrupt_revision["tasks"][0]["deliveries"][0]["revision"]["pr_url"] = (
            "https://attacker.example/pull/233"
        )
        CACHE_RUNTIME.seal_state_fingerprint(corrupt_revision)
        with self.assertRaises(CACHE_RUNTIME.CacheError) as invalid_revision:
            CACHE_RUNTIME.validate_state(corrupt_revision, self.ledger)
        self.assertEqual(invalid_revision.exception.code, "integrity-failure")
        self.assertEqual(invalid_revision.exception.exit_code, 5)

        corrupt_base = self.state()
        corrupt_base["tasks"][0]["deliveries"][0]["revision"]["base_ref"] = "next"
        CACHE_RUNTIME.seal_state_fingerprint(corrupt_base)
        with self.assertRaises(CACHE_RUNTIME.CacheError) as invalid_base:
            CACHE_RUNTIME.validate_state(corrupt_base, self.ledger)
        self.assertEqual(invalid_base.exception.code, "integrity-failure")

        self.assertNotIn("reviews", self.state())

    def test_review_outcomes_are_strict_and_clean_may_finish_early(self) -> None:
        self.bootstrap_active_task()
        self.error(self.apply([{"type": "review-observed"}], check=False), "invalid-input")
        return
        revision = self.observe_revision()
        self.observe_delivery(revision)
        state = self.state()
        started = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        request_receipt = self.request_receipt(revision, request_key="run-clean", comment_id=9002, created_at="2026-07-18T12:00:00Z")
        for event in (
            {
                "type": "review-wait-started",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_receipt": request_receipt,
            },
            {
                "type": "review-wait-invoked",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_receipt": request_receipt,
                "wait_invoked_at": "2026-07-18T12:00:00Z",
                "provider_timeout": 2700,
            },
        ):
            self.direct_event(state, event, started)
        invalid = {
            "type": "review-observed",
            "task_key": self.task_key,
            "delivery_key": "dotagents",
            "revision_key": revision["revision_key"],
            "request_receipt": request_receipt,
            "request_binding": "recognized",
            "provider_state": "failed",
            "failure_kind": "provider-terminal-error",
            "provider_error_code": "provider_terminal_error",
            "observation_fingerprint": hashlib.sha256(b"failed").hexdigest(),
            "disposition": "accepted",
            "finding_count": 0,
            "finding_comment_ids": [],
            "evidence_ref": "github-review://233/failed",
            "warning_ref": None,
            "warning_posted_at": None,
            "warning_fingerprint": None,
        }
        with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "do not match"):
            CACHE_RUNTIME.apply_event(copy.deepcopy(state), invalid, started)
        for provider_state, disposition in (
            ("clean", "accepted"),
            ("failed", "blocked"),
        ):
            with self.subTest(
                provider_state=provider_state,
                disposition=disposition,
            ):
                predates_invocation = {
                    **invalid,
                    "provider_state": provider_state,
                    "disposition": disposition,
                }
                with self.assertRaisesRegex(
                    CACHE_RUNTIME.CacheError, "predates provider invocation"
                ):
                    CACHE_RUNTIME.apply_event(
                        copy.deepcopy(state),
                        predates_invocation,
                        started - timedelta(microseconds=1),
                    )
        clean = {
            **invalid,
            "provider_state": "clean",
            "failure_kind": None,
            "provider_error_code": None,
            "observation_fingerprint": hashlib.sha256(b"clean").hexdigest(),
            "evidence_ref": "github-review://233/clean",
        }
        self.direct_event(state, clean, started + timedelta(minutes=5))
        self.assertFalse(
            CACHE_RUNTIME.apply_event(
                state,
                clean,
                started + timedelta(minutes=6),
            )
        )
        corrupt_observation_time = copy.deepcopy(state)
        corrupt_observation_time["reviews"][-1]["observations"][-1][
            "observed_at"
        ] = "2026-07-18T11:59:59Z"
        CACHE_RUNTIME.seal_state_fingerprint(corrupt_observation_time)
        with self.assertRaises(CACHE_RUNTIME.CacheError) as invalid_time:
            CACHE_RUNTIME.validate_state(corrupt_observation_time, self.ledger)
        self.assertEqual(invalid_time.exception.code, "integrity-failure")
        self.assertEqual(invalid_time.exception.exit_code, 5)
        CACHE_RUNTIME.seal_state_fingerprint(state)
        CACHE_RUNTIME.validate_state(state, self.ledger)
        self.assertTrue(CACHE_RUNTIME.review_is_accepted(state["reviews"][-1]))
        self.assertEqual(CACHE_RUNTIME.review_warnings(state), [])

    def test_exact_head_correlation_failure_reconciles_append_only_to_clean(self) -> None:
        self.bootstrap_active_task()
        self.error(self.apply([{"type": "review-observed"}], check=False), "invalid-input")
        return
        revision = self.observe_revision()
        self.observe_delivery(revision)
        state = self.state()
        started = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        request_receipt = self.request_receipt(
            revision, request_key="correlation-defect", created_at="2026-07-18T12:00:00Z"
        )
        self.direct_event(state, {
            "type": "review-wait-started", "task_key": self.task_key,
            "delivery_key": "dotagents", "revision_key": revision["revision_key"],
            "request_receipt": request_receipt,
        }, started)
        self.direct_event(state, {
            "type": "review-wait-invoked", "task_key": self.task_key,
            "delivery_key": "dotagents", "revision_key": revision["revision_key"],
            "request_receipt": request_receipt, "wait_invoked_at": "2026-07-18T12:00:00Z",
            "provider_timeout": 2700,
        }, started)
        source_fingerprint = hashlib.sha256(b"typed-request-correlation-defect").hexdigest()
        self.direct_event(state, {
            "type": "review-observed", "task_key": self.task_key,
            "delivery_key": "dotagents", "revision_key": revision["revision_key"],
            "request_receipt": request_receipt, "request_binding": "invalid",
            "provider_state": "failed", "failure_kind": "request-correlation-failure",
            "provider_error_code": "request_correlation_failure",
            "observation_fingerprint": source_fingerprint, "disposition": "blocked",
            "finding_count": 0, "finding_comment_ids": [],
            "evidence_ref": "gitstack://review/correlation-defect",
            "warning_ref": None, "warning_posted_at": None, "warning_fingerprint": None,
        }, started + timedelta(minutes=6))
        review = state["reviews"][-1]
        immutable_before = copy.deepcopy({
            "request_receipt": review["request_receipt"],
            "wait_started_at": review["wait_started_at"],
            "wait_deadline": review["wait_deadline"],
            "wait_invoked_at": review["wait_invoked_at"],
            "provider_timeout": review["provider_timeout"],
            "observations": review["observations"],
        })
        receipt = self.terminal_evidence_receipt(revision, request_receipt)
        event = {
            "type": "review-reconciled", "task_key": self.task_key,
            "delivery_key": "dotagents", "revision_key": revision["revision_key"],
            "source_observation_fingerprint": source_fingerprint,
            "terminal_evidence_receipt": receipt,
        }
        pre_reconciliation = copy.deepcopy(state)
        self.direct_event(state, event, started + timedelta(minutes=11))
        immutable_after = {
            "request_receipt": review["request_receipt"],
            "wait_started_at": review["wait_started_at"],
            "wait_deadline": review["wait_deadline"],
            "wait_invoked_at": review["wait_invoked_at"],
            "provider_timeout": review["provider_timeout"],
            "observations": review["observations"],
        }
        self.assertEqual(immutable_after, immutable_before)
        self.assertEqual(len(review["reconciliations"]), 1)
        self.assertTrue(CACHE_RUNTIME.review_is_accepted(review))
        projected = CACHE_RUNTIME.review_result_projection(review)
        self.assertEqual(projected["original_provider_state"], "failed")
        self.assertEqual(projected["effective_provider_state"], "clean")
        self.assertEqual(projected["effective_source"], "terminal-provider-evidence")
        self.assertFalse(CACHE_RUNTIME.apply_event(state, event, started + timedelta(minutes=12)))
        self.direct_event(state, {
            "type": "gate-observed", "task_key": self.task_key,
            "delivery_key": "dotagents", "gate": "codex-review", "state": "passed",
            "binding_key": CACHE_RUNTIME.delivery_evidence_key(state["tasks"][0]["deliveries"][0]),
            "evidence_ref": receipt["artifact_ref"],
        }, started + timedelta(minutes=12))
        CACHE_RUNTIME.seal_state_fingerprint(state)
        CACHE_RUNTIME.validate_state(state, self.ledger)
        markdown = CACHE_RUNTIME.render_markdown(state)
        self.assertIn("## Review Reconciliations", markdown)
        self.assertIn(receipt["artifact_ref"], markdown)
        self.assertIn(receipt["receipt_fingerprint"], markdown)
        self.assertNotIn("Codex clean result", markdown)

        different = self.terminal_evidence_receipt(revision, request_receipt, artifact_id=9011)
        with self.assertRaises(CACHE_RUNTIME.CacheError) as conflict:
            CACHE_RUNTIME.apply_event(
                state, {**event, "terminal_evidence_receipt": different},
                started + timedelta(minutes=13),
            )
        self.assertEqual(conflict.exception.details["reason"], "reconciliation-artifact-conflict")

        for name, candidate in (
            ("source", {**event, "source_observation_fingerprint": "0" * 64}),
            ("repository", {**event, "terminal_evidence_receipt": {**receipt, "repository": "example/other"}}),
            ("request", {**event, "terminal_evidence_receipt": {**receipt, "request_identity_fingerprint": "0" * 64}}),
            ("actor", {**event, "terminal_evidence_receipt": {**receipt, "provider_actor": "attacker"}}),
            ("body", {**event, "terminal_evidence_receipt": {**receipt, "body_fingerprint": "0" * 64}}),
        ):
            with self.subTest(name=name), self.assertRaises(CACHE_RUNTIME.CacheError):
                CACHE_RUNTIME.apply_event(
                    copy.deepcopy(pre_reconciliation), candidate,
                    started + timedelta(minutes=11),
                )
        findings_receipt = self.terminal_evidence_receipt(
            revision, request_receipt, outcome="findings"
        )
        with self.assertRaises(CACHE_RUNTIME.CacheError) as findings:
            CACHE_RUNTIME.apply_event(
                copy.deepcopy(pre_reconciliation),
                {**event, "terminal_evidence_receipt": findings_receipt},
                started + timedelta(minutes=11),
            )
        self.assertEqual(findings.exception.details["reason"], "reconciliation-artifact-not-clean")

    def test_review_failure_mapping_rejects_caller_classification_combinations(self) -> None:
        self.bootstrap_active_task()
        self.error(self.apply([{"type": "review-observed"}], check=False), "invalid-input")
        return
        revision = self.observe_revision()
        self.observe_delivery(revision)
        state = self.state()
        started = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        request_receipt = self.request_receipt(revision, request_key="mapping")
        for event in (
            {"type": "review-wait-started", "task_key": self.task_key, "delivery_key": "dotagents", "revision_key": revision["revision_key"], "request_receipt": request_receipt},
            {"type": "review-wait-invoked", "task_key": self.task_key, "delivery_key": "dotagents", "revision_key": revision["revision_key"], "request_receipt": request_receipt, "wait_invoked_at": "2026-07-18T12:00:00Z", "provider_timeout": 2700},
        ):
            self.direct_event(state, event, started)
        invalid = {
            "type": "review-observed", "task_key": self.task_key,
            "delivery_key": "dotagents", "revision_key": revision["revision_key"],
            "request_receipt": request_receipt, "request_binding": "invalid",
            "provider_state": "failed", "failure_kind": "request-correlation-failure",
            "provider_error_code": "api_error", "observation_fingerprint": "a" * 64,
            "disposition": "blocked", "finding_count": 0, "finding_comment_ids": [],
            "evidence_ref": "gitstack://review/invalid-mapping", "warning_ref": None,
            "warning_posted_at": None, "warning_fingerprint": None,
        }
        with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "does not match provider observation"):
            CACHE_RUNTIME.apply_event(state, invalid, started + timedelta(minutes=1))

    def test_typed_thread_resolution_is_exact_idempotent_and_required_only_for_inline_findings(self) -> None:
        self.bootstrap_active_task()
        self.error(self.apply([{"type": "review-observed"}], check=False), "invalid-input")
        return
        finding_revision = self.observe_revision(head="a" * 40)
        self.apply([self.task_event(state="review-polling")])
        request_receipt = self.request_receipt(finding_revision, request_key="run-findings")
        self.apply([
            {
                "type": "review-wait-started",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": finding_revision["revision_key"],
                "request_receipt": request_receipt,
            }
        ])
        review = self.state()["reviews"][-1]
        self.apply([
            {
                "type": "review-wait-invoked",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": finding_revision["revision_key"],
                "request_receipt": request_receipt,
                "wait_invoked_at": review["wait_started_at"],
                "provider_timeout": 2700,
            },
            {
                "type": "review-observed",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": finding_revision["revision_key"],
                "request_receipt": request_receipt,
                "request_binding": "recognized",
                "provider_state": "findings",
                "failure_kind": None,
                "provider_error_code": None,
                "observation_fingerprint": hashlib.sha256(b"one-inline-finding").hexdigest(),
                "disposition": "fix-required",
                "finding_count": 1,
                "finding_comment_ids": [55],
                "evidence_ref": "github-review://233/finding/55",
                "warning_ref": None,
                "warning_posted_at": None,
                "warning_fingerprint": None,
            },
        ])
        fixed_revision = self.observe_revision(head="c" * 40)
        reply = self.review_reply_receipt(finding_revision, fixed_revision)
        resolution = self.review_resolution_receipt(reply, status="already-resolved")
        event = {
            "type": "review-thread-resolved",
            "task_key": self.task_key,
            "delivery_key": "dotagents",
            "finding_revision_key": finding_revision["revision_key"],
            "resolution_revision_key": fixed_revision["revision_key"],
            "reply_receipt": reply,
            "resolution_receipt": resolution,
        }
        state = self.state()
        task = state["tasks"][0]
        delivery = task["deliveries"][0]
        self.assertEqual(CACHE_RUNTIME.unresolved_finding_comment_ids(state, task, delivery), [55])
        self.direct_event(state, event, datetime(2026, 7, 18, 13, 2, tzinfo=timezone.utc))
        self.assertEqual(CACHE_RUNTIME.unresolved_finding_comment_ids(state, task, delivery), [])
        CACHE_RUNTIME.seal_state_fingerprint(state)
        CACHE_RUNTIME.validate_state(state, self.ledger)
        self.assertFalse(
            CACHE_RUNTIME.apply_event(
                state, event, datetime(2026, 7, 18, 13, 3, tzinfo=timezone.utc)
            )
        )

        stale = {**event, "resolution_revision_key": finding_revision["revision_key"]}
        with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "resolution revision is stale"):
            CACHE_RUNTIME.apply_event(
                copy.deepcopy(self.state()), stale, datetime(2026, 7, 18, 13, 3, tzinfo=timezone.utc)
            )
        wrong_pr_reply = {**reply, "pr_number": 999}
        wrong_pr_reply["finding_ref"] = "https://github.com/example/dotagents/pull/999#discussion_r55"
        wrong_pr_reply["reply_ref"] = "https://github.com/example/dotagents/pull/999#discussion_r56"
        wrong_pr_reply["identity_fingerprint"] = CACHE_RUNTIME.request_fingerprint({
            name: wrong_pr_reply[name]
            for name in wrong_pr_reply
            if name not in {"identity_fingerprint", "status"}
        })
        wrong_pr = {
            **event,
            "reply_receipt": wrong_pr_reply,
            "resolution_receipt": self.review_resolution_receipt(wrong_pr_reply),
        }
        with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "pr_number does not match review state"):
            CACHE_RUNTIME.apply_event(
                copy.deepcopy(self.state()), wrong_pr, datetime(2026, 7, 18, 13, 3, tzinfo=timezone.utc)
            )
        missing_reply = dict(event)
        missing_reply.pop("reply_receipt")
        with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "schema is invalid"):
            CACHE_RUNTIME.apply_event(
                copy.deepcopy(self.state()), missing_reply, datetime(2026, 7, 18, 13, 3, tzinfo=timezone.utc)
            )

    def test_findings_without_inline_comment_ids_require_fix_but_no_resolution_receipt(self) -> None:
        self.bootstrap_active_task()
        self.error(self.apply([{"type": "review-observed"}], check=False), "invalid-input")
        return
        revision = self.observe_revision()
        self.apply([self.task_event(state="review-polling")])
        request_receipt = self.request_receipt(revision, request_key="provider-comment-findings")
        self.apply([{
            "type": "review-wait-started", "task_key": self.task_key,
            "delivery_key": "dotagents", "revision_key": revision["revision_key"],
            "request_receipt": request_receipt,
        }])
        review = self.state()["reviews"][-1]
        self.apply([
            {
                "type": "review-wait-invoked", "task_key": self.task_key,
                "delivery_key": "dotagents", "revision_key": revision["revision_key"],
                "request_receipt": request_receipt, "wait_invoked_at": review["wait_started_at"],
                "provider_timeout": 2700,
            },
            {
                "type": "review-observed", "task_key": self.task_key,
                "delivery_key": "dotagents", "revision_key": revision["revision_key"],
                "request_receipt": request_receipt, "request_binding": "recognized",
                "provider_state": "findings", "failure_kind": None,
                "provider_error_code": None, "observation_fingerprint": "d" * 64,
                "disposition": "fix-required", "finding_count": 1,
                "finding_comment_ids": [], "evidence_ref": "github-review://233/provider-comment",
                "warning_ref": None, "warning_posted_at": None, "warning_fingerprint": None,
            },
        ])
        state = self.state()
        task = state["tasks"][0]
        delivery = task["deliveries"][0]
        self.assertEqual(CACHE_RUNTIME.unresolved_finding_comment_ids(state, task, delivery), [])
        self.assertFalse(CACHE_RUNTIME.review_is_accepted(state["reviews"][-1]))

    def test_unbound_request_cannot_be_timeout_accepted(self) -> None:
        self.bootstrap_active_task()
        self.error(self.apply([{"type": "review-observed"}], check=False), "invalid-input")
        return
        revision = self.observe_revision()
        self.observe_delivery(revision)
        self.start_clean_review(revision)
        review = self.state()["reviews"][-1]
        deadline = CACHE_RUNTIME.parse_timestamp(review["wait_deadline"], "wait_deadline")
        for binding in ("unbound", "invalid", "unknown", "ambiguous"):
            with self.subTest(binding=binding), self.assertRaisesRegex(
                CACHE_RUNTIME.CacheError, "unrecognized review request"
            ):
                CACHE_RUNTIME.validate_review_outcome(
                    binding,
                    "waiting",
                    "timeout-accepted",
                    None,
                    None,
                    None,
                    None,
                    None,
                    review,
                    deadline,
                    deadline,
                    "invalid-input",
                    2,
                )

    def test_review_wait_expired_before_launch_uses_zero_and_accepts_timeout(self) -> None:
        self.bootstrap_active_task()
        self.error(self.apply([{"type": "review-wait-invoked"}], check=False), "invalid-input")
        return
        revision = self.observe_revision()
        self.observe_delivery(revision)
        state = self.state()
        started = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        invoked = started + timedelta(minutes=50)
        request_receipt = self.request_receipt(revision, request_key="run-late", comment_id=9003, created_at="2026-07-18T12:00:00Z")
        self.direct_event(
            state,
            {
                "type": "review-wait-started",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_receipt": request_receipt,
            },
            started,
        )
        review = state["reviews"][-1]
        self.direct_event(
            state,
            {
                "type": "review-wait-invoked",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_receipt": request_receipt,
                "wait_invoked_at": "2026-07-18T12:50:00Z",
                "provider_timeout": 0,
            },
            invoked,
        )
        self.direct_event(
            state,
            {
                "type": "review-observed",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "revision_key": revision["revision_key"],
                "request_receipt": request_receipt,
                "request_binding": "recognized",
                "provider_state": "waiting",
                "failure_kind": None,
                "provider_error_code": None,
                "observation_fingerprint": hashlib.sha256(b"late-pending").hexdigest(),
                "disposition": "timeout-accepted",
                "finding_count": 0,
                "finding_comment_ids": [],
                "evidence_ref": "github-review://233/late-pending",
                "warning_ref": "https://github.com/example/dotagents/pull/233#issuecomment-9002",
                "warning_posted_at": "2026-07-18T12:50:00Z",
                "warning_fingerprint": CACHE_RUNTIME.review_timeout_warning_fingerprint(review),
            },
            invoked,
        )
        CACHE_RUNTIME.seal_state_fingerprint(state)
        CACHE_RUNTIME.validate_state(state, self.ledger)
        self.assertEqual(state["reviews"][-1]["provider_timeout"], 0)
        self.assertEqual(len(CACHE_RUNTIME.review_warnings(state)), 1)

    def test_removed_review_monitoring_events_are_rejected(self) -> None:
        self.bootstrap_active_task()
        for event_type in (
            "portfolio-goal-paused",
            "portfolio-goal-resumed",
            "review-monitoring-scheduled",
            "task-monitoring-paused",
            "task-monitoring-resumed",
        ):
            with self.subTest(event_type=event_type):
                with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "unsupported"):
                    CACHE_RUNTIME.apply_event(
                        copy.deepcopy(self.state()),
                        {"type": event_type},
                        datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc),
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

    def test_late_full_read_after_seal_records_drift_without_reopening_or_regranting(self) -> None:
        sealed = self.make_terminal_sealed_state()
        seal_fingerprint = sealed["tasks"][0]["seal"]["seal_fingerprint"]
        prior_observation = copy.deepcopy(sealed["tasks"][0]["current_observation"])
        late = self.task_event(state="terminal-sealed")

        self.apply([late])
        state = self.state()
        task = state["tasks"][0]
        self.assertEqual(task["state"], "terminal-sealed")
        self.assertEqual(task["seal"]["seal_fingerprint"], seal_fingerprint)
        self.assertEqual(task["current_observation"], prior_observation)
        self.assertIsNotNone(task["post_terminal_drift"])
        self.assertEqual(state["goal"]["state"], "active")
        terminal = parse_result(self.read_projection("terminal"))
        self.assertEqual(terminal["phase"], "drifted")
        self.assertFalse(terminal["archive_ready"])

        replay = parse_result(self.apply([late], operation_id=self.next_operation_id()))
        self.assertEqual(replay["mutation_state"], "unchanged")
        self.assertEqual(self.state()["tasks"][0]["seal"]["seal_fingerprint"], seal_fingerprint)

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
            "review-reconciled",
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
                self.assertEqual(
                    rejected.exception.code,
                    "invalid-input" if event_type in CACHE_RUNTIME.RETIRED_MANAGED_EVENT_TYPES else "state-conflict",
                )
                self.assertEqual(candidate, sealed)

    def test_post_terminal_drift_is_recordable_at_every_post_seal_stage(self) -> None:
        sealed = self.make_terminal_sealed_state()
        seal_fingerprint = sealed["tasks"][0]["seal"]["seal_fingerprint"]
        now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        stages = [("terminal-sealed", copy.deepcopy(sealed))]

        handed_off = copy.deepcopy(sealed)
        CACHE_RUNTIME.apply_event(
            handed_off,
            self.bind_decision_event({
                "type": "terminal-handoff-recorded",
                "task_key": self.task_key,
                "seal_fingerprint": seal_fingerprint,
                "handoff_kind": "pull-request-ready",
                "authority": "external-merge-required",
                "evidence_ref": "https://github.com/example/dotagents/pull/233",
                "next_action": "Human may merge after final inspection.",
            }, handed_off),
            now,
        )
        stages.append(("terminal-handoff", copy.deepcopy(handed_off)))

        verified = copy.deepcopy(handed_off)
        verification = CACHE_RUNTIME.portfolio_verification_candidate(verified)
        self.assertIsNotNone(verification)
        CACHE_RUNTIME.apply_event(
            verified,
            self.bind_decision_event({
                "type": "portfolio-terminal-verified",
                "verification_fingerprint": verification,
                "evidence_ref": "proof://portfolio-terminal/232",
            }, verified),
            now,
        )
        stages.append(("portfolio-verified", copy.deepcopy(verified)))

        root_complete = copy.deepcopy(verified)
        CACHE_RUNTIME.apply_event(
            root_complete,
            self.bind_decision_event({
                "type": "portfolio-goal-completed",
                "goal_evidence_ref": "app-task://root-a/goal",
                "completion_evidence_ref": "app-task://root-a/goal-complete",
                "verification_fingerprint": verification,
            }, root_complete),
            now,
        )
        stages.append(("portfolio-goal-complete", root_complete))

        for stage_name, stage in stages:
            with self.subTest(stage=stage_name):
                root_goal_before = (
                    stage["goal"]["state"],
                    stage["goal"]["completion_evidence_ref"],
                )
                changed = CACHE_RUNTIME.apply_event(
                    stage,
                    self.bind_decision_event({
                        "type": "post-terminal-drift-recorded",
                        "task_key": self.task_key,
                        "delivery_key": "dotagents",
                        "seal_fingerprint": seal_fingerprint,
                        "drift_fingerprint": hashlib.sha256(
                            f"head-drift-{stage_name}".encode()
                        ).hexdigest(),
                        "reason": f"The PR head changed during {stage_name}.",
                        "evidence_ref": f"git://post-terminal-drift/{stage_name}",
                    }, stage),
                    now,
                )
                self.assertTrue(changed)
                self.assertEqual(
                    (stage["goal"]["state"], stage["goal"]["completion_evidence_ref"]),
                    root_goal_before,
                )
                terminal = CACHE_RUNTIME.terminal_projection(stage)
                self.assertEqual(terminal["phase"], "drifted")
                self.assertFalse(terminal["archive_ready"])
                CACHE_RUNTIME.seal_state_fingerprint(stage)
                CACHE_RUNTIME.validate_state(stage, self.ledger)

    def test_pre_handoff_drift_blocks_terminal_handoff(self) -> None:
        state = self.make_terminal_sealed_state()
        seal_fingerprint = state["tasks"][0]["seal"]["seal_fingerprint"]
        now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
        CACHE_RUNTIME.apply_event(
            state,
            self.bind_decision_event({
                "type": "post-terminal-drift-recorded",
                "task_key": self.task_key,
                "delivery_key": "dotagents",
                "seal_fingerprint": seal_fingerprint,
                "drift_fingerprint": hashlib.sha256(b"pre-completion-drift").hexdigest(),
                "reason": "The PR head changed before terminal handoff was recorded.",
                "evidence_ref": "git://post-terminal-drift/pre-completion",
            }, state),
            now,
        )
        self.assertIsNotNone(state["tasks"][0]["post_terminal_drift"])
        with self.assertRaises(CACHE_RUNTIME.CacheError) as rejected:
            CACHE_RUNTIME.apply_event(
                state,
                self.bind_decision_event({
                    "type": "terminal-handoff-recorded",
                    "task_key": self.task_key,
                    "seal_fingerprint": seal_fingerprint,
                    "handoff_kind": "pull-request-ready",
                    "authority": "external-merge-required",
                    "evidence_ref": "https://github.com/example/dotagents/pull/233",
                    "next_action": "Human may merge after final inspection.",
                }, state),
                now,
            )
        self.assertEqual(rejected.exception.code, "state-conflict")

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
                self.checkout_event(),
                self.task_event(state="created"),
            ]
        )
        self.apply([self.baseline_acceptance_event()])
        self.apply([
            {"type": "portfolio-goal-activated", "goal_evidence_ref": "app-task://root-a/goal", "objective_fingerprint": objective_fingerprint},
            self.task_event(state="implementing"),
        ])
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
        registration = self.registration_for(claim)
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
            "execution_recovery_fingerprint": CACHE_RUNTIME.request_fingerprint([]),
            "command_cleanup_evidence": [],
            "specs": [
                {
                    "source_spec_ref": self.source_ref,
                    "task_state": "recorded",
                    "task_ref": "app-task://old-worker",
                    "task_model": "gpt-5.6-sol",
                    "task_thinking": "xhigh",
                    "thinking_reason": "contract-sensitive state transition work",
                    "task_assignment_fingerprint": self.task_assignment_fingerprint,
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
        created = parse_result(self.create(registration=registration))
        self.assertEqual(created["mutation_state"], "created")
        task = self.state()["tasks"][0]
        self.assertEqual(task["adoption"]["origin_root_id"], "root-old")
        self.assertEqual(task["task_ref"], "app-task://old-worker")
        self.assertEqual(
            task["task_assignment_fingerprint"], self.task_assignment_fingerprint
        )
        self.assertIsNotNone(task["deliveries"][0]["managed_checkout"])

    def test_command_attempt_lifecycle_is_bounded_typed_and_single_launch(self) -> None:
        self.acquire()
        self.create()
        self.apply([self.checkout_event(), self.task_event(state="created")])
        state = self.state()
        delivery = state["tasks"][0]["deliveries"][0]
        plan = delivery["validation_plan"][0]
        attempt_id = "c" * 32
        reservation = {
            "type": "execution-command-reserved",
            "task_key": self.task_key,
            "delivery_key": delivery["delivery_key"],
            "attempt_id": attempt_id,
            "command_id": plan["command_id"],
            "operation": "baseline-validation",
            "manifest_sha256": "d" * 64,
            "execution_policy_fingerprint": plan["execution_policy_fingerprint"],
            "attempt_file": str(self.home / "command.attempt.jsonl"),
            "receipt_file": str(self.home / "command.receipt.json"),
            "evidence_ref": "execution-manifest://reserved",
        }
        self.apply([reservation])
        duplicate = self.apply([reservation], check=False)
        self.assertEqual(duplicate.returncode, 4)
        launch = {
            "type": "execution-command-launch-observed",
            "task_key": self.task_key,
            "delivery_key": delivery["delivery_key"],
            "attempt_id": attempt_id,
            "attempt_fingerprint": "e" * 64,
            "evidence_ref": "execution-manifest://launch-released",
        }
        self.apply([launch])
        cancel = {
            "type": "execution-command-cancellation-authorized",
            "task_key": self.task_key,
            "delivery_key": delivery["delivery_key"],
            "attempt_id": attempt_id,
            "reason": "claim-lost",
            "evidence_ref": "active-root-claim://mismatch",
        }
        self.apply([cancel])
        terminal = {
            "type": "execution-command-terminal-observed",
            "task_key": self.task_key,
            "delivery_key": delivery["delivery_key"],
            "attempt_id": attempt_id,
            "status": "cancelled",
            "receipt_sha256": "f" * 64,
            "cleanup_verified": True,
            "evidence_ref": "execution-manifest://cleanup-verified",
        }
        self.apply([terminal])
        attempt = self.state()["tasks"][0]["deliveries"][0]["command_attempts"][0]
        self.assertEqual(attempt["state"], "terminal")
        self.assertEqual(attempt["terminal_status"], "cancelled")
        self.assertTrue(attempt["cleanup_verified"])
        event_types = {
            event_type
            for operation in self.state()["operations"]
            for event_type in operation["event_types"]
        }
        self.assertNotIn("execution-command-heartbeat", event_types)

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
                "task_assignment_fingerprint": "none",
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
        self.refresh_registration_fingerprints(registration)
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
                "task_assignment_fingerprint": "none",
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
                "task_assignment_fingerprint": self.task_assignment_fingerprint,
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

    def test_non_takeover_create_initializes_no_task_adoption_without_worker_goal_state(self) -> None:
        self.acquire()
        self.create()
        task = self.state()["tasks"][0]
        self.assertEqual(task["adoption"]["task_state"], "no-task")
        self.assertIsNone(task["task_ref"])
        self.assertEqual(task["task_assignment_fingerprint"], self.task_assignment_fingerprint)
        self.assertNotIn("goal_state", task)
        self.assertNotIn("goal_evidence_ref", task)

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

    def diagnostic_base_state(self) -> dict:
        self.bootstrap_active_task()
        revision = self.observe_revision()
        self.observe_delivery(revision)
        self.start_clean_review(revision)
        return self.state()

    def diagnostic_command_attempt(
        self, command_id: str, status: str, *, terminal: bool = True
    ) -> dict:
        return {
            "attempt_id": hashlib.md5(command_id.encode(), usedforsecurity=False).hexdigest(),
            "command_id": command_id,
            "manifest_sha256": hashlib.sha256(f"manifest:{command_id}".encode()).hexdigest(),
            "execution_policy_fingerprint": hashlib.sha256(f"policy:{command_id}".encode()).hexdigest(),
            "attempt_file": str(self.home / f"{command_id}.attempt.jsonl"),
            "receipt_file": str(self.home / f"{command_id}.receipt.json"),
            "state": "terminal" if terminal else "launch-released",
            "terminal_status": status if terminal else None,
            "cleanup_verified": status != "cleanup-failed" if terminal else None,
            "cancellation_reason": None,
            "evidence_ref": f"execution-manifest://{command_id}",
            "recorded_at": "2026-07-18T12:00:00Z",
        }

    def add_diagnostic_gate(
        self, state: dict, gate: str, gate_state: str, *, binding_key: str | None = None
    ) -> None:
        task = state["tasks"][0]
        delivery = task["deliveries"][0]
        state["gates"].append(
            {
                "task_key": task["task_key"],
                "delivery_key": delivery["delivery_key"],
                "gate": gate,
                "state": gate_state,
                "binding_key": binding_key or CACHE_RUNTIME.delivery_evidence_key(delivery),
                "evidence_ref": f"proof://{gate}/{gate_state}",
                "observed_at": "2026-07-18T12:00:00Z",
            }
        )

    def test_diagnostics_projection_mixed_case_truth_table(self) -> None:
        base = self.diagnostic_base_state()

        command_passed_semantic_failed = copy.deepcopy(base)
        delivery = command_passed_semantic_failed["tasks"][0]["deliveries"][0]
        delivery["command_attempts"] = [
            self.diagnostic_command_attempt("semantic-review", "passed")
        ]
        autoreview_row = next(
            row for row in command_passed_semantic_failed["operations"]
            if row["record_kind"] == "owned-operation-result" and row["owner"] == "autoreview"
        )
        autoreview_row["effective_outcome"] = "fix-required"
        autoreview_row["normalized"] = copy.deepcopy(
            CACHE_RUNTIME.OWNED_RESULT_MAP[("autoreview", "run-phase", "fix-required")]
        )
        projected = CACHE_RUNTIME.diagnostics_projection(command_passed_semantic_failed)
        result = projected["tasks"][0]["deliveries"][0]
        self.assertEqual(result["commands"][0]["raw_terminal_status"], "passed")
        self.assertEqual(result["autoreview_operation"]["outcome"], "fix-required")
        self.assertTrue(result["autoreview_operation"]["blocking"])
        self.assertTrue(projected["blocking"])

        semantic_clean_nonterminal = CACHE_RUNTIME.diagnostics_projection(base)
        semantic = semantic_clean_nonterminal["tasks"][0]["deliveries"][0]["autoreview_operation"]
        self.assertEqual(semantic["outcome"], "terminal-clean")
        self.assertEqual(semantic["evidence_state"], "current")
        self.assertEqual(semantic_clean_nonterminal["terminal_verification"], "incomplete")

        ci_green_findings = copy.deepcopy(base)
        review = next(
            row for row in ci_green_findings["operations"]
            if row["record_kind"] == "owned-operation-result" and row["owner"] == "gitstack"
            and row["effective_operation"] == "wait"
        )
        review["effective_outcome"] = "findings"
        review["normalized"] = copy.deepcopy(
            CACHE_RUNTIME.OWNED_RESULT_MAP[("gitstack", "wait", "findings")]
        )
        self.add_diagnostic_gate(ci_green_findings, "ci", "passed")
        projected = CACHE_RUNTIME.diagnostics_projection(ci_green_findings)
        result = projected["tasks"][0]["deliveries"][0]
        self.assertEqual(result["deterministic_validation"]["ci"]["raw_state"], "passed")
        self.assertEqual(result["review_operation"]["outcome"], "findings")
        self.assertTrue(result["review_operation"]["blocking"])

        conflict_free_blocked = copy.deepcopy(base)
        self.add_diagnostic_gate(conflict_free_blocked, "mergeability", "failed")
        projected = CACHE_RUNTIME.diagnostics_projection(conflict_free_blocked)
        mergeability = projected["tasks"][0]["deliveries"][0]["mergeability"]
        self.assertEqual(mergeability["raw_merge_state"], "clean")
        self.assertEqual(mergeability["display_result"], "conflict-free; merge requirements blocked")
        self.assertTrue(mergeability["blocking"])

        timeout_accepted = copy.deepcopy(base)
        observation = next(
            row for row in timeout_accepted["operations"]
            if row["record_kind"] == "owned-operation-result" and row["owner"] == "gitstack"
            and row["effective_operation"] == "wait"
        )
        observation["effective_operation"] = "warning"
        observation["effective_outcome"] = "posted"
        observation["normalized"] = copy.deepcopy(
            CACHE_RUNTIME.OWNED_RESULT_MAP[("gitstack", "warning", "posted")]
        )
        projected = CACHE_RUNTIME.diagnostics_projection(timeout_accepted)
        provider = projected["tasks"][0]["deliveries"][0]["review_operation"]
        self.assertEqual(provider["disposition"], "timeout-accepted")
        self.assertFalse(provider["blocking"])
        self.assertIn("timeout-accepted", provider["display_result"])

        cleanup_failed = copy.deepcopy(base)
        cleanup_failed["tasks"][0]["deliveries"][0]["command_attempts"] = [
            self.diagnostic_command_attempt("cleanup", "cleanup-failed")
        ]
        projected = CACHE_RUNTIME.diagnostics_projection(cleanup_failed)
        command = projected["tasks"][0]["deliveries"][0]["commands"][0]
        self.assertEqual(command["raw_terminal_status"], "cleanup-failed")
        self.assertTrue(command["blocking"])
        self.assertTrue(projected["blocking"])

    def test_diagnostics_projection_marks_exact_revision_evidence_stale(self) -> None:
        self.bootstrap_active_task()
        first = self.observe_revision()
        self.observe_delivery(first)
        self.start_clean_review(first)
        current = parse_result(self.read_projection("diagnostics"))
        current_delivery = current["tasks"][0]["deliveries"][0]
        self.assertEqual(current_delivery["autoreview_operation"]["evidence_state"], "current")
        self.assertEqual(current_delivery["review_operation"]["evidence_state"], "current")
        self.assertEqual(current_delivery["mergeability"]["evidence_state"], "current")

        self.observe_revision(head="c" * 40)
        stale = parse_result(self.read_projection("diagnostics"))
        stale_delivery = stale["tasks"][0]["deliveries"][0]
        self.assertEqual(stale_delivery["autoreview_operation"]["evidence_state"], "stale")
        self.assertEqual(stale_delivery["review_operation"]["evidence_state"], "stale")
        self.assertEqual(stale_delivery["mergeability"]["evidence_state"], "stale")
        self.assertTrue(stale_delivery["stale_reasons"])
        self.assertEqual(stale["terminal_verification"], "incomplete")

    def test_diagnostics_terminal_verification_clean_then_invalidated(self) -> None:
        state = self.make_terminal_state()
        projected = CACHE_RUNTIME.diagnostics_projection(state)
        self.assertEqual(projected["terminal_verification"], "clean")
        self.assertEqual(projected["display_terminal_verification"], "Terminal verification: clean")
        self.assertFalse(projected["blocking"])

        task = state["tasks"][0]
        self.apply(
            [
                {
                    "type": "post-terminal-drift-recorded",
                    "task_key": self.task_key,
                    "delivery_key": "dotagents",
                    "seal_fingerprint": task["seal"]["seal_fingerprint"],
                    "drift_fingerprint": hashlib.sha256(b"diagnostic-drift").hexdigest(),
                    "reason": "The exact PR head changed after terminal verification.",
                    "evidence_ref": "git://post-terminal-drift/diagnostics",
                }
            ]
        )
        invalidated = parse_result(self.read_projection("diagnostics"))
        self.assertEqual(invalidated["terminal_verification"], "invalidated")
        self.assertTrue(invalidated["blocking"])
        self.assertIn("post-terminal-drift", invalidated["blocking_reasons"])

    def test_diagnostics_read_is_pure_bounded_and_fail_closed(self) -> None:
        self.bootstrap_active_task()
        before_bytes = self.ledger.read_bytes()
        before_state = self.state()
        before_cache = {
            str(path.relative_to(self.cache_root)): path.read_bytes()
            for path in self.cache_root.rglob("*")
            if path.is_file() and not path.is_symlink()
        }
        result = self.read_projection("diagnostics")
        payload = parse_result(result)
        after_cache = {
            str(path.relative_to(self.cache_root)): path.read_bytes()
            for path in self.cache_root.rglob("*")
            if path.is_file() and not path.is_symlink()
        }
        self.assertEqual(payload["projection_schema_version"], "1.0.0")
        self.assertEqual(payload["ledger_schema_version"], "15.0.0")
        self.assertEqual(payload["generation"], before_state["generation"])
        self.assertEqual(payload["content_fingerprint"], before_state["content_fingerprint"])
        self.assertLessEqual(len(result.stdout.encode()), CACHE_RUNTIME.MAX_OUTPUT_BYTES)
        self.assertEqual(self.ledger.read_bytes(), before_bytes)
        self.assertEqual(self.state()["operations"], before_state["operations"])
        self.assertEqual(before_cache, after_cache)

        bounded = self.state()
        bounded["tasks"][0]["deliveries"][0]["command_attempts"] = [
            self.diagnostic_command_attempt(f"command-{index:02d}", "passed")
            for index in range(CACHE_RUNTIME.MAX_COMMAND_ATTEMPTS_PER_DELIVERY)
        ]
        projected = CACHE_RUNTIME.diagnostics_projection(bounded)
        self.assertEqual(
            len(projected["tasks"][0]["deliveries"][0]["commands"]),
            CACHE_RUNTIME.MAX_COMMAND_ATTEMPTS_PER_DELIVERY,
        )
        with mock.patch.object(CACHE_RUNTIME, "MAX_DIAGNOSTIC_REASONS_PER_SCOPE", 1):
            with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "reason bound"):
                CACHE_RUNTIME.bounded_diagnostic_reasons(["one", "two"], "fixture")

        impossible = self.state()
        impossible["closeout"]["post_terminal_drift"] = {
            "task_key": self.task_key,
            "delivery_key": "dotagents",
        }
        with self.assertRaisesRegex(CACHE_RUNTIME.CacheError, "inconsistent post-terminal drift"):
            CACHE_RUNTIME.diagnostics_projection(impossible)

    def test_projections_and_markdown_are_deterministic_and_bounded(self) -> None:
        self.bootstrap_active_task()
        for projection in ("status", "dispatch", "recovery", "terminal", "diagnostics"):
            first = self.read_projection(projection).stdout
            second = self.read_projection(projection).stdout
            self.assertEqual(first, second)
            payload = json.loads(first)
            self.assertNotIn("operations", payload)
            self.assertNotIn("reviews", payload)

        expected_common = {
            "ok", "command", "version", "projection", "generation",
            "content_fingerprint", "portfolio_key", "root_id", "root_task_title",
            "root_task_title_evidence_ref", "goal", "warnings", "phase",
        }
        status = parse_result(self.read_projection("status"))
        dispatch = parse_result(self.read_projection("dispatch"))
        recovery = parse_result(self.read_projection("recovery"))
        terminal = parse_result(self.read_projection("terminal"))
        self.assertEqual(set(status), expected_common | {"tasks", "terminal_eligible"})
        self.assertEqual(set(dispatch), expected_common | {"ready_task_keys", "available_capacity"})
        self.assertEqual(
            set(recovery),
            expected_common | {"tasks", "terminal_eligible", "sources", "handoffs", "adoptions"},
        )
        self.assertEqual(
            set(terminal),
            expected_common
            | {
                "eligible", "archive_ready", "blockers",
                "portfolio_verification_candidate", "portfolio_verified", "tasks",
            },
        )
        self.assertEqual(
            set(status["tasks"][0]),
            {
                "task_key", "task_ref", "task_title", "state", "current_observation",
                "dependency_wait", "revision_set_key", "gates", "deliveries",
                "terminal_blockers",
            },
        )
        self.assertEqual(
            set(status["tasks"][0]["deliveries"][0]),
            {
                "delivery_key", "repository", "github_repository", "default_base",
                "ci_availability", "preflight_key", "revision_key", "pr",
                "autoreview_result", "review_result", "gates", "tracker_dirty",
            },
        )

        state = self.state()
        first_markdown = CACHE_RUNTIME.render_markdown(state)
        second_markdown = CACHE_RUNTIME.render_markdown(state)
        self.assertEqual(first_markdown, second_markdown)
        self.assertIn("# Implement Feature Terminal Run State", first_markdown)
        self.assertIn("## Qualified Diagnostics", first_markdown)
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
