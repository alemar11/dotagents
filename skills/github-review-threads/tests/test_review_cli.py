from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from reviews_lib import __version__
from reviews_lib import reviews as cli
from reviews_lib.review_mutation import (
    add_operation_marker,
    build_reservation,
    operation_id_for_mutation,
    packet_fingerprint,
    text_fingerprint,
)


ARTIFACT = Path(__file__).resolve().parents[1] / "scripts" / "reviews"


class ReviewCliContractTests(unittest.TestCase):
    def test_review_mutation_help_requires_g_reservation_only(self) -> None:
        """Public parser contract from original g ``test_cli``."""

        for command in ("request", "comment", "reply", "resolve"):
            output = io.StringIO()
            with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as raised:
                cli.main([command, "--help"])
            self.assertEqual(raised.exception.code, 0)
            help_text = output.getvalue()
            self.assertIn("--reservation-file", help_text)
            self.assertNotIn("--ledger-file", help_text)

            completed = subprocess.run(
                [str(ARTIFACT), command, "--help"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("--reservation-file", completed.stdout)
            self.assertNotIn("--ledger-file", completed.stdout)


class HistoricalReservationRootTests(unittest.TestCase):
    def test_roots_remain_historical_v1_plugin_paths(self) -> None:
        home = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(home, ignore_errors=True))
        with mock.patch.object(cli, "_trusted_user_home", return_value=home):
            self.assertEqual(
                cli._reservation_cache_root(),
                home / ".cache/dotagents/plugins/g/review-mutations",
            )
            self.assertEqual(
                cli._operation_journal_root(),
                home / ".cache/dotagents/plugins/g/review-operations",
            )

    def test_standalone_entrypoint_sees_previously_consumed_v1_reservation(self) -> None:
        """A marker under the historical v1 root must block replay via the reviews CLI."""

        home = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(home, ignore_errors=True))
        head = "b" * 40
        request_fingerprint = "a" * 64
        body = "evidence body"
        operation_id = operation_id_for_mutation(
            "review-warning",
            "owner/repo",
            12,
            head,
            request_fingerprint=request_fingerprint,
        )
        marked = add_operation_marker(body, operation_id)
        packet = build_reservation(
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
            body_fingerprint=text_fingerprint(marked),
            reply_receipt_fingerprint=None,
            expected_generation=1,
            expected_state_fingerprint="c" * 64,
            expected_claim_fingerprint="d" * 64,
            expected_task_state="review-polling",
        )
        reservation_file = home / "reservation.json"
        reservation_file.write_text(json.dumps(packet), encoding="utf-8")
        body_file = home / "body.md"
        body_file.write_text(body, encoding="utf-8")

        root = home / ".cache/dotagents/plugins/g/review-mutations"
        root.mkdir(parents=True)
        marker = {
            "schema": packet["schema"],
            "reservation_id": packet["reservation_id"],
            "operation_id": packet["operation_id"],
            "packet_fingerprint": packet_fingerprint(packet),
            "reservation_file": str(reservation_file.resolve()),
            "consumed_at": datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
        }
        (root / f"{operation_id}.consumed.json").write_text(
            json.dumps(marker, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )

        with mock.patch.object(cli, "_trusted_user_home", return_value=home):
            observed = cli._read_consumed_marker(
                packet, str(reservation_file), require_consumed=True
            )
            self.assertIsNotNone(observed)
            self.assertEqual(observed["operation_id"], operation_id)
            with self.assertRaises(cli.ReviewError) as consumed:
                cli._consume_reservation(packet, str(reservation_file))
            self.assertEqual(consumed.exception.code, "reservation_consumed")

            api = mock.Mock(side_effect=AssertionError("must not post after consume"))
            stdout = io.StringIO()
            with mock.patch.object(cli, "_verify_pr_head"), mock.patch.object(
                cli, "gh_api_paginated_list", return_value=[]
            ), mock.patch.object(cli, "require_worktree", return_value=None), mock.patch.object(
                cli, "_viewer_login", return_value="agent"
            ), mock.patch.object(cli, "api_request", api), contextlib.redirect_stdout(stdout):
                code = cli.main(
                    [
                        "--json",
                        "comment",
                        "--repo",
                        "owner/repo",
                        "--pr",
                        "12",
                        "--head",
                        head,
                        "--request-key",
                        "warning",
                        "--request-fingerprint",
                        request_fingerprint,
                        "--body-file",
                        str(body_file),
                        "--reservation-file",
                        str(reservation_file),
                        "--allow-non-project",
                    ]
                )

        self.assertNotEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["version"], __version__)
        api.assert_not_called()


if __name__ == "__main__":
    unittest.main()
