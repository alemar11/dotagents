#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import urllib.parse
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
SKILL_DIR = REPO_ROOT / "skills" / "okf"
SKILL_PATH = SKILL_DIR / "SKILL.md"
ASSETS_DIR = SKILL_DIR / "assets"
SPEC_PATH = ASSETS_DIR / "spec.md"
MANIFEST_PATH = ASSETS_DIR / "manifest.json"
REFERENCES_DIR = SKILL_DIR / "references"
SCRIPT_PATH = SKILL_DIR / "scripts" / "okf"
REQUIRED_REFERENCE_FILES = [
    "README.md",
    "writing-okf.md",
    "validation.md",
    "examples.md",
]
MANIFEST_KEYS = {
    "repo",
    "ref",
    "resolved_commit",
    "source_subpath",
    "content_sha256",
    "spec_version",
    "downloaded_at",
    "official_tree_url",
}
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SPEC_VERSION_RE = re.compile(r"(?m)^\*\*Version ([0-9]+\.[0-9]+)\*\*$")
CLI_SPEC_VERSION_RE = re.compile(r'(?m)^SPEC_VERSION = "([0-9]+\.[0-9]+)"$')


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_markdown_links(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8")
    kept: list[str] = []
    in_fence = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(line)
    return [target.strip() for target in MARKDOWN_LINK_RE.findall("\n".join(kept))]


def resolve_local_link(markdown_path: Path, target: str) -> Path:
    decoded = urllib.parse.unquote(target.split("#", 1)[0])
    return (markdown_path.parent / decoded).resolve()


def main() -> int:
    errors: list[str] = []

    for required in [SKILL_PATH, SPEC_PATH, MANIFEST_PATH, SCRIPT_PATH]:
        if not required.exists():
            errors.append(f"Missing required file: {required}")

    if SCRIPT_PATH.exists():
        if not os.access(SCRIPT_PATH, os.X_OK):
            errors.append(f"OKF CLI is not executable: {SCRIPT_PATH}")
        first_line = SCRIPT_PATH.read_text(encoding="utf-8").splitlines()[:1]
        if first_line != ["#!/usr/bin/env python3"]:
            errors.append("OKF CLI must be a direct Python script with a python3 shebang.")

    for name in REQUIRED_REFERENCE_FILES:
        path = REFERENCES_DIR / name
        if not path.exists():
            errors.append(f"Missing OKF reference file: {path}")

    if MANIFEST_PATH.exists():
        manifest = load_json(MANIFEST_PATH)
        extra = set(manifest).difference(MANIFEST_KEYS)
        missing = MANIFEST_KEYS.difference(manifest)
        if extra:
            errors.append(f"Manifest has unexpected keys: {sorted(extra)!r}")
        if missing:
            errors.append(f"Manifest is missing keys: {sorted(missing)!r}")
        expected = {
            "repo": "GoogleCloudPlatform/open-knowledge-format",
            "ref": "main",
            "source_subpath": "SPEC.md",
            "official_tree_url": "https://github.com/GoogleCloudPlatform/open-knowledge-format/tree/main",
        }
        for key, expected_value in expected.items():
            if manifest.get(key) != expected_value:
                errors.append(f"Manifest {key} mismatch: expected {expected_value!r}, got {manifest.get(key)!r}")
        for key in ["resolved_commit", "content_sha256", "spec_version", "downloaded_at"]:
            if not manifest.get(key):
                errors.append(f"Manifest missing required value for {key!r}.")
        if SPEC_PATH.exists():
            spec_match = SPEC_VERSION_RE.search(SPEC_PATH.read_text(encoding="utf-8"))
            if not spec_match:
                errors.append("Bundled spec does not declare a recognizable version.")
            elif manifest.get("spec_version") != spec_match.group(1):
                errors.append(
                    "Manifest spec_version does not match the bundled spec: "
                    f"expected {spec_match.group(1)!r}, got {manifest.get('spec_version')!r}"
                )
        if SCRIPT_PATH.exists():
            cli_match = CLI_SPEC_VERSION_RE.search(SCRIPT_PATH.read_text(encoding="utf-8"))
            if not cli_match:
                errors.append("OKF CLI does not declare SPEC_VERSION.")
            elif manifest.get("spec_version") != cli_match.group(1):
                errors.append(
                    "OKF CLI SPEC_VERSION does not match the manifest: "
                    f"expected {manifest.get('spec_version')!r}, got {cli_match.group(1)!r}"
                )
        if SPEC_PATH.exists() and manifest.get("content_sha256"):
            import hashlib

            local_hash = hashlib.sha256(SPEC_PATH.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
            if local_hash != manifest["content_sha256"]:
                errors.append(
                    f"Bundled spec hash does not match manifest: expected {manifest['content_sha256']!r}, got {local_hash!r}"
                )

    runtime_docs = [SKILL_PATH] + [REFERENCES_DIR / name for name in REQUIRED_REFERENCE_FILES]
    forbidden = [
        ".agents/skills/maintainer",
        "okf_spec_refresh.py",
        "okf_spec_check.py",
        "refresh okf spec",
    ]
    for path in runtime_docs:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in content:
                errors.append(f"Runtime OKF doc {path} should not reference maintainer internals: {marker}")

    allowed_local_targets = {
        SKILL_PATH.resolve(),
        SPEC_PATH.resolve(),
        MANIFEST_PATH.resolve(),
        SCRIPT_PATH.resolve(),
    }
    allowed_local_targets.update((REFERENCES_DIR / name).resolve() for name in REQUIRED_REFERENCE_FILES)
    for path in runtime_docs:
        if not path.exists():
            continue
        for link in iter_markdown_links(path):
            if not link or link.startswith("#") or link.startswith(("http://", "https://", "mailto:")):
                continue
            target = resolve_local_link(path, link)
            if target not in allowed_local_targets:
                errors.append(f"Runtime OKF doc {path.name} links to undeclared local target: {link}")
            elif not target.exists():
                errors.append(f"Broken local link in runtime OKF doc {path.name}: {link}")

    if errors:
        print("OKF spec/reference validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("OKF spec/reference validation passed.")
    print(f"- Spec file: {SPEC_PATH}")
    print(f"- Manifest: {MANIFEST_PATH}")
    print(f"- Runtime CLI: {SCRIPT_PATH}")
    print(f"- Reference files: {', '.join(REQUIRED_REFERENCE_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
