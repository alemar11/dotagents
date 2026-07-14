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
feature_slug: account-settings-export
delivery_mode: pull-request
issue_mutation_authority: pr-body-closeout-only
branch_name: feature/account-settings-export
pr_closeout: merge-ready
pr_shape: single-pr
source_prd_ref: draft-prd:account-settings-export
prd_body_fingerprint: sha256:7f4a9c21d003
capture_mode: defer-to-caller
capture_outcome: deferred
option_resolution: see-canonical-run-option-rows-below
option_rows_fingerprint: sha256:4f8179bf10138c6335fd3819265f93cf06f6b9c2bc3b6c53fcfd6aa6691d05d7
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
| `run:mode` | `run` | `mode` | `full-flow` | `owner-instruction` | `fixture-intent` |
| `run:execution_profile` | `run` | `execution_profile` | `standard` | `default` | `none` |
| `run:tracker_backend` | `run` | `tracker_backend` | `github` | `tracker-config` | `project-memory/config/issue-tracker.md` |
| `run:effective_target` | `run` | `effective_target` | `draft-publish-commands` | `runtime-derived` | `run:no_mutation_override+run:no_mutation_output` |
| `run:no_mutation_override` | `run` | `no_mutation_override` | `dry-run` | `owner-instruction` | `fixture-intent` |
| `run:no_mutation_output` | `run` | `no_mutation_output` | `publish-commands` | `owner-instruction` | `fixture-intent` |
| `run:local_mirror` | `run` | `local_mirror` | `not-requested` | `default` | `none` |
| `run:local_mirror_path` | `run` | `local_mirror_path` | `not-applicable` | `default` | `none` |
| `run:partial_output` | `run` | `partial_output` | `withhold` | `default` | `none` |
| `run:delivery_mode` | `run` | `delivery_mode` | `pull-request` | `default` | `none` |
| `run:issue_mutation_authority` | `run` | `issue_mutation_authority` | `pr-body-closeout-only` | `runtime-derived` | `run:tracker_backend+run:delivery_mode` |
| `run:branch_name` | `run` | `branch_name` | `feature/account-settings-export` | `runtime-derived` | `run:delivery_mode+feature_slug` |
| `run:pr_closeout` | `run` | `pr_closeout` | `merge-ready` | `default` | `run:delivery_mode` |
| `run:pr_shape` | `run` | `pr_shape` | `single-pr` | `runtime-derived` | `current-repository` |

## Representative Emitted Issue

This serialization check emits every `issue:01` row with an artifact-local
fingerprint. The graph-wide fingerprint remains in the issue-phase handoff.

```markdown
# account-settings-export: 01 Export account settings end to end

issue_type: task
workflow_state: ready-for-agent
source_prd_ref: draft-prd:account-settings-export

## Option Resolution

issue_option_rows_fingerprint: sha256:92b2748d73d29436dc88e2544f51cff216032a0a758f0b2dc65fc421de7a4592

| row_id | scope_id | field | value | source | evidence |
| --- | --- | --- | --- | --- | --- |
| `issue:01:delivery_source` | `issue:01` | `delivery_source` | `feature-level-inherited` | `source-prd` | `draft-prd:account-settings-export` |
| `issue:01:delivery_mode` | `issue:01` | `delivery_mode` | `pull-request` | `source-prd` | `run:delivery_mode` |
| `issue:01:issue_mutation_authority` | `issue:01` | `issue_mutation_authority` | `pr-body-closeout-only` | `source-prd` | `run:issue_mutation_authority` |
| `issue:01:pr_shape` | `issue:01` | `pr_shape` | `single-pr` | `source-prd` | `run:pr_shape` |
| `issue:01:pr_closeout` | `issue:01` | `pr_closeout` | `merge-ready` | `source-prd` | `run:pr_closeout` |
| `issue:01:parallelization` | `issue:01` | `parallelization` | `independent` | `runtime-derived` | `issue-graph:01` |
| `issue:01:closeout_mode` | `issue:01` | `closeout_mode` | `feature-pr-closes-issue` | `runtime-derived` | `run:tracker_backend+issue:01:pr_shape` |
| `issue:01:integration_mode` | `issue:01` | `integration_mode` | `single-repo-pr` | `runtime-derived` | `run:delivery_mode+current-repository` |
| `issue:01:domain_closeout` | `issue:01` | `domain_closeout` | `implementation-closeout` | `runtime-derived` | `domain_knowledge_delta+issue-graph:01` |
| `issue:01:branch_name` | `issue:01` | `branch_name` | `feature/account-settings-export` | `source-prd` | `run:branch_name` |
```

## Representative Issue-Phase Handoff

option_rows_fingerprint: sha256:21619b114c0e689b1b0f364620775abacc3603dcaa30881e83c406ef7518c471
issue_count: 1
issue_refs: draft-issue:account-settings-export:01

## Expected Pipeline

1. `$plan-feature` reviews project memory and resolves the effective target.
2. `$grill-me-with-context` runs with `capture_mode=defer-to-caller`, resolves
   only blockers that affect the PRD or issue split, performs no documentation
   writes, and returns a structured `domain_knowledge_delta`.
3. The PRD phase returns the PRD body, a draft PRD publish command,
   `source_prd_ref=draft-prd:account-settings-export`, and
   `prd_body_fingerprint=sha256:7f4a9c21d003`, with
   the structured delivery handoff tuple
   `delivery_mode=pull-request`,
   `issue_mutation_authority=pr-body-closeout-only`,
   `branch_name=feature/account-settings-export`,
   `pr_closeout=merge-ready`, and `pr_shape=single-pr`. When the delta is
   required, the PRD body carries it under `## Domain Knowledge Handoff`.
4. The issue phase returns hardened issue bodies plus draft issue publish commands.
   Every issue `## Delivery` and `## Orchestrator Handoff` projection carries
   `branch_name: feature/account-settings-export`.
   Draft issue bodies may contain `source_prd_ref: draft-prd:account-settings-export`
   only because no hosted PRD number exists yet. A required knowledge delta is
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
   close issues from the draft PRD ref.
6. Any `$codex-orchestrator` session settings remain runtime-only; they are not
   copied into the PRD, generated issue bodies, `## Orchestrator Handoff`, or
   draft publish commands.
7. Each phase verifies the incoming `option_rows_fingerprint`; the issue-phase
   report returns the recomputed fingerprint over all run and `issue:<NN>` rows.

## Expected Draft Publish Plan

- Publish the PRD first and capture the created issue number as `PRD_NUMBER`.
- Confirm the draft issue commands carry the same PRD body fingerprint as the
  draft PRD command.
- Replace every issue body line
  `source_prd_ref: draft-prd:account-settings-export` with
  `source_prd_ref: #$PRD_NUMBER` before creating hosted implementation issues.
- Attach each generated implementation issue to the PRD parent when the tracker
  supports parent/sub-issues.
- Publish the final integration and domain-knowledge closeout task last, after
  all terminal issue IDs are known, and preserve its dependency edges.
- Draft commands may include the intended future `ready-for-agent` labels, but
  the issues are not executable agent-ready output until `source_prd_ref` is replaced
  with the durable PRD issue number.
- Return exact commands without executing them.

## Expected Runtime Efficiency Evidence

- Snapshot the supplied intent, generated PRD, and each issue body once per
  fingerprint; carry paths/refs, fingerprints, changed headings, and gate
  excerpts between phases.
- Full bodies are returned only because this fixture explicitly requests draft
  publish output.
- Report `routing`, `prd`, each `issue-hardening:<id>`, and
  `issue-graph-and-publication` token deltas only for run-scoped,
  uncontaminated counter intervals. Label interleaved deltas `exact-interval`;
  otherwise report one `tokens=unavailable` result without estimation.

## Failure Conditions

- A repo-local `.scratch/` PRD or issue file is created.
- `CONTEXT.md`, project domain docs, or ADRs are edited during the planning run.
- A GitHub issue is created, edited, labeled, typed, closed, or attached.
- An implementation worker receives `commit`, `push`, or `pr` authorization
  from project memory, plan-feature output, tracker defaults, or the draft PRD
  ref alone.
- Draft PRDs, generated issues, and draft publish commands include worker
  authorization fields or worker capability modes.
- Draft PRDs, generated issues, or draft publish commands include orchestration
  session values such as worker surfaces, worker counts, checkpoint approval,
  or publication authority. The canonical source-contract
  `issue_mutation_authority` is allowed and must remain independently resolved.
- A phase handoff or generated structured field uses a prose choice, boolean
  option, non-canonical field name, or enum value outside `options.md`.
- A PRD-phase handoff, generated issue `## Delivery`, or generated issue
  `## Orchestrator Handoff` omits
  `branch_name: feature/account-settings-export`.
- Generated issues use a prose `source_prd_ref` such as the PRD title when a stable
  draft ref is available.
- A required `domain_knowledge_delta` is omitted, captured during planning, or
  placed in a docs-only task instead of the last integration task.
- The final integration task permits direct edits to `CONTEXT.md`, domain docs,
  or ADRs without invoking `$project-memory domain-memory` and running its
  internal domain-modeling workflow.
- Unchanged PRD or issue bodies are repeatedly emitted between phases without a
  draft-output, publication, or failed-gate reason.
