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
        """Validate the machine-facing package identity and metadata name."""
        self.assertEqual(SKILL_ROOT.name, "maintainer")
        self.assertRegex(read("SKILL.md"), r"(?m)^name: maintainer$")
        self.assertIn('display_name: "Maintainer"', read("agents/openai.yaml"))

    def test_invocation_metadata_is_manual_only(self) -> None:
        """Validate the machine-consumed implicit-invocation policy."""
        metadata = read("agents/openai.yaml")
        self.assertFalse(root_mapping_boolean(metadata, "policy", "allow_implicit_invocation"))

    def test_all_entrypoint_references_exist(self) -> None:
        """Validate SKILL.md reference paths as a structural invariant."""
        references = set(re.findall(r"references/([a-z0-9_-]+\.md)", read("SKILL.md")))
        self.assertGreater(len(references), 10)
        missing = sorted(
            name for name in references if not (SKILL_ROOT / "references" / name).is_file()
        )
        self.assertEqual(missing, [])

    def test_retired_health_route_has_no_compatibility_alias(self) -> None:
        """Validate retired-token absence and the replacement file invariant."""
        maintenance_docs = [SKILL_ROOT / "SKILL.md"]
        maintenance_docs.extend((SKILL_ROOT / "references").glob("*.md"))
        combined = "\n".join(path.read_text(encoding="utf-8") for path in maintenance_docs)
        retired_reference = "doc-" + "consistency.md"
        retired_task = "audit " + "consistency"

        self.assertNotIn(retired_reference, combined)
        self.assertNotIn(retired_task, combined)
        self.assertFalse((SKILL_ROOT / "references" / retired_reference).exists())
        self.assertTrue((SKILL_ROOT / "references" / "skill-health.md").is_file())

    def test_no_stale_uppercase_identity_remains(self) -> None:
        """Validate absence of retired package identity tokens."""
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
        """Validate the parsed field/value registry contract across packages."""
        option_files = sorted(REPO_ROOT.glob("skills/**/references/options.md"))
        option_files.extend(sorted(REPO_ROOT.glob("plugins/**/references/options.md")))
        option_files.append(SKILL_ROOT / "references" / "options.md")
        expected = {
            REPO_ROOT / "plugins/gitstack/references/options.md",
            REPO_ROOT / "skills/code-wiki/references/options.md",
            REPO_ROOT / "skills/implement-feature/references/options.md",
            REPO_ROOT / "skills/improve-codebase-architecture/references/options.md",
            REPO_ROOT / "skills/plan-feature/references/options.md",
            REPO_ROOT / "skills/plan-harder/references/options.md",
            REPO_ROOT / "skills/postgres/references/options.md",
            REPO_ROOT / "skills/project-memory/references/options.md",
            SKILL_ROOT / "references/options.md",
        }
        self.assertEqual(expected.difference(option_files), set())
        self.assertEqual(option_registry_failures(option_files), [])

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


if __name__ == "__main__":
    unittest.main()
