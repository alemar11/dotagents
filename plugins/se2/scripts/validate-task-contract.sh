#!/usr/bin/env bash
set -euo pipefail

# Static-only package validation. This script never probes the ChatGPT/Codex
# application and cannot establish live task creation or monitoring capacity.
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
plugin_root="$(cd -- "${script_dir}/.." && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required for static SE2 contract validation" >&2
  exit 2
fi

python3 - "${plugin_root}" <<'PY'
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


root = Path(sys.argv[1]).resolve()
errors: list[str] = []


def require_file(relative: str) -> Path:
    path = root / relative
    if not path.is_file():
        errors.append(f"missing file: {relative}")
    return path


manifest_path = require_file(".codex-plugin/plugin.json")
manifest = None
if manifest_path.is_file():
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"invalid manifest JSON: {error}")

if isinstance(manifest, dict):
    if manifest.get("name") != "se2":
        errors.append("manifest name must be se2")
    if manifest.get("skills") != "./skills/":
        errors.append("manifest skills path must be ./skills/")
    version = manifest.get("version")
    if not isinstance(version, str) or not re.fullmatch(
        r"\d+\.\d+\.\d+(?:\+codex\.[A-Za-z0-9._-]+)?", version
    ):
        errors.append("manifest version must be semantic major.minor.patch with an optional Codex cachebuster")


def read(relative: str) -> str:
    path = require_file(relative)
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"cannot read {relative}: {error}")
        return ""


preflight = read("references/task-preflight.md")
handoff = read("references/task-handoff.md")
feature = read("skills/feature/SKILL.md")
implement = read("skills/implement/SKILL.md")
feature_profile = read("skills/feature/references/task-profile.md")
implement_profile = read("skills/implement/references/task-profile.md")
feature_meta = read("skills/feature/agents/openai.yaml")
implement_meta = read("skills/implement/agents/openai.yaml")

common_contract = f"{preflight}\n{handoff}"
if re.search(r"gpt-5\.6-|reasoning:\s*(?:medium|max)|topology:\s*[a-z]", common_contract):
    errors.append("root task references must not select a model, reasoning level, or topology")
for required in ("unsupported-runtime", "roles_verified", "github_mutation"):
    if required not in preflight:
        errors.append(f"task-preflight.md is missing common gate: {required}")
for required in ("task_identity", "kind: partial", "kind: final", "reconciliation"):
    if required not in handoff:
        errors.append(f"task-handoff.md is missing common evidence: {required}")
for required in (
    "<emoji> <outcome specific>",
    "exactly one contextual emoji",
    "display metadata only",
    "title-unverified",
    "title-drift",
    "duplicate task",
):
    if required not in handoff:
        errors.append(f"task-handoff.md is missing title rule: {required}")

for name, content in (("task-preflight", preflight), ("task-handoff", handoff)):
    if not content.startswith("# "):
        errors.append(f"{name} reference must start with a Markdown heading")

for name, content in (("feature", feature), ("implement", implement)):
    if not content.startswith("---\n") or "\n---\n" not in content[4:]:
        errors.append(f"{name} skill is missing standard front matter")
    if "../../references/task-preflight.md" not in content:
        errors.append(f"{name} skill does not reference task-preflight.md")
    if "../../references/task-handoff.md" not in content:
        errors.append(f"{name} skill does not reference task-handoff.md")
    profile_ref = "references/task-profile.md"
    if profile_ref not in content:
        errors.append(f"{name} skill does not reference its task-profile.md")

if (
    "role: planner" not in feature_profile
    or "gpt-5.6-sol" not in feature_profile
    or "reasoning: medium" not in feature_profile
    or "topology: single-planner-task" not in feature_profile
    or 'title_template: "🤖 Plan Feature · <Feature outcome>"' not in feature_profile
):
    errors.append("feature task profile must define the Sol/medium planner and title")
if (
    "role: orchestrator" not in implement_profile
    or "gpt-5.6-sol" not in implement_profile
    or "reasoning: medium" not in implement_profile
    or "role: worker" not in implement_profile
    or "gpt-5.6-luna" not in implement_profile
    or "reasoning: max" not in implement_profile
    or 'title_template: "🤖 Implement Feature · <Feature outcome>"' not in implement_profile
    or 'title_template: "🛠️ Implement Task · <Task outcome>"' not in implement_profile
):
    errors.append("implement task profile must define roles and canonical titles")
if "unsupported-runtime" not in implement or "topology" not in implement.lower():
    errors.append("implement skill must fail closed for unsupported runtime profiles")
for name, content in (("feature", feature_meta), ("implement", implement_meta)):
    if "allow_implicit_invocation: false" not in content:
        errors.append(f"{name} metadata must disable implicit invocation")

mermaid_match = re.search(r"~~~mermaid\n(.*?)\n~~~", feature, re.DOTALL)
if not mermaid_match:
    errors.append("feature skill must contain a fenced Mermaid graph")
elif re.search(r"\b(?:preview|publish)\b", mermaid_match.group(1), re.IGNORECASE):
    errors.append("preview/publish must not be visible Mermaid graph nodes or edges")

if errors:
    for error in errors:
        print(error, file=sys.stderr)
    raise SystemExit(1)

print(f"Static SE2 task contract validation passed: {root}")
PY
