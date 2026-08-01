from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scope_repair_validator import validate_scope_repair


FIXTURE = Path(__file__).parent / "fixtures" / "scope-repair.json"


class ScopeRepairTests(unittest.TestCase):
    def fixture(self) -> dict[str, object]:
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_accepts_monotonic_path_expansion_and_matching_audit(self) -> None:
        fixture = self.fixture()

        result = validate_scope_repair(
            fixture["before"], fixture["after"], fixture["request"]
        )

        self.assertEqual("applied", result["repair_outcome"])
        self.assertEqual(["src/components/**"], result["added_spec_paths"])
        self.assertEqual(["src/components/**"], result["added_issue_paths"])

    def test_accepts_idempotent_no_op(self) -> None:
        fixture = self.fixture()
        before = {
            "spec": copy.deepcopy(fixture["after"]["spec"]),
            "issue": copy.deepcopy(fixture["after"]["issue"]),
        }
        after = copy.deepcopy(fixture["after"])
        after["audit"]["previous_spec_allowed_paths"] = copy.deepcopy(
            after["spec"]["allowed_paths"]
        )
        after["audit"]["previous_issue_allowed_paths"] = copy.deepcopy(
            after["issue"]["allowed_paths"]
        )

        result = validate_scope_repair(before, after, fixture["request"])

        self.assertEqual("no-op", result["repair_outcome"])

    def test_rejects_path_removal(self) -> None:
        fixture = self.fixture()
        after = copy.deepcopy(fixture["after"])
        after["issue"]["allowed_paths"].remove("tests/workflow/**")

        with self.assertRaisesRegex(ValueError, "removed an allowed path"):
            validate_scope_repair(fixture["before"], after, fixture["request"])

    def test_rejects_other_stable_field_change(self) -> None:
        fixture = self.fixture()
        after = copy.deepcopy(fixture["after"])
        after["spec"]["stable"]["target_branch_name"] = "feature/other"

        with self.assertRaisesRegex(ValueError, "stable Feature Spec field"):
            validate_scope_repair(fixture["before"], after, fixture["request"])

    def test_rejects_requested_path_not_covered_by_issue(self) -> None:
        fixture = self.fixture()
        after = copy.deepcopy(fixture["after"])
        after["issue"]["allowed_paths"].remove("src/components/**")

        with self.assertRaisesRegex(ValueError, "requested path is not authorized"):
            validate_scope_repair(fixture["before"], after, fixture["request"])

    def test_rejects_runtime_identity_and_nonportable_paths(self) -> None:
        fixture = self.fixture()
        request = copy.deepcopy(fixture["request"])
        request["worker_id"] = "thread-1"

        with self.assertRaisesRegex(ValueError, "keys are not exact"):
            validate_scope_repair(fixture["before"], fixture["after"], request)

        request = copy.deepcopy(fixture["request"])
        request["requested_paths"] = ["/Users/example/private.ts"]
        with self.assertRaisesRegex(ValueError, "must not be absolute"):
            validate_scope_repair(fixture["before"], fixture["after"], request)

    def test_rejects_audit_that_does_not_match_mutation(self) -> None:
        fixture = self.fixture()
        after = copy.deepcopy(fixture["after"])
        after["audit"]["authorized_issue_allowed_paths"] = ["src/workflow/**"]

        with self.assertRaisesRegex(ValueError, "audit does not match"):
            validate_scope_repair(fixture["before"], after, fixture["request"])

    def test_rejects_audit_that_omits_request_evidence(self) -> None:
        fixture = self.fixture()
        after = copy.deepcopy(fixture["after"])
        after["audit"]["evidence_refs"] = ["different:evidence"]

        with self.assertRaisesRegex(ValueError, "audit does not match"):
            validate_scope_repair(fixture["before"], after, fixture["request"])


if __name__ == "__main__":
    unittest.main()
