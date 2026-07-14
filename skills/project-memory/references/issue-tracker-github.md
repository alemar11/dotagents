# Issue Tracker: GitHub

Feature Specs and implementation issues for this repo live as GitHub issues. Use
`$gitstack:github-issues` for GitHub issue lifecycle operations.

## Configuration

| Key | Type | Value | Allowed values | Meaning |
| --- | --- | --- | --- | --- |
| `tracker_backend` | enum | `github` | `github`, `local` | Feature Specs and implementation issues are written as GitHub issues. |
| `change_delivery_target` | enum | `pull-request-ready-for-merge-but-not-merged` | `local-commit-created-without-pushing`, `changes-pushed-to-target-branch-without-pull-request`, `validated-draft-pull-request-published`, `pull-request-ready-for-merge-but-not-merged` | Exact implementation stopping point. A local-only commit leaves the hosted issue open. |

GitHub is the authoritative artifact store in this mode. Do not create or keep
repo-local `planning/tmp/` Feature Spec/issue mirrors, `project-memory/features/` mirrors, or
other local planning copies merely to feed `gh --body-file`. Temporary body
files must live outside the repo and be removed after mutation. Create a
persistent mirror only when the canonical Plan Feature rows contain
`local_mirror=requested` and a validated `local_mirror_path`.

Feature-planning workflows write to GitHub by default in this mode after setup,
planning identity, and blockers are resolved. Branch only on the canonical
`effective_target`: `configured-tracker` writes to GitHub,
`draft-publish-commands` returns exact draft commands, and `local-dry-run`
returns non-executable local artifacts.

## Non-Mutating Runs

Require a non-`none` `no_mutation_override` before either non-mutating target.
For `effective_target=local-dry-run`, return local paths and bodies without
writing GitHub. For `effective_target=draft-publish-commands`, ask
`$gitstack:github-issues` for draft issue bodies and exact `gh` commands without
executing them.
When returning draft commands before the Feature Spec issue exists, use
`source_spec_ref=draft-spec:<feature-slug>` and publish the Feature Spec first; generated
issue bodies must replace that draft ref with `source_spec_ref: #<spec-number>` before
hosted mutation.
Treat `no_mutation_override`, `no_mutation_output`, and the derived
non-mutating target as run-scoped rows. Do not record them as durable
issue-tracker configuration.

## Conventions

Infer the repo from `git remote -v` unless this file records a specific target.
Use `$gitstack:github-issues` to create, read, edit, comment on, label, type, attach, or
close GitHub issues.

Use `project-memory/config/triage-labels.md` for type and label mappings. The
default GitHub issue types are:

- `Bug` for `bug`
- `Feature` for `feature`
- `Task` for `task`

The default GitHub workflow-state labels are lowercase tracker values:

- `needs-triage` for `needs-triage`
- `needs-info` for `needs-info`
- `ready-for-agent` for `ready-for-agent`
- `ready-for-human` for `ready-for-human`
- `wontfix` for `wontfix`

If GitHub issue types are disabled or customized for the organization, record
the actual available values or fallback label convention in
`project-memory/config/triage-labels.md`.

## Delivery Defaults

- Default `change_delivery_target`:
  `pull-request-ready-for-merge-but-not-merged`.
- Branch naming: PR targets default to `feature/<feature-slug>`.
  `changes-pushed-to-target-branch-without-pull-request` uses the exact branch
  carried by scoped authorized-user evidence.
- PR shape: one draft PR for a single repo or monorepo feature. In multi-repo
  work, every involved repo uses the same branch name and opens its own PR.
  Generated implementation issues are scheduling units and normally close from
  the relevant PR body.
- Multi-repo Feature Spec shape: use a single Feature Spec only when that is the accepted
  planning source. Otherwise use linked repo-scoped partial Feature Specs or generated
  issues; each one names its affected repo and links the siblings that define
  the same feature. No central repo, central issue, project label, or global
  Feature Spec is required as durable setup configuration.
- Exceptions: `changes-pushed-to-target-branch-without-pull-request` requires
  `source=authorized-user-instruction` plus exact feature-scope and target-branch
  evidence, or a `source-spec` row preserving that evidence. Final-commit issue
  closure additionally requires a separate
  `issue_update_permission=direct-issue-updates-explicitly-authorized` row whose
  explicitly authorizes that closeout for the same scope, target, and branch.

## Runtime Boundary

- Tracker setup records artifact routing, delivery-target defaults, and closeout
  conventions only.

## Title Format

- Feature Spec issue: `Feature Spec: <Feature Name>`
- Implementation issue: `<feature-slug>: <NN> <vertical outcome>`

Use the accepted lowercase kebab-case `<feature-slug>` from `$plan-feature`,
the Feature Spec planning identity, or the Feature Spec source path. Derive it from the Feature Spec title
only when no accepted slug exists. Use two-digit ordering (`01`, `02`, `03`)
for implementation issues so the global issue list remains scannable even
outside the Feature Spec sub-issue view.

## When a skill says "publish to the issue tracker"

Use `$gitstack:github-issues` to create a GitHub issue.

For feature planning:

- The Feature Spec is a GitHub issue titled `Feature Spec: <Feature Name>` with type `Feature`
  unless the repo maps `feature` to a different value.
- Generated implementation issues are the execution graph. Do not create a
  separate execution-plan issue. A requested non-authoritative summary remains
  a response view and is not tracker publication.
- Implementation issues are GitHub sub-issues of the Feature Spec issue with type
  `Task` unless the repo maps `task` to a different value.
- Implementation issue titles use
  `<feature-slug>: <NN> <vertical outcome>`.
- `$plan-feature` owns Feature Spec and generated issue body shape, including
  `source_spec_ref`, delivery metadata, partial Feature Spec links, and issue graph
  validation. Source references must use the canonical `source_spec_ref` field.

For triage:

- Existing bug reports should use the mapped `bug` type.
- Existing feature or enhancement requests should use the mapped `feature`
  type.
- Existing maintenance, docs, cleanup, follow-up, or implementation work items
  should use the mapped `task` type.
- Workflow state belongs in the mapped triage labels, not in the GitHub issue
  type.

## Completion

When all acceptance criteria pass and validation is complete, close that
implementation issue from the relevant PR body with a GitHub closing keyword
such as `Closes #<issue-number>`. For either pull-request delivery target,
the relevant feature or repo PR closes generated implementation issues.
Final-commit closure is allowed only for
`issue_completion_method=final-commit-closing-keyword` with
`issue_update_permission=direct-issue-updates-explicitly-authorized` and exact separately scoped
authorization evidence. The issue closes when that authorized
commit reaches the default branch.

Use closing keywords only for issues actually satisfied by the change. Do not
add the parent Feature Spec closing keyword from an individual child issue. For a
whole Feature Spec final feature or integration PR, the root delivery orchestrator may
add that parent keyword only after its resolved review policy and all Feature Spec
closeout gates pass.

## When a skill says "fetch the relevant issue"

Use `$gitstack:github-issues` to view the issue and recent comments.
