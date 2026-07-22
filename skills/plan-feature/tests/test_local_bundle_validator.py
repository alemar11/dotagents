from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from local_bundle_validator import validate_local_bundle


SPEC = """# Feature Spec: Probe

issue_type: feature

## Source
probe
## Planning Identity
- Delivery type: `local-branch`.
## Problem
probe
## Goals
probe
## Non-Goals
probe
## Users And Use Cases
probe
## Requirements
probe
## Product / Repository Scope
probe
## Feature Dependencies
| upstream_feature_spec_ref | dependency_reason |
| --- | --- |
## Acceptance Criteria
- [ ] The probe works.
## Validation Expectations
probe
## Risks
probe
## Open Questions
none
## Issue-Splitting Notes
probe
"""

ISSUE = """# probe: 01 Deliver probe

issue_type: task
workflow_state: ready-for-agent

## Execution Contract
| Field | Value |
| --- | --- |
| `source_spec_ref` | `planning/features/probe/SPEC.md` |
| `feature_slug` | `probe` |
| `affected_repositories` | `current-repository` |
| `allowed_paths` | `src/`; `planning/features/probe/issues/01-deliver-probe.md`; `planning/features/probe/issues/done/01-deliver-probe.md` |
| `target_branch_name` | `feature/probe` |
| `delivery_type` | `local-branch` |
| `dependency_ids` | `none` |
## Goal
probe
## Non-Goals
probe
## Context
probe
## Requirements
probe
## Implementation Plan
probe
## Acceptance Criteria
- [ ] The issue proves the probe.
## Validation
probe
## Executor Update Contract
probe
## Completion
probe
"""


class LocalBundleValidatorTests(unittest.TestCase):
    def write_bundle(self, root: Path, *, spec: str = SPEC, issue: str = ISSUE) -> None:
        bundle = root / "planning/features/probe"
        issues = bundle / "issues"
        issues.mkdir(parents=True)
        mappings = root / "project-memory/config"
        mappings.mkdir(parents=True)
        (mappings / "triage-labels.md").write_text(
            """# Mappings

## Issue Types
| Canonical type | Transport | Tracker value |
| --- | --- | --- |
| `feature` | `local-header` | `feature` |
| `task` | `local-header` | `task` |

## Workflow States
| Canonical state | Transport | Tracker value |
| --- | --- | --- |
| `ready-for-agent` | `local-header` | `ready-for-agent` |
""",
            encoding="utf-8",
        )
        (bundle / "SPEC.md").write_text(spec, encoding="utf-8")
        (issues / "01-deliver-probe.md").write_text(issue, encoding="utf-8")

    def test_accepts_a_structurally_complete_local_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_bundle(root)

            self.assertEqual([], validate_local_bundle(root))

    def test_rejects_missing_feature_metadata_and_tracker_scope(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_bundle(
                root,
                spec=SPEC.replace("issue_type: feature\n\n", ""),
                issue=ISSUE.replace(
                    "; `planning/features/probe/issues/done/01-deliver-probe.md`", ""
                ),
            )

            failures = validate_local_bundle(root)

        self.assertIn("probe: missing local feature type header", failures)
        self.assertIn("probe/01: active/done tracker paths missing from scope", failures)

    def test_accepts_local_tracker_with_github_pr_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_bundle(
                root,
                spec=SPEC.replace("`local-branch`", "`github-pr`"),
                issue=ISSUE.replace("`local-branch`", "`github-pr`"),
            )
            self.assertEqual([], validate_local_bundle(root))

    def test_rejects_issue_delivery_that_differs_from_feature_spec(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_bundle(
                root,
                issue=ISSUE.replace("`local-branch`", "`github-pr`"),
            )
            failures = validate_local_bundle(root)
        self.assertIn("probe/01: delivery_type does not match Spec", failures)


if __name__ == "__main__":
    unittest.main()
