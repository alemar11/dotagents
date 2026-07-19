"""Deterministic comparison and promotion decision for completed pilot runs."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from code_wiki.pilot.common import hash_path, write_json, write_text_atomic
from code_wiki.pilot.contracts import load_graph
from code_wiki.pilot.runtime import ExecutionError, TokenUsage, parse_terminal_usage
from code_wiki.pilot.provenance import (
    load_provenance_key,
    manifest_evidence_sha256,
    verify_receipt,
)
from code_wiki.pilot.runner import RUN_SCHEMA_VERSION, skill_root
from code_wiki.version import VERSION


PROMOTION_STATUSES = {"promote", "revise", "reject", "inconclusive"}
USAGE_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "uncached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_model_tokens",
)


def _read_manifest(path: Path, expected_mode: str) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"cannot read {expected_mode} manifest: {exc}"]
    if not isinstance(value, dict):
        return {}, [f"{expected_mode} manifest must be an object"]
    if value.get("schema_version") != RUN_SCHEMA_VERSION:
        errors.append(f"{expected_mode} manifest schema_version is invalid")
    if value.get("mode") != expected_mode:
        errors.append(f"{expected_mode} manifest mode is invalid")

    identity = value.get("identity")
    if not isinstance(identity, dict):
        errors.append(f"{expected_mode} identity must be an object")
        identity = {}
    expected_graph = load_graph(skill_root(), expected_mode)
    if identity.get("graph_sha256") != expected_graph.graph_sha256:
        errors.append(f"{expected_mode} graph hash does not match the shipped contract")
    if identity.get("node_hashes") != expected_graph.node_hashes:
        errors.append(f"{expected_mode} node hashes do not match the shipped contracts")
    if identity.get("code_wiki_cli_version") != VERSION:
        errors.append(f"{expected_mode} Code Wiki CLI version is not current")
    for field in (
        "source_commit",
        "model",
        "reasoning_effort",
        "codex_cli_version",
        "code_wiki_cli_version",
        "graph_sha256",
        "execution_evidence",
    ):
        if not isinstance(identity.get(field), str) or not identity[field]:
            errors.append(f"{expected_mode} identity field {field} is missing")
    if identity.get("execution_evidence") not in {"live", "fixture"}:
        errors.append(f"{expected_mode} execution_evidence is invalid")

    output = value.get("output")
    if not isinstance(output, dict):
        errors.append(f"{expected_mode} output must be an object")
        output = {}
    expected_root = path.parent.resolve()
    def manifest_path(raw: Any, field: str, sentinel: Path) -> Path:
        if not isinstance(raw, str) or not raw:
            errors.append(f"{expected_mode} output path {field} is invalid")
            return sentinel
        try:
            return Path(raw).expanduser().resolve()
        except (OSError, RuntimeError, ValueError):
            errors.append(f"{expected_mode} output path {field} is invalid")
            return sentinel

    recorded_root = manifest_path(output.get("root"), "root", expected_root / ".invalid-root")
    wiki_path = manifest_path(output.get("wiki_path"), "wiki_path", expected_root / ".invalid-wiki")
    if recorded_root != expected_root:
        errors.append(f"{expected_mode} output root does not match manifest location")
    if wiki_path != expected_root / "wiki":
        errors.append(f"{expected_mode} wiki path is not the canonical output wiki")
    recorded_manifest = manifest_path(
        output.get("manifest_path"),
        "manifest_path",
        expected_root / ".invalid-manifest",
    )
    if recorded_manifest != path:
        errors.append(f"{expected_mode} manifest path is not self-consistent")
    provenance_path = expected_root / "artifacts" / "execution-provenance.json"
    recorded_provenance = manifest_path(
        output.get("provenance_path"),
        "provenance_path",
        expected_root / ".invalid-provenance",
    )
    if recorded_provenance != provenance_path:
        errors.append(f"{expected_mode} provenance path is not canonical")
    provenance: dict[str, Any] = {}
    if not provenance_path.is_file():
        errors.append(f"{expected_mode} execution provenance is missing")
    else:
        provenance_hash = hash_path(provenance_path)
        if output.get("provenance_sha256") != provenance_hash:
            errors.append(f"{expected_mode} execution provenance hash is invalid")
        try:
            raw_provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{expected_mode} execution provenance JSON is invalid: {exc}")
        else:
            if isinstance(raw_provenance, dict):
                provenance = raw_provenance
            else:
                errors.append(f"{expected_mode} execution provenance must be an object")
    provenance_identity = {
        "run_id": value.get("run_id"),
        "execution_evidence": identity.get("execution_evidence"),
        "source_commit": identity.get("source_commit"),
        "graph_sha256": identity.get("graph_sha256"),
        "model": identity.get("model"),
        "reasoning_effort": identity.get("reasoning_effort"),
        "codex_cli_version": identity.get("codex_cli_version"),
        "code_wiki_cli_version": identity.get("code_wiki_cli_version"),
    }
    if provenance.get("schema_version") != 1:
        errors.append(f"{expected_mode} execution provenance schema_version is invalid")
    for field, expected_value in provenance_identity.items():
        if provenance.get(field) != expected_value:
            errors.append(f"{expected_mode} execution provenance field {field} is inconsistent")
    if provenance.get("manifest_evidence_sha256") != manifest_evidence_sha256(value):
        errors.append(f"{expected_mode} execution provenance does not bind the run manifest")
    validated_execution_evidence: str | None = None
    if provenance.get("execution_evidence") == "live":
        try:
            signing_key = load_provenance_key()
        except RuntimeError as exc:
            errors.append(f"{expected_mode} live execution provenance cannot be verified: {exc}")
        else:
            if provenance.get("signature_algorithm") != "hmac-sha256-v1":
                errors.append(f"{expected_mode} live execution signature algorithm is invalid")
            elif provenance.get("signing_key_sha256") != hashlib.sha256(signing_key).hexdigest():
                errors.append(f"{expected_mode} live execution signing key does not match")
            elif not verify_receipt(provenance, signing_key):
                errors.append(f"{expected_mode} live execution signature is invalid")
            else:
                validated_execution_evidence = "live"
    elif provenance.get("execution_evidence") == "fixture":
        if (
            provenance.get("signature_algorithm") != "none"
            or provenance.get("signing_key_sha256") is not None
            or provenance.get("signature") is not None
        ):
            errors.append(f"{expected_mode} fixture execution provenance must be unsigned")
        else:
            validated_execution_evidence = "fixture"
    else:
        errors.append(f"{expected_mode} execution provenance type is invalid")
    value["_validated_execution_evidence"] = validated_execution_evidence
    if not wiki_path.is_dir():
        errors.append(f"{expected_mode} wiki directory is missing")
    else:
        expected_hash = output.get("wiki_sha256")
        if not isinstance(expected_hash, str) or hash_path(wiki_path) != expected_hash:
            errors.append(f"{expected_mode} wiki artifact hash is invalid")

    source = value.get("source")
    if not isinstance(source, dict):
        errors.append(f"{expected_mode} source evidence must be an object")
        source = {}
    for field in ("original_checkout_unchanged", "source_mutation"):
        if not isinstance(source.get(field), bool):
            errors.append(f"{expected_mode} source field {field} must be boolean")
    for field in (
        "original_head_before",
        "original_head_after",
        "original_status_before",
        "original_status_after",
        "snapshot_tree_sha256_before",
        "snapshot_tree_sha256_after",
    ):
        if not isinstance(source.get(field), str):
            errors.append(f"{expected_mode} source field {field} must be a string")
    if source.get("original_checkout_unchanged") is True and (
        source.get("original_head_before") != source.get("original_head_after")
        or source.get("original_status_before") != source.get("original_status_after")
    ):
        errors.append(f"{expected_mode} original-checkout proof is inconsistent")
    if source.get("source_mutation") is False and (
        source.get("snapshot_tree_sha256_before") != source.get("snapshot_tree_sha256_after")
    ):
        errors.append(f"{expected_mode} snapshot mutation proof is inconsistent")

    metrics = value.get("metrics")
    if not isinstance(metrics, dict):
        errors.append(f"{expected_mode} metrics must be an object")
        metrics = {}
    for bucket_name in ("generation", "reader"):
        bucket = metrics.get(bucket_name)
        if not isinstance(bucket, dict):
            errors.append(f"{expected_mode} {bucket_name} metrics must be an object")
            continue
        for field in (*USAGE_FIELDS, "model_call_count", "failed_terminal_calls", "wall_time_ms"):
            raw = bucket.get(field)
            if not isinstance(raw, int) or isinstance(raw, bool) or raw < 0:
                errors.append(f"{expected_mode} {bucket_name}.{field} must be a nonnegative integer")
        if all(isinstance(bucket.get(field), int) for field in USAGE_FIELDS):
            if bucket["cached_input_tokens"] > bucket["input_tokens"]:
                errors.append(f"{expected_mode} {bucket_name} cached input exceeds input")
            if bucket["uncached_input_tokens"] != bucket["input_tokens"] - bucket["cached_input_tokens"]:
                errors.append(f"{expected_mode} {bucket_name} uncached input is inconsistent")
            expected_total = (
                bucket["input_tokens"]
                + bucket["output_tokens"]
                + bucket["reasoning_output_tokens"]
            )
            if bucket["total_model_tokens"] != expected_total:
                errors.append(f"{expected_mode} {bucket_name} total model tokens are inconsistent")

    nodes = value.get("nodes")
    if not isinstance(nodes, dict):
        errors.append(f"{expected_mode} nodes must be an object")
        nodes = {}
    recomputed = {
        "generation": {"usage": TokenUsage.zero(), "calls": 0, "failed": 0},
        "reader": {"usage": TokenUsage.zero(), "calls": 0, "failed": 0},
    }
    provenance_invocations: list[dict[str, Any]] = []
    for node_id, contract in expected_graph.nodes.items():
        state = nodes.get(node_id)
        if not isinstance(state, dict):
            errors.append(f"{expected_mode} node state is missing: {node_id}")
            continue
        if state.get("node_kind") != contract.node_kind or state.get("contract_sha256") != contract.sha256:
            errors.append(f"{expected_mode} node state contract is invalid: {node_id}")
        attempts = state.get("attempts")
        if not isinstance(attempts, list):
            errors.append(f"{expected_mode} node attempts must be a list: {node_id}")
            continue
        if not contract.node_kind.startswith("agent-"):
            continue
        bucket_name = "reader" if contract.node_kind == "agent-reader" else "generation"
        for attempt in attempts:
            recomputed[bucket_name]["calls"] += 1
            if not isinstance(attempt, dict):
                errors.append(f"{expected_mode} node attempt is not an object: {node_id}")
                recomputed[bucket_name]["failed"] += 1
                continue
            if attempt.get("status") != "pass":
                recomputed[bucket_name]["failed"] += 1
            stdout_value = attempt.get("stdout_path")
            stdout_relative: str | None = None
            stdout_hash: str | None = None
            if isinstance(stdout_value, str):
                try:
                    stdout_candidate = Path(stdout_value).expanduser().resolve()
                    stdout_relative = stdout_candidate.relative_to(expected_root).as_posix()
                except (OSError, ValueError):
                    stdout_candidate = None
                if stdout_candidate is not None and stdout_candidate.is_file():
                    stdout_hash = hash_path(stdout_candidate)
            stderr_value = attempt.get("stderr_path")
            stderr_relative: str | None = None
            stderr_hash: str | None = None
            if isinstance(stderr_value, str):
                try:
                    stderr_candidate = Path(stderr_value).expanduser().resolve()
                    stderr_relative = stderr_candidate.relative_to(expected_root).as_posix()
                except (OSError, ValueError):
                    stderr_candidate = None
                if stderr_candidate is not None and stderr_candidate.is_file():
                    stderr_hash = hash_path(stderr_candidate)
            provenance_invocations.append(
                {
                    "node_id": node_id,
                    "attempt": attempt.get("attempt"),
                    "status": attempt.get("status"),
                    "stdout_path": stdout_relative,
                    "stdout_sha256": stdout_hash,
                    "stderr_path": stderr_relative,
                    "stderr_sha256": stderr_hash,
                }
            )
            if attempt.get("status") != "pass":
                continue
            try:
                stdout_path = Path(str(stdout_value)).expanduser().resolve()
                stdout_path.relative_to(expected_root / "raw")
            except (OSError, TypeError, ValueError):
                errors.append(f"{expected_mode} raw stdout path is unsafe: {node_id}")
                continue
            try:
                usage = parse_terminal_usage(stdout_path.read_text(encoding="utf-8"))
            except (OSError, ExecutionError) as exc:
                errors.append(f"{expected_mode} raw terminal usage is invalid for {node_id}: {exc}")
                continue
            if attempt.get("usage") != usage.as_dict():
                errors.append(f"{expected_mode} recorded attempt usage is invalid: {node_id}")
            recomputed[bucket_name]["usage"] = recomputed[bucket_name]["usage"] + usage
    for bucket_name in ("generation", "reader"):
        bucket = metrics.get(bucket_name) if isinstance(metrics.get(bucket_name), dict) else {}
        expected_usage = recomputed[bucket_name]["usage"].as_dict()
        if any(bucket.get(field) != expected_usage[field] for field in USAGE_FIELDS):
            errors.append(f"{expected_mode} {bucket_name} usage does not match raw terminal events")
        if bucket.get("model_call_count") != recomputed[bucket_name]["calls"]:
            errors.append(f"{expected_mode} {bucket_name} model-call count is inconsistent")
        if bucket.get("failed_terminal_calls") != recomputed[bucket_name]["failed"]:
            errors.append(f"{expected_mode} {bucket_name} failed-terminal count is inconsistent")
    if provenance.get("invocations") != provenance_invocations:
        errors.append(f"{expected_mode} execution provenance does not match raw invocations")

    def durable_artifact(node_id: str, relative: str) -> dict[str, Any] | None:
        state = nodes.get(node_id)
        attempts = state.get("attempts") if isinstance(state, dict) else None
        if not isinstance(attempts, list) or not attempts:
            errors.append(f"{expected_mode} durable artifact has no node attempt: {relative}")
            return None
        attempt = attempts[-1]
        outputs = attempt.get("output_artifacts") if isinstance(attempt, dict) else None
        recorded_hash = outputs.get(relative) if isinstance(outputs, dict) else None
        artifact_path = expected_root / relative
        if not artifact_path.is_file():
            errors.append(f"{expected_mode} durable artifact is missing: {relative}")
            return None
        if not isinstance(recorded_hash, str) or hash_path(artifact_path) != recorded_hash:
            errors.append(f"{expected_mode} durable artifact hash is invalid: {relative}")
        try:
            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{expected_mode} durable artifact JSON is invalid at {relative}: {exc}")
            return None
        if not isinstance(artifact, dict):
            errors.append(f"{expected_mode} durable artifact must be an object: {relative}")
            return None
        return artifact

    validation_artifact = durable_artifact("validate", "artifacts/validation.json")
    if validation_artifact is not None:
        artifact_status = validation_artifact.get("validation_status")
        artifact_exit = validation_artifact.get("validator_exit_code")
        if artifact_status not in {"pass", "fail"}:
            errors.append(f"{expected_mode} durable validation status is invalid")
        if not isinstance(artifact_exit, int) or isinstance(artifact_exit, bool):
            errors.append(f"{expected_mode} durable validator exit code is invalid")
        elif (artifact_status == "pass") != (artifact_exit == 0):
            errors.append(f"{expected_mode} durable validation status contradicts its exit code")
        if value.get("validation_status") != artifact_status:
            errors.append(f"{expected_mode} manifest validation status contradicts durable evidence")
        if validation_artifact.get("validated_wiki_sha256") != output.get("wiki_sha256"):
            errors.append(f"{expected_mode} validated wiki hash does not match final wiki")
        validation_state = nodes.get("validate")
        if isinstance(validation_state, dict) and validation_state.get("status") != artifact_status:
            errors.append(f"{expected_mode} validation node status contradicts durable evidence")

    reader = value.get("reader_evaluation")
    if reader is not None and not isinstance(reader, dict):
        errors.append(f"{expected_mode} reader evaluation must be an object or null")
    if isinstance(reader, dict):
        reader_enums = {
            "reader_status": {"pass", "fail"},
            "required_page_completeness": {"pass", "fail"},
            "navigation_link_integrity": {"pass", "fail"},
            "evidence_fidelity": {"pass", "fail"},
            "unsupported_claim_risk": {"none", "material"},
        }
        for field, allowed in reader_enums.items():
            if reader.get(field) not in allowed:
                errors.append(f"{expected_mode} reader field {field} is invalid")
        omissions = reader.get("material_omissions")
        if not isinstance(omissions, list) or any(not isinstance(item, str) for item in omissions):
            errors.append(f"{expected_mode} reader material_omissions is invalid")
        elif all(reader.get(field) == "pass" for field in (
            "required_page_completeness",
            "navigation_link_integrity",
            "evidence_fidelity",
        )) and reader.get("unsupported_claim_risk") == "none" and not omissions:
            if reader.get("reader_status") != "pass":
                errors.append(f"{expected_mode} reader_status contradicts passing reader components")
        elif reader.get("reader_status") != "fail":
            errors.append(f"{expected_mode} reader_status contradicts failing reader components")
    reader_state = nodes.get("reader")
    reader_attempts = reader_state.get("attempts") if isinstance(reader_state, dict) else None
    if isinstance(reader_attempts, list) and reader_attempts:
        reader_artifact = durable_artifact("reader", "artifacts/reader-evaluation.json")
        if reader_artifact != reader:
            errors.append(f"{expected_mode} manifest reader evaluation contradicts durable evidence")
    elif reader is not None:
        errors.append(f"{expected_mode} manifest has reader evidence without a reader node attempt")

    terminal_status = value.get("terminal_status")
    validation_status = value.get("validation_status")
    if terminal_status not in {"running", "completed", "failed"}:
        errors.append(f"{expected_mode} terminal_status is invalid")
    if validation_status not in {"not-run", "pass", "fail"}:
        errors.append(f"{expected_mode} validation_status is invalid")
    if terminal_status == "completed" and validation_status == "pass":
        if not isinstance(reader, dict) or not isinstance(reader_attempts, list) or not reader_attempts:
            errors.append(f"{expected_mode} completed passing run is missing reader evidence")
        incomplete_nodes = [
            node_id
            for node_id, state in nodes.items()
            if isinstance(state, dict)
            and state.get("node_kind") != "agent-repair"
            and state.get("status") != "pass"
        ]
        if incomplete_nodes:
            errors.append(
                f"{expected_mode} completed passing run has incomplete nodes: {', '.join(sorted(incomplete_nodes))}"
            )
    return value, errors


def _metric(run: dict[str, Any], bucket: str, field: str, default: int = 0) -> int:
    try:
        value = run["metrics"][bucket][field]
    except (KeyError, TypeError):
        return default
    return value if isinstance(value, int) and not isinstance(value, bool) else default


def _percent(numerator: int, denominator: int) -> str | None:
    if denominator == 0:
        return None
    value = Decimal(numerator) * Decimal(100) / Decimal(denominator)
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _reader_omissions(run: dict[str, Any]) -> set[str]:
    reader = run.get("reader_evaluation")
    if not isinstance(reader, dict) or not isinstance(reader.get("material_omissions"), list):
        return set()
    return {str(item).strip() for item in reader["material_omissions"] if str(item).strip()}


def build_decision(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    baseline_errors: list[str],
    candidate_errors: list[str],
    baseline_path: Path,
    candidate_path: Path,
) -> dict[str, Any]:
    reasons: list[str] = []
    gates: dict[str, dict[str, Any]] = {}
    evidence_errors = [*baseline_errors, *candidate_errors]
    gates["evidence_complete"] = {"pass": not evidence_errors, "errors": evidence_errors}
    if evidence_errors:
        reasons.extend(evidence_errors)

    identity_fields = (
        "source_commit",
        "model",
        "reasoning_effort",
        "codex_cli_version",
        "code_wiki_cli_version",
        "execution_evidence",
    )
    baseline_identity = baseline.get("identity") if isinstance(baseline.get("identity"), dict) else {}
    candidate_identity = candidate.get("identity") if isinstance(candidate.get("identity"), dict) else {}
    baseline_source = baseline.get("source") if isinstance(baseline.get("source"), dict) else {}
    candidate_source = candidate.get("source") if isinstance(candidate.get("source"), dict) else {}
    mismatches = [
        field
        for field in identity_fields
        if baseline_identity.get(field) != candidate_identity.get(field)
    ]
    reader_hash_match = (
        isinstance(baseline_identity.get("node_hashes"), dict)
        and isinstance(candidate_identity.get("node_hashes"), dict)
        and baseline_identity["node_hashes"].get("reader")
        == candidate_identity["node_hashes"].get("reader")
    )
    if not reader_hash_match:
        mismatches.append("reader_contract_hash")
    gates["identity_match"] = {"pass": not mismatches, "mismatched_fields": mismatches}
    if mismatches:
        reasons.append("comparison identity mismatch: " + ", ".join(mismatches))

    baseline_execution_evidence = baseline.get("_validated_execution_evidence")
    candidate_execution_evidence = candidate.get("_validated_execution_evidence")
    live_evidence = (
        baseline_execution_evidence == "live"
        and candidate_execution_evidence == "live"
    )
    gates["live_execution_evidence"] = {
        "pass": live_evidence,
        "baseline": baseline_execution_evidence,
        "candidate": candidate_execution_evidence,
    }
    if not live_evidence:
        reasons.append("fixture-backed runs are not eligible for a promotion decision")

    baseline_generation = {
        field: _metric(baseline, "generation", field)
        for field in (*USAGE_FIELDS, "model_call_count", "failed_terminal_calls", "wall_time_ms")
    }
    candidate_generation = {
        field: _metric(candidate, "generation", field)
        for field in (*USAGE_FIELDS, "model_call_count", "failed_terminal_calls", "wall_time_ms")
    }
    baseline_reader = {
        field: _metric(baseline, "reader", field)
        for field in (*USAGE_FIELDS, "model_call_count", "failed_terminal_calls", "wall_time_ms")
    }
    candidate_reader = {
        field: _metric(candidate, "reader", field)
        for field in (*USAGE_FIELDS, "model_call_count", "failed_terminal_calls", "wall_time_ms")
    }

    baseline_quality = (
        baseline.get("terminal_status") == "completed"
        and baseline.get("validation_status") == "pass"
        and isinstance(baseline.get("reader_evaluation"), dict)
        and baseline["reader_evaluation"].get("reader_status") == "pass"
        and baseline_source.get("original_checkout_unchanged") is True
        and baseline_source.get("source_mutation") is False
        and baseline_generation["failed_terminal_calls"] == 0
    )
    candidate_quality = (
        candidate.get("terminal_status") == "completed"
        and candidate.get("validation_status") == "pass"
        and isinstance(candidate.get("reader_evaluation"), dict)
        and candidate["reader_evaluation"].get("reader_status") == "pass"
        and candidate_source.get("original_checkout_unchanged") is True
        and candidate_source.get("source_mutation") is False
        and candidate_generation["failed_terminal_calls"] == 0
    )
    candidate_only_omissions = sorted(_reader_omissions(candidate) - _reader_omissions(baseline))
    candidate_regressions: list[str] = []
    if baseline.get("validation_status") == "pass" and candidate.get("validation_status") != "pass":
        candidate_regressions.append("candidate strict validation failed")
    baseline_reader_status = (
        baseline.get("reader_evaluation", {}).get("reader_status")
        if isinstance(baseline.get("reader_evaluation"), dict)
        else None
    )
    candidate_reader_status = (
        candidate.get("reader_evaluation", {}).get("reader_status")
        if isinstance(candidate.get("reader_evaluation"), dict)
        else None
    )
    if baseline_reader_status == "pass" and candidate_reader_status == "fail":
        candidate_regressions.append("candidate reader evaluation failed")
    if candidate_source.get("source_mutation") is True and baseline_source.get("source_mutation") is False:
        candidate_regressions.append("candidate mutated its source snapshot")
    if candidate_generation["failed_terminal_calls"] > baseline_generation["failed_terminal_calls"]:
        candidate_regressions.append("candidate recorded an additional failed terminal model call")
    if candidate_only_omissions:
        candidate_regressions.append("candidate has material omissions absent from baseline")
    gates["quality_and_safety"] = {
        "baseline_pass": baseline_quality,
        "candidate_pass": candidate_quality,
        "candidate_only_material_omissions": candidate_only_omissions,
        "candidate_regressions": candidate_regressions,
    }

    baseline_uncached = baseline_generation["uncached_input_tokens"]
    candidate_uncached = candidate_generation["uncached_input_tokens"]
    baseline_wall = baseline_generation["wall_time_ms"]
    candidate_wall = candidate_generation["wall_time_ms"]
    denominators_defined = baseline_uncached > 0 and baseline_wall > 0
    gates["defined_arithmetic"] = {
        "pass": denominators_defined,
        "baseline_uncached_input_tokens": baseline_uncached,
        "baseline_wall_time_ms": baseline_wall,
    }
    if not denominators_defined:
        reasons.append("baseline denominator is zero for an efficiency ratio")

    token_reduction_pass = denominators_defined and candidate_uncached * 100 <= baseline_uncached * 80
    total_tokens_pass = (
        candidate_generation["total_model_tokens"]
        <= baseline_generation["total_model_tokens"]
    )
    wall_time_pass = denominators_defined and candidate_wall * 100 <= baseline_wall * 125
    gates["uncached_input_reduction"] = {
        "pass": token_reduction_pass,
        "required_percent": "20.00",
        "observed_savings_percent": _percent(baseline_uncached - candidate_uncached, baseline_uncached),
    }
    gates["total_generation_tokens"] = {
        "pass": total_tokens_pass,
        "baseline": baseline_generation["total_model_tokens"],
        "candidate": candidate_generation["total_model_tokens"],
    }
    gates["wall_time"] = {
        "pass": wall_time_pass,
        "maximum_percent_of_baseline": "125.00",
        "observed_percent_of_baseline": _percent(candidate_wall, baseline_wall),
    }

    if evidence_errors or mismatches or not live_evidence or not denominators_defined:
        status = "inconclusive"
    elif candidate_regressions:
        status = "reject"
        reasons.extend(candidate_regressions)
    elif not baseline_quality or not candidate_quality:
        status = "inconclusive"
        reasons.append("both runs do not provide complete passing quality and safety evidence")
    elif token_reduction_pass and total_tokens_pass and wall_time_pass:
        status = "promote"
        reasons.append("all quality, safety, identity, and efficiency gates passed")
    else:
        status = "revise"
        if not token_reduction_pass:
            reasons.append("candidate uncached input reduction is below 20 percent")
        if not total_tokens_pass:
            reasons.append("candidate total generation model tokens exceed baseline")
        if not wall_time_pass:
            reasons.append("candidate wall time exceeds 125 percent of baseline")

    decision = {
        "schema_version": 1,
        "promotion_status": status,
        "reasons": reasons,
        "inputs": {
            "baseline_run": str(baseline_path.resolve()),
            "candidate_run": str(candidate_path.resolve()),
        },
        "identity": {
            "baseline": baseline_identity,
            "candidate": candidate_identity,
        },
        "metrics": {
            "baseline": {"generation": baseline_generation, "reader": baseline_reader},
            "candidate": {"generation": candidate_generation, "reader": candidate_reader},
        },
        "quality": {
            "baseline": baseline.get("reader_evaluation"),
            "candidate": candidate.get("reader_evaluation"),
        },
        "gates": gates,
    }
    if status not in PROMOTION_STATUSES:
        raise AssertionError(status)
    return decision


def render_markdown(decision: dict[str, Any]) -> str:
    baseline = decision["metrics"]["baseline"]["generation"]
    candidate = decision["metrics"]["candidate"]["generation"]
    rows = (
        ("Input tokens", "input_tokens"),
        ("Cached input tokens", "cached_input_tokens"),
        ("Uncached input tokens", "uncached_input_tokens"),
        ("Output tokens", "output_tokens"),
        ("Reasoning output tokens", "reasoning_output_tokens"),
        ("Total generation model tokens", "total_model_tokens"),
        ("Model calls", "model_call_count"),
        ("Failed terminal calls", "failed_terminal_calls"),
        ("Wall time ms", "wall_time_ms"),
    )
    lines = [
        "# Code Wiki Markdown Node-Graph Comparison",
        "",
        f"Promotion status: `{decision['promotion_status']}`",
        "",
        "## Reasons",
        "",
        *[f"- {reason}" for reason in decision["reasons"]],
        "",
        "## Generation Metrics",
        "",
        "| Metric | Baseline | Node graph |",
        "| --- | ---: | ---: |",
        *[f"| {label} | {baseline[field]} | {candidate[field]} |" for label, field in rows],
        "",
        "## Gate Evidence",
        "",
    ]
    for name, evidence in decision["gates"].items():
        lines.append(f"- `{name}`: `{str(evidence.get('pass')).lower()}` — `{json.dumps(evidence, sort_keys=True)}`")
    lines.extend(
        [
            "",
            "The report is evidence only. It never changes Code Wiki's default workflow.",
            "",
        ]
    )
    return "\n".join(lines)


def compare_runs(baseline_run: str, candidate_run: str, out: str) -> tuple[int, dict[str, Any]]:
    baseline_path = Path(baseline_run).expanduser().resolve()
    candidate_path = Path(candidate_run).expanduser().resolve()
    output_root = Path(out).expanduser().resolve()

    def overlaps(first: Path, second: Path) -> bool:
        try:
            first.relative_to(second)
            return True
        except ValueError:
            pass
        try:
            second.relative_to(first)
            return True
        except ValueError:
            return False

    for run_root in (baseline_path.parent, candidate_path.parent):
        if overlaps(output_root, run_root):
            raise RuntimeError("comparison output must be disjoint from both input run roots")
    if output_root.exists():
        unexpected = [
            path
            for path in output_root.iterdir()
            if path.name not in {"comparison.json", "comparison.md"}
            or path.is_symlink()
            or not path.is_file()
        ]
        if unexpected:
            raise RuntimeError(f"comparison output contains unsafe or unexpected entries: {output_root}")
    output_root.mkdir(parents=True, exist_ok=True)
    baseline, baseline_errors = _read_manifest(baseline_path, "baseline")
    candidate, candidate_errors = _read_manifest(candidate_path, "node-graph")
    decision = build_decision(
        baseline,
        candidate,
        baseline_errors,
        candidate_errors,
        baseline_path,
        candidate_path,
    )
    write_json(output_root / "comparison.json", decision)
    write_text_atomic(output_root / "comparison.md", render_markdown(decision))
    return 0, decision
