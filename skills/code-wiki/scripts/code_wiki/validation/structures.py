"""Required table and page-structure validation."""

from __future__ import annotations

import re

from code_wiki.validation.content import is_deep_dive_content_page
from code_wiki.validation.text import main_html_fragment, table_texts, visible_text


def any_table_has(table_values: list[str], groups: tuple[tuple[str, ...], ...]) -> bool:
    for table_value in table_values:
        if all(any(term in table_value for term in group) for group in groups):
            return True
    return False


def validate_required_table(
    html_rel_path: str,
    table_values: list[str],
    groups: tuple[tuple[str, ...], ...],
    label: str,
    errors: list[str],
) -> None:
    if not table_values:
        errors.append(f"{html_rel_path} is missing required {label} table")
        return
    if not any_table_has(table_values, groups):
        readable = ", ".join("/".join(group) for group in groups)
        errors.append(f"{html_rel_path} {label} table is missing required columns/concepts: {readable}")


def validate_required_structures(
    html_rel_path: str,
    text: str,
    inventory: dict[str, object],
    errors: list[str],
    warnings: list[str],
) -> None:
    tables = table_texts(text)
    main_text = visible_text(text).lower()

    if html_rel_path == "pages/project-context.html":
        validate_required_table(
            html_rel_path,
            tables,
            (
                ("use case", "capability", "scenario", "user", "audience"),
                ("surface", "entry", "api", "command", "package", "route", "module"),
                ("constraint", "responsibility", "owner", "license", "security", "support"),
            ),
            "project context/use-case",
            errors,
        )
        if "where to go" not in main_text and "official" not in main_text and "upstream" not in main_text:
            warnings.append(f"{html_rel_path} should route readers to official/upstream docs when the repo provides them")

    elif html_rel_path == "pages/public-interfaces.html":
        validate_required_table(
            html_rel_path,
            tables,
            (
                ("surface", "api", "command", "route", "package", "module", "export"),
                ("consumer", "entry", "caller", "usage"),
                ("owner", "file", "module", "path"),
                ("stability", "contract", "public", "internal"),
            ),
            "public surface matrix",
            errors,
        )

    elif html_rel_path == "pages/runtime-state.html":
        validate_required_table(
            html_rel_path,
            tables,
            (
                ("state", "carrier", "lifecycle", "object", "store", "context"),
                ("create", "owner", "initialize", "allocated"),
                ("mutate", "update", "write", "change"),
                ("observe", "callback", "read", "event"),
                ("cleanup", "shutdown", "destroy", "release"),
            ),
            "state/lifecycle",
            errors,
        )

    elif html_rel_path == "pages/flows-advanced.html":
        validate_required_table(
            html_rel_path,
            tables,
            (
                ("trigger", "failure", "condition", "edge"),
                ("detect", "branch", "function", "check"),
                ("owner", "cleanup", "handler"),
                ("effect", "status", "error", "callback", "event"),
                ("recover", "retry", "fallback", "abort", "rollback"),
            ),
            "failure-path",
            errors,
        )

    elif html_rel_path == "pages/testing-and-ops.html":
        validate_required_table(
            html_rel_path,
            tables,
            (
                ("task", "change", "scenario"),
                ("command", "run", "script"),
                ("when", "scope", "source"),
                ("expected", "signal", "artifact", "output"),
            ),
            "exact command",
            errors,
        )
        if not re.search(r"<pre\b|<code\b", main_html_fragment(text), re.IGNORECASE):
            errors.append(f"{html_rel_path} must include copy-paste validation commands in code/pre markup")

    elif html_rel_path == "pages/change-guide.html":
        validate_required_table(
            html_rel_path,
            tables,
            (
                ("change", "task"),
                ("compatibility", "risk", "public", "breaking"),
                ("validation", "test", "command"),
                ("rollback", "backout", "revert"),
            ),
            "compatibility/rollback",
            errors,
        )

    elif html_rel_path == "pages/source-map.html":
        if "generated" not in main_text:
            warnings.append(f"{html_rel_path} should classify generated artifacts or state that none were found")
        if "vendor" not in main_text and "third-party" not in main_text and "third party" not in main_text:
            warnings.append(f"{html_rel_path} should classify vendored or third-party code, or state that none was found")

    if is_deep_dive_content_page(html_rel_path):
        if not any(term in main_text for term in ("state", "flow", "entry", "change", "test", "risk")):
            warnings.append(f"{html_rel_path} should name entrypoints, state/flow, change risks, and tests")

