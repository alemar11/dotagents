from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts/delivery-preflight"
LOADER = importlib.machinery.SourceFileLoader("delivery_preflight_runtime", str(TOOL))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
RUNTIME = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(RUNTIME)


class FakeClient:
    def __init__(self, responses: dict[str, object]):
        self.responses = responses
        self.request_count = 0

    def get(
        self,
        endpoint: str,
        *,
        allow_not_found: bool = False,
        jq: str | None = None,
    ) -> object:
        self.request_count += 1
        if endpoint not in self.responses:
            if allow_not_found:
                return None
            raise AssertionError(f"unexpected endpoint: {endpoint}")
        value = self.responses[endpoint]
        if isinstance(value, Exception):
            raise value
        return value


def responses(*, workflows: list[dict] | None = None, push: bool = True) -> dict[str, object]:
    repository = "example/repo"
    sha = "a" * 40
    return {
        f"repos/{repository}": {
            "default_branch": "main",
            "permissions": {"push": push, "pull": True},
        },
        f"repos/{repository}/branches/main/protection": None,
        f"repos/{repository}/rules/branches/main": [],
        f"repos/{repository}/pulls?state=open&per_page=1": [],
        f"repos/{repository}/actions/workflows?per_page=100": [
            item.get("path") or item.get("name")
            for item in workflows or []
            if item.get("state") == "active"
        ],
        f"repos/{repository}/commits/main": [sha],
        f"repos/{repository}/commits/{sha}/check-runs?per_page=100": [],
        f"repos/{repository}/commits/{sha}/status": [],
        f"repos/{repository}/git/trees/{sha}?recursive=1": [],
    }


def packet(*delivery_keys: str) -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "deliveries": [
            {
                "delivery_key": key,
                "github_repository": "example/repo",
                "target_branch": "main",
            }
            for key in delivery_keys
        ],
    }


class DeliveryPreflightTests(unittest.TestCase):
    def test_not_configured_is_explicit_and_passes(self) -> None:
        result = RUNTIME.inspect(packet("repo"), FakeClient(responses()))
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "passed")
        delivery = result["deliveries"][0]
        self.assertEqual(delivery["ci_availability"], "not-configured")
        self.assertEqual(delivery["blockers"], [])
        self.assertRegex(delivery["preflight_key"], r"^[0-9a-f]{64}$")

    def test_active_workflow_configures_ci(self) -> None:
        result = RUNTIME.inspect(
            packet("repo"),
            FakeClient(
                responses(
                    workflows=[
                        {
                            "state": "active",
                            "path": ".github/workflows/test.yml",
                        }
                    ]
                )
            ),
        )
        self.assertEqual(result["deliveries"][0]["ci_availability"], "configured")

    def test_required_context_configures_ci(self) -> None:
        fixture = responses()
        fixture["repos/example/repo/branches/main/protection"] = {
            "required_status_checks": {"contexts": ["test"]}
        }
        result = RUNTIME.inspect(packet("repo"), FakeClient(fixture))
        self.assertEqual(result["deliveries"][0]["ci_availability"], "configured")

    def test_repository_ci_config_configures_ci(self) -> None:
        fixture = responses()
        sha = "a" * 40
        fixture[f"repos/example/repo/git/trees/{sha}?recursive=1"] = [
            ".circleci/config.yml"
        ]
        result = RUNTIME.inspect(packet("repo"), FakeClient(fixture))
        self.assertEqual(result["deliveries"][0]["ci_availability"], "configured")

    def test_default_base_is_url_encoded_for_github_endpoints(self) -> None:
        fixture = responses()
        fixture["repos/example/repo"]["default_branch"] = "release/v1"
        fixture["repos/example/repo/branches/release%2Fv1/protection"] = fixture.pop(
            "repos/example/repo/branches/main/protection"
        )
        fixture["repos/example/repo/rules/branches/release%2Fv1"] = fixture.pop(
            "repos/example/repo/rules/branches/main"
        )
        fixture["repos/example/repo/commits/release%2Fv1"] = fixture.pop(
            "repos/example/repo/commits/main"
        )
        result = RUNTIME.inspect(packet("repo"), FakeClient(fixture))
        self.assertEqual(result["deliveries"][0]["default_base"], "release/v1")

    def test_missing_push_permission_is_a_blocker(self) -> None:
        result = RUNTIME.inspect(packet("repo"), FakeClient(responses(push=False)))
        self.assertFalse(result["ok"])
        self.assertIn(
            "push-permission-unavailable", result["deliveries"][0]["blockers"]
        )

    def test_incomplete_policy_surface_is_a_blocker(self) -> None:
        fixture = responses()
        fixture["repos/example/repo/rules/branches/main"] = {}
        result = RUNTIME.inspect(packet("repo"), FakeClient(fixture))
        self.assertFalse(result["ok"])
        self.assertIn(
            "repository-rules-visibility-unavailable",
            result["deliveries"][0]["blockers"],
        )

    def test_incomplete_ci_surface_is_not_not_configured(self) -> None:
        fixture = responses()
        fixture["repos/example/repo/actions/workflows?per_page=100"] = {}
        with self.assertRaisesRegex(RUNTIME.PreflightError, "CI surfaces are incomplete"):
            RUNTIME.inspect(packet("repo"), FakeClient(fixture))

    def test_duplicate_repository_queries_are_deduplicated(self) -> None:
        client = FakeClient(responses())
        result = RUNTIME.inspect(packet("repo-a", "repo-b"), client)
        self.assertEqual(len(result["deliveries"]), 2)
        self.assertEqual(client.request_count, 9)
        self.assertEqual(
            {item["delivery_key"] for item in result["deliveries"]},
            {"repo-a", "repo-b"},
        )

    def test_packet_is_strict_and_requires_absolute_regular_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "packet.json"
            path.write_text(json.dumps(packet("repo")))
            self.assertEqual(RUNTIME.read_packet(str(path))["deliveries"][0]["delivery_key"], "repo")
            value = packet("repo")
            value["extra"] = True
            path.write_text(json.dumps(value))
            with self.assertRaises(RUNTIME.PreflightError):
                RUNTIME.read_packet(str(path))

    def test_shipped_help_version_and_missing_gh_doctor(self) -> None:
        version = subprocess.run(
            [sys.executable, str(TOOL), "--version"],
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(version.stdout.strip(), "1.0.0")
        help_result = subprocess.run(
            [sys.executable, str(TOOL), "--help"],
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("delivery capability", help_result.stdout)
        environment = os.environ.copy()
        environment["PATH"] = ""
        doctor = subprocess.run(
            [sys.executable, str(TOOL), "--json", "doctor"],
            env=environment,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(doctor.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["gh"]["auth_source"], "missing")


if __name__ == "__main__":
    unittest.main()
