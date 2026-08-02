from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gitstack import health
from gitstack.common import Result


class HealthContractTests(unittest.TestCase):
    def doctor_for(self, auth_payload: object, *, returncode: int = 1) -> dict[str, object]:
        calls: list[list[str]] = []
        stack_status = {
            "ok": False,
            "status": "missing",
            "installed": False,
            "command": "stack",
            "repository": "github/gh-stack",
            "version": None,
            "publisher_verification": None,
            "reason": None,
            "gh_path": "/usr/bin/gh",
        }

        def fake_run(command: list[str]) -> Result:
            calls.append(command)
            if command[0] == "gh":
                stdout = auth_payload if isinstance(auth_payload, str) else json.dumps(auth_payload)
                return Result(returncode, stdout, "provider diagnostic that must stay private")
            return Result(0, "/tmp/repository\n", "")

        with mock.patch.object(
            health.shutil,
            "which",
            side_effect=lambda tool: f"/usr/bin/{tool}",
        ), mock.patch.object(health, "run", side_effect=fake_run), mock.patch.object(
            health,
            "extension_status",
            return_value=stack_status,
        ):
            payload = health.doctor()

        self.assertEqual(calls[0], health.AUTH_STATUS_COMMAND)
        return payload

    def assert_authentication(self, payload: dict[str, object], expected: str) -> None:
        checks = payload["checks"]
        self.assertIsInstance(checks, dict)
        gh = checks["gh"]
        self.assertEqual(gh["authentication_status"], expected)
        self.assertEqual(gh["authenticated"], expected == "verified")
        self.assertEqual(payload["provider_ready"], expected == "verified")

    def test_structured_success_is_verified_even_when_command_is_nonzero(self) -> None:
        payload = self.doctor_for(
            {
                "hosts": {
                    "github.com": [
                        {
                            "active": True,
                            "state": "success",
                            "login": "example",
                            "tokenSource": "keyring",
                            "scopes": "private scopes",
                        }
                    ]
                }
            }
        )
        self.assert_authentication(payload, "verified")
        rendered = json.dumps(payload)
        self.assertNotIn("example", rendered)
        self.assertNotIn("keyring", rendered)
        self.assertNotIn("private scopes", rendered)

    def test_network_looking_provider_error_is_unverified(self) -> None:
        payload = self.doctor_for(
            {
                "hosts": {
                    "github.com": [
                        {
                            "active": True,
                            "state": "error",
                            "error": "lookup api.github.com: no such host",
                            "token": "secret-value",
                        }
                    ]
                }
            }
        )
        self.assert_authentication(payload, "unverified")
        rendered = json.dumps(payload)
        self.assertNotIn("no such host", rendered)
        self.assertNotIn("secret-value", rendered)

    def test_auth_looking_provider_error_is_also_unverified(self) -> None:
        payload = self.doctor_for(
            {
                "hosts": {
                    "github.com": [
                        {
                            "active": True,
                            "state": "error",
                            "error": "authentication token is invalid",
                        }
                    ]
                }
            }
        )
        self.assert_authentication(payload, "unverified")
        self.assertNotIn("invalid", json.dumps(payload))

    def test_no_active_account_is_unverified(self) -> None:
        payload = self.doctor_for(
            {"hosts": {"github.com": [{"active": False, "state": "success"}]}}
        )
        self.assert_authentication(payload, "unverified")

    def test_multiple_active_accounts_fail_closed(self) -> None:
        payload = self.doctor_for(
            {
                "hosts": {
                    "github.com": [
                        {"active": True, "state": "success"},
                        {"active": True, "state": "success"},
                    ]
                }
            }
        )
        self.assert_authentication(payload, "unverified")

    def test_malformed_json_is_unverified(self) -> None:
        payload = self.doctor_for("not-json")
        self.assert_authentication(payload, "unverified")

    def test_missing_gh_is_not_checked(self) -> None:
        calls: list[list[str]] = []
        with mock.patch.object(
            health.shutil,
            "which",
            side_effect=lambda tool: "/usr/bin/git" if tool == "git" else None,
        ), mock.patch.object(
            health,
            "run",
            side_effect=lambda command: calls.append(command) or Result(0, "/tmp/repository\n", ""),
        ):
            payload = health.doctor()

        self.assert_authentication(payload, "not-checked")
        self.assertFalse(payload["ok"])
        self.assertFalse(any(command[0] == "gh" for command in calls))

    def test_human_output_distinguishes_verified_unverified_and_missing(self) -> None:
        verified = self.doctor_for(
            {"hosts": {"github.com": [{"active": True, "state": "success"}]}},
            returncode=0,
        )
        unverified = self.doctor_for(
            {"hosts": {"github.com": [{"active": True, "state": "error"}]}},
        )
        missing = json.loads(json.dumps(unverified))
        missing["checks"]["gh"].update(
            {"ok": False, "authentication_status": "not-checked"}
        )

        self.assertIn("gh: installed; authentication verified", health.doctor_text(verified))
        self.assertIn("gh: installed; authentication unverified", health.doctor_text(unverified))
        self.assertIn("gh: missing", health.doctor_text(missing))


if __name__ == "__main__":
    unittest.main()
