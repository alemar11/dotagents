"""Opt-in baseline and Markdown node-graph execution."""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

from code_wiki.claim_matrix import synthesize_claim_matrix
from code_wiki.evidence import parse_evidence_ref
from code_wiki.inventory import build_inventory, write_json as write_inventory
from code_wiki.pilot.common import git_output, hash_path, utc_now, write_json
from code_wiki.pilot.contracts import GraphContract, NodeContract, load_graph
from code_wiki.pilot.runtime import (
    CodexExecutor,
    ExecutionError,
    FixtureExecutor,
    InvocationResult,
    TokenUsage,
)
from code_wiki.pilot.provenance import (
    load_or_create_provenance_key,
    manifest_evidence_sha256,
    sign_receipt,
)
from code_wiki.pilot.snapshot import (
    SourceSnapshot,
    assert_snapshot_clean,
    create_snapshot,
    source_status,
)
from code_wiki.scaffold import scaffold
from code_wiki.validation import validate
from code_wiki.version import VERSION
from code_wiki.wiki_contract import REQUIRED_PAGES


REASONING_EFFORTS = {"low", "medium", "high", "xhigh"}
RUN_SCHEMA_VERSION = 1
STUDY_PAGE_RE = re.compile(r"^## Page: `([^`]+)`$", re.MULTILINE)
STUDY_EVIDENCE_RE = re.compile(r"(?:\[|`)([^\]\r\n`]+:\d+(?:-\d+)?)(?:\]|`)")
STUDY_REQUIRED_TOPICS = (
    "architecture",
    "interface",
    "lifecycle",
    "flow",
    "operation",
    "test",
    "failure",
    "change",
    "risk",
    "validation",
    "rollback",
)


def skill_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _artifact_path(output_root: Path, snapshot: SourceSnapshot, artifact: str) -> Path:
    return snapshot.snapshot_path if artifact == "source" else output_root / artifact


def _artifact_hashes(
    output_root: Path,
    snapshot: SourceSnapshot,
    artifacts: tuple[str, ...],
) -> dict[str, str]:
    result: dict[str, str] = {}
    for artifact in artifacts:
        path = _artifact_path(output_root, snapshot, artifact)
        if not path.exists():
            raise RuntimeError(f"declared artifact is missing: {artifact}")
        result[artifact] = hash_path(
            path,
            exclude_git_metadata=artifact == "source",
        )
    return result


def _minimal_output_artifacts(artifacts: tuple[str, ...]) -> list[str]:
    selected: list[str] = []
    for artifact in sorted(artifacts, key=lambda value: (len(Path(value).parts), value)):
        if any(artifact == parent or artifact.startswith(f"{parent}/") for parent in selected):
            continue
        selected.append(artifact)
    return selected


def _seed_staging_outputs(
    output_root: Path,
    staging_root: Path,
    artifacts: tuple[str, ...],
) -> None:
    for artifact in _minimal_output_artifacts(artifacts):
        source = output_root / artifact
        target = staging_root / artifact
        _reject_symlinks(source)
        if source.is_dir():
            shutil.copytree(source, target)
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def _materialize_declared_inputs(
    output_root: Path,
    input_root: Path,
    snapshot: SourceSnapshot,
    artifacts: tuple[str, ...],
) -> None:
    """Build a read-only view containing only this node's declared inputs."""
    del snapshot
    non_source = tuple(artifact for artifact in artifacts if artifact != "source")
    for artifact in _minimal_output_artifacts(non_source):
        source = output_root / artifact
        target = input_root / artifact
        _reject_symlinks(source)
        if source.is_dir():
            shutil.copytree(source, target)
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def _persist_artifact_evidence(
    source_root: Path,
    output_root: Path,
    *,
    evidence_kind: str,
    node_id: str,
    attempt: int,
    artifacts: tuple[str, ...],
) -> str | None:
    non_source = tuple(artifact for artifact in artifacts if artifact != "source")
    if not non_source:
        return None
    relative_root = Path("artifacts") / "node-evidence" / evidence_kind / f"{node_id}-attempt-{attempt}"
    evidence_root = output_root / relative_root
    if evidence_root.exists():
        raise RuntimeError(f"node artifact evidence already exists: {relative_root.as_posix()}")
    for artifact in _minimal_output_artifacts(non_source):
        source = source_root / artifact
        target = evidence_root / artifact
        if not source.exists():
            raise RuntimeError(f"cannot preserve missing node artifact evidence: {artifact}")
        _reject_symlinks(source)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return relative_root.as_posix()


def _declared_input_paths(
    input_root: Path,
    snapshot: SourceSnapshot,
    artifacts: tuple[str, ...],
) -> dict[str, str]:
    return {
        artifact: str(snapshot.snapshot_path if artifact == "source" else input_root / artifact)
        for artifact in artifacts
    }


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must be a JSON object")
    return value


def _sanitize_source_metadata(root: Path) -> None:
    """Remove durable source/output paths from a source-free node's view."""
    inventory_path = root / "wiki" / "data" / "inventory.json"
    if inventory_path.is_file():
        inventory = _load_json_object(inventory_path, "isolated inventory")
        repo = inventory.get("repo")
        if not isinstance(repo, dict):
            raise RuntimeError("isolated inventory repo metadata must be an object")
        repo["path"] = "source-not-declared"
        repo["remote_url"] = None
        write_json(inventory_path, inventory)

    matrix_path = root / "wiki" / "data" / "claim-matrix.json"
    if matrix_path.is_file():
        matrix = _load_json_object(matrix_path, "isolated claim matrix")
        repo = matrix.get("repo")
        inventory = matrix.get("inventory")
        if not isinstance(repo, dict) or not isinstance(inventory, dict):
            raise RuntimeError("isolated claim-matrix metadata must contain object fields")
        repo["path"] = "source-not-declared"
        repo["web_url"] = None
        inventory["path"] = "wiki/data/inventory.json"
        write_json(matrix_path, matrix)


def _assert_paths_hidden(root: Path, hidden_paths: tuple[Path, ...]) -> None:
    encoded = tuple(str(path).encode("utf-8") for path in hidden_paths)
    for candidate in root.rglob("*"):
        if not candidate.is_file():
            continue
        try:
            contents = candidate.read_bytes()
        except OSError as exc:
            raise RuntimeError(f"cannot inspect isolated node input {candidate}: {exc}") from exc
        if any(value in contents for value in encoded):
            raise RuntimeError(f"source-free node input exposes a durable path: {candidate}")


def _restore_source_metadata(output_root: Path, staging_root: Path) -> None:
    """Restore trusted validator metadata after the source-free model exits."""
    durable_inventory = output_root / "wiki" / "data" / "inventory.json"
    staged_inventory = staging_root / "wiki" / "data" / "inventory.json"
    if durable_inventory.is_file() and staged_inventory.is_file():
        shutil.copy2(durable_inventory, staged_inventory)

    durable_matrix = output_root / "wiki" / "data" / "claim-matrix.json"
    staged_matrix = staging_root / "wiki" / "data" / "claim-matrix.json"
    if durable_matrix.is_file() and staged_matrix.is_file():
        trusted = _load_json_object(durable_matrix, "trusted claim matrix")
        rendered = _load_json_object(staged_matrix, "rendered claim matrix")
        for field in ("repo", "inventory"):
            value = trusted.get(field)
            if not isinstance(value, dict):
                raise RuntimeError(f"trusted claim matrix {field} metadata must be an object")
            rendered[field] = value
        write_json(staged_matrix, rendered)


def _reject_symlinks(path: Path) -> None:
    if path.is_symlink():
        raise RuntimeError(f"declared node output contains a symlink: {path}")
    if not path.is_dir():
        return
    for root, dirnames, filenames in os.walk(path, followlinks=False):
        root_path = Path(root)
        for name in (*dirnames, *filenames):
            candidate = root_path / name
            if candidate.is_symlink():
                raise RuntimeError(f"declared node output contains a symlink: {candidate}")


def _remove_artifact(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _promote_staged_outputs(
    output_root: Path,
    staging_root: Path,
    artifacts: tuple[str, ...],
) -> None:
    for artifact in _minimal_output_artifacts(artifacts):
        source = staging_root / artifact
        target = output_root / artifact
        if not source.exists():
            raise RuntimeError(f"declared staged output is missing: {artifact}")
        _reject_symlinks(source)
        _reject_symlinks(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        replacement = target.with_name(f".{target.name}.replacement-{uuid.uuid4().hex}")
        backup = target.with_name(f".{target.name}.backup-{uuid.uuid4().hex}")
        target_moved = False
        try:
            if source.is_dir():
                shutil.copytree(source, replacement)
            else:
                shutil.copy2(source, replacement)
            _reject_symlinks(replacement)
            if target.exists() or target.is_symlink():
                target.replace(backup)
                target_moved = True
            replacement.replace(target)
        except (OSError, RuntimeError):
            if target_moved and backup.exists() and not target.exists():
                backup.replace(target)
            raise
        else:
            try:
                _remove_artifact(backup)
            except OSError:
                pass
        finally:
            try:
                _remove_artifact(replacement)
            except OSError:
                pass


def _codex_version() -> str:
    try:
        completed = subprocess.run(
            ["codex", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"cannot resolve Codex CLI version: {exc}") from exc
    value = completed.stdout.strip()
    if not value:
        raise RuntimeError("Codex CLI version output is empty")
    return value


def _new_manifest(
    *,
    run_id: str,
    mode: str,
    graph: GraphContract,
    snapshot: SourceSnapshot,
    output_root: Path,
    model: str,
    reasoning_effort: str,
    codex_version: str,
    execution_evidence: str,
) -> dict[str, Any]:
    return {
        "schema_version": RUN_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "terminal_status": "running",
        "validation_status": "not-run",
        "started_at": utc_now(),
        "completed_at": None,
        "identity": {
            "source_commit": snapshot.commit,
            "model": model,
            "reasoning_effort": reasoning_effort,
            "codex_cli_version": codex_version,
            "code_wiki_cli_version": VERSION,
            "execution_evidence": execution_evidence,
            "graph_sha256": graph.graph_sha256,
            "node_hashes": graph.node_hashes,
        },
        "source": {
            "original_checkout": str(snapshot.original_checkout),
            "original_head_before": snapshot.original_head_before,
            "original_head_after": None,
            "original_status_before": snapshot.original_status_before,
            "original_status_after": None,
            "original_checkout_unchanged": None,
            "snapshot_path": str(snapshot.snapshot_path),
            "snapshot_tree_sha256_before": snapshot.snapshot_tree_hash,
            "snapshot_tree_sha256_after": None,
            "source_mutation": False,
        },
        "output": {
            "root": str(output_root),
            "wiki_path": str(output_root / "wiki"),
            "wiki_sha256": None,
            "manifest_path": str(output_root / "run.json"),
            "provenance_path": str(output_root / "artifacts" / "execution-provenance.json"),
            "provenance_sha256": None,
        },
        "nodes": {
            node_id: {
                "node_kind": node.node_kind,
                "contract_sha256": node.sha256,
                "status": "pending",
                "attempts": [],
            }
            for node_id, node in sorted(graph.nodes.items())
        },
        "metrics": {
            "generation": {
                **TokenUsage.zero().as_dict(),
                "model_call_count": 0,
                "failed_terminal_calls": 0,
                "wall_time_ms": 0,
            },
            "reader": {
                **TokenUsage.zero().as_dict(),
                "model_call_count": 0,
                "failed_terminal_calls": 0,
                "wall_time_ms": 0,
            },
        },
        "reader_evaluation": None,
        "error": None,
    }


def _persist(output_root: Path, manifest: dict[str, Any]) -> None:
    write_json(output_root / "run.json", manifest)


def _add_usage(metrics: dict[str, Any], usage: TokenUsage, duration_ms: int) -> None:
    current = TokenUsage(
        metrics["input_tokens"],
        metrics["cached_input_tokens"],
        metrics["output_tokens"],
        metrics["reasoning_output_tokens"],
    )
    total = current + usage
    metrics.update(total.as_dict())
    metrics["wall_time_ms"] += duration_ms


def _node_prompt(
    *,
    node: NodeContract,
    graph: GraphContract,
    snapshot: SourceSnapshot,
    input_root: Path,
    agent_output_root: Path,
    input_hashes: dict[str, str],
    attempt: int,
    validation_feedback: str | None,
) -> str:
    workflow_context = ""
    if node.node_kind == "agent-baseline":
        root = skill_root()
        workflow_files = (
            root / "SKILL.md",
            root / "references" / "repo-study-playbook.md",
            root / "references" / "wiki-html-contract.md",
        )
        workflow_context = "\n\n# Current full Code Wiki workflow\n\n" + "\n\n".join(
            f"## {path.name}\n\n{path.read_text(encoding='utf-8')}" for path in workflow_files
        )
    feedback = f"\n\n# Validation feedback for bounded repair\n\n{validation_feedback}" if validation_feedback else ""
    source_declared = "source" in node.input_artifacts
    input_paths = _declared_input_paths(input_root, snapshot, node.input_artifacts)
    output_paths = {
        artifact: str(agent_output_root / artifact)
        for artifact in node.output_artifacts
    }
    source_access = str(snapshot.snapshot_path) if source_declared else "not-declared"
    return f"""You are executing one opt-in Code Wiki pilot node in a fresh ephemeral context.

Node ID: {node.node_id}
Node kind: {node.node_kind}
Attempt: {attempt}
Graph mode: {graph.mode}
Declared source access: {source_access}
Read-only declared-input root: {input_root}
Writable node-output staging root: {agent_output_root}
Declared input paths: {json.dumps(input_paths, sort_keys=True)}
Declared inputs with SHA-256: {json.dumps(input_hashes, sort_keys=True)}
Declared writable output paths: {json.dumps(output_paths, sort_keys=True)}

Safety and output rules:
- Inspect the source snapshot only when source is a declared input.
- Do not edit, stage, commit, or otherwise mutate the source snapshot.
- Treat every declared input path as read-only.
- Write only the declared outputs under the node-output staging root.
- Do not invoke other agents, Codex, image generation, or external network services.
- Use source-backed evidence from the clean snapshot and exact relative paths and line ranges.
- Do not add outputs that belong to another node.
- Finish after writing the declared outputs; keep the final chat message concise.

# Node instructions

{node.instructions}{workflow_context}{feedback}
"""


def _validate_study_brief(output_root: Path, snapshot: SourceSnapshot) -> None:
    path = output_root / "artifacts" / "study.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"cannot read study brief: {exc}") from exc
    matches = list(STUDY_PAGE_RE.finditer(text))
    pages = [match.group(1) for match in matches]
    if pages != REQUIRED_PAGES:
        raise RuntimeError(
            "study brief page sections must exactly match required pages in order: "
            + ", ".join(REQUIRED_PAGES)
        )
    lowered_brief = text.lower()
    missing_topics = [topic for topic in STUDY_REQUIRED_TOPICS if topic not in lowered_brief]
    if missing_topics:
        raise RuntimeError(
            "study brief is missing required cross-page coverage topics: "
            + ", ".join(missing_topics)
        )
    for index, match in enumerate(matches):
        page = pages[index]
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.end():end]
        words = re.findall(r"\b[A-Za-z0-9][A-Za-z0-9_-]*\b", section)
        if len(words) < 120:
            raise RuntimeError(f"study brief section is too thin for {page}: {len(words)} words")
        evidence: set[tuple[str, int, int]] = set()
        for found in STUDY_EVIDENCE_RE.finditer(section):
            raw_ref = found.group(1)
            parsed = parse_evidence_ref(raw_ref)
            if parsed is None:
                raise RuntimeError(f"study brief evidence path is unsafe: {raw_ref}")
            evidence.add(
                (
                    str(parsed["path"]),
                    int(parsed["start"]),
                    int(parsed["end"]),
                )
            )
        if len(evidence) < 2:
            raise RuntimeError(f"study brief section needs two distinct evidence refs: {page}")
        for relative, start, finish in evidence:
            relative_path = Path(relative)
            if relative_path.is_absolute() or not relative_path.parts or any(
                part in {"", ".", ".."} for part in relative_path.parts
            ):
                raise RuntimeError(f"study brief evidence path is unsafe: {relative}")
            source_root = snapshot.snapshot_path.resolve()
            source_path = (source_root / relative_path).resolve()
            try:
                source_path.relative_to(source_root)
            except ValueError as exc:
                raise RuntimeError(f"study brief evidence escapes source: {relative}") from exc
            if not source_path.is_file():
                raise RuntimeError(f"study brief evidence path does not exist: {relative}")
            line_count = len(source_path.read_text(encoding="utf-8", errors="replace").splitlines())
            if start < 1 or finish < start or finish > line_count:
                raise RuntimeError(
                    f"study brief evidence range is invalid: {relative}:{start}-{finish}"
                )


def _invoke_agent(
    *,
    executor: CodexExecutor | FixtureExecutor,
    node: NodeContract,
    graph: GraphContract,
    snapshot: SourceSnapshot,
    output_root: Path,
    attempt: int,
    validation_feedback: str | None = None,
) -> tuple[dict[str, Any], InvocationResult | None, str | None]:
    started_at = utc_now()
    before = assert_snapshot_clean(snapshot)
    try:
        input_source_hashes = _artifact_hashes(output_root, snapshot, node.input_artifacts)
    except RuntimeError as exc:
        return (
            {
                "attempt": attempt,
                "started_at": started_at,
                "completed_at": utc_now(),
                "status": "fail",
                "model_call_started": False,
                "input_source_artifacts": {},
                "input_source_evidence_path": None,
                "input_artifacts": {},
                "input_evidence_path": None,
                "output_artifacts": {},
                "output_evidence_path": None,
                "source_tree_sha256_before": before,
                "source_tree_sha256_after": None,
                "usage": None,
                "duration_ms": 0,
                "exit_code": None,
                "stdout_path": None,
                "stderr_path": None,
                "error": str(exc),
            },
            None,
            str(exc),
        )
    raw_root = output_root / "raw"
    input_root = Path(tempfile.mkdtemp(prefix=f"code-wiki-{node.node_id}-inputs-"))
    staging_root = Path(tempfile.mkdtemp(prefix=f"code-wiki-{node.node_id}-outputs-"))
    input_hashes: dict[str, str] = {}
    input_source_evidence_path: str | None = None
    input_evidence_path: str | None = None
    output_hashes: dict[str, str] = {}
    output_evidence_path: str | None = None
    result: InvocationResult | None = None
    try:
        _materialize_declared_inputs(
            output_root,
            input_root,
            snapshot,
            node.input_artifacts,
        )
        _seed_staging_outputs(output_root, staging_root, node.output_artifacts)
        if "source" not in node.input_artifacts:
            input_source_evidence_path = _persist_artifact_evidence(
                input_root,
                output_root,
                evidence_kind="input-source",
                node_id=node.node_id,
                attempt=attempt,
                artifacts=node.input_artifacts,
            )
            _sanitize_source_metadata(input_root)
            _sanitize_source_metadata(staging_root)
            hidden_paths = (
                snapshot.snapshot_path,
                snapshot.original_checkout,
                output_root,
            )
            _assert_paths_hidden(input_root, hidden_paths)
            _assert_paths_hidden(staging_root, hidden_paths)
        input_hashes = _artifact_hashes(input_root, snapshot, node.input_artifacts)
        input_evidence_path = _persist_artifact_evidence(
            input_root,
            output_root,
            evidence_kind="input",
            node_id=node.node_id,
            attempt=attempt,
            artifacts=node.input_artifacts,
        )
        prompt = _node_prompt(
            node=node,
            graph=graph,
            snapshot=snapshot,
            input_root=input_root,
            agent_output_root=staging_root,
            input_hashes=input_hashes,
            attempt=attempt,
            validation_feedback=validation_feedback,
        )
        result = executor.invoke(
            node_id=node.node_id,
            attempt=attempt,
            prompt=prompt,
            snapshot=snapshot.snapshot_path,
            input_root=input_root,
            output_root=staging_root,
            raw_root=raw_root,
            source_allowed="source" in node.input_artifacts,
        )
        after = assert_snapshot_clean(snapshot)
        if "source" not in node.input_artifacts:
            _restore_source_metadata(output_root, staging_root)
        staged_output_hashes = _artifact_hashes(staging_root, snapshot, node.output_artifacts)
        output_hashes = staged_output_hashes
        output_evidence_path = _persist_artifact_evidence(
            staging_root,
            output_root,
            evidence_kind="output",
            node_id=node.node_id,
            attempt=attempt,
            artifacts=node.output_artifacts,
        )
        _promote_staged_outputs(output_root, staging_root, node.output_artifacts)
        output_hashes = _artifact_hashes(output_root, snapshot, node.output_artifacts)
        if output_hashes != staged_output_hashes:
            raise RuntimeError(f"promoted output hashes changed for node {node.node_id}")
    except (ExecutionError, OSError, RuntimeError) as exc:
        source_after: str | None = None
        try:
            source_after = assert_snapshot_clean(snapshot)
        except RuntimeError:
            pass
        stdout_path = (
            result.stdout_path
            if result is not None
            else raw_root / f"{node.node_id}-attempt-{attempt}.jsonl"
        )
        stderr_path = (
            result.stderr_path
            if result is not None
            else raw_root / f"{node.node_id}-attempt-{attempt}.stderr.txt"
        )
        failure = (
            {
                "attempt": attempt,
                "started_at": started_at,
                "completed_at": utc_now(),
                "status": "fail",
                "model_call_started": (
                    result is not None
                    or isinstance(exc, ExecutionError) and exc.model_call_started
                ),
                "input_source_artifacts": input_source_hashes,
                "input_source_evidence_path": input_source_evidence_path,
                "input_artifacts": input_hashes,
                "input_evidence_path": input_evidence_path,
                "output_artifacts": output_hashes,
                "output_evidence_path": output_evidence_path,
                "source_tree_sha256_before": before,
                "source_tree_sha256_after": source_after,
                "usage": result.usage.as_dict() if result is not None else None,
                "duration_ms": result.duration_ms if result is not None else 0,
                "exit_code": (
                    result.exit_code
                    if result is not None
                    else exc.exit_code if isinstance(exc, ExecutionError) else None
                ),
                "stdout_path": str(stdout_path) if stdout_path.exists() else None,
                "stderr_path": str(stderr_path) if stderr_path.exists() else None,
                "error": str(exc),
            },
            result,
            str(exc),
        )
        return failure
    else:
        return (
            {
                "attempt": attempt,
                "started_at": started_at,
                "completed_at": utc_now(),
                "status": "pass",
                "model_call_started": True,
                "input_source_artifacts": input_source_hashes,
                "input_source_evidence_path": input_source_evidence_path,
                "input_artifacts": input_hashes,
                "input_evidence_path": input_evidence_path,
                "output_artifacts": output_hashes,
                "output_evidence_path": output_evidence_path,
                "source_tree_sha256_before": before,
                "source_tree_sha256_after": after,
                "usage": result.usage.as_dict(),
                "duration_ms": result.duration_ms,
                "exit_code": result.exit_code,
                "stdout_path": str(result.stdout_path),
                "stderr_path": str(result.stderr_path),
                "error": None,
            },
            result,
            None,
        )
    finally:
        shutil.rmtree(input_root, ignore_errors=True)
        shutil.rmtree(staging_root, ignore_errors=True)


def _prepare(
    node: NodeContract,
    snapshot: SourceSnapshot,
    output_root: Path,
    title: str,
) -> dict[str, Any]:
    started_at = utc_now()
    before = assert_snapshot_clean(snapshot)
    input_hashes = _artifact_hashes(output_root, snapshot, node.input_artifacts)
    input_evidence_path = _persist_artifact_evidence(
        output_root,
        output_root,
        evidence_kind="input",
        node_id=node.node_id,
        attempt=1,
        artifacts=node.input_artifacts,
    )
    wiki = output_root / "wiki"
    inventory_path = wiki / "data" / "inventory.json"
    matrix_path = wiki / "data" / "claim-matrix.json"
    inventory = build_inventory(str(snapshot.snapshot_path))
    write_inventory(str(inventory_path), inventory)
    with redirect_stdout(io.StringIO()):
        scaffold(str(wiki), title, False)
    synthesize_claim_matrix(str(snapshot.snapshot_path), str(inventory_path), str(matrix_path))
    after = assert_snapshot_clean(snapshot)
    output_hashes = _artifact_hashes(output_root, snapshot, node.output_artifacts)
    output_evidence_path = _persist_artifact_evidence(
        output_root,
        output_root,
        evidence_kind="output",
        node_id=node.node_id,
        attempt=1,
        artifacts=node.output_artifacts,
    )
    return {
        "attempt": 1,
        "started_at": started_at,
        "completed_at": utc_now(),
        "status": "pass",
        "model_call_started": False,
        "input_source_artifacts": input_hashes,
        "input_source_evidence_path": None,
        "input_artifacts": input_hashes,
        "input_evidence_path": input_evidence_path,
        "output_artifacts": output_hashes,
        "output_evidence_path": output_evidence_path,
        "source_tree_sha256_before": before,
        "source_tree_sha256_after": after,
        "usage": None,
        "duration_ms": 0,
        "exit_code": 0,
        "stdout_path": None,
        "stderr_path": None,
        "error": None,
    }


def _strict_validate(
    node: NodeContract,
    snapshot: SourceSnapshot,
    output_root: Path,
    attempt: int,
) -> tuple[dict[str, Any], str, str]:
    started_at = utc_now()
    before = assert_snapshot_clean(snapshot)
    input_hashes = _artifact_hashes(output_root, snapshot, node.input_artifacts)
    input_evidence_path = _persist_artifact_evidence(
        output_root,
        output_root,
        evidence_kind="input",
        node_id=node.node_id,
        attempt=attempt,
        artifacts=node.input_artifacts,
    )
    capture = io.StringIO()
    started = time.monotonic()
    with redirect_stdout(capture):
        exit_code = validate(str(output_root / "wiki"), strict=True)
    duration_ms = max(1, round((time.monotonic() - started) * 1000))
    output = capture.getvalue()
    status = "pass" if exit_code == 0 else "fail"
    validation_path = output_root / "artifacts" / "validation.json"
    write_json(
        validation_path,
        {
            "validation_status": status,
            "validator_exit_code": exit_code,
            "validator_output": output,
            "validated_wiki_sha256": hash_path(output_root / "wiki"),
        },
    )
    after = assert_snapshot_clean(snapshot)
    output_hashes = _artifact_hashes(output_root, snapshot, node.output_artifacts)
    output_evidence_path = _persist_artifact_evidence(
        output_root,
        output_root,
        evidence_kind="output",
        node_id=node.node_id,
        attempt=attempt,
        artifacts=node.output_artifacts,
    )
    return (
        {
            "attempt": attempt,
            "started_at": started_at,
            "completed_at": utc_now(),
            "status": status,
            "model_call_started": False,
            "input_source_artifacts": input_hashes,
            "input_source_evidence_path": None,
            "input_artifacts": input_hashes,
            "input_evidence_path": input_evidence_path,
            "output_artifacts": output_hashes,
            "output_evidence_path": output_evidence_path,
            "source_tree_sha256_before": before,
            "source_tree_sha256_after": after,
            "usage": None,
            "duration_ms": duration_ms,
            "exit_code": exit_code,
            "stdout_path": None,
            "stderr_path": None,
            "error": None if exit_code == 0 else "strict wiki validation failed",
        },
        status,
        output,
    )


def _load_reader(output_root: Path) -> dict[str, Any]:
    path = output_root / "artifacts" / "reader-evaluation.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid reader evaluation {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError("reader evaluation must be an object")
    enums = {
        "reader_status": {"pass", "fail"},
        "required_page_completeness": {"pass", "fail"},
        "navigation_link_integrity": {"pass", "fail"},
        "evidence_fidelity": {"pass", "fail"},
        "unsupported_claim_risk": {"none", "material"},
    }
    for field, allowed in enums.items():
        if value.get(field) not in allowed:
            raise RuntimeError(f"reader evaluation field {field} is invalid")
    omissions = value.get("material_omissions")
    if not isinstance(omissions, list) or any(not isinstance(item, str) for item in omissions):
        raise RuntimeError("reader evaluation material_omissions must be a string list")
    if not isinstance(value.get("summary"), str) or not value["summary"].strip():
        raise RuntimeError("reader evaluation summary must be a nonempty string")
    derived_status = (
        "pass"
        if all(value[field] == "pass" for field in (
            "required_page_completeness",
            "navigation_link_integrity",
            "evidence_fidelity",
        ))
        and value["unsupported_claim_risk"] == "none"
        and not omissions
        else "fail"
    )
    if value["reader_status"] != derived_status:
        raise RuntimeError(
            f"reader_status must be {derived_status} for the component results, risk, and omissions"
        )
    return value


def _mark_agent_result(
    manifest: dict[str, Any],
    node: NodeContract,
    attempt_record: dict[str, Any],
    result: InvocationResult | None,
    error: str | None,
) -> None:
    node_state = manifest["nodes"][node.node_id]
    node_state["attempts"].append(attempt_record)
    passed = result is not None and error is None
    node_state["status"] = "pass" if passed else "fail"
    bucket_name = "reader" if node.node_kind == "agent-reader" else "generation"
    metrics = manifest["metrics"][bucket_name]
    if attempt_record.get("model_call_started") is True:
        metrics["model_call_count"] += 1
        if result:
            _add_usage(metrics, result.usage, result.duration_ms)
        else:
            metrics["failed_terminal_calls"] += 1
    if not passed:
        manifest["error"] = error


def _run_pre_validation_graph(
    *,
    graph: GraphContract,
    snapshot: SourceSnapshot,
    output_root: Path,
    title: str,
    executor: CodexExecutor | FixtureExecutor,
    manifest: dict[str, Any],
) -> bool:
    excluded = {node.node_id for node in graph.nodes.values() if node.node_kind in {"validate", "agent-repair", "agent-reader"}}
    remaining = set(graph.nodes) - excluded
    completed: set[str] = set()
    while remaining:
        ready = sorted(
            node_id
            for node_id in remaining
            if set(graph.nodes[node_id].dependencies).issubset(completed)
        )
        if not ready:
            manifest["error"] = "no runnable node remains before validation"
            return False
        deterministic = [node_id for node_id in ready if graph.nodes[node_id].node_kind == "prepare"]
        if deterministic:
            for node_id in deterministic:
                node = graph.nodes[node_id]
                try:
                    attempt = _prepare(node, snapshot, output_root, title)
                except RuntimeError as exc:
                    manifest["nodes"][node_id]["status"] = "fail"
                    manifest["error"] = str(exc)
                    return False
                manifest["nodes"][node_id]["attempts"].append(attempt)
                manifest["nodes"][node_id]["status"] = "pass"
                remaining.remove(node_id)
                completed.add(node_id)
                _persist(output_root, manifest)
            continue

        workers = min(3, len(ready))
        results: dict[str, tuple[dict[str, Any], InvocationResult | None, str | None]] = {}
        with ThreadPoolExecutor(max_workers=workers) as pool:
            future_map = {
                pool.submit(
                    _invoke_agent,
                    executor=executor,
                    node=graph.nodes[node_id],
                    graph=graph,
                    snapshot=snapshot,
                    output_root=output_root,
                    attempt=1,
                ): node_id
                for node_id in ready
            }
            for future in as_completed(future_map):
                results[future_map[future]] = future.result()
        all_passed = True
        for node_id in ready:
            node = graph.nodes[node_id]
            attempt, result, error = results[node_id]
            if result and node.node_kind == "agent-study":
                try:
                    _validate_study_brief(output_root, snapshot)
                except RuntimeError as exc:
                    attempt["status"] = "fail"
                    attempt["error"] = str(exc)
                    error = str(exc)
            _mark_agent_result(manifest, node, attempt, result, error)
            remaining.remove(node_id)
            if result is None or error is not None:
                all_passed = False
            else:
                completed.add(node_id)
        _persist(output_root, manifest)
        if not all_passed:
            return False
    return True


def _finish_source_state(manifest: dict[str, Any], snapshot: SourceSnapshot) -> None:
    original_after = source_status(snapshot.original_checkout)
    original_head_after = git_output(snapshot.original_checkout, "rev-parse", "HEAD")
    manifest["source"]["original_head_after"] = original_head_after
    manifest["source"]["original_status_after"] = original_after
    manifest["source"]["original_checkout_unchanged"] = (
        original_after == snapshot.original_status_before
        and original_head_after == snapshot.original_head_before
    )
    try:
        after_hash = assert_snapshot_clean(snapshot)
    except RuntimeError:
        manifest["source"]["source_mutation"] = True
        after_hash = hash_path(snapshot.snapshot_path, exclude_git_metadata=True)
    manifest["source"]["snapshot_tree_sha256_after"] = after_hash
    if original_after != snapshot.original_status_before:
        manifest["error"] = "original source checkout changed during pilot run"


def _write_execution_provenance(
    output_root: Path,
    manifest: dict[str, Any],
    signing_key: bytes | None,
) -> None:
    invocations: list[dict[str, Any]] = []
    for node_id, state in sorted(manifest["nodes"].items()):
        if not str(state.get("node_kind", "")).startswith("agent-"):
            continue
        for attempt in state.get("attempts", []):
            stdout_value = attempt.get("stdout_path") if isinstance(attempt, dict) else None
            stdout_relative: str | None = None
            stdout_sha256: str | None = None
            if isinstance(stdout_value, str):
                stdout_path = Path(stdout_value).expanduser().resolve()
                try:
                    stdout_relative = stdout_path.relative_to(output_root).as_posix()
                except ValueError as exc:
                    raise RuntimeError(f"raw invocation path escapes output root: {stdout_path}") from exc
                if stdout_path.is_file():
                    stdout_sha256 = hash_path(stdout_path)
            stderr_value = attempt.get("stderr_path") if isinstance(attempt, dict) else None
            stderr_relative: str | None = None
            stderr_sha256: str | None = None
            if isinstance(stderr_value, str):
                stderr_path = Path(stderr_value).expanduser().resolve()
                try:
                    stderr_relative = stderr_path.relative_to(output_root).as_posix()
                except ValueError as exc:
                    raise RuntimeError(f"raw invocation path escapes output root: {stderr_path}") from exc
                if stderr_path.is_file():
                    stderr_sha256 = hash_path(stderr_path)
            invocations.append(
                {
                    "node_id": node_id,
                    "attempt": attempt.get("attempt") if isinstance(attempt, dict) else None,
                    "status": attempt.get("status") if isinstance(attempt, dict) else "fail",
                    "model_call_started": (
                        attempt.get("model_call_started") if isinstance(attempt, dict) else False
                    ),
                    "stdout_path": stdout_relative,
                    "stdout_sha256": stdout_sha256,
                    "stderr_path": stderr_relative,
                    "stderr_sha256": stderr_sha256,
                }
            )
    identity = manifest["identity"]
    provenance = {
        "schema_version": 1,
        "run_id": manifest["run_id"],
        "execution_evidence": identity["execution_evidence"],
        "source_commit": identity["source_commit"],
        "graph_sha256": identity["graph_sha256"],
        "model": identity["model"],
        "reasoning_effort": identity["reasoning_effort"],
        "codex_cli_version": identity["codex_cli_version"],
        "code_wiki_cli_version": identity["code_wiki_cli_version"],
        "manifest_evidence_sha256": manifest_evidence_sha256(manifest),
        "invocations": invocations,
        "signature_algorithm": "hmac-sha256-v1" if signing_key else "none",
        "signing_key_sha256": hashlib.sha256(signing_key).hexdigest() if signing_key else None,
        "signature": None,
    }
    if signing_key:
        provenance["signature"] = sign_receipt(provenance, signing_key)
    provenance_path = output_root / "artifacts" / "execution-provenance.json"
    write_json(provenance_path, provenance)
    manifest["output"]["provenance_sha256"] = hash_path(provenance_path)


def run_pilot(
    *,
    mode: str,
    repo: str,
    commit: str,
    out: str,
    model: str,
    reasoning_effort: str,
    title: str | None = None,
    executor_fixture: str | None = None,
    cache_root: str | None = None,
) -> tuple[int, dict[str, Any]]:
    if not model.strip():
        raise RuntimeError("pilot run requires an explicit model")
    if reasoning_effort not in REASONING_EFFORTS:
        raise RuntimeError(f"unsupported reasoning effort: {reasoning_effort}")
    output_root = Path(out).expanduser().resolve()
    source_root = Path(repo).expanduser().resolve()
    if cache_root and not executor_fixture:
        raise RuntimeError("--cache-root is test-only and requires --executor-fixture")
    resolved_cache_root = (
        Path(cache_root).expanduser().resolve()
        if cache_root
        else Path("~/.cache/dotagents/skills/code-wiki/pilot").expanduser().resolve()
    )

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

    if overlaps(resolved_cache_root, source_root):
        raise RuntimeError("pilot cache root must be disjoint from the source repository")
    if overlaps(resolved_cache_root, output_root):
        raise RuntimeError("pilot cache root must be disjoint from the output directory")
    signing_key = (
        None
        if executor_fixture
        else load_or_create_provenance_key(resolved_cache_root)
    )
    try:
        output_root.relative_to(source_root)
    except ValueError:
        pass
    else:
        raise RuntimeError("pilot output must be outside the source repository")
    if output_root.exists() and any(output_root.iterdir()):
        raise RuntimeError(f"pilot output directory must be empty: {output_root}")
    output_root.mkdir(parents=True, exist_ok=True)

    graph = load_graph(skill_root(), mode)
    snapshot = create_snapshot(repo, commit, str(resolved_cache_root))
    executor: CodexExecutor | FixtureExecutor
    if executor_fixture:
        executor = FixtureExecutor(Path(executor_fixture).expanduser().resolve())
    else:
        executor = CodexExecutor(model, reasoning_effort)
    run_id = str(uuid.uuid4())
    manifest = _new_manifest(
        run_id=run_id,
        mode=mode,
        graph=graph,
        snapshot=snapshot,
        output_root=output_root,
        model=model,
        reasoning_effort=reasoning_effort,
        codex_version="fixture-not-invoked" if executor_fixture else _codex_version(),
        execution_evidence="fixture" if executor_fixture else "live",
    )
    _persist(output_root, manifest)
    generation_started = time.monotonic()
    ok = _run_pre_validation_graph(
        graph=graph,
        snapshot=snapshot,
        output_root=output_root,
        title=title or snapshot.original_checkout.name,
        executor=executor,
        manifest=manifest,
    )

    validation_node = next(node for node in graph.nodes.values() if node.node_kind == "validate")
    validation_output = ""
    if ok:
        validation_attempt, validation_status, validation_output = _strict_validate(
            validation_node, snapshot, output_root, 1
        )
        manifest["nodes"][validation_node.node_id]["attempts"].append(validation_attempt)
        manifest["nodes"][validation_node.node_id]["status"] = validation_status
        manifest["validation_status"] = validation_status
        _persist(output_root, manifest)
        if validation_status == "fail":
            repair_contract = next(
                (
                    node
                    for node in graph.nodes.values()
                    if node.node_kind == "agent-repair" and node.repair_target == validation_node.node_id
                ),
                None,
            )
            repair_attempt_number = 1
            if repair_contract is None and validation_node.repair_target:
                repair_contract = graph.nodes[validation_node.repair_target]
                repair_attempt_number = 2
            if repair_contract is None:
                manifest["error"] = "validation failed and graph has no bounded repair node"
            else:
                repair_attempt, repair_result, repair_error = _invoke_agent(
                    executor=executor,
                    node=repair_contract,
                    graph=graph,
                    snapshot=snapshot,
                    output_root=output_root,
                    attempt=repair_attempt_number,
                    validation_feedback=validation_output,
                )
                _mark_agent_result(
                    manifest, repair_contract, repair_attempt, repair_result, repair_error
                )
                if repair_result:
                    validation_attempt, validation_status, validation_output = _strict_validate(
                        validation_node, snapshot, output_root, 2
                    )
                    manifest["nodes"][validation_node.node_id]["attempts"].append(validation_attempt)
                    manifest["nodes"][validation_node.node_id]["status"] = validation_status
                    manifest["validation_status"] = validation_status
                else:
                    ok = False
                _persist(output_root, manifest)

    manifest["metrics"]["generation"]["wall_time_ms"] = max(
        1,
        round((time.monotonic() - generation_started) * 1000),
    )

    if ok and manifest["validation_status"] == "pass":
        reader_node = next(node for node in graph.nodes.values() if node.node_kind == "agent-reader")
        reader_attempt, reader_result, reader_error = _invoke_agent(
            executor=executor,
            node=reader_node,
            graph=graph,
            snapshot=snapshot,
            output_root=output_root,
            attempt=1,
        )
        _mark_agent_result(manifest, reader_node, reader_attempt, reader_result, reader_error)
        if reader_result:
            try:
                manifest["reader_evaluation"] = _load_reader(output_root)
            except RuntimeError as exc:
                manifest["nodes"][reader_node.node_id]["status"] = "fail"
                manifest["error"] = str(exc)
                ok = False
        else:
            ok = False

    validation_path = output_root / "artifacts" / "validation.json"
    if manifest["validation_status"] == "pass" and validation_path.is_file():
        try:
            validation_evidence = json.loads(validation_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            manifest["error"] = f"cannot re-read validation evidence: {exc}"
            ok = False
        else:
            if validation_evidence.get("validated_wiki_sha256") != hash_path(output_root / "wiki"):
                manifest["error"] = "wiki changed after strict validation"
                ok = False

    _finish_source_state(manifest, snapshot)
    if not manifest["source"]["original_checkout_unchanged"] or manifest["source"]["source_mutation"]:
        ok = False
    wiki = output_root / "wiki"
    if wiki.is_dir():
        manifest["output"]["wiki_sha256"] = hash_path(wiki)
    manifest["terminal_status"] = "completed" if ok or manifest["validation_status"] == "fail" else "failed"
    manifest["completed_at"] = utc_now()
    _write_execution_provenance(output_root, manifest, signing_key)
    _persist(output_root, manifest)
    success = (
        manifest["terminal_status"] == "completed"
        and manifest["validation_status"] == "pass"
        and manifest["reader_evaluation"] is not None
    )
    return (0 if success else 1), manifest
