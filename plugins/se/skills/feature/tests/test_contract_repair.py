from __future__ import annotations

import copy
import importlib.machinery
import importlib.util
import unittest
from pathlib import Path


VALIDATOR = Path(__file__).parents[3] / "scripts" / "validate-contract-repair"
loader = importlib.machinery.SourceFileLoader("contract_repair_validator", str(VALIDATOR))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)
validate = module.validate


def artifact(ref: str, kind: str, stable: dict, progress: str = "open") -> dict:
    return {
        "ref": ref,
        "kind": kind,
        "stable": stable,
        "executor_owned": {"checkboxes": progress, "progress": [], "evidence": []},
    }


class ContractRepairTests(unittest.TestCase):
    def fixture(self) -> dict:
        request = {
            "repair_id": "019fae9a-38e7-77d2-a73c-e03990cf1f94",
            "source_spec_ref": "example/project#238",
            "originating_issue_refs": ["example/project#239"],
            "known_issue_refs": ["example/project#240"],
            "conflicting_clauses": ["example/project#238:AC-03 conflicts with validation"],
            "reason": "The accepted validation omits the required semantic case.",
            "contract_evidence_refs": ["example/project#238:AC-03"],
            "repository_evidence_refs": ["src/workflow/expression-node.tsx:84"],
            "test_evidence_refs": ["tests/workflow/expression.test.ts:31"],
            "runtime_evidence_refs": [],
        }
        before = [
            artifact("example/project#238", "spec", {"allowed_paths": ["src/workflow/**"], "validation": ["npm test"]}),
            artifact("example/project#239", "issue", {"acceptance": ["valid expression"], "dependencies": []}),
            artifact("example/project#240", "issue", {"acceptance": ["save expression"], "dependencies": []}),
        ]
        after = copy.deepcopy(before)
        after[0]["stable"]["allowed_paths"].append("src/components/**")
        after[1]["stable"]["acceptance"] = ["valid expression", "invalid expression rejected"]
        after[2]["stable"]["dependencies"] = ["example/project#239"]
        changed = [item["ref"] for item in after if item["stable"] != next(x for x in before if x["ref"] == item["ref"])["stable"]]
        result = {
            "repair_id": request["repair_id"], "repair_outcome": "applied",
            "source_spec_ref": request["source_spec_ref"],
            "changed_artifact_refs": changed, "created_artifact_refs": [],
            "superseded_artifact_refs": [], "audit_ref": "example/project#239:comment-7",
            "readback_refs": ["example/project#238@r2", "example/project#239@r4", "example/project#240@r3"],
            "completed_operations": ["update-spec", "update-issues", "verify-bundle", "append-audit"],
            "missing_operations": [], "blocker": None,
        }
        audit = {key: request[key] for key in module.REQUEST_KEYS}
        audit.update({key: result[key] for key in (
            "changed_artifact_refs", "created_artifact_refs", "superseded_artifact_refs",
            "readback_refs", "completed_operations", "missing_operations",
        )})
        audit["executor_owned_preserved_refs"] = sorted(item["ref"] for item in before)
        return {"request": request, "before": before, "after": after, "result": result, "audit": audit}

    def test_accepts_allowed_paths_semantic_validation_and_multiple_issues(self) -> None:
        result = validate(self.fixture())
        self.assertEqual("applied", result["repair_outcome"])

    def test_preserves_executor_owned_progress_and_evidence(self) -> None:
        payload = self.fixture()
        payload["after"][1]["executor_owned"]["progress"] = ["changed by planner"]
        with self.assertRaisesRegex(ValueError, "executor-owned content changed"):
            validate(payload)

    def test_rejects_runtime_identity_anywhere(self) -> None:
        payload = self.fixture()
        payload["audit"]["run_id"] = "run-1"
        with self.assertRaisesRegex(ValueError, "keys are not exact"):
            validate(payload)

    def test_accepts_created_and_superseded_issue_refs(self) -> None:
        payload = self.fixture()
        payload["after"] = [item for item in payload["after"] if item["ref"] != "example/project#240"]
        payload["after"].append(artifact("example/project#241", "issue", {"acceptance": ["replacement"], "dependencies": ["example/project#239"]}))
        payload["result"]["created_artifact_refs"] = ["example/project#241"]
        payload["result"]["superseded_artifact_refs"] = ["example/project#240"]
        payload["result"]["changed_artifact_refs"] = ["example/project#238", "example/project#239"]
        for key in ("created_artifact_refs", "superseded_artifact_refs", "changed_artifact_refs"):
            payload["audit"][key] = payload["result"][key]
        payload["audit"]["executor_owned_preserved_refs"] = ["example/project#238", "example/project#239"]
        self.assertTrue(validate(payload)["valid"])

    def test_partial_publication_requires_blocker_and_exact_remainder(self) -> None:
        payload = self.fixture()
        payload["result"].update({"repair_outcome": "blocked", "missing_operations": ["append-audit"], "blocker": "partial-publication"})
        payload["audit"]["missing_operations"] = ["append-audit"]
        self.assertTrue(validate(payload)["valid"])
        payload["result"]["blocker"] = None
        with self.assertRaisesRegex(ValueError, "requires a blocker"):
            validate(payload)

    def test_resumable_result_requires_complete_bundle_readback(self) -> None:
        payload = self.fixture()
        payload["result"]["readback_refs"] = []
        payload["audit"]["readback_refs"] = []
        with self.assertRaisesRegex(ValueError, "complete readback"):
            validate(payload)


if __name__ == "__main__":
    unittest.main()
