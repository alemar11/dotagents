# Orchestration Policy

Use this reference when creating or reviewing
`project-memory/agents/orchestration-policy.md`.

This file is optional runtime configuration for `$codex-orchestrator`. It does
not replace `project-memory/agents/issue-tracker.md`, the linked `Source PRD`,
generated issue bodies, or the orchestrator ledger.

## Default Shape

Use conservative defaults unless the owner explicitly chooses stronger
automation:

```markdown
# Orchestration Policy

auto_dispatch: `false`
eligible_sources: `durable-generated-issue-with-handoff`
excluded_sources: `draft-prd-ref, missing-handoff, ambiguous-delivery-mode, cyclic-dependency-graph`
worker_surfaces: `none`
max_active_delegated_workers: `0`
max_active_cli_subagents: `0`
max_active_codex_app_threads: `0`
session_wide_delegated_worker_cap: `0`
authorization_ceiling: `inspect, implement`
publication_policy: `none`
issue_mutation_policy: `pr-body-closeout-only`
heartbeat: `manual`

## Stop For Owner

- source PRD is a `draft-prd:<...>` ref
- `## Orchestrator Handoff` is missing or contradicts the issue body
- delivery mode, dependency graph, closeout, or gates are missing or unsafe
- requested worker surface is unavailable
- requested authorization exceeds `authorization_ceiling`
- commit, push, PR, direct issue mutation, merge, release, or deployment is
  required but not explicitly authorized
- focused tests, CI, autoreview, live proof, or integration proof fails
- scope, source graph, delivery path, or stop conditions change
```

## Structured Values

- `auto_dispatch`: `true` lets `$codex-orchestrator` dispatch a matching
  bounded wave without interactive approval after it records and reports the
  checkpoint. `false` preserves the blocking Approach Checkpoint flow.
- `eligible_sources`: source shapes that may use auto-dispatch, normally
  `durable-generated-issue-with-handoff` or `local-checklist`.
- `excluded_sources`: source shapes that must stop for owner input. Always
  exclude draft PRD refs, missing handoff sections, ambiguous delivery modes,
  and cyclic dependency graphs.
- `worker_surfaces`: allowed surfaces such as `none`, `cli-subagent`,
  `codex-app-thread`, or `auto`. These are ceilings, not assignments.
- `max_active_delegated_workers`, `max_active_cli_subagents`,
  `max_active_codex_app_threads`, and
  `session_wide_delegated_worker_cap`: caps, not quotas. The orchestrator may
  use fewer workers or keep work in the root thread.
- `authorization_ceiling`: maximum allowed runtime capability modes, such as
  `inspect` and `implement`. Commit, push, PR, merge, close, release, and
  deployment capabilities require explicit owner or PRD-backed authority.
- `publication_policy`: use `none` unless the owner explicitly wants
  PRD-backed publication to run automatically after gates.
- `issue_mutation_policy`: prefer `pr-body-closeout-only`. Direct comments,
  labels, or closure require explicit mutation authority.
- `heartbeat`: `manual`, `disabled`, `every-5-minutes`, or a custom policy
  when monitoring is configured.

Lower-snake-case keys and lower-kebab-case values are canonical. Lists may be
stored as comma-separated values or short Markdown lists when that is clearer.

## Ownership Boundary

`orchestration-policy.md` controls when `$codex-orchestrator` may dispatch
runtime work without asking again. It never grants planning authority, tracker
publication authority, worker assignments, or issue body fields by itself.

Do not copy this policy into PRDs, generated implementation issues,
`## Orchestrator Handoff`, draft publish commands, or tracker templates. The
orchestrator reads the policy, resolves actual workstream behavior from the
source graph and current repo state, then records the effective checkpoint in
the ledger.

When the file is missing, `$codex-orchestrator` must preserve the interactive
default: build the Approach Checkpoint and wait for explicit owner approval
before creating workers, starting root-owned implementation, mutating source
state, committing, pushing, or opening PRs.
