# Issue Phase

Use this reference when `plan-feature` needs to turn a Feature Spec into vertical
implementation issues that can be assigned to agents or humans. This is an
internal phase, not a public skill.

## Goal

Split a Feature Spec into vertical, agent-ready implementation issues. Every generated
issue must be hardened with `$plan-harder` before it is returned or published.

## Hard Requirements

- Use `references/options.md` as the sole owner of option values, sources,
  evidence projection, and valid cross-field tuples. Render each issue with
  `references/issue-body-template.md`; use `references/vertical-slices.md` for
  slicing, readiness, and the blocking verticality gate.
- Run `$plan-harder` once for every issue with
  `planning_mode=issue-hardening` and `output_surface=caller`. This phase owns
  body merging and writes; `$plan-harder` returns only its structured result.
- Every generated issue includes `## Completion` and the canonical
  `## Orchestrator Handoff`; the handoff restates validated issue data without
  granting worker authorization.
- Treat the final hardened issue bodies as the execution graph. Validate IDs,
  direct edges, acyclicity, startability, and integration proof; never persist a
  separate scheduling artifact.
- A required domain delta has exactly one final integration owner, never a
  docs-only task, and requires `$project-memory` with
  `memory_slice=domain-memory` and
  `domain_operation=implementation-closeout`.
- Treat `tracker_backend` as planning-artifact write authority only through the
  resolved `effective_target`; use `$project-memory`'s
  `references/tracker-publishing.md` for publication and stable
  `source_spec_ref` mechanics.
- Withhold unresolved work by default. Only
  `partial_output=allow-non-agent-ready` permits a visible `needs-info` or
  `ready-for-human` issue; it never permits a `ready-for-agent` claim.
- Do not add worker authorization defaults, worker capability modes, worker
  surfaces or counts, checkpoint approval, publication permission, runtime
  mutation overrides, or other orchestration session settings to planning
  artifacts. Preserve source-contract `issue_update_permission` and its
  evidence as delivery metadata, not worker permission.

## Boundaries

- Do not implement the issues.
- This phase never rewrites the Feature Spec. A requested Feature Spec update runs through the
  Feature Spec phase before issue splitting and supplies a new verified handoff.
- Do not create horizontal layer tickets such as "backend only", "frontend
  only", or "tests only" when a vertical slice is practical.
- Do not ask for separate issue write/publish confirmation after `plan-feature`
  has resolved setup, planning identity, blockers, and effective target. Ask
  only when the canonical target snapshot is missing, ambiguous, or
  internally contradictory.

## Phase Handoff Inputs

Receive the verified run-level `option_resolution` rows and
`option_rows_fingerprint` defined by `references/options.md`, plus:

- the planning identity (`feature_slug` and any selected `product_slug`,
  `workspace_path`, `context_file`, `project_slug`, `repository_layout`,
  `child_repository_layout`, `workspace_context`, `workspace_parent_source_ref`,
  `workspace_feature_repos`, and issue target repos);
- the resolved `source_spec_ref` and draft fingerprint when applicable;
- `workspace_child_source_refs`, mapping each feature-wide repo to its
  repo-scoped partial Feature Spec ref when
  `workspace_context=multi-repository-workspace`. Keys are canonical repo slugs and
  must match `workspace_feature_repos`; each generated issue's target repos
  must be a non-empty subset of `workspace_feature_repos`;
- `capture_outcome` and the structured `domain_knowledge_delta`;
- the mapped tracker/type configuration needed at publication.

Verify the incoming run-row `option_rows_fingerprint` before splitting. Every
issue adds exactly one row per Per-Issue Registry field plus its effective
`target_branch_name` data row. After the issue graph and every `issue:<NN>` row are final, recompute the
fingerprint over the complete run-plus-issue row set and carry that value in the
phase publication handoff and completion output, not in individual issue
bodies.

Validate `capture_outcome=deferred` when
`domain_knowledge_delta.knowledge_delta=required` and
`capture_outcome=no-durable-change` when `knowledge_delta=none`. Preserve a
non-empty `unresolved` list independently as planning blockers. For
`mode=issues-from-existing-spec`, reconstruct the pair from the Feature Spec's canonical
Domain Knowledge Handoff when the explicit phase handoff is unavailable; an
existing canonical Feature Spec with a handoff resolves to `required` plus
`deferred`, while no handoff resolves to `none` plus `no-durable-change`. Never invent
`capture_outcome=captured` in Plan Feature.

## Structured Issue Values

Create the complete Per-Issue Registry row set from `references/options.md`
after the graph exists and before output. An authorized issue-level override
atomically resolves the complete delivery tuple; never retain incompatible
feature-level values or derive authority from prose. Keep IDs, reasons,
evidence, refs, branches, and domain-closeout payloads as data outside enum
values.

Render the validated rows through `references/issue-body-template.md`.
`issue_type` and `workflow_state` stay canonical in issue bodies;
`project-memory/config/triage-labels.md` maps them only at the GitHub boundary.
Reject retired planning aliases before splitting; do not normalize them in the
issue phase.

## Workflow

### 1. Load Inputs

Find or ask for the Feature Spec source:

- `planning/features/<feature-slug>/SPEC.md`,
- a GitHub Feature Spec issue,
- `orchestration/<project-slug>/features/<feature-slug>/SPEC.md`,
- a linked GitHub workspace Feature Spec issue,
- a handoff `source_spec_ref` from the Feature Spec phase or an existing durable Feature Spec
  source,
- pasted Feature Spec text,
- another project document that clearly acts as the Feature Spec.

Also inspect:

- `project-memory/config/issue-tracker.md`,
- `project-memory/config/project-layout.md`,
- `project-memory/config/triage-labels.md`,
- `CONTEXT.md` or `CONTEXT-MAP.md`,
- `TRANSLATION.md`, when present for the selected context,
- `project-memory/adr/`,
- orchestrator workspace docs such as `orchestration/<project>/PROJECT.md`,
  `orchestration/<project>/repos/*.md`, and feature `integration-gates.md` when
  planning from a local orchestrator workspace,
- nearby source files, tests, and docs relevant to the Feature Spec.

Load `domain_knowledge_delta` from the Plan Feature handoff. For
`issues-from-existing-spec`, reconstruct it from `## Domain Knowledge Handoff`
when that section exists. Treat an unresolved item that changes implementation
scope as a blocker; do not silently move product questions into the final task.

If there is no Feature Spec-quality source, stop and ask the user to provide one or run
the Feature Spec phase first.

For `lean-issues`, read the durable Feature Spec once, then inspect only tracker/type
mappings and source/tests directly needed to validate its candidate slices.
Keep the profile only when one repo/context is unambiguous, no more than two
vertical issues are expected, and no cross-repo gate, enabling slice, unresolved
blocker, or separate domain-closeout owner appears. Otherwise widen to
`standard`, load the broader context above, and record the first failed lean
condition. The lean profile does not weaken any hardening or output gate.

Resolve and carry the planning identity before splitting:

- `feature_slug`: explicit handoff value first, then the Feature Spec directory slug,
  then title-derived fallback only when no accepted path exists.
- For multi-context repos or monorepos: `product_slug`, `workspace_path`, and
  `context_file`.
- `repository_layout`: use the Feature Spec handoff value first, then
  `project-memory/config/project-layout.md`, then safe repo evidence.
  For a workspace issue graph spanning multiple child partials, the handoff
  must use `repository_layout=multi-repository-workspace` as the workspace graph
  snapshot; do not choose one child repo's durable topology as the run-level
  value. Record child repo topology only in each issue's
  `issue_repository_layout` row.
- `workspace_context`: use the Feature Spec handoff value first; when absent,
  derive `multi-repository-workspace` from `repository_layout=multi-repository-workspace`,
  linked repo-scoped partial Feature Spec siblings, or parent/global source
  evidence; otherwise default to `not-applicable`.
- `workspace_parent_source_ref`: use the Feature Spec handoff value first;
  default to `not-applicable` when absent.
- For `repository_layout=multi-repository-workspace` or
  `workspace_context=multi-repository-workspace`: `project_slug` or
  `workspace_parent_source_ref`, plus affected repos, are required.
- `source_spec_ref`: use the durable Feature Spec issue number, local Feature Spec path, or stable
  draft ref passed by the Feature Spec phase or existing durable Feature Spec source. In
  either non-mutating effective target, keep the draft ref in returned bodies.
- For workspace issues with one target repo, select `source_spec_ref` from
  `workspace_child_source_refs` using that issue's target repo. For root-owned
  integration or domain-closeout issues spanning multiple repos, use
  `workspace_parent_source_ref` when it is not `not-applicable`. When no
  parent/global source exists, do not create a root-owned spanning issue:
  split the work into repo-scoped integration or domain-closeout issues using
  their child partial refs, or stop for an explicit workspace-level source and
  owner. Never choose an individual child partial as the primary source for
  spanning work.
  For `draft-publish-commands`, include the replacement step required before
  hosted mutation; for `local-dry-run`, label it non-executable.

Receive the complete verified feature delivery tuple and `target_branch_name` data
from the Feature Spec handoff. Do not infer, default, or reinterpret those fields here.
When a Feature Spec lacks canonical rows or contains retired vocabulary, stop
before splitting. Consume it only after the active artifact is canonical and a
stale-vocabulary scan is clean.
Missing, contradictory, or unauthorized rows block splitting.

If a multi-context local Markdown repo lacks an accepted product/context or the
feature slug can collide with another product according to tracker conventions,
stop and resolve that identity before writing issues.

Review Feature Spec open questions before splitting. If any open question affects scope,
acceptance criteria, dependencies, validation, publication target, permissions,
data contracts, or cross-repo contracts, treat it as a blocker instead of
creating `ready-for-agent` issues.

### 2. Split Into Vertical Issues

Use `references/vertical-slices.md` to create a proposed issue list. Apply
vertical slicing whenever practical. Order issues for sequential agentic
implementation, and make dependencies explicit rather than relying on issue
numbering.

Before hardening, validate the generated issue graph from the proposed issue
list, carrying the verified feature delivery tuple, including
the issue-effective `issue_repository_layout`, into each issue:

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
- issue-level topology: use the repo-scoped Feature Spec or target repo
  `child_repository_layout`; for root-owned issues spanning multiple repos, use
  `multi-repository-workspace` when `workspace_context=multi-repository-workspace`; fall
  back to the run-level value only when the issue is neither repo-scoped nor
  workspace-spanning.
- generated issue bodies keep `repository_layout` equal to the source Feature
  Spec's feature/workspace graph value and emit `issue_repository_layout` as the
  issue-effective workstream topology used by Orchestrator.
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
- include enough context to be implemented without rereading the whole Feature Spec,
- include product/workspace/context scope for monorepo work, or affected repos
  and integration gates for orchestrator work,
- include a durable `source_spec_ref` pointer, copied feature-level
  `change_delivery_target`, `pull_request_count_strategy`, issue-level parallelization, dependencies,
  closeout, and any delivery or integration exception,
- include a `## Orchestrator Handoff` section that restates the dispatchable
  source Feature Spec, feature slug, `change_delivery_target`,
  `change_delivery_permission`, `change_delivery_permission_evidence`,
  `codex_review_requirement`,
  `pull_request_count_strategy`, affected repos or product scope, scope, start
  rule, dependencies, validation, and closeout,
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
  landed rather than copying the Feature Spec blindly,
- include `git diff --check` or the repository's equivalent documentation diff
  check,
- record one completion proof covering both integration and durable capture.

### 3. Harden Every Issue With `$plan-harder`

For each issue, call `$plan-harder` with `planning_mode=issue-hardening` using
only that issue's draft body and the minimum relevant Feature Spec context. Explicitly
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
from the Feature Spec, repo evidence, or project memory, stop and return the blocker
instead of publishing an agent-ready issue.

### 4. Run The Verticality Gate

Run the blocking gate in `references/vertical-slices.md` against every final
hardened body before metadata assignment or output. Apply its repair and
withholding rules. Re-run `$plan-harder` for every materially changed issue,
then revalidate IDs, direct edges, acyclicity, startability, handoff consistency,
and cross-repo or domain-closeout proof.

Do not emit `ready-for-agent` until all remaining issues pass. Before output,
also verify portable evidence, absence of runtime worker settings, consistent
handoff/delivery/validation/completion/dependency sections, sufficient local
rationale, and no duplicated sections introduced by hardening. Repair or
withhold failures.

### 5. Apply Issue Type And Triage State

Read `project-memory/config/triage-labels.md` and map canonical issue types
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
- Use `ready-for-human` when the Feature Spec requires human judgment before an agent can
  proceed.

Canonical values are decision inputs, not necessarily tracker values. Before
writing an issue file or calling `$gitstack:github-issues`, resolve the mapped tracker
value from `project-memory/config/triage-labels.md`. In default GitHub mode,
`ready-for-agent` maps to the same lowercase label. In custom tracker setups,
do not assume the canonical string is the label; read the mapping first.

### 6. Publish Or Return Issues

Use `project-memory/config/issue-tracker.md` for the target, and read
`$project-memory`'s `references/tracker-publishing.md` for shared
effective-target, temporary body-file, and `source_spec_ref` rules:

- `tracker_backend=github`: with `effective_target=configured-tracker`, create
  issues through `$gitstack:github-issues`, attach them
  to the Feature Spec parent when the Feature Spec source is a GitHub issue, set the mapped
  `task` issue type when available, then apply mapped labels such as
  `ready-for-agent` for `ready-for-agent`. Do not create a repo-local
  `planning/tmp/` mirror unless `local_mirror=requested`; when requested, write
  issue mirrors under `local_mirror_path`. Pass sanitized
  issue titles, bodies, target repo, labels, types, and parent/sub-issue intent
  to `$gitstack:github-issues`; do not assemble direct mutating `gh issue create` shell
  commands with generated Markdown in this phase.
- GitHub workspace issues: create linked repo or partial issues through
  `$gitstack:github-issues`, using Feature Spec parent/sub-issue relationships where available.
  Derive `<project-slug>` and affected repos from the Feature Spec/project context or ask
  for them. Repo-local implementation PRs or child issues link back to the
  relevant Feature Spec or partial issue. Do not create local orchestrator feature
  artifacts or `planning/tmp/` mirrors unless `local_mirror=requested`; write any
  requested mirrors under `local_mirror_path`.
- `tracker_backend=local`: with `effective_target=configured-tracker`, write to the configured repo-local issue
  path, normally `planning/features/<feature-slug>/issues/<NN>-<slug>.md`, with
  `issue_type:`, `workflow_state:`, and `source_spec_ref:` lines near the top and
  a heading that follows the local issue title convention
  `<feature-slug>: <NN> <vertical outcome>`. Use the
  authoritative feature slug from the handoff or Feature Spec path; derive it from the
  Feature Spec title only when no accepted slug/path exists.
- Local workspace issues: write to
  `orchestration/<project-slug>/features/<feature-slug>/issues/<NN>-<slug>.md` with
  `issue_type:`, `workflow_state:`, and `source_spec_ref:` lines near the top and
  a heading that follows the local issue title convention
  `<feature-slug>: <NN> <vertical outcome>`. Create the
  project/feature directories only when writing the actual feature artifacts,
  not during setup. The issue phase owns the issue files and reads
  `PROJECT.md`, `repos/*.md`, and `integration-gates.md`; it never creates or
  refreshes those supporting files. A broader artifact update belongs to the
  Feature Spec phase and must finish before the issue-phase handoff.
For GitHub Feature Specs, every generated implementation or vertical feature issue must
be attached to the Feature Spec issue as a sub-issue when the tracker supports it. If an
issue is created before the parent relationship is set, use `$gitstack:github-issues` to
attach it afterward. Keep `source_spec_ref: #<spec-number>` in the issue body as well.
For multi-repo work, related partial Feature Specs and repo issues must link to each
other by URL or issue number.

When GitHub issue types are available, create or update each implementation
issue with the mapped `task` type, usually `Task`. If issue types are disabled
or unsupported, publish without a type and keep the mapped state labels.

For orchestrator workspace issues, include `repository_layout`,
`issue_repository_layout`, `workspace_context=multi-repository-workspace`,
`workspace_parent_source_ref` when a parent/global source exists, affected
repos, cross-repo contract notes, integration gates by name or link, repo-local
PR or implementation issue links when they exist, expected repo PR slots or
pre-implementation placeholders, and the proof required before the issue can
move to `done` or close. Placeholders
are delivery expectations for scheduling, not completion proof;
`$codex-orchestrator` records real PR links or equivalent integration proof
during source closeout.

Every generated agent-ready implementation issue must include the
`## Orchestrator Handoff` shape from `references/issue-body-template.md`. The
handoff may repeat structured data from `## Delivery`, `## Validation`,
`## Completion`, and `## Dependencies` so an orchestrator can register the issue
without inferring from loose prose. It must not contain worker authorization,
publication authority, runtime issue-mutation overrides, or orchestration
session settings. It must carry the independently resolved source-contract
`issue_update_permission` and evidence required by the delivery tuple; those
fields do not authorize a worker.

When a final domain owner exists, publish or write it last, attach it to the
same Feature Spec parent, and keep its dependency metadata in the generated feature-ID
space (`01`, `02`, ...), including after hosted issue numbers or local paths
exist. Track those published or local refs separately. In draft command mode,
preserve the same last-task ordering and replacement rules.

Every published or returned issue renders the complete validated Per-Issue
Registry row set through `references/issue-body-template.md`. This is the sole
cross-session scheduling projection and carries its independently verifiable
`issue_option_rows_fingerprint`; do not duplicate the full Feature Spec branch and PR
narrative. Keep generated dependency IDs and domain payloads as data, and apply
the exact direct-commit evidence transfer and independent mutation-owner rules
from `references/options.md`. Missing, conflicting, or unauthorized rows block
publication.

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

Render `## Delivery` only through `references/issue-body-template.md` from the
complete verified Per-Issue Registry rows. Do not hardcode another default
delivery tuple in this phase.

Every published or returned issue must state its completion path:

- GitHub: close the implementation issue from the relevant PR body with a
  closing keyword, following `issue_completion_method`. Final-commit closure requires
  `issue_completion_method=final-commit-closing-keyword`,
  `issue_update_permission=direct-issue-updates-explicitly-authorized`, and its exact scoped
  authorization evidence. Do not add the parent Feature Spec closing keyword from an individual child
  issue. For a whole Feature Spec final feature
  or integration PR, the root delivery orchestrator adds that parent keyword
  only after its resolved review policy and all Feature Spec closeout gates pass.
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
  `plan-feature`, Feature Spec path, or configured tracker target. Derive it from the
  Feature Spec title without the `Feature Spec:` prefix only as a fallback.
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
target, generated issue bodies may use `source_spec_ref: draft-spec:<...>` only
in returned output. For `draft-publish-commands`, the publish plan must create
the Feature Spec first, capture the hosted Feature Spec number, replace the draft ref with
`source_spec_ref: #<number>`, and then create or attach implementation issues.
For `local-dry-run`, return the Feature Spec body fingerprint and label the ref
non-executable.
When a blocker or unresolved question appears under `plan-feature`, return it
as an issue-splitting blocker instead of publishing a `needs-info` issue by
default. When `partial_output=allow-non-agent-ready`, the phase may return or
publish the affected issue as `needs-info` or `ready-for-human` after target
resolution, with the blocker visible and no agent-ready claim.

### 7. Report Completion

Summarize:

- source Feature Spec,
- canonical keyed run/issue option rows and option-resolution evidence, including any
  execution-profile widening reason,
- `option_rows_fingerprint` for the complete run-plus-issue row set,
- authoritative `feature_slug`,
- product/workspace/context, project topology, or orchestrator project identity used, when
  applicable,
- number of issues produced,
- verticality gate result, including any repairs, merges, splits,
  enabling-slice exceptions, or withheld anomalies,
- issue graph validation summary, including dependency and acyclicity checks,
- confirmation that each issue includes a validated `## Orchestrator Handoff`
  section,
- GitHub Feature Spec parent issue and sub-issues attached, when applicable,
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

Keep one Feature Spec snapshot keyed by `source_spec_ref` and fingerprint. For each issue,
store its current body in the configured target or transient body file and
carry only the issue id/ref, body fingerprint, changed headings, hardening
status, and failed-gate excerpts into the next pass. Do not repeat unchanged
Feature Spec or issue bodies between `$plan-harder`, repair, graph, and publication
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
  publication and `source_spec_ref` contract.
