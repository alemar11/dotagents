from __future__ import annotations

import re
from pathlib import Path


EXECUTION_FIELDS = [
    "source_spec_ref",
    "feature_slug",
    "affected_repositories",
    "allowed_paths",
    "target_branch_name",
    "delivery_type",
    "dependency_ids",
]

SPEC_SECTIONS = [
    "Source",
    "Planning Identity",
    "Problem",
    "Goals",
    "Non-Goals",
    "Users And Use Cases",
    "Requirements",
    "Product / Repository Scope",
    "Feature Dependencies",
    "Acceptance Criteria",
    "Validation Expectations",
    "Risks",
    "Open Questions",
    "Issue-Splitting Notes",
]

ISSUE_SECTIONS = [
    "Execution Contract",
    "Goal",
    "Non-Goals",
    "Context",
    "Requirements",
    "Implementation Plan",
    "Acceptance Criteria",
    "Validation",
    "Executor Update Contract",
    "Completion",
]


def sections(contents: str) -> list[str]:
    return re.findall(r"(?m)^## (.+)$", contents)


def section(contents: str, name: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(name)}\n(.*?)(?=^## |\Z)", contents
    )
    if not match:
        raise ValueError(f"missing section: {name}")
    return match.group(1)


def table_rows(contents: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in contents.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if all(re.fullmatch(r"-+", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def checklist(contents: str) -> list[str]:
    return re.findall(r"(?m)^- \[[ xX]\] (.+)$", contents)


def configured_value(repository: Path, section_name: str, canonical: str) -> str:
    mappings = (
        repository / "project-memory/config/triage-labels.md"
    ).read_text(encoding="utf-8")
    mapping_section = section(mappings, section_name)
    for row in table_rows(mapping_section)[1:]:
        if len(row) >= 3 and row[0].strip("`") == canonical:
            if row[1].strip("`") != "local-header":
                raise ValueError(f"{canonical} does not use local-header")
            return row[2].strip("`")
    raise ValueError(f"missing local mapping: {canonical}")


def validate_local_bundle(repository: Path) -> list[str]:
    failures: list[str] = []
    try:
        feature_value = configured_value(repository, "Issue Types", "feature")
        task_value = configured_value(repository, "Issue Types", "task")
        ready_value = configured_value(
            repository, "Workflow States", "ready-for-agent"
        )
    except (OSError, ValueError) as error:
        return [str(error)]

    feature_root = repository / "planning" / "features"
    specs = sorted(feature_root.glob("*/SPEC.md"))
    if not specs:
        return ["no local Feature Specs found"]

    for spec_path in specs:
        feature_slug = spec_path.parent.name
        spec = spec_path.read_text(encoding="utf-8")
        relative_spec = spec_path.relative_to(repository).as_posix()
        prefix = f"{feature_slug}: "

        if not spec.startswith("# Feature Spec: "):
            failures.append(prefix + "invalid Feature Spec title")
        if not re.search(rf"(?m)^issue_type: {re.escape(feature_value)}$", spec):
            failures.append(prefix + "missing local feature type header")
        if any(section_name not in sections(spec) for section_name in SPEC_SECTIONS):
            failures.append(prefix + "missing required Feature Spec section")

        dependency_rows = table_rows(section(spec, "Feature Dependencies"))
        if not dependency_rows or dependency_rows[0] != [
            "upstream_feature_spec_ref",
            "dependency_reason",
        ]:
            failures.append(prefix + "invalid Feature Dependencies table")

        spec_criteria = checklist(section(spec, "Acceptance Criteria"))
        if not spec_criteria or len(spec_criteria) != len(set(spec_criteria)):
            failures.append(prefix + "acceptance criteria are empty or duplicated")
        delivery_match = re.search(
            r"(?m)^- Delivery type: `?(github-pr|local-branch)`?[.]?$",
            section(spec, "Planning Identity"),
        )
        if delivery_match is None:
            failures.append(prefix + "missing or invalid delivery type")
            delivery_type = None
        else:
            delivery_type = delivery_match.group(1)

        issue_paths = sorted((spec_path.parent / "issues").glob("[0-9][0-9]-*.md"))
        if not issue_paths:
            failures.append(prefix + "no implementation issues")
            continue

        issue_ids = {path.name[:2] for path in issue_paths}
        branches: set[str] = set()
        for issue_path in issue_paths:
            issue = issue_path.read_text(encoding="utf-8")
            issue_id = issue_path.name[:2]
            issue_prefix = f"{feature_slug}/{issue_id}: "

            if not issue.startswith(f"# {feature_slug}: {issue_id} "):
                failures.append(issue_prefix + "invalid issue title")
            if not re.search(rf"(?m)^issue_type: {re.escape(task_value)}$", issue):
                failures.append(issue_prefix + "missing task type header")
            if not re.search(
                rf"(?m)^workflow_state: {re.escape(ready_value)}$", issue
            ):
                failures.append(issue_prefix + "missing ready workflow header")
            if any(section_name not in sections(issue) for section_name in ISSUE_SECTIONS):
                failures.append(issue_prefix + "missing required issue section")
                continue

            rows = table_rows(section(issue, "Execution Contract"))
            fields = [row[0].strip("`") for row in rows[1:] if len(row) == 2]
            values = {
                row[0].strip("`"): row[1].strip("`")
                for row in rows[1:]
                if len(row) == 2
            }
            if fields != EXECUTION_FIELDS:
                failures.append(issue_prefix + "invalid Execution Contract fields")
                continue
            if values["source_spec_ref"] != relative_spec:
                failures.append(issue_prefix + "source_spec_ref does not match Spec")
            if values["feature_slug"] != feature_slug:
                failures.append(issue_prefix + "feature_slug mismatch")
            if values["delivery_type"] != delivery_type:
                failures.append(issue_prefix + "delivery_type does not match Spec")

            active = issue_path.relative_to(repository).as_posix()
            done = active.replace("/issues/", "/issues/done/", 1)
            allowed_paths = values["allowed_paths"]
            if active not in allowed_paths or done not in allowed_paths:
                failures.append(issue_prefix + "active/done tracker paths missing from scope")

            dependencies = values["dependency_ids"]
            if dependencies != "none":
                for dependency in (item.strip() for item in dependencies.split(",")):
                    if dependency not in issue_ids or dependency >= issue_id:
                        failures.append(issue_prefix + f"invalid dependency {dependency}")

            branches.add(values["target_branch_name"])
            criteria = checklist(section(issue, "Acceptance Criteria"))
            if not criteria or len(criteria) != len(set(criteria)):
                failures.append(issue_prefix + "acceptance criteria are empty or duplicated")

        if len(branches) != 1:
            failures.append(prefix + "issues do not share one target branch")

    all_markdown = "\n".join(
        path.read_text(encoding="utf-8") for path in feature_root.rglob("*.md")
    )
    if re.search(r"(?:/Users/|/private/tmp/|/home/|[A-Za-z]:\\)", all_markdown):
        failures.append("bundle contains machine-local absolute paths")

    return failures
