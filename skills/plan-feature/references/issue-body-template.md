# Issue Body Template

Use this shape unless the tracker has a stronger local template. Evidence and
paths must be portable: repo-relative, repo-qualified, hosted, or descriptive.
Never include developer-machine absolute paths.

```markdown
# <feature-slug>: <NN> <vertical outcome>

## Execution Contract

| Field | Value |
| --- | --- |
| `source_spec_ref` | [durable path or hosted ref; proposed refs are valid only in write_mode=propose] |
| `feature_slug` | [authoritative lowercase feature slug] |
| `affected_repositories` | [canonical repo slugs or current-repository] |
| `allowed_paths` | [repo-relative or repo-qualified paths for this slice] |
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

Plan-hardening: final stable $plan-harder issue-hardening pass completed for this issue.

[Concise implementation approach synthesized from the hardening brief. Merge
acceptance and validation details into their owning sections. Explain material
dependency reasons in Context or this prose without repeating dependency IDs.]

## Acceptance Criteria

- [ ] [Specific, verifiable outcome.]

## Validation

- Preferred: [Command, test, or manual check.]
- Fallback: [Equivalent proof when the preferred runner is unavailable, or
  None.]

## Integration Gates

[Include only when separate release, deployment, or cross-repo proof affects
completion.]

## Domain Knowledge Closeout

[Include only on the final implementation/integration issue when the issue
phase receives a knowledge delta as run data. In a single Spec, this issue must
prove integrated feature behavior and satisfy the owner-excluded terminal rule
from `issue-phase.md`. In
a multi-repository bundle, it belongs to the dedicated integration partial,
whose Feature Dependencies already wait for every implementation partial to
merge; its issue dependencies remain local to that integration partial. Every
target surface below must resolve to a repository named in this issue's
`affected_repositories` and a path equal to or contained by one of this issue's
`allowed_paths`.]

- Required workflow:
  - Invoke `$project-memory` with `memory_slice=domain-memory` and
    `domain_operation=implementation-closeout` after integrated behavior is
    proven. Project Memory runs its internal domain-modeling workflow.
knowledge_delta:
  decisions:
    - [Accepted durable term, rule, boundary, or decision.]
  target_surfaces:
    - [current-repository/<repo-relative-path> or <repo-slug>/<repo-relative-path>.]
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

- GitHub tracker: arm this issue with a closing keyword in the relevant
  implementation PR. Use the fully qualified `owner/repository#<number>` form
  when the issue belongs to another repository, and require that PR to target
  its repository's default branch so the keyword can take effect on merge. If
  no relevant PR can carry an effective closing keyword, withhold the
  App-compatible issue or bundle as blocked; a non-closing link is not
  completion proof.
- Local tracker: after implementation, integration proof, and any domain
  closeout succeed, move this file to the `done/` directory of its owning issue
  subtree. Commit and push that move, run final validation and `$autoreview`,
  convert draft PRs to ready-for-review, then obtain current-revision review and
  CI before terminal merge-ready. An ordinary issue moves to
  `planning/features/<feature-slug>/issues/done/<NN>-<slug>.md`; an integration
  issue moves to
  `planning/features/<feature-slug>/integration/issues/done/<NN>-<slug>.md`.
  Create only the selected `done/` directory on demand. For multi-repository
  work, require cross-repo integration proof first. The Execution Contract must
  include the tracker-owning repository plus both the exact active and exact
  destination paths, and both paths must resolve inside that affected Git
  repository. Commit and push the move, then rerun every final gate that the
  resulting head invalidates. The `done/` path reaches the default branch only
  when the later PR merge lands it; at the App terminal state closeout is
  prepared, not globally completed.
- Explicit non-App bundle: follow `non-app-delivery.md`; the eventual executor
  owns authorization and tracker lifecycle. Planning grants neither.
```

Tracker metadata is rendered by `write_mode` and backend rather than duplicated
in the base body:

- GitHub `write_mode=apply`: resolve the mapped task type and
  `ready-for-agent` state transports independently. Require `label` for the
  workflow state. For task-type `native-type` or `label`, mutate tracker
  metadata and do not copy that value into the body. For task-type `body-field`,
  insert the exact configured field in the header metadata region after the H1
  and before the first `##` heading before publication; do not invent a key or
  value.
- Local `write_mode=apply`: insert canonical `issue_type: task` and
  `workflow_state: ready-for-agent` lines below the H1 title.
- `write_mode=propose`: leave both lines out of the proposed body and return the
  intended mappings as report metadata. A proposal is never an applied queue
  state.

For an explicit non-App bundle, append a `non_app_delivery_target` row to the
same Execution Contract exactly as `non-app-delivery.md` requires. Do not add
`explicit_instruction_ref` or another delivery, permission, option, dependency,
or orchestrator-handoff section. Derive issues blocked by this issue by scanning other issues'
`dependency_ids`; keep dependency reasons in Context or implementation prose
without re-listing IDs.

Withhold an issue that still needs a human answer. Agent-ready issue bodies do
not contain a Questions section or unresolved placeholders.
