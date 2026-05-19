"""Repository inventory support for the code-wiki helper."""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path

from common import (
    CODE_EXTENSIONS,
    DOC_NAMES,
    ENTRYPOINT_NAMES,
    EXT_LANGUAGE,
    GENERATED_DOC_PARTS,
    GOVERNANCE_DOC_NAMES,
    INTERFACE_DIR_NAMES,
    INTERFACE_EXTENSIONS,
    MANIFEST_NAMES,
    NOISY_SOURCE_PARTS,
    OPS_ROOT_PARTS,
    SKIP_DIR_NAMES,
    TEST_DIR_NAMES,
    VENDORED_ROOT_PARTS,
    git_metadata,
    normalize_rel,
    utc_now,
)

def iter_repo_files(repo: Path) -> list[str]:
    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [
            name
            for name in dirnames
            if name not in SKIP_DIR_NAMES and not name.endswith(".egg-info")
        ]
        current = Path(dirpath)
        for filename in filenames:
            full_path = current / filename
            if full_path.is_symlink():
                continue
            rel = full_path.relative_to(repo)
            if any(part in SKIP_DIR_NAMES for part in rel.parts):
                continue
            files.append(normalize_rel(rel))
    return sorted(files)


def paths_containing_parts(files: list[str], names: set[str]) -> list[str]:
    found: set[str] = set()
    normalized_names = {name.lower() for name in names}
    for file_path in files:
        parts = Path(file_path).parts[:-1]
        for index, part in enumerate(parts):
            if part.lower() in normalized_names:
                found.add("/".join(parts[: index + 1]))
                break
    return sorted(found)


def is_code_file(path: str) -> bool:
    return Path(path).suffix.lower() in CODE_EXTENSIONS


def lower_parts(path: str) -> tuple[str, ...]:
    return tuple(part.lower() for part in Path(path).parts)


def is_noisy_part(part: str) -> bool:
    return part in NOISY_SOURCE_PARTS or part.startswith(("template", "fixture", "sample"))


def has_noisy_source_part(path: str) -> bool:
    return any(is_noisy_part(part) for part in lower_parts(path))


def is_vendored_path(path: str) -> bool:
    parts = lower_parts(path)
    return bool(parts and parts[0] in VENDORED_ROOT_PARTS)


def is_generated_doc_path(path: str) -> bool:
    parts = lower_parts(path)
    if not parts:
        return False
    if parts[0] == "docs" and len(parts) >= 2:
        if parts[1] in GENERATED_DOC_PARTS or parts[1] in {"css", "img", "js"}:
            return True
        if Path(path).suffix.lower() in {".css", ".html", ".js", ".json", ".svg"}:
            return True
    return any(part.endswith(".docset") for part in parts)


def first_part_index(parts: tuple[str, ...], names: set[str]) -> int | None:
    normalized = {name.lower() for name in names}
    for index, part in enumerate(parts):
        if part.lower() in normalized:
            return index
    return None


def detect_source_roots(files: list[str]) -> list[str]:
    roots: set[str] = set()
    root_level_code = 0
    has_go_mod = "go.mod" in files
    has_python_manifest = any(
        manifest in files
        for manifest in ("pyproject.toml", "setup.py", "setup.cfg")
    )

    for path in files:
        if not is_code_file(path) or is_vendored_path(path) or has_noisy_source_part(path):
            continue
        parts = Path(path).parts
        lowered = tuple(part.lower() for part in parts)
        if len(parts) == 1:
            root_level_code += 1
            continue

        # Common monorepo package layouts should point at the package source,
        # not the whole packages/ or crates/ tree.
        if len(parts) >= 4 and lowered[0] in {"packages", "crates"} and lowered[2] in {"src", "lib"}:
            roots.add("/".join(parts[:3]))
            continue
        if len(parts) >= 3 and lowered[0] == "crates" and parts[-1].lower() in ENTRYPOINT_NAMES:
            roots.add("/".join(parts[:2]))
            continue

        source_index = first_part_index(parts[:-1], {"Source", "Sources", "source", "sources", "src", "lib"})
        if source_index is not None:
            roots.add("/".join(parts[: source_index + 1]))
            continue

        if lowered[0] in {"app", "apps", "cmd", "internal", "pkg", "server"}:
            roots.add(parts[0] if len(parts) < 3 else "/".join(parts[:2]))

    if has_go_mod and root_level_code >= 3:
        roots.add(".")
        roots = {root for root in roots if root == "." or not root.startswith(("internal/", "pkg/"))}

    if has_python_manifest:
        for path in files:
            parts = Path(path).parts
            lowered = lower_parts(path)
            if len(parts) < 2 or parts[-1] != "__init__.py":
                continue
            if is_vendored_path(path) or has_noisy_source_part(path):
                continue
            if lowered[0] in {"docs", "examples", "sample", "samples", "scripts", "test", "tests"}:
                continue
            if lowered[0] == "src" and len(parts) >= 3:
                roots.add("/".join(parts[:2]))
            else:
                roots.add(parts[0])

    return sorted(roots, key=lambda value: (value == ".", value.lower()))


def detect_interface_roots(files: list[str]) -> list[str]:
    roots: set[str] = set()
    for path in files:
        if (
            Path(path).suffix.lower() not in INTERFACE_EXTENSIONS
            or is_vendored_path(path)
            or has_noisy_source_part(path)
        ):
            continue
        parts = Path(path).parts
        interface_index = first_part_index(parts[:-1], INTERFACE_DIR_NAMES)
        if interface_index is not None:
            roots.add("/".join(parts[: interface_index + 1]) or ".")
    return sorted(roots)


def test_root_for_path(path: str) -> str | None:
    parts = Path(path).parts
    lowered = tuple(part.lower() for part in parts)
    if not parts or is_vendored_path(path):
        return None

    for index, part in enumerate(lowered[:-1]):
        if part in {name.lower() for name in TEST_DIR_NAMES}:
            if part == "features" and Path(path).suffix.lower() != ".feature":
                continue
            if lowered[0] == "playground":
                return "playground"
            return "/".join(parts[: index + 1]) or "."

    name = Path(path).name.lower()
    suffix = Path(path).suffix.lower()
    is_test_file = (
        name.endswith("_test.go")
        or name.endswith("_test.rb")
        or name.endswith("_spec.rb")
        or name.endswith(".feature")
        or name.startswith("test_") and suffix == ".py"
        or ".test." in name
        or ".spec." in name
    )
    if not is_test_file:
        return None
    if lowered[0] == "playground":
        return "playground"
    parent = Path(path).parent.as_posix()
    return "." if parent == "." else parent


def detect_test_roots(files: list[str]) -> list[str]:
    roots = {root for path in files if (root := test_root_for_path(path))}
    if "go.mod" in files and "." in roots:
        roots = {"."}
    return sorted(roots, key=lambda value: (value == ".", value.lower()))


def detect_special_roots(files: list[str], names: set[str]) -> list[str]:
    normalized = {name.lower() for name in names}
    roots: set[str] = set()
    for path in files:
        parts = Path(path).parts[:-1]
        for index, part in enumerate(parts):
            if part.lower() in normalized:
                roots.add("/".join(parts[: index + 1]) or ".")
                break
    return sorted(roots)


def detect_generated_doc_roots(files: list[str]) -> list[str]:
    roots: set[str] = set()
    for path in files:
        if not is_generated_doc_path(path):
            continue
        parts = Path(path).parts
        lowered = lower_parts(path)
        if lowered[0] == "docs":
            roots.add("docs")
            if len(parts) >= 2 and lowered[1] == "docsets":
                roots.add("docs/docsets")
            continue
        for index, part in enumerate(lowered):
            if part.endswith(".docset"):
                roots.add("/".join(parts[: index + 1]))
                break
    return sorted(roots)


def detect_governance_docs(files: list[str]) -> list[str]:
    docs: list[str] = []
    for path in files:
        if is_vendored_path(path):
            continue
        name = Path(path).name.lower()
        stem = Path(path).stem.lower()
        if name == "codeowners" or stem in GOVERNANCE_DOC_NAMES or name in {"copying", "license"}:
            docs.append(path)
    return sorted(docs)


def classify_roots(
    files: list[str],
    source_roots: list[str],
    test_roots: list[str],
    interface_roots: list[str],
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(root: str, kind: str, reason: str) -> None:
        key = (root, kind)
        if key in seen:
            return
        seen.add(key)
        candidates.append({"root": root, "kind": kind, "reason": reason})

    for root in source_roots:
        add(root, "source", "primary source root")
    for root in interface_roots:
        add(root, "interfaces", "public headers or API interface root")
    for root in test_roots:
        add(root, "test", "test root or language-specific test file layout")
    for root in detect_special_roots(files, {"docs", "documentation"}):
        add(root, "docs", "documentation root")
    for root in detect_generated_doc_roots(files):
        add(root, "generated-docs", "generated API documentation or docset root")
    for root in detect_special_roots(files, {"example", "examples", "sample", "samples"}):
        add(root, "examples", "example or sample code root")
    for root in detect_special_roots(files, {"playground", "playgrounds", "fixture", "fixtures", "testdata"}):
        add(root, "fixtures", "fixture, playground, or test data root")
    for root in detect_special_roots(files, OPS_ROOT_PARTS):
        add(root, "ops", "CI, automation, or repository operations root")
    for root in detect_special_roots(files, VENDORED_ROOT_PARTS):
        add(root, "vendored", "vendored or bundled dependency root")

    return sorted(candidates, key=lambda item: (item["kind"], item["root"]))


def is_manifest_path(path: str) -> bool:
    name = Path(path).name
    lower_name = name.lower()
    return (
        lower_name in {manifest.lower() for manifest in MANIFEST_NAMES}
        or lower_name in {"makefile", "rakefile", "justfile", "gemfile.lock", "go.sum", "cargo.lock"}
        or lower_name.startswith("readme.")
        or Path(path).suffix.lower() in {".csproj", ".fsproj", ".gemspec", ".sln"}
    )


def primary_manifests(manifests: list[str]) -> list[str]:
    primary: list[str] = []
    for path in manifests:
        parts = lower_parts(path)
        if any(
            part in VENDORED_ROOT_PARTS
            or is_noisy_part(part)
            or part.startswith(".")
            or part in {"docs", "documentation", "examples", "playground", "playgrounds", "fixtures", "testdata"}
            for part in parts
        ):
            continue
        if len(parts) <= 3:
            primary.append(path)
    return primary[:50]


def detect_entrypoints(files: list[str]) -> list[str]:
    entrypoints: list[str] = []
    for path in files:
        if is_vendored_path(path) or has_noisy_source_part(path):
            continue
        parts = Path(path).parts
        name = Path(path).name.lower()
        if (
            name in ENTRYPOINT_NAMES
            or re.search(r"(^|/)(cli|server|main|index)\.[cm]?[jt]sx?$", path)
            or (len(parts) >= 2 and parts[0] in {"bin", "exe"} and not Path(path).name.startswith("."))
        ):
            entrypoints.append(path)
    return entrypoints[:100]


def is_doc_path(path: str) -> bool:
    if is_generated_doc_path(path):
        return False
    name = Path(path).name
    name_upper = name.upper()
    return (
        name in DOC_NAMES
        or name_upper in {doc.upper() for doc in DOC_NAMES}
        or name.lower().startswith("readme.")
        or name_upper.startswith(("LICENSE.", "NOTICE.", "COPYING."))
        or path.startswith("docs/")
        or path.startswith("documentation/")
    )


def build_inventory(repo_arg: str) -> dict[str, object]:
    repo = Path(repo_arg).expanduser().resolve()
    if not repo.is_dir():
        raise SystemExit(f"repo is not a directory: {repo}")

    files = iter_repo_files(repo)
    extensions = Counter(Path(path).suffix.lower() or "[no extension]" for path in files)
    languages = Counter()
    for path in files:
        suffix = Path(path).suffix.lower()
        languages[EXT_LANGUAGE.get(suffix, "Other")] += 1

    manifests = [path for path in files if is_manifest_path(path)]
    docs = [
        path
        for path in files
        if is_doc_path(path)
    ]
    source_roots = detect_source_roots(files)
    test_roots = detect_test_roots(files)
    interface_roots = detect_interface_roots(files)
    entrypoints = detect_entrypoints(files)

    metadata = git_metadata(repo)

    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "repo": {
            "path": str(repo),
            "name": repo.name,
            **metadata,
        },
        "counts": {
            "files": len(files),
            "extensions": dict(sorted(extensions.items())),
            "languages": dict(sorted(languages.items())),
        },
        "manifests": manifests,
        "primary_manifests": primary_manifests(manifests),
        "source_roots": source_roots,
        "interface_roots": interface_roots,
        "test_roots": test_roots,
        "root_candidates": classify_roots(files, source_roots, test_roots, interface_roots),
        "docs": docs,
        "governance_docs": detect_governance_docs(files),
        "entrypoint_candidates": entrypoints,
        "sample_files": files[:250],
    }


def write_json(path_arg: str, data: dict[str, object]) -> None:
    path = Path(path_arg).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
