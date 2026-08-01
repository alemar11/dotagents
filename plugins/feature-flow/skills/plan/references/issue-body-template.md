# Issue Body Template

Use this shape for GitHub implementation issues. Evidence and paths must be
portable: repo-relative, repo-qualified, hosted, or descriptive. Never include
developer-machine absolute paths.

```markdown
# <feature-slug>: <NN> <vertical outcome>

## Execution Contract

| Field | Value |
| --- | --- |
| `source_spec_ref` | [durable hosted ref; proposed refs are valid only in run_mode=preview] |
| `feature_slug` | [authoritative lowercase feature slug] |
| `affected_repositories` | [canonical repo slugs or current-repository] |
| `allowed_paths` | [smallest complete safe repo-relative or repo-qualified envelope for this slice] |
| `target_branch_name` | [one valid branch shared by all affected repositories inside this Feature Spec] |
| `dependency_ids` | [earlier generated issue IDs or none] |

## Goal

[One independently valuable vertical outcome.]

## Non-Goals

- [Excluded work.]

## Context

[Relevant Feature Spec and repository context using portable references.]

## Cross-Repo Notes

[Include only for multi-repository issues: repository roles, interface
contracts, integration order, and named gates.]

## Requirements

- [Requirement this issue must satisfy.]

## Implementation Plan

Plan-hardening: final stable implementation-hardening pass completed for this issue.

This is the planning-time recommended approach. The implementing Codex task may
replace it with a simpler or safer design when the accepted goal, scope,
constraints and acceptance criteria remain unchanged.

[Concise planning-time implementation recommendation synthesized from the
hardening brief. Merge acceptance and validation details into their owning
sections. Explain material dependency reasons in Context or this prose without
repeating dependency IDs.]

## Acceptance Criteria

- [ ] [One unique, individually provable outcome. Keep criterion text and order
  stable; the implementing Codex task owns only the checkbox marker.]

## Validation

- Preferred: [Command, test, or manual check.]
- Fallback: [Equivalent proof when the preferred runner is unavailable, or
  None.]
- Failure policy: [Required prose for paid, external, non-repeatable, or
  otherwise constrained proof: attempt/retry budget, allowed fallback, evidence
  to retain, and required terminal outcome. Omit only when validation is not
  materially constrained.]

## Executor Update Contract

Before starting this issue, after any recovery or handoff, and before final
verification, re-read the current Feature Spec and complete current issue set.
Block declaratively on any change to the goal or Non-Goals, repositories or
allowed paths, `source_spec_ref`, `target_branch_name`, dependencies, acceptance
criterion text/count/order, safety constraints, or material validation
constraints including attempt budgets and required terminal outcomes. Do not
ask the user from the worker task merely to resolve that semantic drift.

The implementing Codex task may update acceptance checkbox markers,
implementation approach and internal design, safer or simpler rewrites,
additional or equivalent tests, compatible clarifications, progress, status,
evidence, and concrete refactors or fixes within accepted scope. It updates this
issue's checkboxes only after current-head proof, then re-reads the GitHub issue
before writing. It updates parent Feature Spec checkboxes only
when Spec-level behavior is proven, and restores an unchecked marker whenever
later evidence invalidates the proof. Root coordination never edits or judges
individual acceptance criteria. Inside an `## Acceptance Criteria` section,
only checkbox markers are execution progress; criterion text, count, and order
remain stable. This does not restrict updates to the other mutable execution
sections named above.

## Integration Gates

[Include only when separate release, deployment, or cross-repo proof affects
completion.]

## Domain Knowledge Closeout

[Include only on a repository-owned final closeout issue when the issue phase
receives a knowledge delta as run data. In a single Spec, this issue must
prove integrated feature behavior and satisfy the owner-excluded terminal rule
from `issue-phase.md`. In
a multi-repository feature, it belongs to an existing implementation member
whose Feature Dependencies supply the exact peer inputs required for proof;
its issue dependencies remain within that member. The payload is only that
member's repository-owned shard. One exact `canonical_decision_target` owns a
cross-repository decision; a non-owner shard may carry a qualified backlink but
not duplicate the record. Every target surface below must resolve to this
issue's sole Git repository and a path equal to or contained by one of this
issue's `allowed_paths`. This section is a Plan-to-Implement handoff, not
evidence that the knowledge has already been captured.]

- Required workflow:
  - Invoke `$project-context` with `memory_slice=domain-memory` and
    `domain_operation=implementation-closeout` after integrated behavior is
    proven. Project Context runs its internal domain-modeling workflow.
knowledge_delta:
  canonical_decision_target: [for a cross-repository decision, exactly
    <feature-id>--<repository-key>/<repo-relative-path> naming the declared
    owning Feature Spec Set member; every backlink copies this exact value]
  decisions:
    - [Accepted durable term, rule, boundary, or decision.]
  target_surfaces:
    - [current-repository/<repo-relative-path>.]
  evidence:
    - [Portable implementation evidence.]
- Closeout proof:
  - [Integration validation; `capture_outcome=captured`; every accepted delta
    item and required named target reconciled; named destinations; and complete
    documentation-diff verification. Treat `deferred` or `no-durable-change`
    for this nonempty accepted delta as blocked, not completed. A supplied
    accepted item rejected or contradicted by landed behavior also blocks for an
    owner decision or separately authorized planning/implementation correction.]

## Completion

- GitHub tracker: after current-head evidence proves the issue criteria, update
  the issue checkboxes and tracker lifecycle truthfully. The selected executor
  owns whether completion is represented by a closing reference, explicit
  close operation, or another supported tracker transition; Plan does
  not choose that delivery mechanism.
```

Tracker metadata is rendered by `run_mode` rather than duplicated in the base
body:

- GitHub `run_mode=publish`: resolve the exact `task` and `ready-for-agent`
  labels from the Feature Flow workflow contract independently. Mutate tracker metadata
  and do not copy those values into the body; do not invent a key or value.
- `run_mode=preview`: leave both lines out of the proposed body and return the
  intended contract metadata as report data. A preview is never a published queue
  state.

Do not add a permission, option, or orchestrator-handoff section.
Derive issues blocked by this issue by scanning other issues'
`dependency_ids`; keep dependency reasons in Context or implementation prose
without re-listing IDs.

Withhold an issue that still needs a human answer. Agent-ready issue bodies do
not contain a Questions section or unresolved placeholders.
