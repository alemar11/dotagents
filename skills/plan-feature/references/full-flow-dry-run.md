# Full-Flow Dry-Run Fixture

Use this fixture to forward-test the planning pipeline without writing local
artifacts or mutating a hosted tracker.

## User Request

```text
Use $plan-feature to plan a feature named "account settings export". This is a
dry run: do not write files and do not mutate GitHub. Return draft publish
commands instead.
```

## Setup Snapshot

```text
mode: full-flow
execution_profile: standard
tracker_backend: github
effective_target: draft-publish-commands
no_mutation_override: dry-run
no_mutation_output: publish-commands
local_mirror: not-requested
local_mirror_path: not-applicable
partial_output: withhold
repository_layout: single-repository
workspace_context: not-applicable
feature_slug: account-settings-export
change_delivery_target: pull-request-ready-for-merge-but-not-merged
change_delivery_permission: granted-for-selected-target
issue_update_permission: pull-request-closing-keyword-only
codex_review_requirement: required-on-current-pull-request-head
target_branch_name: feature/account-settings-export
pull_request_count_strategy: one-pull-request-total
source_spec_ref: draft-spec:account-settings-export
spec_body_fingerprint: sha256:7f4a9c21d003
capture_mode: defer-to-caller
capture_outcome: deferred
option_resolution: see-canonical-run-option-rows-below
option_rows_fingerprint: sha256:99f7ff308ad9038ec8a158876a1438758f4c8878c6e424729c0a0bc06abff4a7
domain_knowledge_delta:
  knowledge_delta: required
  decisions:
    - Account settings export is a user-owned portable archive.
  target_surfaces:
    - current-repository/CONTEXT.md
    - current-repository/project-memory/adr/ADR-account-settings-export.md
  evidence:
    - "Accepted planning decision: account settings export portability."
    - current-repository/src/account-settings/export.ts
  unresolved: []
```

## Canonical Run Option Rows

| row_id | scope_id | field | value | source | evidence |
| --- | --- | --- | --- | --- | --- |
| `run:mode` | `run` | `mode` | `full-flow` | `authorized-user-instruction` | `fixture-intent` |
| `run:execution_profile` | `run` | `execution_profile` | `standard` | `default` | `none` |
| `run:tracker_backend` | `run` | `tracker_backend` | `github` | `tracker-config` | `project-memory/config/issue-tracker.md` |
| `run:effective_target` | `run` | `effective_target` | `draft-publish-commands` | `runtime-derived` | `run:no_mutation_override+run:no_mutation_output` |
| `run:no_mutation_override` | `run` | `no_mutation_override` | `dry-run` | `authorized-user-instruction` | `fixture-intent` |
| `run:no_mutation_output` | `run` | `no_mutation_output` | `publish-commands` | `authorized-user-instruction` | `fixture-intent` |
| `run:local_mirror` | `run` | `local_mirror` | `not-requested` | `default` | `none` |
| `run:local_mirror_path` | `run` | `local_mirror_path` | `not-applicable` | `default` | `none` |
| `run:partial_output` | `run` | `partial_output` | `withhold` | `default` | `none` |
| `run:repository_layout` | `run` | `repository_layout` | `single-repository` | `project-layout-config` | `project-memory/config/project-layout.md` |
| `run:workspace_context` | `run` | `workspace_context` | `not-applicable` | `default` | `none` |
| `run:change_delivery_target` | `run` | `change_delivery_target` | `pull-request-ready-for-merge-but-not-merged` | `default` | `none` |
| `run:change_delivery_permission` | `run` | `change_delivery_permission` | `granted-for-selected-target` | `default` | `permission-source-ref=feature-spec-default:account-settings-export;scope-ref=run;target-ref=draft-spec:account-settings-export;target-branch=feature/account-settings-export` |
| `run:issue_update_permission` | `run` | `issue_update_permission` | `pull-request-closing-keyword-only` | `default` | `permission-source-ref=feature-spec-default:account-settings-export;scope-ref=run;target-ref=draft-spec:account-settings-export;target-branch=feature/account-settings-export` |
| `run:codex_review_requirement` | `run` | `codex_review_requirement` | `required-on-current-pull-request-head` | `default` | `run:change_delivery_target` |
| `run:target_branch_name` | `run` | `target_branch_name` | `feature/account-settings-export` | `runtime-derived` | `run:change_delivery_target+feature_slug` |
| `run:pull_request_count_strategy` | `run` | `pull_request_count_strategy` | `one-pull-request-total` | `runtime-derived` | `affected_repos=current-repository` |

## Representative Emitted Issue

This serialization check emits every `issue:01` row with an artifact-local
fingerprint. The graph-wide fingerprint remains in the issue-phase handoff.

```markdown
# account-settings-export: 01 Export account settings end to end

issue_type: task
workflow_state: ready-for-agent
source_spec_ref: draft-spec:account-settings-export

## Option Resolution

issue_option_rows_fingerprint: sha256:0e11ce282652a7a9f3725fa45a6e30220df157a0d46ee4154cf1d31c57649563

| row_id | scope_id | field | value | source | evidence |
| --- | --- | --- | --- | --- | --- |
| `issue:01:delivery_decision_origin` | `issue:01` | `delivery_decision_origin` | `inherited-from-feature-spec` | `source-spec` | `draft-spec:account-settings-export` |
| `issue:01:change_delivery_target` | `issue:01` | `change_delivery_target` | `pull-request-ready-for-merge-but-not-merged` | `source-spec` | `run:change_delivery_target` |
| `issue:01:change_delivery_permission` | `issue:01` | `change_delivery_permission` | `granted-for-selected-target` | `source-spec` | `permission-source-ref=feature-spec-default:account-settings-export;scope-ref=issue:01;target-ref=draft-spec:account-settings-export;target-branch=feature/account-settings-export;permission-transfer-ref=run` |
| `issue:01:issue_repository_layout` | `issue:01` | `issue_repository_layout` | `single-repository` | `source-spec` | `run:repository_layout` |
| `issue:01:issue_update_permission` | `issue:01` | `issue_update_permission` | `pull-request-closing-keyword-only` | `source-spec` | `permission-source-ref=feature-spec-default:account-settings-export;scope-ref=issue:01;target-ref=draft-spec:account-settings-export;target-branch=feature/account-settings-export;permission-transfer-ref=run` |
| `issue:01:codex_review_requirement` | `issue:01` | `codex_review_requirement` | `required-on-current-pull-request-head` | `source-spec` | `run:codex_review_requirement` |
| `issue:01:pull_request_count_strategy` | `issue:01` | `pull_request_count_strategy` | `one-pull-request-total` | `source-spec` | `run:pull_request_count_strategy` |
| `issue:01:parallelization` | `issue:01` | `parallelization` | `independent` | `runtime-derived` | `issue-graph:01` |
| `issue:01:issue_completion_method` | `issue:01` | `issue_completion_method` | `feature-pull-request-closing-keyword` | `runtime-derived` | `run:tracker_backend+issue:01:pull_request_count_strategy` |
| `issue:01:domain_closeout` | `issue:01` | `domain_closeout` | `implementation-closeout` | `runtime-derived` | `domain_knowledge_delta+issue-graph:01` |
| `issue:01:target_branch_name` | `issue:01` | `target_branch_name` | `feature/account-settings-export` | `source-spec` | `run:target_branch_name` |
```

## Representative Issue-Phase Handoff

option_rows_fingerprint: sha256:8c03de3025fe18cabf269a8d011da37972cdc54a371c90bc7c7c5986684e48c0
issue_count: 1
issue_refs: draft-issue:account-settings-export:01

## Expected Pipeline

1. `$plan-feature` reviews project memory and resolves the effective target.
2. `$grill-me-with-context` runs with `capture_mode=defer-to-caller`, resolves
   only blockers that affect the Feature Spec or issue split, performs no documentation
   writes, and returns a structured `domain_knowledge_delta`.
3. The Feature Spec phase returns the Feature Spec body, a draft Feature Spec publish command,
   `source_spec_ref=draft-spec:account-settings-export`, and
   `spec_body_fingerprint=sha256:7f4a9c21d003`, with
   the structured delivery handoff tuple
   `change_delivery_target=pull-request-ready-for-merge-but-not-merged`,
   `change_delivery_permission=granted-for-selected-target`,
   `repository_layout=single-repository`,
   `issue_update_permission=pull-request-closing-keyword-only`,
   `codex_review_requirement=required-on-current-pull-request-head`,
   `target_branch_name=feature/account-settings-export`, and
   `pull_request_count_strategy=one-pull-request-total`. When the delta is
   required, the Feature Spec body carries it under `## Domain Knowledge Handoff`.
4. The issue phase returns hardened issue bodies plus draft issue publish commands.
   Every issue `## Delivery` and `## Orchestrator Handoff` projection carries
   `repository_layout: single-repository` and
   `target_branch_name: feature/account-settings-export`.
   Draft issue bodies may contain `source_spec_ref: draft-spec:account-settings-export`
   only because no hosted Feature Spec number exists yet. A required knowledge delta is
   assigned to the last integration task, which depends on every terminal
   implementation issue and includes `## Domain Knowledge Closeout`. That task
   requires its later implementor to invoke `$project-memory domain-memory`,
   which runs Project Memory's internal domain-modeling workflow; Plan Feature
   does not run that capture during planning.
   For example, if `02 depends-on 01` while `03` is independent, the
   pre-closeout terminals are `02` and `03`; appended final task `04` depends
   directly on both. Hosted issue numbers are tracked separately and do not
   replace these generated dependency IDs.
5. `$codex-orchestrator` may inspect the resulting issue graph in dry-run mode
   but must not dispatch implementation workers, commit, push, create PRs, or
   close issues from the draft Feature Spec ref.
6. Any `$codex-orchestrator` session settings remain runtime-only; they are not
   copied into the Feature Spec, generated issue bodies, `## Orchestrator Handoff`, or
   draft publish commands.
7. Each phase verifies the incoming `option_rows_fingerprint`; the issue-phase
   report returns the recomputed fingerprint over all run and `issue:<NN>` rows.

## Expected Draft Publish Plan

- Publish the Feature Spec first and capture the created issue number as `SPEC_NUMBER`.
- Confirm the draft issue commands carry the same Feature Spec body fingerprint as the
  draft Feature Spec command.
- Replace every issue body line
  `source_spec_ref: draft-spec:account-settings-export` with
  `source_spec_ref: #$SPEC_NUMBER` before creating hosted implementation issues.
- Attach each generated implementation issue to the Feature Spec parent when the tracker
  supports parent/sub-issues.
- Publish the final integration and domain-knowledge closeout task last, after
  all terminal issue IDs are known, and preserve its dependency edges.
- Draft commands may include the intended future `ready-for-agent` labels, but
  the issues are not executable agent-ready output until `source_spec_ref` is replaced
  with the durable Feature Spec issue number.
- Return exact commands without executing them.

## Expected Runtime Efficiency Evidence

- Snapshot the supplied intent, generated Feature Spec, and each issue body once per
  fingerprint; carry paths/refs, fingerprints, changed headings, and gate
  excerpts between phases.
- Full bodies are returned only because this fixture explicitly requests draft
  publish output.
- Report `routing`, `spec`, each `issue-hardening:<id>`, and
  `issue-graph-and-publication` token deltas only for run-scoped,
  uncontaminated counter intervals. Label interleaved deltas `exact-interval`;
  otherwise report one `tokens=unavailable` result without estimation.

## Failure Conditions

- A repo-local `planning/tmp/` Feature Spec or issue file is created.
- `CONTEXT.md`, project domain docs, or ADRs are edited during the planning run.
- A GitHub issue is created, edited, labeled, typed, closed, or attached.
- An implementation worker receives `commit`, `push`, or `pr` authorization
  from project memory, plan-feature output, tracker defaults, or the draft Feature Spec
  ref alone.
- Draft Feature Specs, generated issues, and draft publish commands include worker
  authorization fields or worker capability modes.
- Draft Feature Specs, generated issues, or draft publish commands include orchestration
  session values such as worker surfaces, worker counts, checkpoint approval,
  or publication authority. The canonical source-contract
  `issue_update_permission` is allowed and must remain independently resolved.
- A phase handoff or generated structured field uses a prose choice, boolean
  option, non-canonical field name, or enum value outside `options.md`.
- A Feature Spec phase handoff, generated issue `## Delivery`, or generated issue
  `## Orchestrator Handoff` omits
  `repository_layout: single-repository` or
  `target_branch_name: feature/account-settings-export`.
- Generated issues use a prose `source_spec_ref` such as the Feature Spec title when a stable
  draft ref is available.
- A required `domain_knowledge_delta` is omitted, captured during planning, or
  placed in a docs-only task instead of the last integration task.
- The final integration task permits direct edits to `CONTEXT.md`, domain docs,
  or ADRs without invoking `$project-memory domain-memory` and running its
  internal domain-modeling workflow.
- Unchanged Feature Spec or issue bodies are repeatedly emitted between phases without a
  draft-output, publication, or failed-gate reason.
