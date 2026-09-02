from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_TARGET = SKILL_ROOT / "scripts" / "validate-fixup-target"
REPLACE_MESSAGE = SKILL_ROOT / "scripts" / "replace-amend-fixup-message"


def run_command(
    arguments: list[str],
    *,
    cwd: Path,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command_environment = os.environ.copy()
    command_environment.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    if environment:
        command_environment.update(environment)
    return subprocess.run(
        arguments,
        cwd=cwd,
        env=command_environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    result = run_command(["git", *arguments], cwd=repository)
    if result.returncode != 0:
        raise AssertionError(
            f"git {' '.join(arguments)} failed:\n{result.stdout}\n{result.stderr}"
        )
    return result


def initialize_repository(repository: Path) -> None:
    git(repository, "init", "--quiet")
    git(repository, "config", "user.name", "G Tests")
    git(repository, "config", "user.email", "g-tests@example.invalid")


def create_commit(repository: Path, subject: str, filename: str) -> str:
    path = repository / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"content for {filename}\n", encoding="utf-8")
    git(repository, "add", filename)

    arguments = ["commit", "--no-verify", "--quiet"]
    if not subject:
        arguments.append("--allow-empty-message")
    arguments.extend(["-m", subject])
    git(repository, *arguments)
    return git(repository, "rev-parse", "HEAD").stdout.strip()


class FixupAdapterCliTests(unittest.TestCase):
    def test_validate_returns_full_sha_for_unique_ancestor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            initialize_repository(repository)
            target_sha = create_commit(repository, "Target subject", "target.txt")
            create_commit(repository, "Follow-up subject", "follow-up.txt")

            result = run_command(
                [str(VALIDATE_TARGET), target_sha[:12]],
                cwd=repository,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), target_sha)
        self.assertEqual(result.stderr, "")

    def test_validate_rejects_missing_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            initialize_repository(repository)
            result = run_command(
                [str(VALIDATE_TARGET), "does-not-exist"],
                cwd=repository,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertNotEqual(result.stderr.strip(), "")

    def test_validate_rejects_target_outside_head_ancestry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            initialize_repository(repository)
            base_sha = create_commit(repository, "Base subject", "base.txt")
            git(repository, "checkout", "-q", "-b", "side")
            target_sha = create_commit(repository, "Side target", "side.txt")
            git(repository, "checkout", "-q", "-b", "head", base_sha)
            create_commit(repository, "Head subject", "head.txt")

            result = run_command(
                [str(VALIDATE_TARGET), target_sha],
                cwd=repository,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not an ancestor", result.stderr)

    def test_validate_rejects_duplicate_reachable_subject(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            initialize_repository(repository)
            target_sha = create_commit(repository, "Repeated subject", "first.txt")
            create_commit(repository, "Repeated subject", "second.txt")

            result = run_command(
                [str(VALIDATE_TARGET), target_sha],
                cwd=repository,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not unique in history", result.stderr)

    def test_validate_rejects_empty_subject(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            initialize_repository(repository)
            target_sha = create_commit(repository, "", "empty-subject.txt")

            result = run_command(
                [str(VALIDATE_TARGET), target_sha],
                cwd=repository,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("non-empty subject", result.stderr)

    def test_replace_preserves_matcher_and_replaces_message(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            edit_path = root / "git-message.txt"
            replacement_path = root / "replacement.txt"
            edit_path.write_text(
                "amend! Original subject\n# generated by Git\n",
                encoding="utf-8",
            )
            replacement_path.write_text(
                "Corrected subject\n\nCorrected body\n",
                encoding="utf-8",
            )

            result = run_command(
                [str(REPLACE_MESSAGE), str(edit_path)],
                cwd=root,
                environment={
                    "G_AMEND_MESSAGE_FILE": str(replacement_path),
                },
            )
            message = edit_path.read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            message,
            "amend! Original subject\n\nCorrected subject\n\nCorrected body\n",
        )

    def test_replace_rejects_missing_matcher_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            edit_path = root / "git-message.txt"
            replacement_path = root / "replacement.txt"
            original = "pick a normal commit message\n"
            edit_path.write_text(original, encoding="utf-8")
            replacement_path.write_text("Corrected subject\n", encoding="utf-8")

            result = run_command(
                [str(REPLACE_MESSAGE), str(edit_path)],
                cwd=root,
                environment={
                    "G_AMEND_MESSAGE_FILE": str(replacement_path),
                },
            )
            updated_message = edit_path.read_text(encoding="utf-8")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("amend-fixup matcher", result.stderr)
        self.assertEqual(updated_message, original)

    def test_replace_rejects_empty_replacement_subject_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            edit_path = root / "git-message.txt"
            replacement_path = root / "replacement.txt"
            original = "amend! Original subject\n"
            edit_path.write_text(original, encoding="utf-8")
            replacement_path.write_text("  \nbody\n", encoding="utf-8")

            result = run_command(
                [str(REPLACE_MESSAGE), str(edit_path)],
                cwd=root,
                environment={
                    "G_AMEND_MESSAGE_FILE": str(replacement_path),
                },
            )
            updated_message = edit_path.read_text(encoding="utf-8")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("non-empty subject", result.stderr)
        self.assertEqual(updated_message, original)

    def test_replace_rejects_nested_matcher_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            edit_path = root / "git-message.txt"
            replacement_path = root / "replacement.txt"
            original = "amend! Original subject\n"
            edit_path.write_text(original, encoding="utf-8")
            replacement_path.write_text(
                "amend! Replacement subject\nbody\n",
                encoding="utf-8",
            )

            result = run_command(
                [str(REPLACE_MESSAGE), str(edit_path)],
                cwd=root,
                environment={
                    "G_AMEND_MESSAGE_FILE": str(replacement_path),
                },
            )
            updated_message = edit_path.read_text(encoding="utf-8")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("omit the amend-fixup matcher", result.stderr)
        self.assertEqual(updated_message, original)

    def test_git_invokes_replace_adapter_for_amend_fixup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repository"
            repository.mkdir()
            initialize_repository(repository)
            target_sha = create_commit(repository, "Original subject", "target.txt")

            refinement = repository / "refinement.txt"
            refinement.write_text("refined content\n", encoding="utf-8")
            git(repository, "add", "refinement.txt")

            replacement_path = root / "replacement.txt"
            replacement_path.write_text(
                "Corrected subject\n\nCorrected body\n",
                encoding="utf-8",
            )
            result = run_command(
                ["git", "commit", "--no-verify", f"--fixup=amend:{target_sha}"],
                cwd=repository,
                environment={
                    "GIT_EDITOR": str(REPLACE_MESSAGE),
                    "G_AMEND_MESSAGE_FILE": str(replacement_path),
                },
            )
            head_subject = git(repository, "log", "-1", "--format=%s").stdout.strip()
            head_message = git(repository, "log", "-1", "--format=%B").stdout
            parent_sha = git(repository, "rev-parse", "HEAD^").stdout.strip()
            target_subject = git(
                repository, "show", "-s", "--format=%s", target_sha
            ).stdout.strip()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(head_subject, "amend! Original subject")
        self.assertIn("Corrected subject\n\nCorrected body", head_message)
        self.assertEqual(parent_sha, target_sha)
        self.assertEqual(target_subject, "Original subject")


if __name__ == "__main__":
    unittest.main()
