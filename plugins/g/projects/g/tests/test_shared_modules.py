from __future__ import annotations

import io
import sys
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from g.ci_output import extract_failure_snippet, extract_log_from_job_archive
from g.integrity import canonical_json, fingerprint, text_fingerprint
from g.repository import is_repo_reference, normalize_remote


class RepositoryTests(unittest.TestCase):
    def test_normalize_remote_handles_supported_git_url_forms(self) -> None:
        self.assertEqual(
            normalize_remote("git@github.com:owner/repo.git"), "owner/repo"
        )
        self.assertEqual(
            normalize_remote("https://github.com/owner/repo.git"), "owner/repo"
        )
        self.assertEqual(
            normalize_remote("ssh://github.com/owner/repo.git"), "owner/repo"
        )

    def test_repository_reference_requires_exact_owner_and_name(self) -> None:
        self.assertTrue(is_repo_reference("owner/repo"))
        self.assertFalse(is_repo_reference("owner/repo/extra"))
        self.assertFalse(is_repo_reference("owner only"))


class IntegrityTests(unittest.TestCase):
    def test_fingerprint_uses_canonical_key_order(self) -> None:
        left = {"b": 2, "a": 1}
        right = {"a": 1, "b": 2}

        self.assertEqual(canonical_json(left), '{"a":1,"b":2}')
        self.assertEqual(fingerprint(left), fingerprint(right))
        self.assertEqual(fingerprint(left), text_fingerprint(canonical_json(left)))


class CiOutputTests(unittest.TestCase):
    def test_job_archive_returns_longest_nonempty_log(self) -> None:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("short.txt", "short")
            archive.writestr("long.txt", "first\nsecond\nthird")

        text, error = extract_log_from_job_archive(buffer.getvalue())

        self.assertEqual(text, "first\nsecond\nthird")
        self.assertEqual(error, "")

    def test_failure_snippet_is_centered_on_latest_failure(self) -> None:
        log = "setup\nerror: first\nretry\nfailed: final\ncleanup"

        self.assertEqual(
            extract_failure_snippet(log, max_lines=3, context=1),
            "retry\nfailed: final\ncleanup",
        )


if __name__ == "__main__":
    unittest.main()
