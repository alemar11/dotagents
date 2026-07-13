# Issue Phase

Use this reference when `plan-feature` needs to turn a PRD into vertical
implementation issues that can be assigned to agents or humans. This is an
internal phase, not a public skill.

## Goal

Split a PRD into vertical, agent-ready implementation issues. Every generated
issue must be hardened with `$plan-harder` before it is returned or published.

## Hard Requirements

- Load and follow `$plan-harder` for every issue.
- Pass exactly one issue at a time to `$plan-harder` with
  `planning_mode=issue-hardening` and `output_surface=caller`, and request the
  structured caller result.
- Use the returned `$plan-harder` brief to enrich `## Implementation Plan` and
  merge acceptance, validation, dependency, and blocker details into the
  matching top-level sections. If `$plan-harder` finds an unresolved blocker,
  preserve it in the withheld result or explicitly authorized partial issue.
- Do not publish or return an issue as ready for execution until it includes
  the hardened implementation guidance and provenance line.
- Before assigning final tracker metadata, writing files, returning bodies,
  generating draft commands, or mutating hosted trackers, run the verticality
  gate from `references/vertical-slices.md` against the final hardened issue
  bodies. Repair, merge, split, re-harden, or withhold anomalies before output.
- Include a `## Completion` section in every generated implementation issue.
- Include a `## Orchestrator Handoff` section in every generated implementation
  issue. The handoff is the canonical dispatch grouping for
  `$codex-orchestrator`; it restates issue-level scheduling and closeout data
  already present elsewhere in the issue body without granting worker
  authorization.
- Do not use `needs-info` as a normal output state for generated
  implementation issues. Treat unresolved product, domain, dependency, or
  acceptance-criteria questions as blockers to resolve before publishing,
  unless `partial_output=allow-non-agent-ready`. The default
  `partial_output=withhold` keeps them unpublished.
- `$plan-harder` must not write files. With `output_surface=caller` it returns
  only the structured hardening result; this phase owns issue-body merging and
  any issue tracker or local Markdown writes.
- Use the authoritative feature slug in this order: explicit slug from
  `plan-feature`, PRD file path directory, configured tracker path, then PRD
  title-derived slug as a fallback only.
- Inherit delivery mode from the PRD. The PRD is the canonical place for the
  full branch and PR strategy, but every generated issue must copy the
  effective feature-level `delivery_mode` label for cross-session scheduling.
  Use `delivery_source=feature-level-inherited` unless an authorized option row
  selects `delivery_source=issue-level-override`.
- Treat the generated issue set as the execution graph. Before returning or
  publishing issues, validate issue order, dependency references, acyclicity,
  startability waves, and cross-repo integration proof requirements from the
  final hardened issue bodies themselves after `$plan-harder` has been merged.
  Do not create a separate planning issue, local plan file, PRD plan section, or
  inline scheduling artifact. If the user asks for a summary, label it as a
  non-authoritative view derived from the generated issues.
- When `domain_knowledge_delta.knowledge_delta` is `required`, make its capture and
  verification part of the final integration task. Prefer an existing terminal
  task that already owns feature-level integration proof. Otherwise append one
  final integration and domain-knowledge closeout task that depends on every
  terminal implementation issue. This final task must be system-verifiable and
  must not be a docs-only horizontal ticket. It must require its implementor to
  invoke `$project-memory` with `memory_slice=domain-memory` and
  `domain_operation=implementation-closeout`, which runs its internal
  domain-modeling workflow for the durable content update.
- Treat `tracker_backend` as planning-artifact write authority. When the
  `effective_target=configured-tracker`, publish GitHub issues for
  `github` backends and write Markdown files for `local` backends. Return draft
  bodies or commands only for `effective_target=local-dry-run` or
  `effective_target=draft-publish-commands`.
- Use structured values for multi-choice issue body fields. This phase owns the
  `parallelization`, `closeout_mode`, and `integration_mode` values documented
  below; `delivery_mode` and `pr_closeout` come from the PRD, while
  `issue_type` and `workflow_state` use the canonical Triage contract before
  any GitHub boundary mapping.
- Do not add worker authorization defaults, worker capability modes, or worker
  surface choices to PRDs, generated issues, issue files, hosted issue bodies,
  or draft publish commands. `$codex-orchestrator` resolves those per
  workstream and session.
- Do not add checkpoint approval, publication permission, runtime issue-mutation
  overrides, or worker permissions to `## Orchestrator Handoff`. Those are
  runtime authorization decisions owned by `$codex-orchestrator`. Preserve the
  independently resolved source-contract `issue_mutation_authority` and
  `issue_mutation_authority_evidence`; the orchestrator validates them and they
  do not directly authorize a worker.
- Treat `$codex-orchestrator` session settings as runtime-only. Do not copy
  worker surfaces, worker counts, or checkpoint choices into PRDs, generated
  issues, local issue files, hosted issue bodies, or draft publish commands.
- For publication mechanics, effective targets, and stable `source_prd_ref`
  behavior in draft command runs, use `$project-memory`'s `references/tracker-publishing.md`.

## Boundaries

- Do not implement the issues.
- This phase never rewrites the PRD. A requested PRD update runs through the
  PRD phase before issue splitting and supplies a new verified handoff.
- Do not create horizontal layer tickets such as "backend only", "frontend
  only", or "tests only" when a vertical slice is practical.
- Do not ask for separate issue write/publish confirmation after `plan-feature`
  has resolved setup, planning identity, blockers, and effective target. Ask
  only when the canonical target snapshot is missing, ambiguous, or
  internally contradictory.

## Phase Handoff Inputs

When called by `plan-feature`, receive the same publishing target and planning
identity fields used by the PRD phase, with `source_prd_ref` resolved or
carried from the draft handoff:

```text
mode: <full-flow|issues-from-existing-prd>
execution_profile: <lean-issues|standard>
tracker_backend: <github|local>
effective_target: <configured-tracker|local-dry-run|draft-publish-commands>
no_mutation_override: <none|dry-run|temp|rehearsal|validation|disabled-writes|draft-output>
no_mutation_output: <not-applicable|local-artifacts|publish-commands>
local_mirror: <not-requested|requested>
local_mirror_path: <repo-relative mirror root|not-applicable>
partial_output: <withhold|allow-non-agent-ready>
delivery_mode: <pull-request|direct-commit>
issue_mutation_authority: <none|pr-body-closeout-only|explicit-direct-mutation>
issue_mutation_authority_evidence: <source PRD/owner evidence or none>
branch_name: <feature branch or exact authorized direct-commit target branch>
pr_closeout: <merge-ready|draft-only|not-applicable>
pr_shape: <single-pr|per-repo-pr|none>
source_prd_ref: <#prd-number|repo-relative PRD path|draft-prd:slug>
feature_slug: <accepted feature slug>
product_slug: <accepted product slug or not-applicable>
workspace_path: <accepted workspace path or not-applicable>
context_file: <selected CONTEXT.md or not-applicable>
project_slug: <accepted orchestrator project slug or not-applicable>
option_resolution: <keyed run rows; append issue:<NN> rows before output>
option_rows_fingerprint: <incoming run-row sha256, then complete run-plus-issue sha256 on output>
capture_outcome: <deferred|no-durable-change>
domain_knowledge_delta: <structured deferred delta or PRD handoff>
```

Verify the incoming run-row `option_rows_fingerprint` before splitting. Every
issue adds exactly one row per Per-Issue Registry field plus its effective
`branch_name` data row. After the issue graph and every `issue:<NN>` row are final, recompute the
fingerprint over the complete run-plus-issue row set and carry that value into
publication and completion output.

Validate `capture_outcome=deferred` when
`domain_knowledge_delta.knowledge_delta=required` and
`capture_outcome=no-durable-change` when `knowledge_delta=none`. Preserve a
non-empty `unresolved` list independently as planning blockers. For
`mode=issues-from-existing-prd`, reconstruct the pair from the PRD's canonical
Domain Knowledge Handoff when the explicit phase handoff is unavailable; a
legacy PRD with a handoff resolves to `required` plus `deferred`, while no
handoff resolves to `none` plus `no-durable-change`. Never invent
`capture_outcome=captured` in Plan Feature.

## Structured Issue Values

Use these values in generated issue bodies:

- `parallelization`: `independent`, `depends-on`, `blocks`, or
  `root-integrated`. Store generated issue ids separately in `dependency_ids`
  and `blocked_issue_ids`; never append ids to the enum value.
- `closeout_mode`: `feature-pr-closes-issue`, `repo-pr-closes-issue`,
  `direct-commit-closes-issue`, or `local-done-move-after-proof` names the
  concrete completion path. Use `local-done-move-after-proof` for local
  markdown issues even when the delivery mode is `direct-commit`;
  `direct-commit-closes-issue` is only for hosted trackers or other sources
  where an authorized final commit can close the source item.
- `issue_mutation_authority`: `none`, `pr-body-closeout-only`, or
  `explicit-direct-mutation`. The explicit value is required for
  `direct-commit-closes-issue` and must come from separately preserved owner
  evidence; it is not inferred from `delivery_mode=direct-commit`.
- `integration_mode`: `single-repo-pr`, `repo-pr`, `direct-commit`, or
  `not-applicable`.
- `domain_closeout`: `not-applicable` or `implementation-closeout`; decisions,
  targets, evidence, and `domain_operation` remain separate data fields.

The feature-level delivery tuple is copied from the PRD by default. An
authorized issue-level override atomically resolves `delivery_mode`,
`issue_mutation_authority`, `pr_shape`, `pr_closeout`, `closeout_mode`, and
`integration_mode` before
output. `issue_type` and `workflow_state` remain canonical in issue bodies;
`project-memory/agents/triage-labels.md` maps them only at the GitHub boundary.
Lower-kebab-case values are canonical. Treat older uppercase kebab-case values
as legacy aliases when reading existing artifacts. When updating an artifact
that contains legacy aliases, rewrite touched structured values to
lower-kebab-case.

## Workflow

### 1. Load Inputs

Find or ask for the PRD source:

- `.scratch/<feature-slug>/PRD.md`,
- a GitHub PRD issue,
- `projects/<project-slug>/features/<feature-slug>/PRD.md`,
- a linked GitHub workspace PRD issue,
- a handoff `source_prd_ref` from the PRD phase or an existing durable PRD
  source,
- pasted PRD text,
- another project document that clearly acts as the PRD.

Also inspect:

- `project-memory/agents/issue-tracker.md`,
- `project-memory/agents/triage-labels.md`,
- `CONTEXT.md` or `CONTEXT-MAP.md`,
- `TRANSLATION.md`, when present for the selected context,
- `project-memory/adr/`,
- orchestrator workspace docs such as `projects/<project>/PROJECT.md`,
  `projects/<project>/repos/*.md`, and feature `integration-gates.md` when
  planning from a local orchestrator workspace,
- nearby source files, tests, and docs relevant to the PRD.

Load `domain_knowledge_delta` from the Plan Feature handoff. For
`issues-from-existing-prd`, reconstruct it from `## Domain Knowledge Handoff`
when that section exists. Treat an unresolved item that changes implementation
scope as a blocker; do not silently move product questions into the final task.

If there is no PRD-quality source, stop and ask the user to provide one or run
the PRD phase first.

For `lean-issues`, read the durable PRD once, then inspect only tracker/type
mappings and source/tests directly needed to validate its candidate slices.
Keep the profile only when one repo/context is unambiguous, no more than two
vertical issues are expected, and no cross-repo gate, enabling slice, unresolved
blocker, or separate domain-closeout owner appears. Otherwise widen to
`standard`, load the broader context above, and record the first failed lean
condition. The lean profile does not weaken any hardening or output gate.

Resolve and carry the planning identity before splitting:

- `feature_slug`: explicit handoff value first, then the PRD directory slug,
  then title-derived fallback only when no accepted path exists.
- For multi-context repos or monorepos: `product_slug`, `workspace_path`, and
  `context_file`.
- For orchestrator workspaces: `project_slug` and affected repos.
- `delivery_mode`: inherit from the PRD `## Delivery Mode` section. If the PRD
  lacks it, infer `pull-request` when repo shape and affected repo set are
  unambiguous; otherwise stop and require the PRD delivery mode to be resolved.
- `branch_name`: inherit the structured PRD value. For `direct-commit`, verify
  that it equals the exact target branch in the preserved
  `delivery_mode_evidence`; missing or conflicting evidence is blocking.
- `issue_mutation_authority`: inherit the structured PRD value. For GitHub
  direct-commit, require `explicit-direct-mutation` plus separately preserved
  owner evidence explicitly authorizing final-commit closure for the same
  scope, target, and branch. Missing evidence is blocking; do not derive this
  value from direct-commit publication authority.
- `pr_shape`: inherit the canonical value from the PRD. For a legacy PRD that
  lacks it, apply `references/options.md` legacy normalization once, record the
  canonical value and migration evidence, and use only that value downstream.
- `pr_closeout`: for `pull-request`, inherit the structured `pr_closeout` value.
  Default missing legacy values to `merge-ready`. Use `draft-only` only when the
  PRD or its option-resolution record carries that canonical value; do not
  compare source prose during issue splitting. For `direct-commit`, use
  `not-applicable`.
- `source_prd_ref`: use the durable PRD issue number, local PRD path, or stable
  draft ref passed by the PRD phase or existing durable PRD source. In
  either non-mutating effective target, keep the draft ref in returned bodies.
  For `draft-publish-commands`, include the replacement step required before
  hosted mutation; for `local-dry-run`, label it non-executable.

If a multi-context local Markdown repo lacks an accepted product/context or the
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
- `pr_shape`: inherited from the PRD or its one-time legacy normalization and
  copied in each issue.
- `pr_closeout`: inherited from the PRD for `pull-request` and copied in each
  issue.
- ordered issue map with `<NN>` and short intent.
- dependency graph plus `blocks` / `depends-on` intent.
- dependency edge validity check: every `depends-on` / `blocks` reference must
  resolve to a generated issue ID in this feature set (`01`, `02`, ...), and
  the graph must be acyclic.
- Normalize each dependency edge from prerequisite to downstream consumer:
  `02 depends-on 01` and `01 blocks 02` both produce `01 -> 02`. Before adding
  domain closeout, snapshot terminal issues as pre-closeout nodes with no
  downstream consumers (out-degree zero). When an existing terminal issue is
  selected as the final owner, exclude it from the terminal prerequisites added
  to itself.
- startability waves and unblock conditions.
- repo-level boundaries and integration proof requirements for orchestrator
  work.
- Treat the issue bodies as the durable ordering contract for scheduling and
  worker-routing. Do not persist a separate scheduling artifact.

When `domain_knowledge_delta.knowledge_delta` is `required`, choose its final owner from
that pre-closeout terminal snapshot after the initial graph is formed:

1. If exactly one terminal issue already runs the end-to-end integration or
   release proof, add domain closeout to that issue and make it depend directly
   on every other terminal issue so it cannot start before sibling outcomes
   land.
2. Otherwise append the last generated issue as a final integration and
   domain-knowledge closeout task. It depends directly on every terminal issue,
   reruns the feature-level integration proof, invokes `$project-memory` with
   `memory_slice=domain-memory` and
   `domain_operation=implementation-closeout`, updates the named
   context/docs/ADR targets through Project Memory's internal domain-modeling
   workflow and the feature delivery path, and verifies the resulting docs
   against the implemented behavior.
3. Add the exact decisions, target surfaces, and evidence under
   `## Domain Knowledge Closeout`; merge corresponding work into Requirements,
   Acceptance Criteria, Validation, Completion, and Orchestrator Handoff.
4. Mark the task `root-integrated` only when root ownership is actually
   required; otherwise use explicit `depends-on` IDs.

The final owner is part of the implementation graph and must be passed through
`$plan-harder`. Never append a documentation-only task. When
`knowledge_delta=none`, do not create a synthetic closeout issue. After choosing or appending
the owner, revalidate generated IDs, direct dependency edges, acyclicity,
startability waves, and final-task ordering before hardening begins. Treat an
existing integration owner that does not depend on every other terminal issue
as an invalid graph.

Every issue should:

- deliver a user-visible or system-verifiable increment,
- include enough context to be implemented without rereading the whole PRD,
- include product/workspace/context scope for monorepo work, or affected repos
  and integration gates for orchestrator work,
- include a durable `source_prd_ref` pointer, copied feature-level
  `delivery_mode`, `pr_shape`, issue-level parallelization, dependencies,
  closeout, and any delivery or integration exception,
- include a `## Orchestrator Handoff` section that restates the dispatchable
  source PRD, feature slug, `delivery_mode`, `pr_shape`, affected repos or
  product scope, scope, start rule, dependencies, validation, closeout, and
  `integration_mode`,
- have clear non-goals,
- include acceptance criteria and validation,
- list dependencies on earlier issues only when truly needed,
- keep dependency references in `dependency_ids` / `blocked_issue_ids` as
  issue IDs (`01`, `02`, ...) rather than prose titles,
- avoid circular dependencies that can lock the queue.

The final domain owner must additionally:

- validate the integrated feature after all terminal dependencies complete,
- update only the target durable surfaces named by the knowledge delta, using
  `current-repository/<path>` or `<repo-slug>/<path>` ownership so multi-repo
  destinations are unambiguous,
- reconcile provisional planning language with the behavior that actually
  landed rather than copying the PRD blindly,
- include `git diff --check` or the repository's equivalent documentation diff
  check,
- record one completion proof covering both integration and durable capture.

### 3. Harden Every Issue With `$plan-harder`

For each issue, call `$plan-harder` with `planning_mode=issue-hardening` using
only that issue's draft body and the minimum relevant PRD context. Explicitly
request `output_surface=caller` and the structured result from
`$plan-harder`'s `references/templates.md`.

After `$plan-harder` returns:

- require `result_status`, `implementation_plan`, `acceptance_criteria`,
  `validation`, `dependencies`, and `blockers`; treat a non-empty `blockers`
  list or `result_status: blocked` as a blocker rather than an agent-ready brief,
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

### 4. Run The Verticality Gate

Before assigning final tracker type/status, writing files, returning issue
bodies, generating draft commands, or mutating hosted trackers, review every
final hardened issue body against `references/vertical-slices.md`.

For each issue, verify that it:

- delivers one independently verifiable product or system outcome,
- has acceptance criteria written as outcomes, not internal chores,
- is not only a layer ticket such as frontend-only, backend-only, tests-only,
  docs-only, fixture-only, refactor-only, migration-only, configuration-only,
  or observability-only work,
- includes the minimum layers needed to make the outcome real,
- can be validated on its own,
- lists only direct dependencies by generated issue ID,
- has no hidden ordering assumption that is only implied by issue numbering,
- keeps the `## Orchestrator Handoff`, `## Delivery`, `## Validation`,
  `## Completion`, and `## Dependencies` sections consistent.

For the final domain owner, also verify that `## Domain Knowledge Closeout`
contains the carried decisions, target surfaces, and evidence, and that its goal
and acceptance criteria prove integrated behavior in addition to documentation.
Require an explicit `$project-memory domain-memory` implementation step and
proof that it ran the internal domain-modeling workflow; reject a direct ad hoc
edit presented as equivalent. Reject ambiguous bare target or repo-local
evidence paths in multi-repo work.

Allow a separate enabling issue only when it satisfies all exception rules from
`references/vertical-slices.md`: no useful vertical slice can be implemented
before it, it unblocks at least one named later vertical issue, it is
independently verifiable, it has clear acceptance criteria, it is small enough
for one focused implementation pass, and its dependencies and consumers are
listed explicitly. Name the issue by the capability it unlocks, not the code
layer it changes.

If the gate finds an anomaly:

- merge chore-only tests, docs, fixtures, migrations, configuration, or
  observability work into the vertical issue whose outcome they prove,
- keep required domain capture in the final integration owner; if the proposed
  owner is docs-only, merge it into an existing terminal integration issue or
  broaden it only to the real feature-level integration proof,
- split mixed issues by independently verifiable behavior rather than by code
  layer,
- reframe infrastructure work as a concrete system outcome only when that is
  true and independently verifiable,
- keep a separate enabling issue only with a visible enabling-slice exception
  rationale in its context or requirements,
- re-run `$plan-harder` for any issue whose scope materially changes,
- revalidate dependency IDs, acyclicity, startability waves, handoff
  consistency, and cross-repo proof after every repair,
- withhold issues whose blocker cannot be resolved from the PRD, repo evidence,
  or project memory.

Do not publish or return a normal `ready-for-agent` issue set until the
verticality gate passes for every issue or withholds every unresolved anomaly.
If the gate changes issue IDs, dependencies, titles, validation, or affected
repos, update all affected issue bodies before output.

Before assigning final metadata, returning bodies, writing files, or publishing
issues, run a small documentation gate over the final issue bodies. Verify that
each issue has portable evidence references, no runtime worker settings,
consistent handoff/delivery/completion wording, enough rationale for the next
agent to act without rereading the entire PRD, and no duplicated or nested
sections introduced by `$plan-harder`. Repair the issue bodies before output
when this gate fails.

### 5. Apply Issue Type And Triage State

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
- Use `needs-info` only when `partial_output=allow-non-agent-ready` and
  the next action is a concrete question for a human/reporter. Do not count
  `needs-info` issues as agent-ready, and do not publish them from
  `plan-feature` under `partial_output=withhold`.
- Use `ready-for-human` when the PRD requires human judgment before an agent can
  proceed.

Canonical values are decision inputs, not necessarily tracker values. Before
writing an issue file or calling `$gitstack:github-issues`, resolve the mapped tracker
value from `project-memory/agents/triage-labels.md`. In default GitHub mode,
`ready-for-agent` maps to the same lowercase label. In custom tracker setups,
do not assume the canonical string is the label; read the mapping first.

### 6. Publish Or Return Issues

Use `project-memory/agents/issue-tracker.md` for the target, and read
`$project-memory`'s `references/tracker-publishing.md` for shared
effective-target, temporary body-file, and `source_prd_ref` rules:

- `tracker_backend=github`: with `effective_target=configured-tracker`, create
  issues through `$gitstack:github-issues`, attach them
  to the PRD parent when the PRD source is a GitHub issue, set the mapped
  `task` issue type when available, then apply mapped labels such as
  `ready-for-agent` for `ready-for-agent`. Do not create a repo-local
  `.scratch/` mirror unless `local_mirror=requested`; when requested, write
  issue mirrors under `local_mirror_path`. Pass sanitized
  issue titles, bodies, target repo, labels, types, and parent/sub-issue intent
  to `$gitstack:github-issues`; do not assemble direct mutating `gh issue create` shell
  commands with generated Markdown in this phase.
- GitHub workspace issues: create linked repo or partial issues through
  `$gitstack:github-issues`, using PRD parent/sub-issue relationships where available.
  Derive `<project-slug>` and affected repos from the PRD/project context or ask
  for them. Repo-local implementation PRs or child issues link back to the
  relevant PRD or partial issue. Do not create local orchestrator feature
  artifacts or `.scratch/` mirrors unless `local_mirror=requested`; write any
  requested mirrors under `local_mirror_path`.
- `tracker_backend=local`: with `effective_target=configured-tracker`, write to the configured repo-local issue
  path, normally `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, with
  `issue_type:`, `workflow_state:`, and `source_prd_ref:` lines near the top and
  a heading that follows the local issue title convention
  `<feature-slug>: <NN> <vertical outcome>`. Use the
  authoritative feature slug from the handoff or PRD path; derive it from the
  PRD title only when no accepted slug/path exists.
- Local workspace issues: write to
  `projects/<project-slug>/features/<feature-slug>/issues/<NN>-<slug>.md` with
  `issue_type:`, `workflow_state:`, and `source_prd_ref:` lines near the top and
  a heading that follows the local issue title convention
  `<feature-slug>: <NN> <vertical outcome>`. Create the
  project/feature directories only when writing the actual feature artifacts,
  not during setup. The issue phase owns the issue files and reads
  `PROJECT.md`, `repos/*.md`, and `integration-gates.md`; it never creates or
  refreshes those supporting files. A broader artifact update belongs to the
  PRD phase and must finish before the issue-phase handoff.
For GitHub PRDs, every generated implementation or vertical feature issue must
be attached to the PRD issue as a sub-issue when the tracker supports it. If an
issue is created before the parent relationship is set, use `$gitstack:github-issues` to
attach it afterward. Keep `source_prd_ref: #<prd-number>` in the issue body as well.
For multi-repo work, related partial PRDs and repo issues must link to each
other by URL or issue number.

When GitHub issue types are available, create or update each implementation
issue with the mapped `task` type, usually `Task`. If issue types are disabled
or unsupported, publish without a type and keep the mapped state labels.

For orchestrator workspace issues, include affected repos, cross-repo contract
notes, integration gates by name or link, repo-local PR or implementation issue
links when they exist, expected repo PR slots or pre-implementation
placeholders, and the proof required before the issue can move to `done` or
close. Placeholders are delivery expectations for scheduling, not completion
proof; `$codex-orchestrator` records real PR links or equivalent integration
proof during source closeout.

Every generated agent-ready implementation issue must include the
`## Orchestrator Handoff` shape from `references/issue-body-template.md`. The
handoff may repeat structured data from `## Delivery`, `## Validation`,
`## Completion`, and `## Dependencies` so an orchestrator can register the issue
without inferring from loose prose. It must not contain worker authorization,
publication authority, runtime issue-mutation overrides, or orchestration
session settings. It must carry the independently resolved source-contract
`issue_mutation_authority` and evidence required by the delivery tuple; those
fields do not authorize a worker.

When a final domain owner exists, publish or write it last, attach it to the
same PRD parent, and keep its dependency metadata in the generated feature-ID
space (`01`, `02`, ...), including after hosted issue numbers or local paths
exist. Track those published or local refs separately. In draft command mode,
preserve the same last-task ordering and replacement rules.

Every published or returned issue must preserve cross-session scheduling
metadata without duplicating the full PRD branch and PR details:

- `source_prd_ref`: required. Prefer a stable GitHub issue number or local PRD path.
  Use a stable `draft-prd:<...>` ref only for non-mutating output before hosted
  mutation.
- `delivery_mode`: required. Copy the effective value from the PRD and record
  the source separately as `delivery_source=feature-level-inherited`. For an
  authorized exception, use `delivery_source=issue-level-override`, store the
  authorization ref in `delivery_source_evidence`, and atomically resolve the
  complete delivery tuple described below; never append provenance to an enum
  value.
- `delivery_source_evidence`: for every effective `direct-commit` issue,
  preserve the PRD/owner `owner-ref` and target branch, set
  `scope-ref=issue:<NN>`, preserve the PRD `target-ref` verbatim, and add
  `scope-transfer-ref=run` when the delivery is feature-level inherited. A
  missing owner token or a target/branch change blocks publication.
- `issue_mutation_authority`: required. Use `none` for local trackers,
  `pr-body-closeout-only` for GitHub pull-request delivery, and
  `explicit-direct-mutation` for GitHub direct-commit only when the separate
  owner closeout row is valid.
- `issue_mutation_authority_evidence`: for
  `explicit-direct-mutation`, project the separately authorized evidence to
  `scope-ref=issue:<NN>`, preserve the same target and branch tokens as
  `delivery_source_evidence`, preserve its independent closeout `owner-ref`, and
  add `scope-transfer-ref=run` for feature-level inheritance. Recovery
  fingerprints the delivery and mutation evidence separately.
- `branch_name`: required data. Inherit the feature branch for
  `delivery_source=feature-level-inherited`. For an issue-level
  `delivery_mode=direct-commit` override, copy the exact authorized target
  branch named by `delivery_source_evidence`; reject missing or conflicting
  branch data.
- `pr_shape`: required. For feature-level inheritance, copy `single-pr`,
  `per-repo-pr`, or `none` from the PRD. For an issue-level override, derive it
  from the effective issue `delivery_mode` and repo scope through
  `references/options.md`; do not re-derive it from prose.
- `pr_closeout`: required. Copy `merge-ready`, `draft-only`, or `not-applicable`
  from the PRD only for feature-level inheritance. For an issue-level override
  or a legacy issue with a missing value, resolve from the effective issue
  `delivery_mode`: `merge-ready` for `pull-request` unless canonical override
  evidence selects `draft-only`, and `not-applicable` for `direct-commit`.
  Never resolve it from PR-shape prose.
- `parallelization`: required. Use `independent`, `depends-on`, `blocks`, or
  `root-integrated`. Put ids in `dependency_ids` and `blocked_issue_ids`.
- `dependency_ids`, `blocked_issue_ids`, and `dependency_reason`: required data
  fields; use `none` when empty.
- `domain_closeout`: required. Use `not-applicable` unless the issue owns
  `## Domain Knowledge Closeout`; for that final owner, copy
  `implementation-closeout` and put the exact decisions, target surfaces,
  evidence, `memory_slice=domain-memory`, and
  `domain_operation=implementation-closeout` in
  `domain_closeout_data`.
- `closeout_mode`: required. Resolve the concrete completion path from the
  effective issue `delivery_mode` and tracker backend, using
  `feature-pr-closes-issue`, `repo-pr-closes-issue`,
  `direct-commit-closes-issue`, or `local-done-move-after-proof`.
  For local markdown trackers, use `local-done-move-after-proof` even when
  `delivery_mode` is `direct-commit`.
  `direct-commit-closes-issue` additionally requires
  `issue_mutation_authority=explicit-direct-mutation`; otherwise stop before
  emitting an agent-ready issue.
- `integration_mode`: required. Resolve it from the effective issue
  `delivery_mode`; use `not-applicable` for an ordinary issue with no
  exceptional integration path.

### Validation Commands

Generated issues should name the preferred validation command and, when repo
evidence suggests runners may differ by environment, an equivalent fallback.
Examples: prefer the repo script in `package.json`, `pyproject.toml`, `Makefile`,
or project docs; include `pytest` as a fallback when `python -m pytest` may be
unavailable because the Python shim or module path is missing.

If the preferred command fails only because the command wrapper is unavailable
and an equivalent fallback passes, record both outcomes in validation proof
instead of treating the issue as blocked. Do not hide real test failures behind
a fallback.

For ordinary single-repo or monorepo `pull-request` issues, the
`## Delivery` section can be as small as:

```markdown
## Delivery

- delivery_mode: pull-request
- delivery_source: feature-level-inherited
- delivery_source_evidence: source_prd_ref
- issue_mutation_authority: pr-body-closeout-only
- issue_mutation_authority_evidence: source_prd_ref
- branch_name: feature/<feature-slug>
- pr_shape: single-pr
- pr_closeout: merge-ready
- parallelization: independent
- dependency_ids: none
- blocked_issue_ids: none
- closeout_mode: feature-pr-closes-issue
- integration_mode: not-applicable
```

Every published or returned issue must state its completion path:

- GitHub: close the implementation issue from the relevant PR body with a
  closing keyword, following `closeout_mode`. Final-commit closure requires
  `closeout_mode=direct-commit-closes-issue`,
  `issue_mutation_authority=explicit-direct-mutation`, and its exact scoped
  authorization evidence. Do not add the parent PRD closing keyword from an individual child
  issue. For a whole-PRD final feature
  or integration PR, the root delivery orchestrator adds that parent keyword
  only after its final current-head review and all PRD closeout gates pass.
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

Use `effective_target` from the `plan-feature` handoff without re-resolving it.
`configured-tracker` creates the GitHub issues or writes the local issue files.
`local-dry-run` returns paths and bodies without writing.
`draft-publish-commands` returns exact hosted commands without mutation. In
hosted tracker modes, local file writes apply only when
`effective_target=configured-tracker` and `local_mirror=requested`; hosted
body-file inputs are transient files outside the repo and are owned by
`$gitstack:github-issues`. Hosted tracker mutation in
this phase is limited to generated planning issue publication, parent/sub-issue
links, issue type metadata, and initial workflow-state labels. After
implementation scheduling starts, issue lifecycle comments, label changes,
direct closure, and closeout mutations belong to `$codex-orchestrator`.

Immediately before returning issue bodies, writing local issue files, handing
content to `$gitstack:github-issues`, or generating draft publish commands, re-scan every
final issue body for machine-local absolute paths and replace them with
sanitized evidence references. Treat any remaining unsanitized developer path as
a blocker for hosted publication or shared draft command output.

For `tracker_backend=github`, branch only on `effective_target`:
`configured-tracker` publishes, `local-dry-run` returns issue bodies and target
refs without mutation, and `draft-publish-commands` asks
`$gitstack:github-issues` for exact draft commands. Under either non-mutating
target, generated issue bodies may use `source_prd_ref: draft-prd:<...>` only
in returned output. For `draft-publish-commands`, the publish plan must create
the PRD first, capture the hosted PRD number, replace the draft ref with
`source_prd_ref: #<number>`, and then create or attach implementation issues.
For `local-dry-run`, return the PRD body fingerprint and label the ref
non-executable.
When a blocker or unresolved question appears under `plan-feature`, return it
as an issue-splitting blocker instead of publishing a `needs-info` issue by
default. When `partial_output=allow-non-agent-ready`, the phase may return or
publish the affected issue as `needs-info` or `ready-for-human` after target
resolution, with the blocker visible and no agent-ready claim.

### 7. Report Completion

Summarize:

- source PRD,
- canonical keyed run/issue option rows and option-resolution evidence, including any
  execution-profile widening reason,
- `option_rows_fingerprint` for the complete run-plus-issue row set,
- authoritative `feature_slug`,
- product/workspace/context or orchestrator project identity used, when
  applicable,
- number of issues produced,
- verticality gate result, including any repairs, merges, splits,
  enabling-slice exceptions, or withheld anomalies,
- issue graph validation summary, including dependency and acyclicity checks,
- confirmation that each issue includes a validated `## Orchestrator Handoff`
  section,
- GitHub PRD parent issue and sub-issues attached, when applicable,
- where issues were published or that output stayed in chat,
- `local_mirror` result and `local_mirror_path`,
- issue types and labels/statuses assigned,
- completion instruction included,
- any blocked issues and why,
- `knowledge_delta`, `capture_outcome`, and the exact final issue ref that owns
  capture, or `capture_outcome=no-durable-change`,
- the `partial_output` result and whether any non-agent-ready partial issues
  were withheld or published as `needs-info` / `ready-for-human`,
- confirmation that `$plan-harder` was run once per issue, that each issue
  includes the standard plan-hardening provenance line, and that the hardening
  output was merged into the issue without duplicated sections.

## Evidence And Phase Metrics

Keep one PRD snapshot keyed by `source_prd_ref` and fingerprint. For each issue,
store its current body in the configured target or transient body file and
carry only the issue id/ref, body fingerprint, changed headings, hardening
status, and failed-gate excerpts into the next pass. Do not repeat unchanged
PRD or issue bodies between `$plan-harder`, repair, graph, and publication
steps. Re-open or emit a complete body only when its fingerprint changed, a
gate needs the relevant section, draft/chat output requires it, or final
publication/review needs it.

When run-scoped counters cover uncontaminated intervals, checkpoint and report
these independent deltas:

```text
phase=issue-split; tokens=<exact delta|unavailable>
phase=issue-hardening:<issue-id>; tokens=<exact delta|unavailable>
phase=issue-graph-and-publication; tokens=<exact delta|unavailable>
```

Also report the references actually loaded and final body fingerprints. Label
an interleaved cumulative delta `exact-interval` and do not attribute it to an
issue phase or hardening call. If exact counters are unavailable, record one
`tokens=unavailable` result for the issue phase; never estimate, reread session
archives, or block publication to obtain metrics.

## Issue Body Shape

Before composing or validating issue bodies, read
`references/issue-body-template.md`. Use that template unless the tracker has a
stronger local template. Keep `## Questions` out of `ready-for-agent` issues;
include it only when `partial_output=allow-non-agent-ready`.

## References

- `references/vertical-slices.md`: issue splitting rules.
- `references/issue-body-template.md`: generated implementation issue body
  template.
- `$project-memory`'s `references/tracker-publishing.md`: shared tracker
  publication and `source_prd_ref` contract.
