from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gitstack.common import GitStackError
from gitstack.provider_text import api_request, read_text_file
from gitstack.review_mutation import (
    ReservationError,
    add_operation_marker,
    build_reservation,
    operation_id_for_mutation,
    text_fingerprint,
    validate_reservation_packet,
)


class ProviderTextContractTests(unittest.TestCase):
    HOSTILE = "`backticks` $(command) ${HOME} $PATH 'single' \"double\"\n-leading\nUnicode ✓ 🚀"

    def test_reservation_rejects_operation_identity_replacement(self) -> None:
        operation_id = operation_id_for_mutation(
            "review-warning",
            "owner/repo",
            12,
            "b" * 40,
            request_fingerprint="a" * 64,
        )
        packet = build_reservation(
            mutation_kind="review-warning",
            repository="owner/repo",
            pr_number=12,
            head_sha="b" * 40,
            task_key="task",
            delivery_key="delivery",
            operation_id=operation_id,
            request_key="warning",
            request_fingerprint="a" * 64,
            thread_id=None,
            thread_fingerprint=None,
            finding_comment_id=None,
            body_fingerprint="c" * 64,
            reply_receipt_fingerprint=None,
            expected_generation=1,
            expected_state_fingerprint="d" * 64,
            expected_claim_fingerprint="e" * 64,
            expected_task_state="review-polling",
        )
        tampered = dict(packet)
        tampered["operation_id"] = "f" * 32
        with self.assertRaises(ReservationError):
            validate_reservation_packet(tampered)

    def test_hostile_utf8_bytes_are_opaque_and_fingerprinted(self) -> None:
        with tempfile.NamedTemporaryFile("wb") as handle:
            expected = self.HOSTILE.encode("utf-8")
            handle.write(expected)
            handle.flush()
            payload = read_text_file(handle.name, field="body")

        self.assertEqual(payload.data, expected)
        self.assertEqual(payload.text, self.HOSTILE)
        self.assertEqual(payload.proof()["bytes"], len(expected))
        self.assertRegex(payload.proof()["sha256"], r"^[0-9a-f]{64}$")

    def test_rejects_relative_symlink_directory_and_invalid_utf8(self) -> None:
        with self.assertRaises(GitStackError) as relative:
            read_text_file("message.md", field="body")
        self.assertEqual(relative.exception.code, "provider_text_path_invalid")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            regular = root / "body.md"
            regular.write_text("body", encoding="utf-8")
            link = root / "link.md"
            link.symlink_to(regular)
            with self.assertRaises(GitStackError):
                read_text_file(str(link), field="body")
            with self.assertRaises(GitStackError):
                read_text_file(str(root), field="body")
            invalid = root / "invalid.md"
            invalid.write_bytes(b"\xff")
            with self.assertRaises(GitStackError) as invalid_error:
                read_text_file(str(invalid), field="body")
            self.assertEqual(invalid_error.exception.code, "provider_text_invalid")

    def test_title_rejects_multiline_but_accepts_leading_hyphen(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as handle:
            handle.write("- safe title")
            handle.flush()
            self.assertEqual(read_text_file(handle.name, field="title", single_line=True).text, "- safe title")
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as handle:
            handle.write("line one\nline two")
            handle.flush()
            with self.assertRaises(GitStackError):
                read_text_file(handle.name, field="title", single_line=True)

    def test_api_transport_keeps_provider_text_out_of_argv(self) -> None:
        completed = mock.Mock(returncode=0, stdout=b"{}", stderr=b"")
        with mock.patch("gitstack.provider_text.subprocess.run", return_value=completed) as run:
            result = api_request("POST", "repos/owner/repo/issues/1/comments", {"body": self.HOSTILE})

        self.assertEqual(result.returncode, 0)
        command = run.call_args.args[0]
        self.assertNotIn(self.HOSTILE, command)
        self.assertNotIn("body", " ".join(command))
        self.assertFalse(run.call_args.kwargs["shell"])
        request = json.loads(run.call_args.kwargs["input"].decode("utf-8"))
        self.assertEqual(request["body"], self.HOSTILE)

    def test_shipped_cli_needs_no_external_skill_for_reserved_dry_run(self) -> None:
        artifact = Path(__file__).resolve().parents[3] / "scripts" / "gitstack"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            body_file = root / "-message.md"
            body_file.write_text(self.HOSTILE, encoding="utf-8")
            request_fingerprint = "a" * 64
            head = "b" * 40
            operation_id = operation_id_for_mutation(
                "review-warning",
                "owner/repo",
                12,
                head,
                request_fingerprint=request_fingerprint,
            )
            reservation = build_reservation(
                mutation_kind="review-warning",
                repository="owner/repo",
                pr_number=12,
                head_sha=head,
                task_key="task",
                delivery_key="delivery",
                operation_id=operation_id,
                request_key="warning",
                request_fingerprint=request_fingerprint,
                thread_id=None,
                thread_fingerprint=None,
                finding_comment_id=None,
                body_fingerprint=text_fingerprint(add_operation_marker(self.HOSTILE, operation_id)),
                reply_receipt_fingerprint=None,
                expected_generation=1,
                expected_state_fingerprint="c" * 64,
                expected_claim_fingerprint="d" * 64,
                expected_task_state="review-polling",
            )
            reservation_file = root / "reservation.json"
            reservation_file.write_text(json.dumps(reservation), encoding="utf-8")
            fake_gh = root / "gh"
            fake_gh.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                f"assert {self.HOSTILE!r} not in sys.argv\n"
                f"print(json.dumps({{'number': 12, 'url': 'https://api.github.com/repos/owner/repo/pulls/12', 'head': {{'sha': {head!r}}}}}))\n",
                encoding="utf-8",
            )
            fake_gh.chmod(0o755)
            environment = os.environ.copy()
            environment["HOME"] = str(root)
            environment["PATH"] = f"{root}:{environment['PATH']}"
            completed = subprocess.run(
                [
                    str(artifact), "--json", "reviews", "comment",
                    "--repo", "owner/repo", "--pr", "12",
                    "--body-file", str(body_file), "--head", head,
                    "--request-key", "warning", "--request-fingerprint", request_fingerprint,
                    "--reservation-file", str(reservation_file),
                    "--dry-run", "--allow-non-project",
                ],
                cwd=root,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn(self.HOSTILE, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["action"]["status"], "dry-run")


if __name__ == "__main__":
    unittest.main()
