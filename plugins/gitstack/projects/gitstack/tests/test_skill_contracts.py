from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[3]


def read(relative: str) -> str:
    return (PLUGIN_ROOT / relative).read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    start = text.index(f"## {heading}")
    remainder = text[start + len(f"## {heading}") :]
    for match in re.finditer(r"(?m)^## ", remainder):
        if remainder[: match.start()].count("```") % 2 == 0:
            return remainder[: match.start()]
    return remainder


class GitStackSkillContractTests(unittest.TestCase):
    def test_public_skill_catalog_names_and_ui_metadata_stay_aligned(self) -> None:
        expected = {
            "git-commit",
            "github-actions",
            "github",
            "github-investigation",
            "github-issues",
            "github-releases",
            "github-repository-triage",
            "github-review-threads",
            "github-stars",
            "submit",
        }
        skills_root = PLUGIN_ROOT / "skills"
        actual = {path.name for path in skills_root.iterdir() if path.is_dir()}
        self.assertEqual(actual, expected)

        for name in sorted(expected):
            skill = read(f"skills/{name}/SKILL.md")
            metadata = read(f"skills/{name}/agents/openai.yaml")
            short_description = re.search(
                r'^  short_description: "(.+)"$', metadata, flags=re.MULTILINE
            )
            with self.subTest(name=name):
                self.assertRegex(skill, rf"\A---\nname: {re.escape(name)}\n")
                self.assertIsNotNone(short_description)
                assert short_description is not None
                self.assertGreaterEqual(len(short_description.group(1)), 25)
                self.assertLessEqual(len(short_description.group(1)), 64)
                self.assertIn(f"Use $gitstack:{name}", metadata)

    def test_all_skills_route_shell_network_execution_to_shared_contract(self) -> None:
        skills_root = PLUGIN_ROOT / "skills"
        contract = PLUGIN_ROOT / "references" / "network-execution.md"
        self.assertTrue(contract.is_file())

        for skill_path in sorted(skills_root.glob("*/SKILL.md")):
            text = skill_path.read_text(encoding="utf-8")
            with self.subTest(skill=skill_path.parent.name):
                self.assertIn(
                    "Before any shell command that may contact GitHub or a package registry",
                    text,
                )
                self.assertIn(
                    "[Network execution](../../references/network-execution.md)",
                    text,
                )

        contract_text = contract.read_text(encoding="utf-8")
        self.assertIn("sandbox_permissions=require_escalated", contract_text)
        self.assertIn("<plugin-root>/scripts/gitstack --json doctor", contract_text)

    def test_structured_auth_probe_has_one_source_owner(self) -> None:
        source_root = PLUGIN_ROOT / "projects" / "gitstack" / "src" / "gitstack"
        expected_command = [
            "gh",
            "auth",
            "status",
            "--active",
            "--hostname",
            "github.com",
            "--json",
            "hosts",
        ]

        def literal_list(node: ast.AST) -> object:
            if not isinstance(node, ast.List):
                return None
            try:
                return ast.literal_eval(node)
            except (ValueError, TypeError):
                return None

        owners: list[str] = []
        for path in sorted(source_root.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            if any(
                literal_list(node) == expected_command
                for node in ast.walk(tree)
            ):
                owners.append(path.name)
        self.assertEqual(owners, ["health.py"])

        tree = ast.parse((source_root / "health.py").read_text(encoding="utf-8"))
        assignment = next(
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "AUTH_STATUS_COMMAND"
                for target in node.targets
            )
        )
        self.assertEqual(ast.literal_eval(assignment.value), expected_command)

    def test_executable_fences_do_not_inline_provider_text(self) -> None:
        unsafe = re.compile(
            r"--(?:title|body|description|comment|reply-body)(?:=|\s+)[\"']|"
            r"\s-[fF]\s+body=|\s-m\s+[\"']"
        )
        for relative in (
            "skills/github-issues/references/workflows.md",
            "skills/github-releases/references/workflows.md",
            "skills/github-review-threads/references/workflows.md",
            "skills/github-review-threads/references/script-summary.md",
            "skills/submit/references/workflows.md",
        ):
            text = read(relative)
            fences = re.findall(r"```(?:bash|sh)\n(.*?)```", text, flags=re.DOTALL)
            with self.subTest(relative=relative):
                self.assertFalse(any(unsafe.search(fence) for fence in fences))

        review_docs = read("skills/github-review-threads/references/script-summary.md")
        self.assertNotIn("--reply-body", review_docs)
        self.assertNotIn("--selection", review_docs)
        self.assertIn("`address` is read-only", review_docs)

    def test_github_connector_is_declared_and_runtime_required(self) -> None:
        manifest = json.loads(read(".app.json"))

        github = manifest["apps"]["github"]
        self.assertEqual(set(github), {"id"})
        self.assertTrue(github["id"].startswith("connector_"))
        self.assertIn(
            "required GitHub connector",
            read("skills/github/SKILL.md"),
        )

    def test_issue_composers_normalize_provider_boundary(self) -> None:
        paths = (
            "skills/github-repository-triage/SKILL.md",
            "skills/github-repository-triage/references/workflows.md",
            "skills/github-investigation/SKILL.md",
            "skills/submit/SKILL.md",
            "skills/submit/references/workflows.md",
        )

        for relative in paths:
            text = read(relative)
            with self.subTest(relative=relative):
                self.assertIn("mutation_mode=apply", text)
                self.assertIn("issue_operation", text)
                self.assertIn("exact", text.lower())

    def test_review_composers_supply_exact_pr_and_one_operation(self) -> None:
        routes = {
            "skills/github-repository-triage/references/workflows.md": "review_operation=reply",
            "skills/github-investigation/SKILL.md": "review_operation=check|wait",
            "skills/submit/SKILL.md": "review_operation=request",
            "skills/submit/references/workflows.md": "`review_operation`",
        }

        for relative, operation in routes.items():
            text = read(relative)
            with self.subTest(relative=relative):
                self.assertIn(operation, text)
                normalized = " ".join(text.lower().split()).replace(",", "")
                self.assertRegex(normalized, r"exact (repository and pr|pr)")

        submit = read("skills/submit/SKILL.md")
        self.assertIn("review_operation=wait", submit)
        self.assertIn("one operation per", submit)

        review_threads = read("skills/github-review-threads/SKILL.md")
        self.assertIn("reviews request", review_threads)
        self.assertIn("full head SHA", review_threads)
        self.assertIn("persist its complete", review_threads)
        self.assertIn("request receipt", review_threads)
        self.assertIn("never substitutes a newer comment", review_threads)
        self.assertIn("There is no direct legacy fallback", read("skills/github-review-threads/references/workflows.md"))

    def test_submit_always_requests_current_head_codex_review_for_new_and_existing_prs(self) -> None:
        skill = read("skills/submit/SKILL.md")
        workflow_steps = {
            int(number): " ".join(body.split())
            for number, body in re.findall(
                r"(?ms)^([0-9]+)\. (.*?)(?=^[0-9]+\. |\Z)",
                section(skill, "Workflow"),
            )
        }
        workflows = read("skills/submit/references/workflows.md")
        publish = section(workflows, "Publish New Work")
        existing = section(workflows, "Existing PR")
        publish_normalized = " ".join(publish.split())
        existing_normalized = " ".join(existing.split())
        metadata = read("skills/submit/agents/openai.yaml")

        self.assertEqual(sorted(workflow_steps), list(range(1, 10)))
        self.assertIn("existing PR", workflow_steps[6])
        self.assertIn("newly created PR", workflow_steps[7])
        self.assertIn("existing PR", workflow_steps[7])
        self.assertIn("review_operation=request", workflow_steps[7])
        self.assertIn("mutation_mode=apply", workflow_steps[7])
        self.assertIn("provider=codex", workflow_steps[7])
        self.assertIn("full published head SHA", workflow_steps[7])
        self.assertIn("complete typed request receipt", workflow_steps[7])
        self.assertIn("review_operation=wait", workflow_steps[8])
        self.assertIn("only when", workflow_steps[8])
        self.assertIn("review_operation=request", publish)
        self.assertIn("review_operation=wait", publish)
        self.assertIn("review request", existing)
        self.assertIn("without changing its `isDraft` value", workflow_steps[6])
        self.assertIn("ready PR must remain ready", workflow_steps[6])
        self.assertIn("post-update `isDraft` value", publish_normalized)
        self.assertIn("do not run `publish open --draft`", publish_normalized)
        self.assertIn("If `isDraft=false`, keep the PR ready", existing_normalized)
        self.assertIn("request a current-head Codex review", metadata)

    def test_submit_links_every_confirmed_resolved_issue_for_default_branch_closure(self) -> None:
        skill = read("skills/submit/SKILL.md")
        workflows = read("skills/submit/references/workflows.md")
        workflows_normalized = " ".join(workflows.split())
        existing = " ".join(section(workflows, "Existing PR").split())

        self.assertIn("closing_issue_refs", skill)
        self.assertIn("Never infer an issue from a bare number", skill)
        self.assertIn("require the PR base to equal", skill)
        self.assertIn("Read back the PR body", skill)
        self.assertIn("## Issues", workflows)
        self.assertIn("Closes #10", workflows)
        self.assertIn("Closes #123", workflows)
        self.assertIn("Closes octo-org/octo-repo#100", workflows)
        self.assertIn("Each issue gets its own complete `Closes` line", workflows)
        self.assertIn("current `defaultBranchRef.name`", workflows_normalized)
        self.assertIn("--base <default-branch>", workflows)
        self.assertIn(
            "preserve unrelated template and author content",
            workflows_normalized,
        )
        self.assertIn("closing_issue_refs=[]", workflows)
        self.assertIn("Preserve every previously valid closing reference", existing)
        self.assertIn("read back every expected line exactly once", existing)

    def test_review_wait_duration_is_caller_owned(self) -> None:
        paths = (
            "skills/github-review-threads/SKILL.md",
            "skills/github-review-threads/references/script-summary.md",
            "skills/github-review-threads/references/workflows.md",
        )

        for relative in paths:
            text = read(relative)
            with self.subTest(relative=relative):
                self.assertIn("--timeout <caller-owned-duration>", text)
                self.assertNotIn("--timeout 15m", text)

        owner = " ".join(read("skills/github-review-threads/references/script-summary.md").split())
        self.assertIn("composing caller that owns a deadline", owner)
        self.assertIn("GitStack never replaces, extends, or segments it", owner)

    def test_invocation_registry_excludes_result_and_judgment_fields(self) -> None:
        options = read("references/options.md")

        self.assertIn("protocol inputs, not", options)
        self.assertNotIn("`review_state`", options)
        self.assertNotIn("`refactor_disposition`", options)
        self.assertIn(
            "`review_state` is factual CLI result state, not an invocation",
            read("skills/github-review-threads/references/script-summary.md"),
        )
        self.assertIn(
            "`refactor_disposition` is a judgment returned by",
            read("skills/github-investigation/SKILL.md"),
        )

    def test_git_commit_fixups_are_explicit_targeted_and_never_autosquashed(self) -> None:
        options = read("references/options.md")
        skill = read("skills/git-commit/SKILL.md")
        workflows = read("skills/git-commit/references/workflows.md")
        metadata = read("skills/git-commit/agents/openai.yaml")

        self.assertRegex(
            options,
            r"\| `commit_kind` \| `regular`, `fixup`, `amend-fixup` \| `regular` \|",
        )
        self.assertIn("`target_commit` is exact factual input", options)
        self.assertIn("review feedback by itself never selects a fixup", skill)
        self.assertIn("require that subject to be unique", skill)
        self.assertIn("scripts/validate-fixup-target", workflows)
        self.assertIn("subject shared by another commit reachable from", workflows)
        self.assertIn("git commit --fixup=\"$target_sha\"", workflows)
        self.assertIn("git commit --fixup=\"amend:$target_sha\"", workflows)
        self.assertIn("git commit --only --fixup=\"$target_sha\"", workflows)
        self.assertIn("git diff --quiet -- <explicit-paths>", workflows)
        self.assertIn(
            "Partial staging within an intended file is unsupported",
            " ".join(workflows.split()),
        )
        self.assertIn("GIT_EDITOR=\"$helper\"", workflows)
        self.assertIn("git commit --fixup=\"amend:$target_sha\"", workflows)
        self.assertIn("Never replace this command with a plain `git commit -F`", workflows)
        self.assertIn("Never use `git commit --amend`", workflows)
        self.assertIn("`git rebase --autosquash`", workflows)
        self.assertIn("force push", workflows)
        self.assertIn("never add trailers", skill)
        self.assertIn("never infer fixup from feedback alone", metadata)
        self.assertIn("never autosquash", metadata)

        submit = " ".join(read("skills/submit/SKILL.md").split())
        self.assertIn("Do not override Git Commit's `commit_kind` selection", submit)
        self.assertIn("target-repository instructions with an exact target", submit)

    def test_amend_fixup_editor_preserves_git_generated_target_matcher(self) -> None:
        helper = PLUGIN_ROOT / "skills/git-commit/scripts/replace-amend-fixup-message"
        self.assertTrue(os.access(helper, os.X_OK))

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            edit_path = root / "COMMIT_EDITMSG"
            replacement_path = root / "replacement.txt"
            edit_path.write_text(
                "amend! Original subject\n\nOriginal subject\n\nOriginal body\n",
                encoding="utf-8",
            )
            replacement_path.write_text(
                "Replacement subject\n\nReplacement body\n",
                encoding="utf-8",
            )
            environment = os.environ.copy()
            environment["GITSTACK_AMEND_MESSAGE_FILE"] = str(replacement_path)

            subprocess.run(
                [str(helper), str(edit_path)],
                check=True,
                env=environment,
                capture_output=True,
                text=True,
            )

            self.assertEqual(
                edit_path.read_text(encoding="utf-8"),
                "amend! Original subject\n\nReplacement subject\n\nReplacement body\n",
            )

    def test_fixup_target_validator_rejects_duplicate_reachable_subjects(self) -> None:
        validator = PLUGIN_ROOT / "skills/git-commit/scripts/validate-fixup-target"
        self.assertTrue(os.access(validator, os.X_OK))

        with tempfile.TemporaryDirectory() as directory:
            environment = os.environ.copy()
            environment.update(
                {
                    "GIT_AUTHOR_NAME": "Test",
                    "GIT_AUTHOR_EMAIL": "test@example.com",
                    "GIT_COMMITTER_NAME": "Test",
                    "GIT_COMMITTER_EMAIL": "test@example.com",
                }
            )
            subprocess.run(["git", "init", "-q", directory], check=True)

            def commit(subject: str) -> str:
                subprocess.run(
                    ["git", "-C", directory, "commit", "--allow-empty", "-m", subject],
                    check=True,
                    env=environment,
                    capture_output=True,
                    text=True,
                )
                return subprocess.check_output(
                    ["git", "-C", directory, "rev-parse", "HEAD"],
                    text=True,
                ).strip()

            commit("Base")
            target_sha = commit("Target subject")
            unique = subprocess.run(
                [str(validator), target_sha],
                cwd=directory,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(unique.returncode, 0, unique.stderr)
            self.assertEqual(unique.stdout.strip(), target_sha)

            commit("Target subject")
            duplicate = subprocess.run(
                [str(validator), target_sha],
                cwd=directory,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertIn("subject is not unique", duplicate.stderr)

    def test_pure_reads_omit_mutation_mode(self) -> None:
        options = read("references/options.md")
        triage = read("skills/github-repository-triage/SKILL.md")
        releases = read("skills/github-releases/SKILL.md")

        self.assertIn("Omit `mutation_mode`", options)
        self.assertIn("Pure queue reads omit both fields", " ".join(triage.split()))
        self.assertIn("Omit `mutation_mode` for `inspect`", releases)

    def test_github_triage_owns_only_queue_grouping(self) -> None:
        triage = read("skills/github-repository-triage/SKILL.md")
        metadata = read("skills/github-repository-triage/agents/openai.yaml")

        self.assertIn("Route evidence-backed issue disposition", triage)
        self.assertIn("$gitstack:github-investigation", triage)
        self.assertIn("routing disposition judgment", metadata)
        self.assertIn("one or more GitHub repositories", triage)
        self.assertIn("gitstack portfolio scan", triage)
        self.assertIn(
            "per-repository failures",
            read(
                "skills/github-repository-triage/references/script-summary.md"
            ).lower(),
        )
        self.assertFalse(
            (PLUGIN_ROOT / "skills/github-repository-triage/references/issue-workflows.md").exists()
        )

    def test_triage_transports_are_strictly_read_only(self) -> None:
        for relative in ("skills/github-repository-triage/SKILL.md",):
            transport = section(read(relative), "Transport")
            normalized = " ".join(transport.split())
            with self.subTest(relative=relative):
                self.assertIn("supported remote reads", normalized)
                self.assertIn(
                    "This skill never performs GitHub writes or automatically "
                    "falls back between write transports",
                    normalized,
                )
                self.assertNotIn("supported remote reads and writes", normalized)
                self.assertNotIn(
                    "An authorized connector write may fall back", normalized
                )

    def test_github_triage_links_canonical_handoff_registry(self) -> None:
        triage = read("skills/github-repository-triage/SKILL.md")

        self.assertIn("`../../references/options.md`", triage)
        self.assertIn("canonical GitStack invocation fields", triage)


if __name__ == "__main__":
    unittest.main()
