---
name: plan-feature
description: Manually converge feature intent or a durable Feature Spec into a complete Feature Spec bundle with hardened agent-ready implementation issues.
---

# Plan Feature Spec

## Purpose And Invocation

Use this planning-only skill to converge feature intent or a durable Feature
Spec into one complete, internally consistent bundle: the Feature Spec set,
hardened vertical implementation issues, tracker metadata, and relationships.
A Feature Spec is the durable parent contract for one bounded product or system
change. GitHub Issues are the authoritative tracker and pull requests are the
fixed delivery boundary; Plan Feature does not select executor publication or
completion behavior.

The public pipeline is:

`Project context routing -> source-route resolution -> optional Idea discovery and validation -> repo-backed clarification -> Feature Spec phase -> issue-graph convergence -> source reconciliation -> deferred domain-memory closeout`

Use it only when the user invokes `$plan-feature`, asks to run Plan Feature, or
a manually invoked parent workflow routes here. Do not auto-select it for an
ordinary planning, implementation, issue-splitting, or triage request. Never
implement the planned feature.

## Structured Option Contract

Load `references/options.md` before the first phase. It defines the complete
default-path run registry:

| Field | Values |
| --- | --- |
| `planning_mode` | `preview`, `publish` |

Reject every unregistered field or value. Plan Feature resolves each GitHub
target from the current Git remote; `github-workflow-contract` owns feature
issue types, workflow states, and their transports. Explicit intake or a
validated linked Feature Spec Set owns the affected repository identities.
Paths, local-root candidates, slugs, refs, branches, dependencies, and domain
handoffs are data.

Resolve `planning_mode` once:

- `publish`: publish through GitHub.
- `preview`: perform no writes and return proposed bodies, target locations,
  metadata, and publication order. Do not return executable commands.

## Fixed Planning Contract

- Load `references/publication.md` before the first phase. Load
  `references/spec-phase.md` before Feature Spec work and
  `references/issue-phase.md` plus `references/vertical-slices.md` before issue
  work. Load each template only with its owning phase. Those references own
  branch-specific validation, publication, recovery, and reporting detail.
- Load `references/scope-repair.md` only when a separately invoked Plan Feature
  task receives its exact structured request. Scope repair remains an internal
  branch of `existing-source`, never a selectable option or a third source
  route.
- Treat the current Git remote and affected repository identities as explicit
  Plan Feature facts. Treat feature issue types, workflow states, and their
  transports as `github-workflow-contract` facts. Reject missing, stale,
  contradictory, or GitHub-incompatible facts instead of turning them into
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
  tracker metadata, and relationships. Every linked multi-repository Spec is
  implementation-eligible; no additional top-level Spec exists. Withhold every
  incomplete bundle.
- Treat Specs and issues as executor-ready briefs, not immutable technical
  scripts. Stable content is the outcome and Non-Goals, source/repository/path/
  branch scope, dependencies, acceptance text/count/order, safety constraints,
  and material validation policy. Checkbox markers, technical approach,
  equivalent tests, compatible clarifications, progress, and evidence remain
  executor-owned. Compare stable content directly; never fingerprint a body.
- The sole stable-source mutation exception is `scope-repair.md`: a separately
  invoked Plan Feature task may add only the smallest evidence-backed monotonic
  `allowed_paths` envelope to the owning Spec and named issue. It preserves
  every other stable field and executor-owned update, records an audit, and
  never consumes or persists Codex runtime identity.
- GitHub Issues and pull-request delivery are fixed workflow boundaries. Do not
  persist provider or delivery selectors in Project Context, Feature Specs, or
  issue contracts.
- Feature Spec and issue acceptance criteria are independent contracts. Before
  publication, require a transient complete, non-contradictory map from every
  Spec criterion to one or more final issues. Checkbox state never changes
  criterion identity and Plan Feature never edits executor-owned markers.
- Give every issue one six-field `## Execution Contract` owned by
  `references/issue-body-template.md`. Keep intra-Spec ordering only in
  `dependency_ids`; keep cross-Spec ordering only in the Spec's mandatory
  `## Feature Dependencies` table.
- Before synthesis or mutation, enumerate durable state and retain
  contract-equivalent issues with their IDs. Create only missing artifacts,
  repair only supported missing metadata or parent attachment, return a
  verified no-op for a complete bundle, and block on duplicates, stale bodies,
  conflicting relationships, or races. Re-read authoritative state immediately
  before preview output, no-op, and mutation.
- Use portable refs and evidence and keep executor transport, task scheduling,
  checkout, review, publication, and merge authority out of planning artifacts.
- Each implementation-eligible Spec owns a unique
  `(affected_repository, target_branch_name)` pair. Multi-repository features
  assign every combined boundary to an existing repo-owned implementation Spec;
  its Feature Dependencies name the peer inputs whose exact revisions the proof
  requires. Ordinary workers collaborate directly, and no dedicated integration
  Spec or worker is generated. A monorepo normally uses one worker/worktree
  across its packages.
  `references/spec-phase.md` owns recoverable multi-repository publication.
- Carry accepted durable planning decisions only as optional
  `knowledge_delta` phase data. Never persist it in a Feature Spec; put it only
  on repository-owned final closeout issues whose repository and allowed paths
  contain their exact target shards. One explicitly named canonical target owns
  each cross-repository decision; other repositories may carry qualified
  backlinks, never duplicate canonical records. `references/issue-phase.md`
  owns sharding, terminal dependency derivation, and continuation evidence.
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
| `$project-context` | Context or ADR routing is missing, stale, or contradictory, or an explicit context closeout is carried by the implementation handoff. | Use only context-related slices; Project Context never supplies GitHub routing or publication behavior. |
| `$github-workflow-contract` | Feature Spec or implementation-issue metadata must be read, validated, proposed, or mutated. | Load the exact feature metadata values and transports; Plan Feature owns when they are published, and never edits the contract at runtime. |
| `$grill-me-with-context` | Repo-backed clarification is materially needed. | Always defer capture to the caller and consume its structured delta. |
| `$plan-harder` | For every missing final implementation issue after structural graph compression and durable-state reconciliation. | At least one issue-hardening call per missing issue, with only the final stable result persisted; contract-equivalent durable issues are validated and retained, and Plan Feature owns artifact writes. |
| `$gitstack:github-issues` | Idea or planning-bundle convergence needs exact reads, or `planning_mode=publish` authorizes a tracker write. | Discovery, source validation, and convergence inspection are pure reads in either planning mode and omit mutation fields; require complete all-state pagination through connector pagination or GitStack's read-only direct-`gh` gap fallback, never a fixed-limit listing, or block. For writes, translate each supported operation to `mutation_mode=apply`, the exact target, and one `issue_operation`; own safe transport, contract metadata, parent/sub-issue attachment, verification, cleanup, and partial recovery. Preview mode never requests dry-run mutations or returns executable commands. |

After implementation begins, generated implementation-issue lifecycle
mutations belong to the selected executor, not Plan Feature. Terminal
source-Idea reconciliation remains planning closeout and occurs before
implementation begins.

## Workflow

### 1. Resolve Setup, Planning Mode, Source Route, And Identity

Read:

- the current repository's GitHub remote, resolved to one exact
  `owner/repository` target;
- `github-workflow-contract` and its `references/github-labels.md`;
- root `CONTEXT.md` first when it exists, treating the current Git repository
  as a selected root; for cross-repository work, use explicit user scope or a
  durable linked Feature Spec Set to authorize repository identities, require
  candidate local Git roots separately, verify each root against one authorized
  identity, and read each available verified repository root context; then
  select every available scoped `CONTEXT.md` matched by affected paths in each
  selected root's `Scoped Contexts` table. Read every available matched context
  before drafting. For a root or matched route with no context, use repository
  evidence without inventing terminology or a dangling context pointer.

Use Project Context only for context-related setup or closeout. Do not use it to
resolve GitHub routing, and do not bootstrap unrelated domain, localization,
ADR, or agent-instruction content.

Resolve `planning_mode` from `references/options.md`, then resolve enough accepted
planning identity to locate the canonical Feature Spec target. Inspect any
supplied ref and that exact target before freezing the route. One canonical
final durable Spec derives `source_route=existing-source` only when it is not a
member of an exact recognized incomplete transaction. No durable Spec derives
`source_route=new-source`; an exact recognized multi-repository publication
transaction, including its staged or final members, derives a continuation of
that route. Multiple, conflicting, foreign, or ambiguous candidates block.
Proposed refs never select the existing-source route. Then finish resolving
`feature_slug`, affected repositories, allowed paths, one target branch shared
only within each implementation-eligible Feature Spec, and any planning-scope
identity from accepted input and repository evidence. For multi-repository
work, generate or preserve one canonical lowercase UUID `feature_id` shared by
every linked Spec.
When intake includes `scope_repair_request`, require one durable
`source_spec_ref` and implementation issue ref, derive ordinary
`source_route=existing-source`, load `references/scope-repair.md`, and reject
proposed sources or runtime coordination fields. Do not add a Plan Feature
option for the repair.
GitHub Issues and pull-request delivery are fixed; no delivery choice is
resolved or persisted.
The affected repository set is explicit feature data. Never infer it from the
current Codex task, the ChatGPT App primary project or saved-project list, or
filesystem proximity.

On the existing-source route, collect the union of exact `- Source Idea:` refs
from the stable intake Spec content and every required linked member as
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

Stop when selected Ideas do not describe one bounded feature. Do not repair a
missing Idea marker through implicit context writes; return the exact
companion-contract prerequisite unless the user separately authorized that
repair.

Resolve each affected Git repository's tracker facts independently and produce
one repo-owned implementation-eligible Feature Spec per repository. Never
synthesize another Spec above that linked set. Do not generate implementation issues until
all required source refs and identical `Feature Spec Set` tables exist.
Proposed refs remain non-executable.

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
With `planning_mode=preview`, build the separate report-only intended projection;
never treat a proposed Spec as durable coverage.

Do not mutate an Idea merely because an interactive clarification is active.
Only a terminal run exit waiting for one specific requester answer may
reconcile that Idea to `needs-info` under `planning_mode=publish`.

On the existing-source route without `scope_repair_request`, inspect open
questions only to validate whether the durable source's stable contract can be
consumed unchanged. Accept
`knowledge_delta` only as
explicit accepted invocation data or an exact continuation handoff supplied
separately from the source; never infer it from or write it into the Feature
Spec. Require every target surface to resolve inside the unchanged source scope;
reject the delta instead of widening source or issue scope. A persisted delta or
`## Domain Knowledge Handoff` is incompatible input. If any answer or repair
would change the source, require a separately authorized Feature Spec update.
Keep `planning_blockers` separate and capture no durable knowledge in planning.
With `scope_repair_request`, skip clarification and use only the existing
contract and supplied portable evidence through `scope-repair.md`. A required
decision beyond a monotonic path expansion returns `full-replan-required`.

### 3. Run The Feature Spec Phase

Preserve current executor-owned checkbox markers and always run the canonical
source-contract validation from
`references/spec-phase.md`, including the exact Feature Dependencies heading
and columns. On the existing-source route, start from any intake member and
traverse its `Feature Spec Set` to require the complete connected stable Spec
set. Without `scope_repair_request`, return each current body and ref without
drafting or publication. If any source needs a change or the set is incomplete,
require a separately authorized update. On the new-source route, load
`references/spec-template.md`, then pass:

- `planning_mode`, derived `source_route`, and project-context facts;
- planning identity and repository scope;
- source-ref state and cross-Spec dependency rows;
- optional validated `source_idea_refs`, normalized Idea evidence, prior
  partial-outcome refs, transient durable coverage maps or report-only intended
  projections, and their per-Spec relevance mapping;
- optional `knowledge_delta` plus separate `planning_blockers`;
- optional exact multi-repository publication-continuation handoff with its
  reconstructable templates, slots, selected Idea/prior-outcome refs, and
  completed plus missing operations;

Require a durable hosted `source_spec_ref` for `planning_mode=publish`, or
a deterministic proposed ref and publication-order note for
`planning_mode=preview`. Never persist a delta marker in the Spec or silently
downgrade `planning_mode`. Route new blockers back through clarification. Always
pass the optional delta directly to the issue phase without adding it to any
Feature Spec body.

For `scope_repair_request`, do not enter ordinary drafting or publication.
Pass the fresh complete bodies and exact request to `scope-repair.md`, which
owns the only permitted Feature Spec path mutation, audit, recovery, and result.

### 4. Run The Issue Phase

Load `references/issue-phase.md`, `references/issue-body-template.md`, and
`references/vertical-slices.md`. Pass the same identity, facts, planning mode,
source ref, optional knowledge delta, linked-set data, and validated cross-Spec
graph, plus any exact continuation handoff.

The issue phase owns vertical splitting, structural graph compression, durable
discovery before synthesis, fixed-ID reuse, uncovered-scope synthesis, missing
artifact output, `$plan-harder` passes per missing final issue, race
revalidation, metadata, dependencies, the Execution Contract, and reporting.
Existing issues must match the stable graph and body contract; conflicts stop
the run, while a complete matching published bundle returns a verified no-op.
For `scope_repair_request`, bypass ordinary synthesis, graph compression,
hardening, metadata repair, and issue creation. `scope-repair.md` and the narrow
branch in `issue-phase.md` may widen only the named issue's `allowed_paths`, then
must rerun complete-bundle validation.

If `knowledge_delta` is present in a single Spec, reuse or add a final
closeout issue, exclude it and its own `dependency_ids` while deriving the
remaining graph's no-dependent terminals, then make it depend directly on all
of them and reject any dependent of the owner. In a multi-repository feature,
partition targets by repository, require one explicit canonical decision target
for every cross-repository decision, and select one final closeout owner inside
each member with a nonempty target shard. Attach only that repository's shard to
its owner, never copy peer issue IDs, and harden and validate every selected
final issue like every other issue.

### 5. Reconcile Idea Sources

Skip this step for `scope_repair_request`; an implementation-time path repair
does not reopen or reconcile Idea planning lifecycle. Otherwise skip this step
when neither selected new-source `source_idea_refs` nor derived
existing-source `bound_source_idea_refs` are present. Otherwise load
`references/idea-source.md`. With `planning_mode=publish` and a complete durable
result, determine cumulative `partial` or `full` coverage separately for every
selected or bound Idea from verified prior Specs plus that result. With
`planning_mode=preview`, or
when another branch returned only a non-durable preview, leave the durable map
unchanged, leave every selected or bound Idea unchanged, and report only
`intended_coverage`, `intended_covered_scope`,
`intended_remaining_scope`, and intended transitions from the separate
projection.

With `planning_mode=publish`, a terminal wait for one specific requester answer may
reconcile the affected Ideas to `needs-info` before a planning result exists.
Reconcile coverage only after every Feature Spec, implementation issue,
metadata mutation, and relationship in the complete published bundle is durable
and verified. A
technical, validation, configuration, or partial publication failure normally
preserves each Idea's prior state. When the requester has answered a prior
`needs-info` blocker, prevent that stale state from surviving a later technical
failure by reconciling it to `needs-triage` at terminal exit.

Partial coverage writes the canonical cumulative planning-outcome block and
returns the Idea to `needs-triage`; full coverage writes the canonical
cumulative block, clears actionable states, and closes the GitHub Idea. Apply
each decision independently and retry only
missing operations after partial source reconciliation. On resume, use the
reconciliation-only branch and treat a closed GitHub Idea as already reconciled
only when its complete canonical record exactly matches
the verified cumulative Spec set and coverage result.

### 6. Report Completion

Return:

- resolved `planning_mode` and derived `source_route`;
- when applicable, the exact `scope_repair_result` from
  `references/scope-repair.md`;
- Feature Spec ref or proposed ref, title, and target location;
- planning identity and project-context facts used;
- retained, created, or proposed issue refs in publication order, repaired
  contract metadata or parent/sub-issue attachment, and verified no-op state when
  applicable;
- graph and verticality validation, including candidate and final issue counts,
  compression repairs, retained-slice reasons, and avoided initial hardening
  calls;
- published tracker metadata when writes occurred;
- discovered candidate refs when discovery ran, selected Idea refs, verified
  prior outcome refs, per-Idea cumulative durable `coverage`, `covered_scope`,
  and `remaining_scope`, or the distinct `intended_coverage`,
  `intended_covered_scope`, and `intended_remaining_scope`; plus published or
  proposed lifecycle transitions and any missing reconciliation operations;
- repository-owned domain closeout owners when present and the derived
  `capture_outcome`;
- exact continuation handoff when publication is incomplete, including every
  created or staged Spec ref, any applicable multi-repository
  publication-transaction identity and its complete predeclared body templates,
  selected Idea and prior-outcome refs, completed and missing operations, and
  the complete `knowledge_delta` until every required repository-owned final
  owner issue is durable and verified;
- blockers and withheld artifacts;

When `knowledge_delta` is present, report `capture_outcome=deferred` plus every
actual or proposed repository-owned final issue ref. Otherwise report
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
- `references/publication.md`: GitHub publication, stable refs, and recovery.
- `references/spec-phase.md`: Feature Spec drafting, routing, and publication.
- `references/scope-repair.md`: separately authorized monotonic allowed-path
  repair, audit, recovery, and result.
- `references/spec-template.md`: default Feature Spec shape.
- `references/issue-phase.md`: issue splitting, hardening, graph validation,
  and publication.
- `references/issue-body-template.md`: generated issue shape and single
  Execution Contract.
- `references/vertical-slices.md`: slicing and readiness gates.
