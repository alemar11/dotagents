from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = SKILLS_ROOT.parent
REMOVED_LEGACY_PLANNING_SKILL = "$to" + "-p" + "rd"
REMOVED_ISSUE_SKILL = "$to" + "-issues"
REMOVED_LEGACY_PLANNING_PATH = "skills/to" + "-p" + "rd"
REMOVED_ISSUE_PATH = "skills/to" + "-issues"
LEGACY_WORKER_AUTH_KEY = "default" + "_worker_authorization"
LEGACY_WORKER_AUTH_HEADING = "Worker " + "Authorization Defaults"
LEGACY_DEFAULT_WORKER_AUTH = "Default worker " + "authorization"
ORCHESTRATION_POLICY_PATH = "project-memory/config/orchestration" + "-policy.md"
STALE_NO_GATES_REMAIN = "no " + "gates remain"
STALE_GATES_RESOLVED = "gates " + "resolved or deferred"
STALE_REPO_PR_PLACEHOLDERS = "repo PR links " + "or placeholders"
AUTO_DISPATCH_KEY = "auto" + "_dispatch"
WORKER_SURFACES_KEY = "worker" + "_surfaces"
MAX_ACTIVE_DELEGATED_WORKERS_KEY = "max" + "_active_delegated_workers"
MAX_ACTIVE_CLI_SUBAGENTS_KEY = "max" + "_active_cli_subagents"
MAX_ACTIVE_CODEX_APP_THREADS_KEY = "max" + "_active_codex_app_threads"
SESSION_WIDE_DELEGATED_WORKER_CAP_KEY = "session" + "_wide_delegated_worker_cap"
AUTHORIZATION_CEILING_KEY = "authorization" + "_ceiling"
RUNTIME_POLICY_FIELDS = (
    AUTO_DISPATCH_KEY + ":",
    WORKER_SURFACES_KEY + ":",
    MAX_ACTIVE_DELEGATED_WORKERS_KEY + ":",
    MAX_ACTIVE_CLI_SUBAGENTS_KEY + ":",
    MAX_ACTIVE_CODEX_APP_THREADS_KEY + ":",
    SESSION_WIDE_DELEGATED_WORKER_CAP_KEY + ":",
    AUTHORIZATION_CEILING_KEY + ":",
)
ACTIVE_TEXT_SUFFIXES = {".json", ".md", ".py", ".sh", ".toml", ".yaml", ".yml"}


def read(relative: str) -> str:
    return (SKILLS_ROOT / relative).read_text(encoding="utf-8")


def read_repo(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def option_row_evidence_is_valid(rows: list[list[str]]) -> bool:
    for _, scope, field, value, source, evidence in rows:
        if source != "default" and evidence in {"", "none"}:
            return False
        permission_bearing = (
            field == "change_delivery_permission"
            and value == "granted-for-selected-target"
        ) or (
            field == "issue_update_permission"
            and value
            in {
                "pull-request-closing-keyword-only",
                "direct-issue-updates-explicitly-authorized",
            }
        )
        if not permission_bearing:
            continue
        if source not in {
            "default",
            "source-spec",
            "authorized-user-instruction",
        }:
            return False
        tokens = dict(
            token.split("=", 1)
            for token in evidence.split(";")
            if "=" in token
        )
        permission_ref = tokens.get("permission-source-ref", "")
        if (
            not permission_ref
            or tokens.get("scope-ref") != scope
            or not tokens.get("target-ref")
            or not tokens.get("target-branch")
        ):
            return False
        if source == "default" and not permission_ref.startswith(
            "feature-spec-default:"
        ):
            return False
        if source == "authorized-user-instruction" and not permission_ref.startswith(
            "authorized-user:"
        ):
            return False
    return True


def parse_option_rows(section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells[0] == "row_id" or all(
            set(cell) <= {"-", ":", " "} for cell in cells
        ):
            continue
        if len(cells) != 6:
            raise ValueError(f"option row has {len(cells)} cells instead of 6")
        rows.append(
            [
                cell[1:-1]
                if len(cell) >= 2
                and cell.startswith("`")
                and cell.endswith("`")
                else cell
                for cell in cells
            ]
        )
    return rows


def fingerprint_option_rows(rows: list[list[str]]) -> str:
    serialized = "".join(
        "\t".join(row) + "\n" for row in sorted(rows, key=lambda row: row[0])
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def markdown_section(contents: str, heading: str, next_heading: str) -> str:
    starts = list(
        re.finditer(rf"^{re.escape(heading)}$", contents, re.MULTILINE)
    )
    ends = list(
        re.finditer(rf"^{re.escape(next_heading)}$", contents, re.MULTILINE)
    )
    if len(starts) != 1 or len(ends) != 1 or ends[0].start() <= starts[0].end():
        raise ValueError(
            f"expected one ordered {heading!r} to {next_heading!r} section"
        )
    return contents[starts[0].end() : ends[0].start()]


def iter_active_text_files() -> list[Path]:
    roots = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "AGENTS.md",
        SKILLS_ROOT,
        REPO_ROOT / ".agents",
    ]
    files: list[Path] = []

    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            files.append(root)
            continue
        for path in root.rglob("*"):
            if (
                path.is_file()
                and path.suffix in ACTIVE_TEXT_SUFFIXES
                and "__pycache__" not in path.parts
            ):
                files.append(path)

    return sorted(set(files))


class FullFlowDryRunFixtureTests(unittest.TestCase):
    def test_multi_repo_workspace_topology_propagation_fixture(self) -> None:
        workspace_feature_repos = ("api", "web")
        child_specs = {
            "api": {
                "source_spec_ref": "https://github.com/example/api/issues/10",
                "repository_layout": "multi-repository-workspace",
                "child_repository_layout": "single-repository",
            },
            "web": {
                "source_spec_ref": "https://github.com/example/web/issues/20",
                "repository_layout": "multi-repository-workspace",
                "child_repository_layout": "monorepo",
            },
        }
        workspace_child_source_refs = {
            repo: spec["source_spec_ref"] for repo, spec in child_specs.items()
        }

        self.assertEqual(set(workspace_child_source_refs), set(workspace_feature_repos))
        for child_spec in child_specs.values():
            self.assertEqual("multi-repository-workspace", child_spec["repository_layout"])
            self.assertIn(
                child_spec["child_repository_layout"],
                {"single-repository", "monorepo", "multi-repository-workspace"},
            )

        def build_issue(
            issue_id: str,
            target_repos: tuple[str, ...],
            parent_source_ref: str,
        ) -> dict[str, object]:
            if not set(target_repos).issubset(workspace_feature_repos):
                raise ValueError("issue target repos must be within workspace_feature_repos")
            if len(target_repos) == 1:
                repo = target_repos[0]
                return {
                    "issue_id": issue_id,
                    "target_repos": target_repos,
                    "source_spec_ref": workspace_child_source_refs[repo],
                    "issue_repository_layout": child_specs[repo]["child_repository_layout"],
                    "workspace_child_source_refs": workspace_child_source_refs,
                }
            if parent_source_ref == "not-applicable":
                raise ValueError("root-owned spanning issues require a workspace-level source")
            return {
                "issue_id": issue_id,
                "target_repos": target_repos,
                "source_spec_ref": parent_source_ref,
                "issue_repository_layout": "multi-repository-workspace",
                "workspace_child_source_refs": workspace_child_source_refs,
            }

        issues = [
            build_issue("01", ("api",), "orchestration/platform/features/auth/SPEC.md"),
            build_issue("02", ("web",), "orchestration/platform/features/auth/SPEC.md"),
            build_issue("03", ("api", "web"), "orchestration/platform/features/auth/SPEC.md"),
        ]

        self.assertEqual("single-repository", issues[0]["issue_repository_layout"])
        self.assertEqual("monorepo", issues[1]["issue_repository_layout"])
        self.assertEqual("multi-repository-workspace", issues[2]["issue_repository_layout"])
        with self.assertRaisesRegex(ValueError, "workspace-level source"):
            build_issue("04", ("api", "web"), "not-applicable")

        ledger_workstreams = {
            issue["issue_id"]: {
                "source_spec_ref": issue["source_spec_ref"],
                "workstream_repository_layout": issue["issue_repository_layout"],
                "workspace_child_source_refs": issue["workspace_child_source_refs"],
            }
            for issue in issues
        }

        self.assertEqual(
            "single-repository",
            ledger_workstreams["01"]["workstream_repository_layout"],
        )
        self.assertEqual(
            "monorepo",
            ledger_workstreams["02"]["workstream_repository_layout"],
        )
        self.assertEqual(
            "multi-repository-workspace",
            ledger_workstreams["03"]["workstream_repository_layout"],
        )
        for workstream in ledger_workstreams.values():
            self.assertEqual(
                set(workstream["workspace_child_source_refs"]),
                set(workspace_feature_repos),
            )

    def test_fixture_covers_pipeline_and_draft_source_spec(self) -> None:
        fixture = read("plan-feature/references/full-flow-dry-run.md")

        for text in (
            "$plan-feature",
            "$grill-me-with-context",
            "The Feature Spec phase",
            "The issue phase",
            "$codex-orchestrator",
        ):
            self.assertIn(text, fixture)

        self.assertNotIn(REMOVED_LEGACY_PLANNING_SKILL, fixture)
        self.assertNotIn(REMOVED_ISSUE_SKILL, fixture)

        self.assertIn("effective_target: draft-publish-commands", fixture)
        self.assertIn("no_mutation_override: dry-run", fixture)
        self.assertIn("no_mutation_output: publish-commands", fixture)
        self.assertIn("option_rows_fingerprint: sha256:", fixture)
        self.assertIn("local_mirror_path: not-applicable", fixture)
        self.assertIn("target_branch_name: feature/account-settings-export", fixture)
        self.assertIn("the structured delivery handoff tuple", fixture)
        self.assertIn(
            "`change_delivery_target=pull-request-ready-for-merge-but-not-merged`",
            fixture,
        )
        self.assertIn(
            "`change_delivery_permission=granted-for-selected-target`",
            fixture,
        )
        self.assertIn("`target_branch_name=feature/account-settings-export`", fixture)
        self.assertIn(
            "`codex_review_requirement=required-on-current-pull-request-head`",
            fixture,
        )
        self.assertIn("`pull_request_count_strategy=one-pull-request-total`", fixture)
        self.assertIn("`repository_layout: single-repository` and\n   `target_branch_name: feature/account-settings-export`", fixture)
        self.assertIn("source_spec_ref: draft-spec:account-settings-export", fixture)
        self.assertIn("spec_body_fingerprint: sha256:7f4a9c21d003", fixture)
        self.assertIn("capture_mode: defer-to-caller", fixture)
        self.assertIn("capture_outcome: deferred", fixture)
        self.assertIn("domain_knowledge_delta", fixture)
        self.assertIn("knowledge_delta: required", fixture)
        self.assertIn("target_surfaces:", fixture)
        self.assertIn("evidence:", fixture)
        self.assertIn("current-repository/src/account-settings/export.ts", fixture)

        option_rows_section = markdown_section(
            fixture,
            "## Canonical Run Option Rows",
            "## Representative Emitted Issue",
        )
        option_rows = parse_option_rows(option_rows_section)

        row_ids = [row[0] for row in option_rows]
        self.assertEqual(len(row_ids), len(set(row_ids)))
        expected_run_fields = {
            "mode",
            "execution_profile",
            "tracker_backend",
            "effective_target",
            "no_mutation_override",
            "no_mutation_output",
            "local_mirror",
            "local_mirror_path",
            "partial_output",
            "repository_layout",
            "workspace_context",
            "change_delivery_target",
            "change_delivery_permission",
            "issue_update_permission",
            "codex_review_requirement",
            "target_branch_name",
            "pull_request_count_strategy",
        }
        self.assertEqual(len(option_rows), len(expected_run_fields))
        self.assertEqual({row[2] for row in option_rows}, expected_run_fields)
        self.assertEqual(
            set(row_ids),
            {f"run:{field}" for field in expected_run_fields},
        )
        self.assertTrue(all(row[1] == "run" for row in option_rows))
        self.assertTrue(option_row_evidence_is_valid(option_rows))
        expected_run_contract = {
            "mode": ("full-flow", "authorized-user-instruction", "fixture-intent"),
            "execution_profile": ("standard", "default", "none"),
            "tracker_backend": (
                "github",
                "tracker-config",
                "project-memory/config/issue-tracker.md",
            ),
            "effective_target": (
                "draft-publish-commands",
                "runtime-derived",
                "run:no_mutation_override+run:no_mutation_output",
            ),
            "no_mutation_override": (
                "dry-run",
                "authorized-user-instruction",
                "fixture-intent",
            ),
            "no_mutation_output": (
                "publish-commands",
                "authorized-user-instruction",
                "fixture-intent",
            ),
            "local_mirror": ("not-requested", "default", "none"),
            "local_mirror_path": ("not-applicable", "default", "none"),
            "partial_output": ("withhold", "default", "none"),
            "repository_layout": (
                "single-repository",
                "project-layout-config",
                "project-memory/config/project-layout.md",
            ),
            "workspace_context": ("not-applicable", "default", "none"),
            "change_delivery_target": (
                "pull-request-ready-for-merge-but-not-merged",
                "default",
                "none",
            ),
            "change_delivery_permission": (
                "granted-for-selected-target",
                "default",
                "permission-source-ref=feature-spec-default:account-settings-export;scope-ref=run;target-ref=draft-spec:account-settings-export;target-branch=feature/account-settings-export",
            ),
            "issue_update_permission": (
                "pull-request-closing-keyword-only",
                "default",
                "permission-source-ref=feature-spec-default:account-settings-export;scope-ref=run;target-ref=draft-spec:account-settings-export;target-branch=feature/account-settings-export",
            ),
            "target_branch_name": (
                "feature/account-settings-export",
                "runtime-derived",
                "run:change_delivery_target+feature_slug",
            ),
            "codex_review_requirement": (
                "required-on-current-pull-request-head",
                "default",
                "run:change_delivery_target",
            ),
            "pull_request_count_strategy": ("one-pull-request-total", "runtime-derived", "affected_repos=current-repository"),
        }
        self.assertEqual(
            {row[2]: (row[3], row[4], row[5]) for row in option_rows},
            expected_run_contract,
        )
        setup_snapshot = markdown_section(
            fixture,
            "## Setup Snapshot",
            "## Canonical Run Option Rows",
        )
        incoming_fingerprints = re.findall(
            r"^option_rows_fingerprint: sha256:([0-9a-f]{64})$",
            setup_snapshot,
            re.MULTILINE,
        )
        self.assertEqual(len(incoming_fingerprints), 1)
        self.assertEqual(
            fingerprint_option_rows(option_rows),
            incoming_fingerprints[0],
        )

        issue_section = markdown_section(
            fixture,
            "## Representative Emitted Issue",
            "## Representative Issue-Phase Handoff",
        )
        issue_rows = parse_option_rows(issue_section)
        expected_issue_fields = {
            "delivery_decision_origin",
            "change_delivery_target",
            "change_delivery_permission",
            "issue_repository_layout",
            "issue_update_permission",
            "codex_review_requirement",
            "pull_request_count_strategy",
            "parallelization",
            "issue_completion_method",
            "domain_closeout",
            "target_branch_name",
        }
        issue_row_ids = [row[0] for row in issue_rows]
        self.assertEqual(len(issue_rows), len(expected_issue_fields))
        self.assertEqual(len(issue_row_ids), len(set(issue_row_ids)))
        self.assertEqual({row[2] for row in issue_rows}, expected_issue_fields)
        self.assertEqual(
            set(issue_row_ids),
            {f"issue:01:{field}" for field in expected_issue_fields},
        )
        self.assertTrue(all(row[1] == "issue:01" for row in issue_rows))
        self.assertTrue(option_row_evidence_is_valid(issue_rows))
        expected_issue_contract = {
            "delivery_decision_origin": (
                "inherited-from-feature-spec",
                "source-spec",
                "draft-spec:account-settings-export",
            ),
            "change_delivery_target": (
                "pull-request-ready-for-merge-but-not-merged",
                "source-spec",
                "run:change_delivery_target",
            ),
            "change_delivery_permission": (
                "granted-for-selected-target",
                "source-spec",
                "permission-source-ref=feature-spec-default:account-settings-export;scope-ref=issue:01;target-ref=draft-spec:account-settings-export;target-branch=feature/account-settings-export;permission-transfer-ref=run",
            ),
            "issue_repository_layout": ("single-repository", "source-spec", "run:repository_layout"),
            "issue_update_permission": (
                "pull-request-closing-keyword-only",
                "source-spec",
                "permission-source-ref=feature-spec-default:account-settings-export;scope-ref=issue:01;target-ref=draft-spec:account-settings-export;target-branch=feature/account-settings-export;permission-transfer-ref=run",
            ),
            "pull_request_count_strategy": ("one-pull-request-total", "source-spec", "run:pull_request_count_strategy"),
            "codex_review_requirement": (
                "required-on-current-pull-request-head",
                "source-spec",
                "run:codex_review_requirement",
            ),
            "parallelization": (
                "independent",
                "runtime-derived",
                "issue-graph:01",
            ),
            "issue_completion_method": (
                "feature-pull-request-closing-keyword",
                "runtime-derived",
                "run:tracker_backend+issue:01:pull_request_count_strategy",
            ),
            "domain_closeout": (
                "implementation-closeout",
                "runtime-derived",
                "domain_knowledge_delta+issue-graph:01",
            ),
            "target_branch_name": (
                "feature/account-settings-export",
                "source-spec",
                "run:target_branch_name",
            ),
        }
        self.assertEqual(
            {row[2]: (row[3], row[4], row[5]) for row in issue_rows},
            expected_issue_contract,
        )
        emitted_fingerprints = re.findall(
            r"^issue_option_rows_fingerprint: sha256:([0-9a-f]{64})$",
            issue_section,
            re.MULTILINE,
        )
        self.assertEqual(len(emitted_fingerprints), 1)
        self.assertEqual(
            fingerprint_option_rows(issue_rows),
            emitted_fingerprints[0],
        )
        self.assertIsNone(
            re.search(r"^option_rows_fingerprint:", issue_section, re.MULTILINE)
        )
        phase_handoff = markdown_section(
            fixture,
            "## Representative Issue-Phase Handoff",
            "## Expected Pipeline",
        )
        graph_fingerprints = re.findall(
            r"^option_rows_fingerprint: sha256:([0-9a-f]{64})$",
            phase_handoff,
            re.MULTILINE,
        )
        self.assertEqual(len(graph_fingerprints), 1)
        self.assertEqual(
            fingerprint_option_rows(option_rows + issue_rows),
            graph_fingerprints[0],
        )
        self.assertIn("## Domain Knowledge Handoff", fixture)
        self.assertIn("## Domain Knowledge Closeout", fixture)
        self.assertIn("last integration task", fixture)
        self.assertIn("$project-memory domain-memory", fixture)
        self.assertIn("internal domain-modeling workflow", fixture)
        self.assertIn("Replace every issue body line", fixture)
        self.assertIn("must not dispatch implementation workers", fixture)
        self.assertNotIn(LEGACY_WORKER_AUTH_KEY, fixture)
        self.assertIn("project memory, plan-feature output, tracker defaults", fixture)
        self.assertIn("authorization fields or worker capability modes", fixture)
        self.assertIn("## Expected Runtime Efficiency Evidence", fixture)
        self.assertIn("each `issue-hardening:<id>`", fixture)
        self.assertIn("one `tokens=unavailable` result without estimation", fixture)
        self.assertIn("repeatedly emitted between phases", fixture)

    def test_non_default_option_sources_reject_empty_or_none_evidence(self) -> None:
        base = [["run:mode", "run", "mode", "full-flow", "authorized-user-instruction", "request-1"]]
        self.assertTrue(option_row_evidence_is_valid(base))
        for invalid in ("", "none"):
            with self.subTest(evidence=invalid):
                row = [base[0][:-1] + [invalid]]
                self.assertFalse(option_row_evidence_is_valid(row))

        default_permission = [[
            "run:change_delivery_permission",
            "run",
            "change_delivery_permission",
            "granted-for-selected-target",
            "default",
            "none",
        ]]
        self.assertFalse(option_row_evidence_is_valid(default_permission))
        default_permission[0][-1] = (
            "permission-source-ref=feature-spec-default:demo;scope-ref=run;"
            "target-ref=draft-spec:demo;target-branch=feature/demo"
        )
        self.assertTrue(option_row_evidence_is_valid(default_permission))
        runtime_derived_permission = [list(default_permission[0])]
        runtime_derived_permission[0][4] = "runtime-derived"
        self.assertFalse(option_row_evidence_is_valid(runtime_derived_permission))

        options = read("plan-feature/references/options.md")
        self.assertIn("Every non-default\nsource requires non-empty evidence", options)

    def test_shared_contract_documents_draft_publish_handoff(self) -> None:
        contract = read("project-memory/references/tracker-publishing.md")

        self.assertIn("source_spec_ref", contract)
        self.assertIn("draft-spec:<feature-slug>", contract)
        self.assertIn("Create or update the Feature Spec first", contract)
        self.assertIn("Replace `source_spec_ref: draft-spec:<...>`", contract)
        self.assertIn("`no_mutation_override=dry-run`", contract)
        self.assertIn("`no_mutation_override=draft-output`", contract)
        self.assertIn("Do not dispatch implementation workers", contract)
        self.assertIn(
            "`temporary_source_execution_permission=granted-by-authorized-user`",
            contract,
        )
        self.assertNotIn("explicit owner decision to use the full Feature Spec body", contract)

    def test_project_memory_does_not_own_orchestration_policy_setup(self) -> None:
        project_memory = read("project-memory/SKILL.md")
        setup_workflow = read("project-memory/references/setup-workflow.md")
        orchestrator = read("codex-orchestrator/SKILL.md")
        worker = read("codex-orchestrator/references/worker.md")
        ledger = read("codex-orchestrator/references/ledger.md")
        ledger_template = read("codex-orchestrator/references/ledger-template.md")
        orchestrator_options = read("codex-orchestrator/references/options.md")

        self.assertNotIn(ORCHESTRATION_POLICY_PATH, project_memory)
        self.assertNotIn("orchestration-policy", setup_workflow)
        self.assertIn("## Structured Configuration", project_memory)
        self.assertNotIn(ORCHESTRATION_POLICY_PATH, orchestrator)
        self.assertIn("## Session Option Resolution", worker)
        self.assertNotIn("policy-auto-dispatched", worker)
        self.assertNotIn("policy-auto-dispatched", ledger)
        for retired in (
            "work_delegation_policy",
            "delegated_worker_visibility",
            "max_concurrent_delegated_workers",
            "max_visible_app_tasks",
        ):
            self.assertNotIn(retired, orchestrator_options)
            self.assertNotIn(retired, ledger_template)
        self.assertIn(
            "`visible_app_task_permission` | `not-requested`, "
            "`granted-by-authorized-user`, `denied-by-authorized-user`",
            orchestrator_options,
        )
        self.assertIn(
            "visible_app_task_permission: "
            "not-requested|granted-by-authorized-user|denied-by-authorized-user",
            ledger_template,
        )
        self.assertIn(
            "internal_subdelegation: allowed-within-assigned-scope",
            ledger_template,
        )
        self.assertIn("## Feature Spec Thread Registry", ledger_template)
        self.assertIn(
            "both authorizes the surface and requires its use for Feature Spec implementation",
            " ".join(orchestrator_options.split()),
        )
        self.assertIn(
            "exactly one active visible Codex App thread for each",
            " ".join(worker.split()),
        )
        self.assertIn("codex_review_poll_owner", ledger_template)
        self.assertIn("## Wave Reports", ledger_template)
        self.assertIn("Execution Report", ledger_template)
        self.assertNotIn("## Wave Checkpoints", ledger)
        self.assertNotIn("## Wave Checkpoints", ledger_template)

    def test_issue_tracker_templates_stay_tracker_focused(self) -> None:
        for relative in (
            "project-memory/references/issue-tracker-github.md",
            "project-memory/references/issue-tracker-local.md",
        ):
            contents = read(relative)
            normalized = " ".join(contents.split())
            with self.subTest(file=relative):
                self.assertIn("## Configuration", contents)
                self.assertIn("| Key | Type | Value | Allowed values | Meaning |", contents)
                self.assertNotIn(ORCHESTRATION_POLICY_PATH, contents)
                self.assertIn("Tracker setup records artifact routing", contents)
                self.assertIn("Branch only on the canonical `effective_target`", normalized)
                self.assertIn("`source_spec_ref`", contents)
                self.assertNotIn("Source " + "Feature Spec", contents)
                if relative.endswith("issue-tracker-local.md"):
                    self.assertIn("must use canonical", normalized)
                else:
                    self.assertIn("canonical `source_spec_ref` field", contents)
                self.assertNotIn("current request explicitly asks for dry-run", contents)
                self.assertNotIn("current-run no-mutation override is active", contents)
                for field in RUNTIME_POLICY_FIELDS:
                    self.assertNotIn(field, contents)

        github_contract = read("project-memory/references/issue-tracker-github.md")
        self.assertIn("`source_spec_ref`, delivery metadata", github_contract)
        self.assertIn("canonical `source_spec_ref` field", github_contract)
        self.assertIn("`local_mirror=requested`", github_contract)
        self.assertNotIn("explicitly asks to keep a local mirror", github_contract)

        local_contract = read("project-memory/references/issue-tracker-local.md")
        self.assertIn("`effective_target=local-dry-run`", local_contract)
        self.assertIn("temporary working space only", local_contract)
        self.assertIn("`planning/features/<feature-slug>/SPEC.md`", local_contract)
        self.assertIn("`planning/features/<feature-slug>/issues/<NN>-<slug>.md`", local_contract)
        self.assertIn("Never use a `planning/tmp/`", local_contract)
        self.assertNotIn("explicitly asks to keep completed issue", local_contract)

    def test_plan_feature_references_internal_phase_templates(self) -> None:
        plan_feature = read("plan-feature/SKILL.md")
        spec_phase = read("plan-feature/references/spec-phase.md")
        issue_phase = read("plan-feature/references/issue-phase.md")
        spec_template = read("plan-feature/references/spec-template.md")
        issue_template = read("plan-feature/references/issue-body-template.md")
        vertical_slices = read("plan-feature/references/vertical-slices.md")
        options = read("plan-feature/references/options.md")
        spec_delivery = read("codex-orchestrator/references/spec-backed-delivery.md")
        normalized_plan_feature = " ".join(plan_feature.split())
        normalized_spec_phase = " ".join(spec_phase.split())
        normalized_spec_template = " ".join(spec_template.split())
        normalized_options = " ".join(options.split())

        self.assertIn("references/full-flow-dry-run.md", plan_feature)
        self.assertIn("`tracker_backend`", plan_feature)
        self.assertIn("keyed\n`option_resolution` rows", plan_feature)
        self.assertIn("`repository_layout`", plan_feature)
        self.assertIn("`child_repository_layout`", plan_feature)
        self.assertIn("run only `$project-memory project-layout`\nbefore recording the option snapshot", plan_feature)
        self.assertIn(
            "`codex_review_requirement`, `target_branch_name`, and",
            plan_feature,
        )
        self.assertIn("Keep worker surfaces, worker counts", plan_feature)
        self.assertIn("run child repo partial planning only when all affected child repos share one effective child `tracker_backend`", normalized_plan_feature)
        self.assertIn("when child backends are mixed", plan_feature)
        self.assertIn("two-pass child publication flow", plan_feature)
        self.assertIn("the run-level `repository_layout` row is `multi-repository-workspace`", normalized_plan_feature)
        self.assertIn("per-issue `issue_repository_layout`", plan_feature)
        self.assertIn("each affected child repo's `project-memory/config/project-layout.md`", plan_feature)
        self.assertIn("`workspace_context=multi-repository-workspace`", plan_feature)
        self.assertIn("`workspace_child_source_refs` repo-to-Feature-Spec mapping", plan_feature)
        self.assertIn("`workspace_child_source_refs=unresolved-first-pass`", plan_feature)
        self.assertIn("Invoke the issue phase only after the required child partial Feature Spec refs", plan_feature)
        self.assertNotIn(ORCHESTRATION_POLICY_PATH, plan_feature)
        self.assertIn("`tracker_backend` as planning-artifact write authority", plan_feature)
        self.assertIn("Planning blockers", plan_feature)
        self.assertIn("Include exactly one canonical domain outcome", plan_feature)
        self.assertNotIn("Domain knowledge: captured in <path or durable surface>", plan_feature)
        self.assertIn("`capture_outcome=deferred`", plan_feature)
        self.assertIn("`capture_outcome=no-durable-change`", plan_feature)
        self.assertIn("`mode=spec-only`", plan_feature)
        self.assertIn("never emits `capture_outcome=captured`", plan_feature)
        self.assertIn("issue lifecycle mutations belong to", plan_feature)
        self.assertNotIn(STALE_NO_GATES_REMAIN, plan_feature)
        self.assertNotIn(STALE_GATES_RESOLVED, plan_feature)
        self.assertIn("references/spec-phase.md", plan_feature)
        self.assertIn("references/issue-phase.md", plan_feature)
        self.assertIn("tracker-publishing.md", spec_phase)
        self.assertIn("## Feature Spec Target Model", spec_phase)
        self.assertIn("planning/features/<feature-slug>/SPEC.md", spec_phase)
        self.assertIn("When `workspace_context=multi-repository-workspace`", spec_phase)
        self.assertIn("Feature Spec body fingerprint", spec_phase)
        self.assertIn("Feature Spec planning-artifact publication", spec_phase)
        self.assertIn("tracker_backend` is the planning-artifact write authority", spec_phase)
        self.assertIn("affected child repo's `project-memory/config/issue-tracker.md`", spec_phase)
        self.assertIn("`project-memory/config/project-layout.md`", spec_phase)
        self.assertIn("source for `child_repository_layout`", spec_phase)
        self.assertIn("one\noption-resolution run may publish only one artifact set", spec_phase)
        self.assertIn("then publish child repo partials in\nchild run(s) that cite the parent `source_spec_ref`", spec_phase)
        self.assertIn("All affected child repos\nin one generated issue graph must share the same effective child backend", spec_phase)
        self.assertIn("child\nbackends are mixed", spec_phase)
        self.assertIn("two-pass child publication flow", spec_phase)
        self.assertIn("`workspace_context=multi-repository-workspace`", spec_phase)
        self.assertIn("Parent `tracker_backend` controls only the parent/global", spec_phase)
        self.assertIn("`effective_target=configured-tracker`", spec_phase)
        self.assertIn("`local_mirror=requested`", spec_phase)
        self.assertIn("validated `local_mirror_path`", spec_phase)
        self.assertIn("`local_mirror_path`", issue_phase)
        self.assertIn("`target_branch_name`", spec_phase)
        self.assertIn("`target_branch_name`", issue_phase)
        self.assertIn("For `effective_target=local-dry-run`", spec_phase)
        self.assertIn(
            "Commit or push targets require exact\nauthorized-user evidence naming the branch",
            options,
        )
        self.assertIn("the structured delivery handoff tuple: `change_delivery_target`,", spec_phase)
        self.assertIn("`repository_layout`", spec_phase)
        self.assertIn("`child_repository_layout`", spec_phase)
        self.assertIn("`workspace_context`, `workspace_parent_source_ref`", spec_phase)
        self.assertIn("`workspace_child_source_refs` mapping each `workspace_feature_repos` repo", spec_phase)
        self.assertIn("Keys are canonical repo slugs and must match\n  `workspace_feature_repos`", spec_phase)
        self.assertIn("workspace_child_source_refs=unresolved-first-pass", normalized_spec_phase)
        self.assertIn("`issue_update_permission`, `issue_update_permission_evidence`", spec_phase)
        self.assertNotIn("- Project topology: verified `repository_layout` row value.", spec_template)
        self.assertIn("- repository_layout: [verified `repository_layout` row value]", spec_template)
        self.assertIn("- child_repository_layout: [child repo durable topology", spec_template)
        self.assertIn("- workspace_context: [multi-repository-workspace or not-applicable].", spec_template)
        self.assertIn("- workspace_feature_repos: [complete feature-wide repo slug set or not-applicable].", spec_template)
        self.assertIn("- workspace_child_source_refs: [complete repo-to-child Feature Spec mapping", spec_template)
        self.assertIn("`unresolved-first-pass` during first-pass workspace child publication", spec_template)
        self.assertIn("Never choose an individual child partial as the primary source", issue_phase)
        self.assertIn("- target_branch_name: [verified exact branch data]", spec_template)
        self.assertIn("branch mutations also require `target-branch=<target_branch_name>`", normalized_options)
        self.assertIn("- target_branch_name: [verified exact branch data]", issue_template)
        self.assertIn("- target_branch_name: [same effective branch data as `## Delivery`]", issue_template)
        self.assertIn(
            "- change_delivery_permission: [verified `change_delivery_permission` row value]",
            issue_template,
        )
        self.assertIn(
            "- codex_review_requirement: [verified `codex_review_requirement` row value]",
            issue_template,
        )
        self.assertIn(
            "- issue_update_permission: [verified `issue_update_permission` row value]",
            issue_template,
        )
        self.assertIn("`issue_update_permission=direct-issue-updates-explicitly-authorized`", issue_phase)
        self.assertIn("Do not resolve delivery or mutation options in this phase", spec_phase)
        self.assertNotIn("Resolve the Feature Spec `change_delivery_target`", spec_phase)
        self.assertIn("delivery permission alone is insufficient", normalized_options)
        self.assertIn("Retired planning and delivery fields are invalid input", options)
        self.assertIn("`issue_completion_method=final-commit-closing-keyword`,\n  `issue_update_permission=direct-issue-updates-explicitly-authorized`", issue_template)
        self.assertNotIn("repository_integration_method", issue_template)
        self.assertNotIn("repository_integration_method", issue_phase)
        self.assertIn("label the ref\nnon-executable", issue_phase)
        for identity_field in (
            "feature_slug",
            "product_slug",
            "workspace_path",
            "context_file",
            "project_slug",
        ):
            self.assertIn(f"`{identity_field}`", issue_phase)
        self.assertNotIn("run explicitly requested no-mutation output", spec_phase)
        self.assertNotIn("explicitly asked for a local mirror", spec_phase)
        self.assertIn("## Effective Planning-Artifact Target", options)
        self.assertIn("## Per-Issue Registry", options)
        self.assertIn("sole owner of option values", issue_phase)
        self.assertIn("sole owner of option values", normalized_spec_phase)
        self.assertIn(
            "Resolve `effective_target` only through `references/options.md`",
            normalized_spec_phase,
        )
        self.assertIn(
            "`references/options.md` solely owns effective-target and local-mirror option resolution",
            normalized_spec_phase,
        )
        self.assertIn(
            "owns transient body transport, mirror-path application, draft-ref replacement",
            normalized_spec_phase,
        )
        self.assertIn(
            "`references/options.md` is the sole owner of option names, values, defaults",
            normalized_spec_template,
        )
        self.assertIn(
            "only projects an already verified option snapshot",
            normalized_spec_template,
        )
        for duplicated_schema in (
            "tracker_backend: <github|local>",
            "change_delivery_target: <pull-request|direct-commit>",
            "pull_request_count_strategy: <one-pull-request-total|one-pull-request-per-repository|none>",
        ):
            self.assertNotIn(duplicated_schema, spec_phase)
            self.assertNotIn(duplicated_schema, issue_phase)
        self.assertIn("Records the issue-effective stopping point", options)
        self.assertIn("Every issue records its effective delivery tuple", options)
        self.assertIn("## Resolution Record", options)
        self.assertIn("Record one six-column row per run field", options)
        self.assertIn("plus issue-effective `target_branch_name`", options)
        self.assertIn(
            "Permission-bearing values require\n`permission-source-ref`, exact `scope-ref`, and `target-ref`",
            options,
        )
        self.assertIn(
            "Canonicalize all rows with columns `row_id`, `scope_id`, `field`, `value`,",
            options,
        )
        self.assertIn("option_rows_fingerprint: sha256:", options)
        self.assertIn("emits\n`issue_option_rows_fingerprint`", options)
        self.assertIn("`issue:<NN>:<field>`", options)
        self.assertIn("`local-artifacts` | `local-dry-run`", options)
        self.assertIn("`issue_completion_method=move-local-issue-to-done-after-proof`", options)
        self.assertIn("`issue_completion_method=final-commit-closing-keyword`", options)
        self.assertIn("Resolve these fields after the issue graph exists", options)
        self.assertIn("`depends-on` requires dependency ids only", options)
        self.assertIn("An issue target override atomically re-resolves", options)
        self.assertIn("Reject every other combination", options)
        self.assertIn("tracker-publishing.md", issue_phase)
        self.assertIn("Do not add worker authorization defaults", issue_phase)
        self.assertNotIn(ORCHESTRATION_POLICY_PATH, issue_phase)
        self.assertIn("final hardened issue bodies", issue_phase)
        self.assertIn("complete Per-Issue Registry row set", issue_phase)
        self.assertIn("atomically resolves the", issue_phase)
        self.assertIn("complete delivery tuple", issue_phase)
        self.assertIn("Do not hardcode another default\ndelivery tuple", issue_phase)
        self.assertNotIn("- change_delivery_target: pull-request", issue_phase)
        self.assertIn("`partial_output=allow-non-agent-ready`", issue_phase)
        self.assertNotIn("explicitly requested partial backlog output", issue_phase)
        self.assertNotIn("unless it explicitly permits partial output", issue_phase)
        self.assertNotIn("current run explicitly requested\nno-mutation", issue_phase)
        self.assertNotIn("user explicitly requested one", issue_phase)
        self.assertIn("machine-local absolute paths", issue_phase)
        self.assertIn("planning issue publication", issue_phase)
        self.assertIn("tracker_backend` as planning-artifact write authority", issue_phase)
        self.assertIn("Run The Verticality Gate", issue_phase)
        self.assertIn("Re-run `$plan-harder`", issue_phase)
        self.assertNotIn(STALE_REPO_PR_PLACEHOLDERS, issue_phase)
        self.assertIn("references/issue-body-template.md", issue_phase)
        self.assertIn("## Orchestrator Handoff", issue_phase)
        self.assertIn("must not contain worker authorization", issue_phase)
        self.assertIn("For root-owned\n  integration or domain-closeout issues spanning multiple repos", issue_phase)
        self.assertIn("Never choose an individual child partial as the primary source", issue_phase)
        self.assertIn("do not choose one child repo's durable topology as the run-level\n  value", issue_phase)
        self.assertIn("for root-owned issues spanning multiple repos, use\n  `multi-repository-workspace`", issue_phase)
        self.assertNotIn("# <feature-slug>: <NN> <vertical outcome>", issue_phase)
        self.assertIn("# Feature Spec: [Feature Name]", spec_template)
        self.assertIn("## Change Delivery Target", spec_template)
        self.assertIn("## Domain Knowledge Handoff", spec_template)
        self.assertIn("# <feature-slug>: <NN> <vertical outcome>", issue_template)
        self.assertIn("issue_type: [canonical bug | feature | task]", issue_template)
        self.assertIn("workflow_state: [canonical state", issue_template)
        self.assertIn("## Option Resolution", issue_template)
        self.assertIn("issue_option_rows_fingerprint:", issue_template)
        self.assertIn(
            "| row_id | scope_id | field | value | source | evidence |",
            issue_template,
        )
        self.assertIn("exactly one row for every Per-Issue Registry field", issue_template)
        self.assertIn("do not infer or omit row metadata here", issue_template)
        self.assertNotIn("\nType: [mapped issue type", issue_template)
        self.assertNotIn("\nStatus: [mapped triage state", issue_template)
        self.assertNotIn("\ntype:", issue_template)
        self.assertNotIn("\nstatus:", issue_template)
        self.assertNotIn("Project Topology: [verified inherited `repository_layout` row value]", issue_template)
        self.assertIn("- repository_layout: [same feature/workspace graph value as the source Feature Spec]", issue_template)
        self.assertIn("- issue_repository_layout: [verified `issue_repository_layout` row value]", issue_template)
        self.assertIn(
            "- change_delivery_permission_evidence: [verified permission-source, scope, target, branch, and transfer evidence]",
            issue_template,
        )
        self.assertIn("- workspace_context: [multi-repository-workspace or not-applicable]", issue_template)
        self.assertIn("- workspace_feature_repos: [complete feature-wide repo slug set or not-applicable]", issue_template)
        self.assertIn("- workspace_child_source_refs: [complete repo-to-Feature-Spec-ref mapping", issue_template)
        self.assertIn("- pull_request_count_strategy: [verified `pull_request_count_strategy` row value]", issue_template)
        self.assertIn("sole owner of delivery, scheduling, closeout", issue_template)
        self.assertIn("without resolving or defaulting them here", issue_template)
        for duplicated_schema in (
            "[pull-request | direct-commit]",
            "[one-pull-request-total | one-pull-request-per-repository | none]",
            "[merge-ready | draft-only | not-applicable]",
            "[independent | depends-on | blocks | root-integrated]",
        ):
            self.assertNotIn(duplicated_schema, issue_template)
        self.assertIn(
            "- issue_repository_layout: [same issue-effective value as `## Delivery`]",
            issue_template,
        )
        self.assertIn(
            "- pull_request_count_strategy: [same effective value as `## Delivery`]",
            issue_template,
        )
        self.assertIn(
            "- change_delivery_permission_evidence: [same evidence as `## Delivery`]",
            issue_template,
        )
        self.assertIn("## Orchestrator Handoff", issue_template)
        self.assertIn("## Domain Knowledge Closeout", issue_template)
        self.assertIn("Do not include worker action grants", issue_template)
        self.assertNotIn(ORCHESTRATION_POLICY_PATH, issue_template)
        self.assertIn("source_spec_ref: [path, issue number, or stable draft ref;", issue_template)
        self.assertIn("draft refs are valid", issue_template)
        self.assertIn("portable references", issue_template)
        self.assertIn("Placeholders are scheduling expectations", issue_template)
        self.assertIn("## Dependency Rules", vertical_slices)
        self.assertIn("## Verticality Gate", vertical_slices)
        self.assertIn("blocking gate", vertical_slices)
        self.assertIn("circular dependencies", vertical_slices)
        self.assertIn("final integration and domain-knowledge closeout task", vertical_slices)
        self.assertIn("orchestrator closeout", vertical_slices)
        self.assertIn("## Orchestrator Handoff", vertical_slices)
        self.assertIn("draft-spec:<...>", spec_delivery)
        self.assertIn("A generated issue's `## Orchestrator Handoff` must contain", spec_delivery)
        self.assertIn("`delivery_decision_origin_evidence`", spec_delivery)
        self.assertIn("for the exact workstream", spec_delivery)
        self.assertIn("The root owns target selection, delivery permission", spec_delivery)
        self.assertIn("Real PR refs replace placeholders before completion", spec_delivery)
        self.assertIn("Named remote branch contains the validated commit", spec_delivery)
        self.assertIn("Local Markdown issues use `move-local-issue-to-done-after-proof`", spec_delivery)
        self.assertIn("Validation Commands", issue_phase)
        self.assertIn("equivalent fallback", issue_phase)
        self.assertIn("move-local-issue-to-done-after-proof", options)
        self.assertIn("- issue_completion_method: [verified `issue_completion_method` row value]", issue_template)
        self.assertIn("Fallback:", issue_template)
        self.assertIn("non-uncommitted delivery target has live proof", issue_template)

    def test_plan_feature_defers_domain_capture_to_final_integration_task(self) -> None:
        plan_feature = read("plan-feature/SKILL.md")
        grill_with_context = read("grill-me-with-context/SKILL.md")
        spec_phase = read("plan-feature/references/spec-phase.md")
        issue_phase = read("plan-feature/references/issue-phase.md")
        issue_template = read("plan-feature/references/issue-body-template.md")
        fixture = read("plan-feature/references/full-flow-dry-run.md")

        self.assertIn("capture_mode=defer-to-caller", plan_feature)
        self.assertIn("domain_knowledge_delta", plan_feature)
        self.assertIn("Initialize every run with a structured", plan_feature)
        self.assertIn("`knowledge_delta=none`", plan_feature)
        self.assertIn("must not update `CONTEXT.md`", plan_feature)
        self.assertIn("final implementation/integration issue", plan_feature)
        self.assertIn("is never docs-only", plan_feature)
        self.assertIn("preserve it in the Feature Spec handoff", plan_feature)
        self.assertIn("Plan Feature never invokes `domain-memory`", plan_feature)

        self.assertIn("## Capture Modes", grill_with_context)
        self.assertIn("`capture_mode=inline` is the default", grill_with_context)
        self.assertIn("### Mode Resolution", grill_with_context)
        self.assertIn("uses `capture_mode=inline`", grill_with_context)
        self.assertIn("Do not infer `capture_mode=defer-to-caller`", grill_with_context)
        self.assertIn("preserves `capture_mode=inline`", grill_with_context)
        self.assertIn("`capture_mode=defer-to-caller`", grill_with_context)
        self.assertIn("Never write `CONTEXT.md`", grill_with_context)
        self.assertIn("domain_knowledge_delta:", grill_with_context)
        self.assertIn("capture_outcome: deferred | no-durable-change", grill_with_context)
        self.assertIn("knowledge_delta: required | none", grill_with_context)
        self.assertIn("<repo-slug>/<repo-relative-path>", grill_with_context)
        self.assertIn("The `unresolved` list is independent\nof `knowledge_delta`", grill_with_context)
        self.assertIn("record\nremaining product-shaping questions there", grill_with_context)
        self.assertIn("For a direct user request, add a", grill_with_context)

        self.assertIn("## Domain Knowledge Handoff", spec_phase)
        self.assertIn("deferred-work carrier", spec_phase)
        self.assertIn("<repo-slug>/<repo-relative-path>", spec_phase)
        self.assertIn("structured\n  `domain_knowledge_delta`", spec_phase)
        self.assertIn("`knowledge_delta`, `decisions`, `target_surfaces`", spec_phase)
        self.assertNotIn("domain_knowledge_delta.status", spec_phase)
        self.assertIn("choose its final owner", issue_phase)
        self.assertIn("append the last generated issue", issue_phase)
        self.assertIn("depend directly\n   on every other terminal issue", issue_phase)
        self.assertIn("Never append a documentation-only task", issue_phase)
        self.assertIn("publish or write it last", issue_phase)
        self.assertIn("Normalize each dependency edge from prerequisite", issue_phase)
        self.assertIn("pre-closeout nodes with no\n  downstream consumers", issue_phase)
        self.assertIn("exclude it from the terminal prerequisites", issue_phase)
        self.assertIn("requires `$project-memory` with", issue_phase)
        self.assertIn("`memory_slice=domain-memory`", issue_phase)
        self.assertIn("`domain_operation=implementation-closeout`", issue_phase)
        self.assertIn("is not a substitute", issue_template)
        self.assertIn("internal domain-modeling workflow completion", issue_template)

        self.assertIn("performs no documentation", fixture)
        self.assertIn("last integration task", fixture)
        self.assertIn("placed in a docs-only task", fixture)
        self.assertIn("pre-closeout terminals are `02` and `03`", fixture)
        self.assertIn("do not\n   replace these generated dependency IDs", fixture)
        self.assertIn("does not run that capture during planning", fixture)

    def test_planning_entrypoints_have_unambiguous_output_contracts(self) -> None:
        plan_feature = read("plan-feature/SKILL.md")
        plan_feature_metadata = read("plan-feature/agents/openai.yaml")
        issue_phase = read("plan-feature/references/issue-phase.md")
        plan_harder = read("plan-harder/SKILL.md")
        plan_harder_options = read("plan-harder/references/options.md")
        plan_harder_templates = read("plan-harder/references/templates.md")
        triage = read("triage/SKILL.md")
        triage_agent_brief = read("triage/references/agent-brief.md")

        self.assertIn("default for new feature intent after input normalization", plan_feature)
        self.assertIn("branch only on that canonical value", plan_feature)
        self.assertIn("Select full-flow for new intent", plan_feature_metadata)
        self.assertNotIn("split it into hardened vertical issues when requested", plan_feature_metadata)
        self.assertIn("`partial_output=allow-non-agent-ready` permits", plan_feature)
        self.assertIn("`planning_mode=issue-hardening`", plan_feature)
        self.assertIn("`output_surface=caller`", plan_feature)
        self.assertIn("output_surface=caller", issue_phase)
        self.assertIn("require `result_status`", issue_phase)
        self.assertIn("`result_status: blocked`", issue_phase)
        self.assertNotIn("require `status`, `implementation_plan`", issue_phase)
        self.assertNotIn("`status: blocked`", issue_phase)
        self.assertIn("result_status: ready | blocked", plan_harder_templates)
        self.assertIn("estimated_complexity: <low|medium|high>", plan_harder_templates)
        self.assertIn("`planning_mode` | `full-plan`, `issue-hardening`", plan_harder_options)
        self.assertIn("`result_status` | `ready`, `blocked`", plan_harder_options)
        self.assertNotIn("issue-hardening caller mode", triage)
        self.assertIn("`planning_mode=issue-hardening`", triage)
        self.assertIn("`output_surface=caller`", triage)
        self.assertIn("`planning_mode=issue-hardening`", triage_agent_brief)
        self.assertIn("`output_surface=caller`", triage_agent_brief)
        self.assertIn("Do not auto-select this skill merely because an implementation request", plan_harder)
        self.assertIn(
            "return only the structured issue-hardening result", plan_harder
        )
        self.assertIn("instead of starting a separate user-facing question loop", plan_harder)

    def test_lean_profiles_reduce_discovery_without_skipping_gates(self) -> None:
        plan_feature = read("plan-feature/SKILL.md")
        spec_phase = read("plan-feature/references/spec-phase.md")
        issue_phase = read("plan-feature/references/issue-phase.md")

        self.assertIn("## Execution Profiles", plan_feature)
        self.assertIn("`lean-spec`", plan_feature)
        self.assertIn("`lean-issues`", plan_feature)
        self.assertIn("Lean profiles reduce discovery and repeated output only", plan_feature)
        for required_gate in (
            "`$plan-harder`",
            "verticality",
            "graph",
            "publication",
            "domain-closeout",
        ):
            self.assertIn(required_gate, plan_feature)

        self.assertIn("For `lean-spec`, begin with only", spec_phase)
        self.assertIn("project-memory/config/domain.md", spec_phase)
        self.assertIn("`CONTEXT-MAP.md` when either exists", spec_phase)
        self.assertIn("Widen to\n`standard`", spec_phase)
        self.assertIn("For `lean-issues`, read the durable Feature Spec once", issue_phase)
        self.assertIn("The lean profile does not weaken any hardening or output gate", issue_phase)
        self.assertIn("at most two candidate vertical", plan_feature)

    def test_planning_uses_delta_evidence_and_exact_optional_metrics(self) -> None:
        plan_feature = read("plan-feature/SKILL.md")
        spec_phase = read("plan-feature/references/spec-phase.md")
        issue_phase = read("plan-feature/references/issue-phase.md")

        self.assertIn("Snapshot each source or artifact in full at most once", plan_feature)
        self.assertIn("Label\n  interleaved cumulative deltas `exact-interval`", plan_feature)
        self.assertIn("Never estimate or make metrics a completion gate", plan_feature)
        self.assertIn("## Evidence And Phase Metrics", spec_phase)
        self.assertIn("phase=spec", spec_phase)
        self.assertIn("completion output should identify the\nFeature Spec and its fingerprint", spec_phase)
        self.assertIn("## Evidence And Phase Metrics", issue_phase)
        self.assertIn("phase=issue-hardening:<issue-id>", issue_phase)
        self.assertIn("Do not repeat unchanged\nFeature Spec or issue bodies", issue_phase)
        self.assertIn("never estimate, reread session\narchives", issue_phase)
        self.assertIn("do not attribute it to an\nissue phase", issue_phase)

    def test_project_memory_triage_and_learn_keep_narrow_authority(self) -> None:
        project_memory = read("project-memory/SKILL.md")
        domain_modeling = read("project-memory/references/domain-modeling.md")
        setup_workflow = read("project-memory/references/setup-workflow.md")
        triage = read("triage/SKILL.md")
        architecture = read("improve-codebase-architecture/SKILL.md")
        learn = read("learn/SKILL.md")

        self.assertIn("Use the smallest requested `memory_slice`", project_memory)
        self.assertIn("only the requested `memory_slice`", project_memory)
        self.assertIn("single public entry point", project_memory)
        self.assertIn("`domain_operation=implementation-closeout`", project_memory)
        self.assertIn("`domain_operation=inline-update`", project_memory)
        self.assertIn("explicitly invoked composed workflow", project_memory)
        self.assertIn("durable domain-memory write authority", project_memory)
        self.assertIn("ready implementation-closeout task", project_memory)
        self.assertIn("internal semantic workflow", domain_modeling)
        self.assertIn("`$project-memory domain-memory` is the public invocation", domain_modeling)
        self.assertFalse((SKILLS_ROOT / "domain-modeling/SKILL.md").exists())
        self.assertIn("Ask only when the target or behavior-affecting value is materially", project_memory)
        self.assertIn("proceed without a second confirmation", setup_workflow)
        self.assertIn("## One-Issue Best-Effort Fallback", triage)
        self.assertIn("`capture_mode=inline`", triage)
        self.assertIn("`capture_mode=defer-to-caller`", triage)
        self.assertIn("Tracker mutation authority alone does not authorize", triage)
        self.assertIn("`memory_slice=domain-memory`", triage)
        self.assertIn("`domain_operation=inline-update`", triage)
        self.assertIn("`capture_mode=inline`", architecture)
        self.assertIn("`domain_operation=inline-update`", architecture)
        self.assertIn("do not apply `ready-for-agent`", triage)
        self.assertIn("wait for\n  an affirmative user reply", learn)
        self.assertIn("Never fall back or redirect to global", learn)

    def test_plan_feature_outputs_do_not_define_runtime_policy(self) -> None:
        for relative in (
            "plan-feature/references/spec-template.md",
            "plan-feature/references/issue-body-template.md",
            "plan-feature/references/issue-phase.md",
            "plan-feature/references/vertical-slices.md",
            "plan-feature/references/full-flow-dry-run.md",
        ):
            contents = read(relative)
            with self.subTest(file=relative):
                for field in RUNTIME_POLICY_FIELDS:
                    self.assertNotIn(field, contents)

    def test_domain_and_triage_handoffs_use_canonical_option_fields(self) -> None:
        project_memory_options = read("project-memory/references/options.md")
        grill_with_context = read("grill-me-with-context/SKILL.md")
        plan_feature = read("plan-feature/SKILL.md")
        issue_phase = read("plan-feature/references/issue-phase.md")
        triage_options = read("triage/references/options.md")
        triage_local = read("triage/references/local-markdown.md")

        self.assertIn(
            "`memory_slice` | `tracker-routing`, `project-layout`, `domain-memory`, `translation-memory`",
            project_memory_options,
        )
        self.assertIn("Use only `tracker-routing` or `project-layout`", plan_feature)
        self.assertIn("`capture_mode` | `inline`, `defer-to-caller`", project_memory_options)
        self.assertIn("`knowledge_delta` | `required`, `none`", project_memory_options)
        self.assertIn(
            "`capture_outcome` | `captured`, `deferred`, `no-durable-change`",
            project_memory_options,
        )
        self.assertIn("knowledge_delta: required | none", grill_with_context)
        self.assertNotIn("\n  status: required | none", grill_with_context)
        self.assertIn("`capture_outcome=deferred`", plan_feature)
        self.assertNotIn("domain_knowledge_delta.status", plan_feature)
        self.assertIn("preserve\n  independent `unresolved` blockers", plan_feature)
        self.assertIn("target, `capture_outcome`, domain-delta", plan_feature)
        self.assertIn("Validate `capture_outcome=deferred`", issue_phase)
        self.assertIn("`capture_outcome=no-durable-change`", issue_phase)
        self.assertIn("Preserve a\nnon-empty `unresolved` list independently", issue_phase)

        self.assertIn("`issue_type` | `bug`, `feature`, `task`", triage_options)
        self.assertIn(
            "`workflow_state` | `needs-triage`, `needs-info`, `ready-for-agent`",
            triage_options,
        )
        self.assertIn("issue_type: bug | feature | task", triage_local)
        self.assertIn("workflow_state: needs-triage | needs-info", triage_local)
        self.assertIn("source_spec_ref:", triage_local)
        self.assertIn("The header metadata region starts after the first H1", triage_options)
        self.assertIn("Reject unknown aliases", triage_options)
        self.assertIn("conflicting duplicate canonical fields", triage_options)
        self.assertIn("Apply the header-region scope", triage_local)
        self.assertNotIn("\nType: bug | feature | task", triage_local)
        self.assertNotIn("\nStatus: needs-triage", triage_local)

    def test_worker_authorization_is_orchestrator_owned(self) -> None:
        ledger = read("codex-orchestrator/references/ledger.md")
        ledger_template = read("codex-orchestrator/references/ledger-template.md")
        worker = read("codex-orchestrator/references/worker.md")
        orchestrator = read("codex-orchestrator/SKILL.md")

        self.assertIn("authorization_resolution: per-workstream", ledger_template)
        self.assertIn("per workstream and session", worker)
        self.assertIn("The root resolves `worker_allowed_actions` per workstream", orchestrator)
        self.assertIn("worker_allowed_actions:", worker)
        self.assertIn("Worker evidence", ledger_template)
        self.assertIn("Worker evidence", worker)
        self.assertIn("feature_spec_thread_assignment", worker)
        self.assertIn("root_implementation_fallback", worker)
        self.assertIn(
            "parallelism=<parallel|sequential|root-owned|simulated>",
            ledger_template,
        )
        self.assertIn("fallback reason", orchestrator)

    def test_project_memory_no_longer_defines_worker_auth_defaults(self) -> None:
        for path in iter_active_text_files():
            contents = path.read_text(encoding="utf-8")
            with self.subTest(file=str(path.relative_to(REPO_ROOT))):
                self.assertNotIn(LEGACY_WORKER_AUTH_KEY, contents)
                self.assertNotIn(LEGACY_WORKER_AUTH_HEADING, contents)
                self.assertNotIn(LEGACY_DEFAULT_WORKER_AUTH, contents)

    def test_removed_public_phase_skills_are_not_referenced(self) -> None:
        for path in iter_active_text_files():
            contents = path.read_text(encoding="utf-8")
            with self.subTest(file=str(path.relative_to(REPO_ROOT))):
                self.assertNotIn(REMOVED_LEGACY_PLANNING_SKILL, contents)
                self.assertNotIn(REMOVED_ISSUE_SKILL, contents)
                self.assertNotIn(REMOVED_LEGACY_PLANNING_PATH, contents)
                self.assertNotIn(REMOVED_ISSUE_PATH, contents)

    def test_runtime_contracts_use_feature_spec_vocabulary(self) -> None:
        retired_term = "p" + "rd"
        for path in iter_active_text_files():
            contents = path.read_text(encoding="utf-8").lower()
            with self.subTest(file=str(path.relative_to(REPO_ROOT))):
                self.assertNotIn(retired_term, contents)


if __name__ == "__main__":
    unittest.main()
