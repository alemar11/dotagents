from __future__ import annotations

import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]


def read(relative: str) -> str:
    return (SKILL_ROOT / relative).read_text(encoding="utf-8")


def root_mapping_boolean(text: str, section: str, field: str) -> bool:
    lines = text.splitlines()
    section_indexes = [
        index for index, line in enumerate(lines) if line == f"{section}:"
    ]
    if len(section_indexes) != 1:
        raise ValueError(f"expected one root {section} mapping")

    field_pattern = re.compile(rf"^(\s*){re.escape(field)}:\s*(true|false)\s*$")
    field_entries = [
        (index, match)
        for index, line in enumerate(lines)
        if not line.lstrip().startswith("#")
        if (match := field_pattern.fullmatch(line))
    ]
    if len(field_entries) != 1:
        raise ValueError(f"expected one {field} boolean")

    section_index = section_indexes[0]
    section_end = next(
        (
            index
            for index in range(section_index + 1, len(lines))
            if lines[index] and not lines[index].startswith((" ", "\t"))
        ),
        len(lines),
    )
    field_index, field_match = field_entries[0]
    if not section_index < field_index < section_end or field_match.group(1) != "  ":
        raise ValueError(f"{field} must be a direct child of root {section}")
    return field_match.group(2) == "true"


def option_registry_rows(path: Path) -> list[tuple[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    rows: list[tuple[str, str]] = []
    for index, line in enumerate(lines):
        if not re.match(r"^\|\s*Field\s*\|\s*Allowed values\s*\|", line):
            continue
        if not line.endswith("|") or line.startswith("||") or line.endswith("||"):
            raise ValueError("malformed registry table header")
        header_cells = [cell.strip() for cell in line[1:-1].split("|")]
        if index + 1 >= len(lines):
            raise ValueError("missing registry table delimiter")
        delimiter = lines[index + 1]
        if (
            not delimiter.startswith("|")
            or not delimiter.endswith("|")
            or delimiter.startswith("||")
            or delimiter.endswith("||")
        ):
            raise ValueError("malformed registry table delimiter")
        delimiter_cells = [
            cell.strip() for cell in delimiter[1:-1].split("|")
        ]
        if len(delimiter_cells) != len(header_cells) or any(
            not re.fullmatch(r":?-{3,}:?", cell) for cell in delimiter_cells
        ):
            if not any(re.fullmatch(r":?-+:?", cell) for cell in delimiter_cells):
                raise ValueError("missing registry table delimiter")
            raise ValueError("malformed registry table delimiter")
        row_count = 0
        for row in lines[index + 2 :]:
            if not row.strip():
                break
            if (
                not row.startswith("|")
                or not row.endswith("|")
                or row.startswith("||")
                or row.endswith("||")
            ):
                raise ValueError(f"malformed registry row {row}")
            cells = [cell.strip() for cell in row[1:-1].split("|")]
            if len(cells) != len(header_cells):
                raise ValueError(f"malformed registry row {row}")
            rows.append(
                (
                    cells[0] if cells else "",
                    cells[1] if len(cells) > 1 else "",
                )
            )
            row_count += 1
        if row_count == 0:
            raise ValueError("registry table has no option rows")
    return rows


def option_registry_failures(option_files: list[Path]) -> list[str]:
    field_pattern = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
    value_pattern = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    failures: list[str] = []
    for path in option_files:
        label = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        try:
            rows = option_registry_rows(path)
        except ValueError as error:
            failures.append(f"{label}: {error}")
            continue
        if not rows:
            failures.append(f"{label}: no option registry rows")
            continue
        for field_cell, values_cell in rows:
            field_match = re.fullmatch(r"`([^`]+)`", field_cell)
            if not field_match:
                failures.append(f"{label}: malformed field cell {field_cell}")
                continue
            field = field_match.group(1)
            if not field_pattern.fullmatch(field):
                failures.append(f"{label}: invalid field {field}")
            values = re.findall(r"`([^`]+)`", values_cell)
            if not values:
                failures.append(f"{label}: {field} has no values")
            if not re.fullmatch(r"`[^`]+`(?:,\s*`[^`]+`)*", values_cell):
                failures.append(f"{label}: {field} has malformed values {values_cell}")
            for value in values:
                if not value_pattern.fullmatch(value):
                    failures.append(f"{label}: {field} has invalid value {value}")
    return failures


class MaintainerContractTests(unittest.TestCase):
    def test_package_identity_is_lowercase_and_aligned(self) -> None:
        self.assertEqual(SKILL_ROOT.name, "maintainer")
        skill = read("SKILL.md")
        self.assertRegex(skill, r"(?m)^name: maintainer$")
        self.assertIn("display_name: \"Maintainer\"", read("agents/openai.yaml"))

    def test_invocation_is_manual_only_and_aligned(self) -> None:
        skill = " ".join(read("SKILL.md").split())
        metadata = read("agents/openai.yaml")
        router = " ".join(read("references/maintenance-router.md").split())
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("This skill is manual-only", skill)
        self.assertIn("Do not auto-select it for ordinary skill", skill)
        self.assertFalse(root_mapping_boolean(metadata, "policy", "allow_implicit_invocation"))
        self.assertIn("This router runs only after the user explicitly invokes", router)
        self.assertIn("must not auto-select this skill", router)
        self.assertIn("Keep `maintainer` manual-only", agents)
        self.assertIn("only repo-level maintainer docs may define explicit", agents)
        self.assertIn("Use `$maintainer` afterward", agents)
        self.assertIn("only when the user explicitly invokes it", agents)
        self.assertIn("During an explicit `$maintainer` run", agents)
        self.assertIn("only when it was explicitly invoked", agents)
        self.assertIn("Manually audit, maintain, and re-engineer repo skills and plugins", readme)
        maintainer_routes = [
            line for line in agents.splitlines() if "$maintainer" in line
        ]
        self.assertGreater(len(maintainer_routes), 5)
        for route in maintainer_routes:
            self.assertIn("explicit", route.lower())

    def test_all_entrypoint_references_exist(self) -> None:
        references = set(re.findall(r"references/([a-z0-9_-]+\.md)", read("SKILL.md")))
        self.assertGreater(len(references), 10)
        missing = sorted(name for name in references if not (SKILL_ROOT / "references" / name).is_file())
        self.assertEqual(missing, [])

    def test_router_and_menu_expose_maintenance_routes(self) -> None:
        router = read("references/maintenance-router.md")
        menu = read("references/task-menu.md")
        for term in ("audit", "workflow-hardening", "package-lifecycle"):
            self.assertIn(term, router)
        self.assertIn("`audit` | Skill/repo health", router)
        self.assertIn("`workflow-hardening` | Sessions, logs, tests", router)
        self.assertIn("`package-lifecycle` | Merge, rename, move", router)
        for task in (
            "audit skill health",
            "harden workflow family",
            "migrate or retire package",
        ):
            self.assertIn(task, menu)

    def test_generic_maintenance_cannot_expand_strategically(self) -> None:
        runbook = read("references/run-maintenance.md")
        router = read("references/maintenance-router.md")
        for term in ("workflow-family hardening", "package migration/retirement", "substantial reshapes"):
            self.assertIn(term, runbook)
        self.assertIn("Do not silently expand generic maintenance", router)

    def test_substantial_reshapes_are_creator_first(self) -> None:
        lifecycle = read("references/package-lifecycle.md")
        upgrade = read("references/skill-upgrade.md")
        for contract in ("$skill-creator", "$plugin-creator"):
            self.assertIn(contract, lifecycle)
            self.assertIn(contract, upgrade)

    def test_runtime_evidence_stays_read_only_until_accepted(self) -> None:
        hardening = read("references/workflow-family-hardening.md")
        normalized = " ".join(hardening.split())
        self.assertIn("$skill-audit", hardening)
        self.assertIn("read-only", hardening)
        self.assertIn("after the finding is accepted", hardening)
        self.assertIn("representative raw session", hardening)
        self.assertIn("reproducible test failure", hardening)
        self.assertIn("may be sufficient", normalized)

    def test_validation_matrix_covers_runtime_and_package_surfaces(self) -> None:
        matrix = read("references/validation-matrix.md")
        for lane in (
            "Runtime skill contract",
            "Composed workflow",
            "Embedded CLI",
            "Plugin",
            "Migration or removal",
            "Non-trivial implementation",
        ):
            self.assertIn(lane, matrix)
        for proof in ("--help", "--version", "--json doctor", "$autoreview"):
            self.assertIn(proof, matrix)
        normalized = " ".join(matrix.split())
        self.assertIn("before/after status", normalized)
        self.assertIn("reinstall introduced no checkout changes", normalized)

    def test_git_mutations_require_explicit_authorization(self) -> None:
        checklist = read("references/release-checklist.md")
        normalized = " ".join(checklist.split())
        self.assertIn("Resolve commit, push, PR, and other publication authority independently", normalized)
        self.assertIn("Otherwise stop after validation", normalized)
        self.assertIn("With explicit commit authority", normalized)
        self.assertIn("With push-only authority, do not stage or commit", normalized)
        self.assertIn("Do not infer commit authority from a bare PR request", normalized)
        self.assertIn("Direct scoped `git` is", normalized)
        self.assertIn("when GitStack is unavailable", normalized)
        self.assertIn("authorized paths plus the staged set are clean", normalized)
        self.assertIn("unrelated pre-existing changes remain unchanged", normalized)
        self.assertIn("global worktree cleanliness is not required", normalized)

    def test_instruction_density_is_a_pre_mutation_mixed_route_gate(self) -> None:
        router = read("references/maintenance-router.md")
        mixed = router.partition("## Mixed Requests")[2].partition("## Task Isolation")[0]
        density = mixed.index("`instruction-density`")
        hardening = mixed.index("`workflow-hardening`")
        lifecycle = mixed.index("`package-lifecycle`")
        maintain = mixed.index("`maintain`")
        self.assertLess(density, hardening)
        self.assertLess(density, lifecycle)
        self.assertLess(density, maintain)
        self.assertIn("stop for approval before mutation", mixed)

    def test_health_route_is_holistic_read_only_and_size_is_diagnostic(self) -> None:
        skill = read("SKILL.md")
        menu = read("references/task-menu.md")
        health = read("references/skill-health.md")
        normalized = " ".join(health.split())

        self.assertIn("references/skill-health.md", skill)
        self.assertIn("audit skill health", menu)
        for area in (
            "structural and policy integrity",
            "metadata and discovery",
            "entrypoint size",
            "reference routing",
            "representative invoked-path cost",
            "applicable validation evidence",
        ):
            self.assertIn(area, " ".join(menu.split()))
        self.assertIn("A direct `audit` request is read-only", normalized)
        for band in ("`normal`", "`review`", "`high-density`", "`over-guideline`"):
            self.assertIn(band, health)
        self.assertIn("Size alone is diagnostic and never produces `result=fail`", normalized)
        self.assertIn("broken active pointers", normalized)
        self.assertIn("unsafe or behavior-breaking policy contradictions", normalized)
        self.assertIn("failed required validation", normalized)

    def test_health_escalates_to_skill_audit_only_on_diagnostic_signals(self) -> None:
        skill = " ".join(read("SKILL.md").split())
        health = " ".join(read("references/skill-health.md").split())

        self.assertIn("Use `$skill-audit` read-only", skill)
        self.assertIn("Invoke `$skill-audit` read-only when any of these signals is present", health)
        for signal in (
            "entrypoint band is not `normal`",
            "description or duplicate candidates appear",
            "instruction sprawl",
            "writing-quality problems",
            "runtime behavior",
            "representative session evidence",
        ):
            self.assertIn(signal, health)

    def test_run_maintenance_consumes_only_safe_health_findings(self) -> None:
        runbook = " ".join(read("references/run-maintenance.md").split())
        health = " ".join(read("references/skill-health.md").split())

        self.assertIn("Run `skill-health.md` read-only", runbook)
        self.assertIn("Rerun `skill-health.md`", runbook)
        self.assertIn("may apply only safe, low-ambiguity findings", health)
        self.assertIn("defer strategic or behavior-sensitive changes", health)

    def test_router_and_release_checklist_own_shared_behavior(self) -> None:
        skill = " ".join(read("SKILL.md").split())
        router = read("references/maintenance-router.md")
        checklist = read("references/release-checklist.md")
        references = list((SKILL_ROOT / "references").glob("*.md"))

        self.assertIn("It owns request routing, mixed-route order, task isolation, delegation", skill)
        self.assertIn("## Delegation", router)
        self.assertIn("## Final Report", checklist)
        self.assertIn("Health evidence", checklist)
        for path in references:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("## Parallel Subagent Pattern", text, path.name)
            self.assertNotIn("## Reporting Contract", text, path.name)

    def test_retired_health_route_has_no_compatibility_alias(self) -> None:
        maintenance_docs = [SKILL_ROOT / "SKILL.md"]
        maintenance_docs.extend((SKILL_ROOT / "references").glob("*.md"))
        combined = "\n".join(path.read_text(encoding="utf-8") for path in maintenance_docs)
        retired_reference = "doc-" + "consistency.md"
        retired_task = "audit " + "consistency"

        self.assertNotIn(retired_reference, combined)
        self.assertNotIn(retired_task, combined)
        self.assertFalse((SKILL_ROOT / "references" / retired_reference).exists())
        self.assertTrue((SKILL_ROOT / "references" / "skill-health.md").is_file())

    def test_lifecycle_commit_split_is_authority_gated(self) -> None:
        lifecycle = " ".join(read("references/package-lifecycle.md").split())
        self.assertIn("When the user explicitly authorizes commits", lifecycle)
        self.assertIn("Without commit authority, report the recommended split", lifecycle)
        self.assertIn("without staging or changing Git history", lifecycle)

    def test_codex_dependencies_are_explicit_and_registered(self) -> None:
        skill = read("SKILL.md")
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        for dependency in ("$skill-audit", "$skill-creator", "$plugin-creator", "$autoreview"):
            self.assertIn(dependency, skill)
            self.assertIn(dependency, readme)
        self.assertIn("`maintainer`", agents.partition("### Codex Dependency Classification")[2])

    def test_no_stale_uppercase_identity_remains(self) -> None:
        candidates = [REPO_ROOT / "AGENTS.md", REPO_ROOT / "README.md"]
        candidates.extend((REPO_ROOT / ".agents" / "skills").rglob("*"))
        stale_patterns = (
            ".agents/skills/" + "Maintainer",
            "$" + "Maintainer",
            "name: " + "Maintainer",
        )
        findings: list[str] = []
        for path in candidates:
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in stale_patterns:
                if pattern in text:
                    findings.append(f"{path.relative_to(REPO_ROOT)}: {pattern}")
        self.assertEqual(findings, [])

    def test_option_registries_use_canonical_field_and_value_syntax(self) -> None:
        option_files = sorted(REPO_ROOT.glob("skills/**/references/options.md"))
        option_files.extend(sorted(REPO_ROOT.glob("plugins/**/references/options.md")))
        option_files.append(SKILL_ROOT / "references" / "options.md")
        expected = {
            REPO_ROOT / "plugins/gitstack/references/options.md",
            REPO_ROOT / "skills/code-wiki/references/options.md",
            REPO_ROOT / "skills/codex-orchestrator/references/options.md",
            REPO_ROOT / "skills/improve-codebase-architecture/references/options.md",
            REPO_ROOT / "skills/plan-feature/references/options.md",
            REPO_ROOT / "skills/plan-harder/references/options.md",
            REPO_ROOT / "skills/postgres/references/options.md",
            REPO_ROOT / "skills/project-memory/references/options.md",
            REPO_ROOT / "skills/triage/references/options.md",
            SKILL_ROOT / "references/options.md",
        }
        self.assertEqual(expected.difference(option_files), set())

        self.assertEqual(option_registry_failures(option_files), [])

    def test_agents_defines_behavior_preserving_compaction_contract(self) -> None:
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        normalized = " ".join(agents.split())

        for contract in (
            "progressive disclosure",
            "one canonical owner",
            "explicit read conditions",
            "decidable from already-loaded content or the target artifact",
            "representative invoked paths",
            "focused contract tests",
        ):
            self.assertIn(contract, normalized)
        self.assertIn("not total repository lines or text moved between files", normalized)
        self.assertIn("trigger, workflow-order, safety, mutation, and output semantics", normalized)

    def test_option_registry_validation_rejects_malformed_rows(self) -> None:
        with TemporaryDirectory() as temp:
            options = Path(temp) / "options.md"
            options.write_text(
                """# Fixture

| Field | Allowed values | Default |
| --- | --- | --- |
| badField | `valid` | none |
| `good_field` | `valid`, prose value | none |
| `missing_delimiter` | `valid` `also-valid` | none |
| `duplicate_delimiter` | `valid`,, `also-valid` | none |
| `missing_values` | | none |
""",
                encoding="utf-8",
            )

            failures = option_registry_failures([options])
            self.assertTrue(any("malformed field cell badField" in item for item in failures))
            malformed_values = [item for item in failures if "malformed values" in item]
            self.assertEqual(len(malformed_values), 4)
            self.assertTrue(any("missing_values has no values" in item for item in failures))

    def test_option_registry_validation_rejects_bad_table_delimiters(self) -> None:
        with TemporaryDirectory() as temp:
            missing = Path(temp) / "missing.md"
            missing.write_text(
                """| Field | Allowed values |
| `badField` | `valid` |
| `good_field` | `valid` |
""",
                encoding="utf-8",
            )
            malformed = Path(temp) / "malformed.md"
            malformed.write_text(
                """| Field | Allowed values |
| -- | --- |
| `good_field` | `valid` |
""",
                encoding="utf-8",
            )
            truncated = Path(temp) / "truncated.md"
            truncated.write_text(
                """| Field | Allowed values | Default | Notes |
| --- | --- |
| `good_field` | `valid` | none | text |
""",
                encoding="utf-8",
            )
            empty = Path(temp) / "empty.md"
            empty.write_text(
                """| Field | Allowed values |
| --- | --- |

No options.
""",
                encoding="utf-8",
            )
            duplicate_outer = Path(temp) / "duplicate-outer.md"
            duplicate_outer.write_text(
                """| Field | Allowed values |
| --- | --- ||
| `good_field` | `valid` |
""",
                encoding="utf-8",
            )
            missing_outer = Path(temp) / "missing-outer.md"
            missing_outer.write_text(
                """| Field | Allowed values |
| --- | ---
| `good_field` | `valid` |
""",
                encoding="utf-8",
            )

            self.assertTrue(
                any(
                    "missing registry table delimiter" in item
                    for item in option_registry_failures([missing])
                )
            )
            self.assertTrue(
                any(
                    "malformed registry table delimiter" in item
                    for item in option_registry_failures([malformed])
                )
            )
            self.assertTrue(
                any(
                    "malformed registry table delimiter" in item
                    for item in option_registry_failures([truncated])
                )
            )
            self.assertTrue(
                any(
                    "registry table has no option rows" in item
                    for item in option_registry_failures([empty])
                )
            )
            for fixture in (duplicate_outer, missing_outer):
                self.assertTrue(
                    any(
                        "malformed registry table delimiter" in item
                        for item in option_registry_failures([fixture])
                    )
                )

    def test_option_registry_validation_rejects_pipe_less_rows(self) -> None:
        with TemporaryDirectory() as temp:
            options = Path(temp) / "options.md"
            options.write_text(
                """| Field | Allowed values | Default |
| --- | --- | --- |
| `good_field` | `valid` | none |
`badField` | `valid` | none

After the table.
""",
                encoding="utf-8",
            )

            self.assertTrue(
                any(
                    "malformed registry row" in item
                    for item in option_registry_failures([options])
                )
            )

    def test_option_registry_validation_rejects_bad_row_boundaries(self) -> None:
        with TemporaryDirectory() as temp:
            duplicate_outer = Path(temp) / "duplicate-outer.md"
            duplicate_outer.write_text(
                """| Field | Allowed values |
| --- | --- |
| `good_field` | `valid` ||
""",
                encoding="utf-8",
            )
            missing_outer = Path(temp) / "missing-outer.md"
            missing_outer.write_text(
                """| Field | Allowed values |
| --- | --- |
| `good_field` | `valid`
""",
                encoding="utf-8",
            )

            for fixture in (duplicate_outer, missing_outer):
                self.assertTrue(
                    any(
                        "malformed registry row" in item
                        for item in option_registry_failures([fixture])
                    )
                )

    def test_closeout_separates_result_from_change_state(self) -> None:
        maintenance_docs = [SKILL_ROOT / "SKILL.md"]
        maintenance_docs.extend((SKILL_ROOT / "references").glob("*.md"))
        combined = "\n".join(path.read_text(encoding="utf-8") for path in maintenance_docs)

        self.assertNotIn("PASS (NOOP)", combined)
        checklist = read("references/release-checklist.md")
        self.assertIn("- `result`: `pass` or `fail`", checklist)
        self.assertIn("- `change_state`: `changed` or `no-change`", checklist)


if __name__ == "__main__":
    unittest.main()
