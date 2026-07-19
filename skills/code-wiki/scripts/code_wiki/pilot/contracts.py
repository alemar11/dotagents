"""Strict Markdown node contracts for the Code Wiki pilot."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


FIELD_NAMES = (
    "node_id",
    "node_kind",
    "dependencies",
    "input_artifacts",
    "output_artifacts",
    "repair_target",
)
ALLOWED_NODE_KINDS = {
    "prepare",
    "agent-baseline",
    "agent-study",
    "agent-synthesize",
    "agent-render",
    "validate",
    "agent-repair",
    "agent-reader",
}
IDENTIFIER_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ContractError(ValueError):
    """Raised when a node document violates the pilot contract."""


@dataclass(frozen=True)
class NodeContract:
    node_id: str
    node_kind: str
    dependencies: tuple[str, ...]
    input_artifacts: tuple[str, ...]
    output_artifacts: tuple[str, ...]
    repair_target: str | None
    instructions: str
    path: Path
    sha256: str


@dataclass(frozen=True)
class GraphContract:
    mode: str
    nodes: dict[str, NodeContract]
    graph_sha256: str

    @property
    def node_hashes(self) -> dict[str, str]:
        return {node_id: node.sha256 for node_id, node in sorted(self.nodes.items())}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _strip_code(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        return value[1:-1].strip()
    return value


def _list_value(value: str, field: str) -> tuple[str, ...]:
    raw = _strip_code(value)
    if raw == "none":
        return ()
    values = tuple(_strip_code(item) for item in value.split(","))
    if not values or any(not item for item in values):
        raise ContractError(f"{field} must be a comma-separated list or none")
    if len(values) != len(set(values)):
        raise ContractError(f"{field} contains duplicate values")
    return values


def _validate_artifact(value: str, field: str) -> None:
    if value == "source":
        return
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or value.startswith("."):
        raise ContractError(f"{field} contains unsafe artifact path: {value}")
    if value != path.as_posix():
        raise ContractError(f"{field} must use canonical POSIX paths: {value}")


def parse_node(path: Path) -> NodeContract:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    fields: dict[str, str] = {}
    instructions_marker = "## Instructions"
    if instructions_marker not in text:
        raise ContractError(f"{path}: missing {instructions_marker}")

    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) != 2:
            continue
        key = _strip_code(columns[0])
        if key in {"Field", "---"} or set(key) == {"-"}:
            continue
        if key not in FIELD_NAMES:
            raise ContractError(f"{path}: unsupported contract field: {key}")
        if key in fields:
            raise ContractError(f"{path}: duplicate contract field: {key}")
        fields[key] = columns[1]

    missing = [field for field in FIELD_NAMES if field not in fields]
    if missing:
        raise ContractError(f"{path}: missing contract fields: {', '.join(missing)}")

    node_id = _strip_code(fields["node_id"])
    node_kind = _strip_code(fields["node_kind"])
    dependencies = _list_value(fields["dependencies"], "dependencies")
    input_artifacts = _list_value(fields["input_artifacts"], "input_artifacts")
    output_artifacts = _list_value(fields["output_artifacts"], "output_artifacts")
    repair_value = _strip_code(fields["repair_target"])
    repair_target = None if repair_value == "none" else repair_value

    if not IDENTIFIER_RE.fullmatch(node_id):
        raise ContractError(f"{path}: noncanonical node_id: {node_id}")
    if path.stem != node_id:
        raise ContractError(f"{path}: filename must match node_id {node_id}")
    if node_kind not in ALLOWED_NODE_KINDS:
        raise ContractError(f"{path}: unsupported node_kind: {node_kind}")
    for dependency in dependencies:
        if not IDENTIFIER_RE.fullmatch(dependency):
            raise ContractError(f"{path}: noncanonical dependency: {dependency}")
    if repair_target and not IDENTIFIER_RE.fullmatch(repair_target):
        raise ContractError(f"{path}: noncanonical repair_target: {repair_target}")
    for value in (*input_artifacts, *output_artifacts):
        _validate_artifact(value, "artifact contract")
    if "source" in output_artifacts:
        raise ContractError(f"{path}: source is read-only and cannot be an output")

    instructions = text.split(instructions_marker, 1)[1].strip()
    if not instructions:
        raise ContractError(f"{path}: instructions must not be empty")
    return NodeContract(
        node_id=node_id,
        node_kind=node_kind,
        dependencies=dependencies,
        input_artifacts=input_artifacts,
        output_artifacts=output_artifacts,
        repair_target=repair_target,
        instructions=instructions,
        path=path,
        sha256=sha256_bytes(raw),
    )


def _dependency_closure(node_id: str, nodes: dict[str, NodeContract]) -> set[str]:
    found: set[str] = set()
    pending = list(nodes[node_id].dependencies)
    while pending:
        current = pending.pop()
        if current in found:
            continue
        found.add(current)
        pending.extend(nodes[current].dependencies)
    return found


def _validate_graph(nodes: dict[str, NodeContract]) -> None:
    for node in nodes.values():
        for dependency in node.dependencies:
            if dependency not in nodes:
                raise ContractError(f"{node.path}: missing dependency: {dependency}")
        if node.repair_target and node.repair_target not in nodes:
            raise ContractError(f"{node.path}: missing repair_target: {node.repair_target}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise ContractError(f"dependency cycle includes {node_id}")
        if node_id in visited:
            return
        visiting.add(node_id)
        for dependency in nodes[node_id].dependencies:
            visit(dependency)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in nodes:
        visit(node_id)

    producers: dict[str, set[str]] = {}
    for node in nodes.values():
        for artifact in node.output_artifacts:
            producers.setdefault(artifact, set()).add(node.node_id)
    for node in nodes.values():
        closure = _dependency_closure(node.node_id, nodes)
        if node.repair_target:
            closure.add(node.repair_target)
        for artifact in node.input_artifacts:
            if artifact == "source":
                continue
            if not (producers.get(artifact, set()) & closure):
                raise ContractError(
                    f"{node.path}: input artifact has no dependency-owned producer: {artifact}"
                )

    repair_nodes = [node for node in nodes.values() if node.repair_target]
    if len(repair_nodes) != 1:
        raise ContractError("each graph must declare exactly one bounded repair edge")
    repair_node = repair_nodes[0]
    if repair_node.node_kind not in {"validate", "agent-repair"}:
        raise ContractError("repair_target is allowed only on validate or agent-repair nodes")


def load_graph(skill_root: Path, mode: str) -> GraphContract:
    if mode not in {"baseline", "node-graph"}:
        raise ContractError(f"unsupported pilot mode: {mode}")
    graph_root = skill_root / "references" / "pilot-nodes" / mode
    paths = sorted(graph_root.glob("*.md"))
    if not paths:
        raise ContractError(f"no node contracts found for {mode}: {graph_root}")
    nodes: dict[str, NodeContract] = {}
    for path in paths:
        node = parse_node(path)
        if node.node_id in nodes:
            raise ContractError(f"duplicate node_id: {node.node_id}")
        nodes[node.node_id] = node
    _validate_graph(nodes)
    graph_material = "".join(
        f"{node.path.name}\0{node.sha256}\n" for node in sorted(nodes.values(), key=lambda item: item.node_id)
    ).encode("utf-8")
    return GraphContract(mode=mode, nodes=nodes, graph_sha256=sha256_bytes(graph_material))
