# Issue Phase

Use this reference when `plan-feature` needs to turn a PRD into vertical
implementation issues that can be assigned to agents or humans. This is an
internal phase, not a public skill.

## Goal

Split a PRD into vertical, agent-ready implementation issues. Every generated
issue must be hardened with `$plan-harder` before it is returned or published.

## Hard Requirements

- Load and follow `$plan-harder` for every issue.
- Pass exactly one issue at a time to `$plan-harder` in issue-hardening mode.
- Use the returned `$plan-harder` brief to enrich `## Implementation Plan` and
  merge acceptance, validation, dependency, and blocker details into the
  matching top-level sections. If `$plan-harder` finds an unresolved blocker,
  preserve it in the withheld result or explicitly authorized partial issue.
- Do not publish or return an issue as ready for execution until it includes
  the hardened implementation guidance and provenance line.
- Include a `## Completion` section in every generated implementation issue.
- Do not use `needs-info` as a normal output state for generated
  implementation issues. Treat unresolved product, domain, dependency, or
  acceptance-criteria questions as blockers to resolve before publishing,
  unless the user explicitly asks for partial non-agent-ready backlog output.
- Remember that `$plan-harder` is chat-output-only. It must not write files;
  this phase owns any issue tracker or local markdown writes.
- Use the authoritative feature slug in this order: explicit slug from
  `plan-feature`, PRD file path directory, configured tracker path, then PRD
  title-derived slug as a fallback only.
- Inherit delivery mode from the PRD. The PRD is the canonical place for the
  full branch and PR strategy, but every generated issue must copy the
  effective feature-level `Delivery mode` label for cross-session scheduling.
  Mark it as inherited from `Source PRD` unless the issue has an explicit
  owner-authorized issue-level exception.
- Treat the generated issue set as the execution graph. Before returning or
  publishing issues, validate issue order, dependency references, acyclicity,
  startability waves, and cross-repo gates from the final hardened issue bodies
  themselves after `$plan-harder` has been merged. Do not create a separate
  planning issue, local plan file, PRD plan section, or inline scheduling
  artifact. If the user asks for a summary, label it as a non-authoritative view
  derived from the generated issues.
- Treat local file write authorization and external issue-tracker mutation
  authorization as separate permissions.
- Use structured values for multi-choice issue body fields. This phase owns the
  `parallelization`, `closeout_mode`, and `integration_mode` values documented
  below; `delivery_mode` comes from the PRD, and `issue_type` / `triage_state`
  come from project memory mappings.
- For publication mechanics, effective targets, and stable `source_prd_ref`
  behavior in draft command runs, use `$setup-project-memory`
  `references/tracker-publishing.md`.

## Boundaries

- Do not implement the issues.
- Do not rewrite the PRD unless the user explicitly asks for a PRD update.
- Do not create horizontal layer tickets such as "backend only", "frontend
  only", or "tests only" when a vertical slice is practical.
- Ask for confirmation before writing local issue files or publishing to a
  hosted issue tracker unless the user explicitly asked to write/publish or
  `plan-feature` passes explicit run authorization after resolving gates.

## Structured Issue Values

Use these values in generated issue bodies:

- `parallelization`: `independent` can start in any eligible wave;
  `depends-on <issue-id>` waits for completion proof; `blocks <issue-id>`
  unlocks later work after completion; `root-integrated` stays in the root
  thread.
- `closeout_mode`: `feature-pr-closes-issue`, `repo-pr-closes-issue`,
  `issue-pr-closes-issue`, `direct-commit-closes-issue`, or
  `local-done-move-after-proof` names the concrete completion path.
- `integration_mode`: `shared-feature-branch`, `repo-pr`, `issue-pr`,
  `direct-commit`, `inspect-only`, or `omitted` records how issue output lands
  when it is not obvious from the PRD.

`delivery_mode` is copied from the PRD. `issue_type` and `triage_state` are
mapped through `project-memory/agents/triage-labels.md`. Lower-kebab-case
values are canonical. Treat older uppercase kebab-case values as legacy aliases
when reading existing artifacts. When updating an artifact that contains legacy
aliases, rewrite touched structured values to lower-kebab-case.

## Workflow

### 1. Load Inputs

Find or ask for the PRD source:

- `.scratch/<feature-slug>/PRD.md`,
- a GitHub PRD issue,
- `projects/<project-slug>/features/<feature-slug>/PRD.md`,
- a GitHub coordination-repo PRD issue,
- a handoff `source_prd_ref` from the PRD phase or an existing durable PRD
  source,
- pasted PRD text,
- another project document that clearly acts as the PRD.

Also inspect:

- `project-memory/agents/issue-tracker.md`,
- `project-memory/agents/triage-labels.md`,
- `CONTEXT.md` or `CONTEXT-MAP.md`,
- `project-memory/adr/`,
- orchestrator workspace docs such as `projects/<project>/PROJECT.md`,
  `projects/<project>/repos/*.md`, and feature `integration-gates.md` when the
  tracker config uses orchestrator mode,
- nearby source files, tests, and docs relevant to the PRD.

If there is no PRD-quality source, stop and ask the user to provide one or run
the PRD phase first.

Resolve and carry the planning identity before splitting:

- `feature_slug`: explicit handoff value first, then the PRD directory slug,
  then title-derived fallback only when no accepted path exists.
- For multi-context repos or monorepos: `product_slug`, `workspace_path`, and
  `context_file`.
- For orchestrator workspaces: `project_slug` and affected repos.
- `delivery_mode`: inherit from the PRD `## Delivery Mode` section. If the PRD
  lacks it, infer `one-feature-branch` only for unambiguous single-repo or
  monorepo work and `one-pr-per-repo` only for unambiguous orchestrator or
  cross-repo work; otherwise stop and require the PRD delivery mode to be
  resolved.
- `source_prd_ref`: use the durable PRD issue number, local PRD path, or stable
  draft ref passed by the PRD phase or existing durable PRD source. In
  `draft-publish-commands` mode, keep the draft ref in returned bodies but
  include the replacement step required before hosted mutation.

If a multi-context local-markdown repo lacks an accepted product/context or the
feature slug can collide with another product according to tracker conventions,
stop and resolve that identity before writing issues.

Review PRD open questions before splitting. If any open question affects scope,
acceptance criteria, dependencies, validation, publication target, permissions,
data contracts, or cross-repo contracts, treat it as a blocker instead of
creating `ready-for-agent` issues.

### 2. Split Into Vertical Issues

Use `references/vertical-slices.md` to create a proposed issue list. Apply
vertical slicing whenever practical. Order issues for sequential agentic
implementation, and make dependencies explicit rather than relying on issue
numbering.

Before hardening, validate the generated issue graph from the proposed issue
list:

- `delivery_mode`: inherited from the PRD and copied in each issue.
- ordered issue map with `<NN>` and short intent.
- dependency graph plus `blocks` / `depends-on` intent.
- dependency edge validity check: every `depends-on` / `blocks` reference must
  resolve to a generated issue ID in this feature set (`01`, `02`, ...), and
  the graph must be acyclic.
- startability waves and unblock conditions.
- repo-level boundaries and integration proof requirements for orchestrator
  work.
- Treat the issue bodies as the durable ordering contract for scheduling and
  worker-routing. Do not persist a separate scheduling artifact.

Every issue should:

- deliver a user-visible or system-verifiable increment,
- include enough context to be implemented without rereading the whole PRD,
- include product/workspace/context scope for monorepo work, or affected repos
  and integration gates for orchestrator work,
- include a durable `Source PRD` pointer, copied feature-level delivery mode,
  issue-level parallelization, dependencies, closeout, and any delivery or
  integration exception,
- have clear non-goals,
- include acceptance criteria and validation,
- list dependencies on earlier issues only when truly needed,
- keep dependency references in issue `Parallelization` lines as issue IDs
  (`01`, `02`, ...) rather than prose titles,
- avoid circular dependencies that can lock the queue.

### 3. Harden Every Issue With `$plan-harder`

For each issue, call `$plan-harder` in issue-hardening mode with only that
issue's draft body and the minimum relevant PRD context.

After `$plan-harder` returns:

- add concise implementation guidance under `## Implementation Plan` only when
  the issue is ready for the queue,
- add the first line under that heading as:
  `Plan-hardening: $plan-harder issue-hardening pass completed for this issue only.`,
- merge non-duplicative details from the hardening brief into the issue's
  top-level acceptance criteria, validation, dependencies, context, and blocker
  sections as appropriate,
- resolve any blocker it identifies before marking the issue agent-ready,
- keep the issue scoped to the original vertical slice,
- repeat for the next issue.

Do not paste the `$plan-harder` output wholesale when it would create nested or
duplicated sections such as a second acceptance-criteria list. Do not batch
multiple issues into one `$plan-harder` call. If a blocker cannot be resolved
from the PRD, repo evidence, or project memory, stop and return the blocker
instead of publishing an agent-ready issue.

Before assigning final tracker type/status, writing files, generating draft
commands, or mutating hosted trackers, revalidate the final hardened issue bodies
as the execution graph. Every `Parallelization`, `Dependencies`, `blocks`, and
`depends-on` reference must resolve to a generated issue ID in this feature set,
the graph must be acyclic, startability waves must still make sense, and
cross-repo gates must still name the required integration proof.

### 4. Apply Issue Type And Triage State

Read `project-memory/agents/triage-labels.md` and map canonical issue types
and triage states to the repo's tracker values.

- Use the canonical `task` type for generated implementation issues unless the
  repo's mapping says otherwise.
- Use `ready-for-agent` only when the issue contains hardened implementation
  guidance, acceptance criteria, validation, and no unresolved blocker.
  Dependencies may still be listed; in that case, the issue is queue-ready but
  must not be started until its dependencies are complete.
- Do not create dependency cycles. Every dependency graph must be acyclic so a
  set of ready issues cannot lock the queue.
- Use `needs-info` only for explicitly requested partial backlog output where
  the next action is a concrete question for a human/reporter. Do not count
  `needs-info` issues as agent-ready, and do not publish them from
  `plan-feature` unless it explicitly permits partial output.
- Use `ready-for-human` when the PRD requires human judgment before an agent can
  proceed.

Canonical values are decision inputs, not necessarily tracker values. Before
writing an issue file or calling `$github-issues`, resolve the mapped tracker
value from `project-memory/agents/triage-labels.md`. In default GitHub mode,
`ready-for-agent` maps to the same lowercase label. In custom tracker setups,
do not assume the canonical string is the label; read the mapping first.

### 5. Publish Or Return Issues

Use `project-memory/agents/issue-tracker.md` for the target, and read
`$setup-project-memory` `references/tracker-publishing.md` for shared
effective-target, temporary body-file, and `source_prd_ref` rules:

- `Tracker mode: github`: create issues through `$github-issues`, attach them
  to the PRD parent when the PRD source is a GitHub issue, set the mapped
  `task` issue type when available, then apply mapped labels such as
  `ready-for-agent` for `ready-for-agent`. Do not create a repo-local
  `.scratch/` mirror unless the user explicitly requested one.
- `Tracker mode: orchestrator-github`: create vertical feature issues in the
  configured coordination repo through `$github-issues`, using the PRD parent
  relationship and the required `<project-slug>` label. Derive
  `<project-slug>` from the PRD/project context or ask for it, ensure the label
  exists in the coordination repo, and apply it to every generated vertical
  feature issue. Repo-local implementation PRs or child issues are linked from
  the coordination issue; repo-local child issues are optional in v1. Do not
  create local orchestrator feature artifacts or `.scratch/` mirrors unless the
  user explicitly requested one.
- `Tracker mode: local-markdown`: write to the configured repo-local issue
  path, normally `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, with `Type:`
  and `Status:` lines near the top and a heading that follows the local issue
  title convention `<feature-slug>: <NN> <vertical outcome>`. Use the
  authoritative feature slug from the handoff or PRD path; derive it from the
  PRD title only when no accepted slug/path exists.
- `Tracker mode: orchestrator-local`: write to
  `projects/<project-slug>/features/<feature-slug>/issues/<NN>-<slug>.md` with
  `Type:` and `Status:` lines near the top and a heading that follows the local
  issue title convention `<feature-slug>: <NN> <vertical outcome>`. Create the
  project/feature directories only when writing the actual feature artifacts,
  not during setup. The issue phase owns the issue files and reads
  `PROJECT.md`, `repos/*.md`, and `integration-gates.md`; it does not create or
  refresh those supporting files unless the user explicitly asks for that
  broader orchestrator artifact update.
- Other tracker: follow the repo-specific instructions.

For GitHub PRDs and GitHub coordination PRDs, every generated implementation or
vertical feature issue must be attached to the PRD issue as a sub-issue. If an
issue is created before the parent relationship is set, use `$github-issues` to
attach it afterward. Keep `Source PRD: #<prd-number>` in the issue body as
well.

For GitHub coordination PRDs, every generated vertical feature issue must share
the same project label as the PRD parent issue, named exactly `<project-slug>`.
This label is separate from issue type and workflow-state labels.

When GitHub issue types are available, create or update each implementation
issue with the mapped `task` type, usually `Task`. If issue types are disabled
or unsupported, publish without a type and keep the mapped state labels.

For orchestrator workspace issues, include affected repos, cross-repo contract
notes, integration gates by name or link, repo-local PR or implementation issue
links, and the proof required before the issue can move to `done` or close.
Repo PR links may be placeholders before implementation when the issue is
otherwise agent-ready, but completion must require replacing them with real PR
links or recording equivalent integration proof.

Every published or returned issue must preserve cross-session scheduling
metadata without duplicating the full PRD branch and PR details:

- `Source PRD`: required. Prefer a stable GitHub issue number or local PRD path.
  Use a stable `draft-prd:<...>` ref only for draft command output before
  hosted mutation.
- `Delivery mode`: required. Copy the effective value from the PRD and mark it
  as feature-level, such as `one-feature-branch (feature-level, inherited from
  Source PRD)`. Feature-level means the mode applies to the whole Source PRD
  feature, not only this generated issue. For an exception, record the
  issue-level override and authorization reason, such as `one-pr-per-issue
  (issue-level override, authorized by <owner/date>)`.
- `Parallelization`: required. Use `independent`,
  `depends-on <issue-id>[, <issue-id>]`, `blocks <issue-id>[, <issue-id>]`, or
  `root-integrated`.
- `Dependencies`: required. Use `None` or direct generated issue IDs with the
  dependency reason.
- `Closeout`: required. State the concrete completion path, such as
  `feature-pr-closes-issue`, `repo-pr-closes-issue`,
  `issue-pr-closes-issue`, `direct-commit-closes-issue`, or
  `local-done-move-after-proof`.
- `Integration mode`: optional for ordinary issues that inherit from the PRD.
  Include it when the issue is cross-repo, exceptional, or otherwise not
  obvious from the PRD delivery mode.

For ordinary single-repo or monorepo `one-feature-branch` issues, the
`## Delivery` section can be as small as:

```markdown
## Delivery

- Delivery mode: one-feature-branch (feature-level, inherited from Source PRD)
- Parallelization: independent
- Closeout: feature-pr-closes-issue
```

Every published or returned issue must state its completion path:

- GitHub: close the implementation issue from the relevant PR body with a
  closing keyword, following `Closeout`. Final-commit closure requires
  `direct-commit` or another explicit authorization. Do not close the PRD parent
  unless the maintainer says the whole PRD is complete.
- Local markdown: move the issue to `issues/done/<NN>-<slug>.md` after
  validation, creating `issues/done/` on demand. Orchestrator workspace issues
  also require recorded cross-repo integration proof. Do not delete the file or
  add a `done` status.

Use this implementation issue title format for both GitHub issue titles and
local markdown issue headings:

```text
<feature-slug>: <NN> <vertical outcome>
```

- `<feature-slug>` is the authoritative lowercase kebab-case slug from
  `plan-feature`, PRD path, or configured tracker target. Derive it from the
  PRD title without the `PRD:` prefix only as a fallback.
- `<NN>` is the two-digit sequence from the vertical issue ordering.
- `<vertical outcome>` is a short imperative or outcome phrase, without a
  trailing period.

Example: `team-invitations: 02 Accept invitation into team`.

If the user did not ask to publish and `plan-feature` did not pass explicit run
authorization, return the hardened issue bodies in chat. If `plan-feature`
passes explicit run authorization, use the effective target from that handoff
without re-asking unless this phase finds a new blocker or unresolved question.
Do not treat "local file writes allowed" as permission to mutate GitHub or
another hosted tracker. In hosted tracker modes, local file write authorization
applies only to explicit local mirrors or dry-run targets; hosted body-file
inputs are transient files outside the repo.

Immediately before returning issue bodies, writing local issue files, handing
content to `$github-issues`, or generating draft publish commands, re-scan every
final issue body for machine-local absolute paths and replace them with
sanitized evidence references. Treat any remaining unsanitized developer path as
a blocker for hosted publication or shared draft command output.

If the configured target is GitHub or GitHub coordination but external mutation
is not authorized, do not mutate GitHub. Ask `$github-issues` for exact draft
commands, or use the configured local dry-run target when one is recorded. In
`draft-publish-commands` mode, generated issue bodies may use
`Source PRD: draft-prd:<...>` only in returned draft output; the publish plan
must create the PRD first, capture the hosted PRD number, replace the draft ref
with `Source PRD: #<number>`, and then create or attach implementation issues.
When a blocker or unresolved question appears under `plan-feature`, return it
as an issue-splitting gate instead of publishing a `needs-info` issue by
default.

### 6. Report Completion

Summarize:

- source PRD,
- authoritative `feature_slug`,
- product/workspace/context or orchestrator project identity used, when
  applicable,
- delivery mode inherited,
- number of issues produced,
- issue graph validation summary, including dependency and acyclicity checks,
- GitHub PRD parent issue and sub-issues attached, when applicable,
- where issues were published or that output stayed in chat,
- issue types and labels/statuses assigned,
- completion instruction included,
- any blocked issues and why,
- whether any non-agent-ready partial issues were withheld or explicitly
  published as `needs-info` / `ready-for-human`,
- confirmation that `$plan-harder` was run once per issue, that each issue
  includes the standard plan-hardening provenance line, and that the hardening
  output was merged into the issue without duplicated sections.

## Issue Body Shape

Before composing or validating issue bodies, read
`references/issue-body-template.md`. Use that template unless the tracker has a
stronger local template. Keep `## Questions` out of `ready-for-agent` issues;
include it only for explicitly authorized partial `needs-info` output.

## References

- `references/vertical-slices.md`: issue splitting rules.
- `references/issue-body-template.md`: generated implementation issue body
  template.
- `$setup-project-memory` `references/tracker-publishing.md`: shared tracker
  publication and `source_prd_ref` contract.
