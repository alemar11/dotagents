---
name: plan-feature
description: Manually converge feature intent or a durable Feature Spec into a complete Feature Spec bundle with hardened agent-ready implementation issues.
---

# Plan Feature

## Purpose And Invocation

Use this planning-only skill to converge feature intent or a durable Feature
Spec into one complete, internally consistent bundle: the Feature Spec set,
hardened vertical implementation issues, tracker metadata, and relationships.
A Feature Spec is the durable parent contract for one bounded product or system
change. The configured tracker may be GitHub or local Markdown. Plan Feature
produces the same implementation-ready planning contract for either backend and
does not select the executor's publication or completion transport.

The public pipeline is:

`Project Memory routing -> source-route resolution -> optional Idea discovery and validation -> repo-backed clarification -> Feature Spec phase -> issue-graph convergence -> source reconciliation -> deferred domain-memory closeout`

Use it only when the user invokes `$plan-feature`, asks to run Plan Feature, or
a manually invoked parent workflow routes here. Do not auto-select it for an
ordinary planning, implementation, issue-splitting, or triage request. Never
implement the planned feature.

## Structured Option Contract

Load `references/options.md` before the first phase. It defines the complete
default-path run registry:

| Field | Values |
| --- | --- |
| `write_mode` | `apply`, `propose` |

Reject every unregistered field or value. Project Memory owns tracker routing
and repository topology; Plan Feature consumes those as facts. Paths, slugs,
refs, branches, dependencies, and domain handoffs are data.

Resolve `write_mode` once:

- `apply`: publish through the configured tracker.
- `propose`: perform no writes and return proposed bodies, target locations,
  metadata, and publication order. Do not return executable commands.

## Fixed Planning Contract

- Load `references/spec-phase.md` before Feature Spec work and
  `references/issue-phase.md` plus `references/vertical-slices.md` before issue
  work. Load each template only with its owning phase. Those references own
  branch-specific validation, publication, recovery, and reporting detail.
- Treat tracker routing, repository topology, issue types, workflow states, and
  their transports as Project Memory facts. Reject missing, stale,
  contradictory, or backend-incompatible facts instead of turning them into
  Plan Feature options.
- Keep one run bounded to one feature and derive one `source_route` from intake
  evidence. No durable Spec selects `new-source`; one canonical durable Spec
  selects `existing-source`; an exact recognized incomplete publication
  transaction resumes `new-source`. Ambiguous or foreign partial state blocks.
- Load `references/idea-discovery.md` only for an explicit discovery request
  without exact refs. Discovery is read-only until the user selects durable
  Ideas. Load `references/idea-source.md` only when selected or source-bound
  Ideas require validation or reconciliation. Ideas may seed new-source
  planning but never rewrite an existing Spec.
- A successful run always returns one complete bundle: every required Feature
  Spec, a nonempty hardened issue graph for every implementation-eligible Spec,
  tracker metadata, and relationships. Coordination-only parents are the only
  zero-issue Specs. Withhold every incomplete bundle.
- Treat Specs and issues as executor-ready briefs, not immutable technical
  scripts. Stable content is the outcome and Non-Goals, source/repository/path/
  branch scope, dependencies, acceptance text/count/order, safety constraints,
  and material validation policy. Checkbox markers, technical approach,
  equivalent tests, compatible clarifications, progress, and evidence remain
  executor-owned. Compare stable content directly; never fingerprint a body.
- Keep `tracker_backend` and `delivery_type` separate. Project Memory owns only
  tracker location. Every implementation-eligible Spec and issue carries the
  stable non-option delivery fact `github-pr` or `local-branch`; support GitHub
  tracker plus PR, local tracker plus local branch, and local tracker plus PR.
  Never infer PR delivery merely from a GitHub repository identity.
- Feature Spec and issue acceptance criteria are independent contracts. Before
  publication, require a transient complete, non-contradictory map from every
  Spec criterion to one or more final issues. Checkbox state never changes
  criterion identity and Plan Feature never edits executor-owned markers.
- Give every issue one seven-field `## Execution Contract` owned by
  `references/issue-body-template.md`. Keep intra-Spec ordering only in
  `dependency_ids`; keep cross-Spec ordering only in the Spec's mandatory
  `## Feature Dependencies` table.
- Before synthesis or mutation, enumerate durable state and retain
  contract-equivalent issues with their IDs. Create only missing artifacts,
  repair only supported missing metadata or parent attachment, return a
  verified no-op for a complete bundle, and block on duplicates, stale bodies,
  conflicting relationships, or races. Re-read authoritative state immediately
  before proposal, no-op, and mutation.
- In local Markdown mode, issue scope includes the tracker repository and both
  the exact active issue path and its derived `done/` path. In every backend,
  use portable refs and evidence and keep executor transport, task scheduling,
  checkout, review, publication, and merge authority out of planning artifacts.
- Each implementation-eligible Spec owns a unique
  `(affected_repository, target_branch_name)` pair. Multi-repository bundles
  assign every combined boundary to an existing repo-owned implementation Spec;
  its Feature Dependencies name the peer inputs whose exact revisions the proof
  requires. Ordinary workers collaborate directly, and no dedicated integration
  Spec or worker is generated. A monorepo normally uses one worker/worktree
  across its packages.
  `references/spec-phase.md` owns recoverable multi-repository publication.
- Carry accepted durable planning decisions only as optional
  `knowledge_delta` phase data. Never persist it in a Feature Spec; put it only
  on a final closeout issue whose repository and allowed paths
  contain every target. `references/issue-phase.md` owns terminal dependency
  derivation and continuation evidence.
- Compress the candidate graph before freezing new IDs or invoking
  `$plan-harder`. Issue count is observation, not a cap. Harden every missing
  final issue only after graph, scope, and ownership stabilize; retain matching
  durable issues and persist only the final hardening result.
- Prefer concise behavioral prose for decisions and failure policy; reserve
  tables for exact identity and scope. Criteria must be unique and individually
  provable. Constrained validation requires an explicit prose failure policy
  before `ready-for-agent`.

## Composed Skills

| Skill | Load when | Boundary |
| --- | --- | --- |
| `$project-memory` | Tracker routing, repository topology, or an explicitly required Idea marker mapping is missing, stale, or contradictory. | Use only `tracker-routing` or `project-layout`; a missing Idea mapping blocks only Idea capture, discovery, or consumption, and Plan Feature never performs domain closeout. |
| `$grill-me-with-context` | Repo-backed clarification is materially needed. | Always defer capture to the caller and consume its structured delta. |
| `$plan-harder` | For every missing final implementation issue after structural graph compression and durable-state reconciliation. | At least one issue-hardening call per missing issue, with only the final stable result persisted; contract-equivalent durable issues are validated and retained, and Plan Feature owns artifact writes. |
| `$gitstack:github-issues` | The owning tracker backend is GitHub and Idea or planning-bundle convergence needs exact reads, or `write_mode=apply` authorizes a tracker write. | Discovery, source validation, and convergence inspection are pure reads in either write mode and omit mutation fields; require complete all-state pagination through connector pagination or GitStack's read-only direct-`gh` gap fallback, never a fixed-limit listing, or block. For writes, translate each supported operation to `mutation_mode=apply`, the exact target, and one `issue_operation`; own safe transport, mapped metadata, parent/sub-issue attachment, verification, cleanup, and partial recovery. Proposal mode never requests dry-run mutations or returns executable commands. |

After implementation begins, generated implementation-issue lifecycle
mutations belong to the selected executor, not Plan Feature. Terminal
source-Idea reconciliation remains planning closeout and occurs before
implementation begins.

## Workflow

### 1. Resolve Setup, Write Mode, Source Route, And Identity

Read:

- `project-memory/config/issue-tracker.md`;
- `project-memory/config/project-layout.md`;
- `project-memory/config/triage-labels.md`;
- root `CONTEXT.md` first when it exists, treating the current Git repository
  as a selected root; in a coordination workspace, also select affected child
  roots from its `Repository Registry` and read each available child root
  context; then
  select every available scoped `CONTEXT.md` matched by affected paths in each
  selected root's `Scoped Contexts` table. Read every available matched context
  before drafting. For a root or matched route with no context, use repository
  evidence without inventing terminology or a dangling context pointer.

Run only the relevant Project Memory routing slice when setup is incomplete.
Do not bootstrap unrelated domain, localization, ADR, or agent-instruction
content.

Resolve `write_mode` from `references/options.md`, then resolve enough accepted
planning identity to locate the canonical Feature Spec target. Inspect any
supplied ref and that exact target before freezing the route. One canonical
final durable Spec derives `source_route=existing-source` only when it is not a
member of an exact recognized incomplete transaction. No durable Spec derives
`source_route=new-source`; an exact recognized multi-repository publication
transaction, including its staged or final members, derives a continuation of
that route. Multiple, conflicting, foreign, or ambiguous candidates block.
Proposed refs never select the existing-source route. Then finish resolving
`feature_slug`, affected repositories, allowed paths, one target branch shared
only within each implementation-eligible Feature Spec, and any
product/workspace identity from accepted input and repository evidence.
Resolve one stable `delivery_type` per implementation-eligible Spec without
adding an option or Project Memory setting. GitHub tracking resolves to its only
supported delivery, `github-pr`; local tracking requires accepted evidence for
`local-branch` or `github-pr`, and repository identity alone is never evidence
for PR delivery.
For a multi-repository workspace, derive workspace behavior from
`repository_layout`; do not ask for another workspace-mode option.

On the existing-source route, collect the union of exact `- Source Idea:` refs
from the stable intake Spec content and every required linked partial as
`bound_source_idea_refs`. Treat this as derived continuation evidence, never as
an option or permission to draft from an Idea again. When the invocation also
supplies `source_idea_refs`, require exact set equality with the bound set. An
additional, missing, different, proposed, or otherwise unbound ref blocks. No
bound refs means the existing-source route has no Idea lifecycle work.

Before ordinary Idea validation or discovery, inspect exact selected refs plus
the invocation or durable handoff for evidence that the complete requested
planning result already exists and only source reconciliation is incomplete.
When that evidence is present, load `references/idea-source.md` and run its
reconciliation-only recovery branch first. Do not enter ordinary source
validation, the Feature Spec or issue phases, reopen completed Ideas, or
republish planning artifacts. Stop after reporting the reconciled or still
missing operations.

Otherwise, when the existing-source route has `bound_source_idea_refs`, load
`references/idea-source.md` and run its immutable continuation validation. Read
the bound Ideas and prior outcomes only to verify their exact relationship to
the unchanged Spec set and to prepare lifecycle reconciliation after bundle
convergence; never normalize them into new requirements or draft from them.
On the new-source route, when the invocation supplies `source_idea_refs`, load
`references/idea-source.md`, run ordinary validation for every durable ref and
tracker owner, read all canonical Idea sections and prior outcomes, and require
explicit selection before combining multiple Ideas.

When the new-source route has no exact refs but the user explicitly asks to
discover captured Ideas, load `references/idea-discovery.md`. Resolve tracker owners before
listing, show only validated candidates with their state and prior outcomes,
and require explicit selection. The selected refs become `source_idea_refs`,
then continue through `references/idea-source.md`; if the user asked only to
inspect the backlog, report and stop without drafting or mutation. Never
discover Ideas implicitly.

Stop when selected Ideas do not describe one bounded feature. Do not route a
missing Idea marker through implicit Project Memory writes; return the exact
setup prerequisite unless the user separately authorized that setup.

If an accepted parent/global Feature Spec is needed, produce it first. Resolve
each affected child repository's tracker and topology facts independently and
link every repo-scoped partial. Do not generate combined implementation issues
until all required source refs and cross-links exist. Proposed refs remain
non-executable.

### 2. Clarify Only Material Unknowns

On the new-source route, run `$grill-me-with-context` only when supplied intent
plus repository evidence cannot support a complete Feature Spec and safe issue
graph. Resolve one blocking decision at a time.

For every selected Idea, normalize the seven canonical sections into transient
planning evidence and a per-element coverage map through
`references/idea-source.md`. Tentative directions remain tentative until
supported by repository evidence or explicit clarification. A blocked element
withholds the requested result; an intentionally deferred element may support
partial coverage only after at least one material element is durably covered.
With `write_mode=propose`, build the separate report-only intended projection;
never treat a proposed Spec as durable coverage.

Do not mutate an Idea merely because an interactive clarification is active.
Only a terminal run exit waiting for one specific requester answer may
reconcile that Idea to `needs-info` under `write_mode=apply`.

On the existing-source route, inspect open questions only to validate whether
the durable source's stable contract can be consumed unchanged. Accept
`knowledge_delta` only as
explicit accepted invocation data or an exact continuation handoff supplied
separately from the source; never infer it from or write it into the Feature
Spec. Require every target surface to resolve inside the unchanged source scope;
reject the delta instead of widening source or issue scope. A persisted delta or
`## Domain Knowledge Handoff` is incompatible input. If any answer or repair
would change the source, require a separately authorized Feature Spec update.
Keep `planning_blockers` separate and capture no durable knowledge in planning.

### 3. Run The Feature Spec Phase

Preserve current executor-owned checkbox markers and always run the canonical
source-contract validation from
`references/spec-phase.md`, including the exact Feature Dependencies heading
and columns. On the existing-source route, start from any intake member and
traverse its links to require the complete connected stable Spec set. Return
each current body and ref without drafting or publication; a coordination-only
parent owns no issues. If any source needs a change or the set is incomplete,
require a separately authorized update. On the new-source route, load
`references/spec-template.md`, then pass:

- `write_mode`, derived `source_route`, Project Memory facts, and stable
  `delivery_type` data;
- planning identity and repository scope;
- source-ref state and cross-Spec dependency rows;
- optional validated `source_idea_refs`, normalized Idea evidence, prior
  partial-outcome refs, transient durable coverage maps or report-only intended
  projections, and their per-Spec relevance mapping;
- optional `knowledge_delta` plus separate `planning_blockers`;
- optional exact multi-repository publication-continuation handoff with its
  reconstructable templates, slots, selected Idea/prior-outcome refs, and
  completed plus missing operations;

Require a durable local or hosted `source_spec_ref` for `write_mode=apply`, or
a deterministic proposed ref and publication-order note for
`write_mode=propose`. Never persist a delta marker in the Spec or silently
downgrade `write_mode`. Route new blockers back through clarification. Always
pass the optional delta directly to the issue phase without adding it to any
Feature Spec body.

### 4. Run The Issue Phase

Load `references/issue-phase.md`, `references/issue-body-template.md`, and
`references/vertical-slices.md`. Pass the same identity, facts, write mode,
source ref, optional knowledge delta, workspace links, and validated cross-Spec
graph, plus any exact continuation handoff.

The issue phase owns vertical splitting, structural graph compression, durable
discovery before synthesis, fixed-ID reuse, uncovered-scope synthesis, missing
artifact output, `$plan-harder` passes per missing final issue, race
revalidation, metadata, dependencies, the Execution Contract, and reporting.
Existing issues must match the stable graph and body contract; conflicts stop
the run, while a complete matching applied bundle returns a verified no-op.

If `knowledge_delta` is present in a single Spec, reuse or add a final
closeout issue, exclude it and its own `dependency_ids` while deriving the
remaining graph's no-dependent terminals, then make it depend directly on all
of them and reject any dependent of the owner. In a
multi-repository bundle, select an existing implementation partial whose scope
contains every knowledge target and whose dependencies cover the inputs needed
for final proof. Attach the delta only to that partial's final closeout issue.
Harden and validate the selected final issue like every other issue.

### 5. Reconcile Idea Sources

Skip this step when neither selected new-source `source_idea_refs` nor derived
existing-source `bound_source_idea_refs` are present. Otherwise load
`references/idea-source.md`. With `write_mode=apply` and a complete durable
result, determine cumulative `partial` or `full` coverage separately for every
selected or bound Idea from verified prior Specs plus that result. With
`write_mode=propose`, or
when another branch returned only a non-durable preview, leave the durable map
unchanged, leave every selected or bound Idea unchanged, and report only
`intended_coverage`, `intended_covered_scope`,
`intended_remaining_scope`, and intended transitions from the separate
projection.

With `write_mode=apply`, a terminal wait for one specific requester answer may
reconcile the affected Ideas to `needs-info` before a planning result exists.
Reconcile coverage only after every Feature Spec, implementation issue,
metadata mutation, and relationship in the complete applied bundle is durable
and verified. A
technical, validation, configuration, or partial publication failure normally
preserves each Idea's prior state. When the requester has answered a prior
`needs-info` blocker, prevent that stale state from surviving a later technical
failure by reconciling it to `needs-triage` at terminal exit.

Partial coverage writes the canonical cumulative planning-outcome block and
returns the Idea to `needs-triage`; full coverage writes the canonical
cumulative block, clears actionable states, and closes the GitHub Idea or marks
the local Idea consumed. Apply each decision independently and retry only
missing operations after partial source reconciliation. On resume, use the
reconciliation-only branch and treat a closed GitHub Idea or local full outcome
as already reconciled only when its complete canonical record exactly matches
the verified cumulative Spec set and coverage result.

### 6. Report Completion

Return:

- resolved `write_mode` and derived `source_route`;
- Feature Spec ref or proposed ref, title, and target location;
- planning identity and Project Memory facts used;
- retained, created, or proposed issue refs in publication order, repaired
  mapped metadata or parent/sub-issue attachment, and verified no-op state when
  applicable;
- graph and verticality validation, including candidate and final issue counts,
  compression repairs, retained-slice reasons, and avoided initial hardening
  calls;
- applied tracker metadata when writes occurred;
- discovered candidate refs when discovery ran, selected Idea refs, verified
  prior outcome refs, per-Idea cumulative durable `coverage`, `covered_scope`,
  and `remaining_scope`, or the distinct `intended_coverage`,
  `intended_covered_scope`, and `intended_remaining_scope`; plus applied or
  proposed lifecycle transitions and any missing reconciliation operations;
- domain closeout owner when present and the derived `capture_outcome`;
- exact continuation handoff when publication is incomplete, including every
  created or staged Spec ref, any applicable multi-repository
  publication-transaction identity and its complete predeclared body templates,
  selected Idea and prior-outcome refs, completed and missing operations, and
  the complete `knowledge_delta` until its final owner issue is durable and
  verified;
- blockers and withheld artifacts;

When `knowledge_delta` is present, report `capture_outcome=deferred` plus its
actual or proposed final issue ref. Otherwise report
`capture_outcome=no-durable-change`. This result is report-only and never
persisted in the Feature Spec. Plan Feature never reports domain knowledge as
captured.

## References

- `references/options.md`: the complete default-path selectable run registry.
- `references/idea-discovery.md`: explicitly requested read-only backlog
  discovery and selection before durable Idea-source intake.
- `references/idea-source.md`: selected durable Idea validation, intent
  normalization, cumulative coverage, Feature Spec projection, outcome records,
  and terminal lifecycle reconciliation.
- `references/spec-phase.md`: Feature Spec drafting, routing, and publication.
- `references/spec-template.md`: default Feature Spec shape.
- `references/issue-phase.md`: issue splitting, hardening, graph validation,
  and publication.
- `references/issue-body-template.md`: generated issue shape and single
  Execution Contract.
- `references/vertical-slices.md`: slicing and readiness gates.
- `references/complete-bundle-proposal.md`: non-mutating complete-bundle
  `write_mode=propose` fixture.
