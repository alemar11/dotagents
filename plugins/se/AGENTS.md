# SE Plugin Maintenance

plugins/se/ is the repository's graph-first workflow package. Learn, Grilling,
Study, Idea, Feature, Implement, and Audit expose distinct workflow surfaces;
Feature owns the repository-scoped textual Feature Plan Set graph.
Keep SE as the sole active owner of these workflow contracts; do not
reintroduce a retired compatibility surface.

## Agent skills

### Domain memory

Read the repository-root [`CONTEXT.md`](../../CONTEXT.md) first, then this
subproject's `CONTEXT.md`. Maintain shared purpose, vocabulary, rules,
boundaries, routing, and cross-project decisions at the repository root;
maintain only subproject-specific deltas, local topics, and local ADRs here.
Keep always-active subproject rules in this `AGENTS.md`; exclude tentative
plans, secrets, raw logs, and duplicated root guidance.

## Shared references

`references/` is the canonical home for SE contracts consumed by multiple
bundled skills. It is a shared ownership boundary, not a general documentation
folder.

- Put a contract in `references/` only when its vocabulary, protocol, safety
  boundary, gate, or other behavior genuinely applies to at least two SE
  skills and needs one canonical owner. Keep skill-specific selection,
  topology, state, templates, and branch detail under
  `skills/<skill>/references/`. (Codex learning)
- Every shared reference must have one entry in the ownership map below, name
  its scope and authority, and be routed explicitly from each consumer at the
  point where it must be read. Consumers cross-reference the owner instead of
  copying or summarizing its doctrine. (Codex learning)
- When editing a shared reference, update every affected consumer route,
  state owner, metadata or documentation surface, and focused validator in the
  same change; then scan for duplicated doctrine, stale routes, and dangling
  links. (Codex learning)
- Load and use a shared reference only when its consumer's declared read
  condition applies. If the behavior becomes specific to one skill, move it
  to that skill's `references/` directory and remove the obsolete shared
  ownership and routes. (Codex learning)

## Ownership map

- .codex-plugin/plugin.json owns SE identity, version, discovery metadata,
  and bundled-skill exposure.
- references/workflow-contract.md owns the semantic Idea hosted shape for SE
  Idea capture.
- references/workflow-graph.md owns the shared workflow-graph vocabulary,
  registry rules, terminal meanings, authority boundaries, and validation
  expectations. It does not own Idea hosted metadata or Feature Plan semantics.
- references/codex-dependency-preflight.md owns the fail-closed availability
  gate before any SE workflow uses a required G-owned GitHub workflow.
- references/codex-runtime-surface.md owns the shared, read-only App-versus-CLI
  classification used by surface-aware SE skills. Keep capability checks in
  the selected skill branch and never use them as surface evidence.
- references/hosted-content-safety.md owns mandatory portable-content
  projection, exact single-line title-artifact normalization, and local-path
  correction before every hosted write produced by Idea, Feature, or Implement,
  plus one bounded non-blocking repair of the same artifact after readback. G
  owns transport and readback, not semantic cleanup.
- scripts/validate-hosted-content-safety owns the static owner-routing,
  duplicate-doctrine, and hosted-template path checks for that contract.
- skills/learn/SKILL.md owns independent durable repository-context routing,
  capture, localization, Code Review Rules, concise AGENTS.md Project Context
  pointer reconciliation, and AGENTS.md compaction proposals and its workflow
  registry; its references own branch-specific detail.
- skills/grilling/SKILL.md owns explicit or composed, read-only, one-question-
  at-a-time handoff refinement. It composes Learn only for initial context
  inspection and returns a refined transient handoff without task creation,
  delegation, or automatic durable capture.
- skills/study/SKILL.md owns explicit-only read-only Study orchestration. It
  owns the shared curated handoff, surface routing, read-only boundary, worker
  cap, and report contract. It composes bundled Grilling, which reads context
  through Learn, before any worker planning. Its `app-runtime.md` reference
  owns separate App controller placement and parent monitoring;
  `cli-runtime.md` owns same-session control; `orchestration.md` owns shared
  native-subagent selection, assignments, setup, monitoring, synthesis, and
  failure handling; `states.md` owns the cross-surface state vocabulary. Study
  never creates additional visible App worker tasks.
- skills/feature/SKILL.md owns the workflow graph manifest, Mermaid overview,
  node registry, Feature Plan Set, Feature identity, Feature-level dependency,
  and local Macro Task contracts, material-question routing, optional read-only
  helpers, structural plan review, publication adapter, and terminal states.
- skills/feature/references/task-profile.md owns the one required Feature
  planner launch and its explicitly requested model/reasoning profile. It does
  not own post-effect profile, identity, title, or execution-target validation.
- skills/feature/steps/ owns the eight lightweight Markdown node contracts.
  Every step file
  keeps the standard front matter and its declared transitions synchronized.
- skills/feature/templates/ owns reusable authoring templates and is not a
  node namespace.
- skills/implement/SKILL.md owns the lightweight workflow graph and
  orchestration entrypoint. Its directly routed references own transition
  conditions, Feature-graph scheduling, repository claims, and its intentionally
  minimal state vocabulary.
- skills/implement/references/candidate-review.md owns candidate-review runtime
  operations, its transient receipt, immutable checkout lifecycle, execution
  recovery, and the Feature-wide review-revision budget;
  skills/implement/references/states.md solely owns its state names and
  meanings. G continues to own the separate hosted review lifecycle.
- skills/implement/scripts/repository-claims is the shipped host-local
  repository-ownership CLI. Its schema and version constants are runtime
  sources of truth; focused tests live under skills/implement/tests/.
- test_all.py is the package discovery aggregator for the executable claims and
  runtime-alignment suites; it owns no behavior tests.
- skills/idea/SKILL.md owns explicit session capture, the transient Idea bundle,
  workflow registry, preview/publish routing, and the capture-only terminal
  boundary. Its references own the canonical body, Idea source handoff, and
  publication recovery details.
- skills/audit/SKILL.md owns explicit-only active-session discovery, frozen
  cohort monitoring, evidence-calibrated graph-conformance reconstruction,
  finding classification, stopping behavior, and its read-only report.
- skills/audit/agents/openai.yaml owns Audit discovery metadata and must keep
  implicit invocation disabled. Audit has no scripts, ledger, task profile, or
  persistent output.
- .agents/plugins/marketplace.json owns repo-local discovery registration.

## Maintenance contract

- Keep Feature planning free of technical implementation authority. Feature
  publishes one complete Feature Plan Set containing only genuinely distinct
  sibling Features, each with a closed set of durable Macro Task projections.
  Use vertical slices when a Feature outcome admits coherent slices; never
  manufacture them by splitting technical layers. Feature-level `blocked_by`
  remains a planning-owned relation,
  but repository identity gives it a deterministic implementation projection:
  a same-repository edge is mandatory stack intent and a cross-repository edge
  is scheduling-only. Macro-local `blocked_by` remains planning-only and may be
  internalized by Implement while preserving every available
  Macro Task outcome. The Plan Set body and registries remain semantic
  authority for both relation levels. After exact hosted identities exist,
  Feature must always
  attempt one native GitHub `blocked by` projection per canonical edge:
  parent Feature to parent Feature, including exact URLs across repositories,
  and child Task to child Task only inside one parent Feature. A missing
  attempt or terminal result blocks publication, but a recorded `failed`,
  `unavailable`, or `unknown` provider result is a non-blocking warning and
  never invalidates the body-backed graph. Implement consumes exactly the
  caller-supplied parent Features as semantic contracts, reads sibling and
  dependency data without expanding that selection, and returns a verified
  standalone or stacked PR topology. Native `blockedBy`/`blocking` state is
  diagnostic only and never changes body-backed scheduling or stack intent.
- Keep Feature clarification proportional. Ask one consolidated batch only
  when material product decisions remain after evidence gathering. A complete
  brief, an explicitly delegated choice, or safe explicit assumptions proceed
  without question-route classifications. Clarification is a nonterminal wait;
  material unresolved decisions still block rather than being guessed.
- Require Review between every complete Feature draft and Publish. The reviewer
  is read-only and may be an optional helper or a separate serial planner lens.
  Review owns deterministic identity, F-AC coverage, closed-registry,
  dependency-DAG, boundary, projection, and maintenance-preservation checks.
  Correctable findings return to Plan while revisions make progress; a hidden
  material decision returns to Clarification. Repeated unresolved or
  no-progress findings block. Do not restore a separate Plan Validation node,
  review-round state machine, or mandatory critic task.
- Keep one human-readable `references/states.md` in every bundled SE skill.
  Each file is that skill's canonical state glossary: it must include every
  workflow node, separate workflow nodes from field-qualified domain or
  persisted states, and say explicitly when the skill owns no checkpoint or
  ledger. Do not present same-named values from different state domains as one
  shared state machine.
- Keep Feature acceptance criteria as ordinary list items with stable bracketed
  `F-AC-NN` identities, never Markdown checkbox state. Feature owns Plan Set
  identity, stable Feature identities, criterion identity, monotonic retirement
  high-water marks, source and question provenance, Feature-level dependency
  relations, each closed Macro Task registry, macro-local planning relations,
  and the durable parent/child projection. Implement owns exact-head delivery
  evidence while preserving every Feature criterion and available Macro Task
  outcome. Sibling Features and their Tasks are never selected implicitly. The
  uppercase bracketed IDs are an explicit rendered-contract syntax exception to
  lower-kebab values.
- Keep Implement concurrency separate from PR delivery topology. Serial work
  may reuse a clean compatible repository worker; concurrent or cross-repository
  work uses isolated lanes, and overlapping writes never share one worktree.
  Capacity and execution order never create stack intent. Every same-repository
  Feature `blocked_by` edge does create stack intent, while cross-repository
  edges remain scheduling-only. Parent drift invalidates dependent evidence.
- Keep Implement's public runtime contract in its `SKILL.md` and directly
  routed references. Its repository-claims CLI remains an ownership-only
  implementation detail and the sole source of truth for its exact schema and
  version; workflow position must never be persisted there. Do not duplicate
  those runtime contracts in maintenance guidance.
- Keep the repository-claims registry to one ownership table for the immutable
  selected repository set. It has no workflow nodes, Features, workers, Git or
  PR state, review state, CI state, TTL, heartbeat, forced release, or stale-owner
  recovery. Only the bound orchestrator uses its fencing token. Blocked and
  deferred runs retain ownership; successful delivery makes exact whole-group
  release the orchestrator's final external effect after every other actor and
  mutation is quiescent. Handoff or abandonment still requires explicit
  authority.
- Keep Feature independent from Implement task and claim handling. Its
  controller creates or resumes one planner task with `gpt-5.6-sol` and
  `high` passed explicitly, then starts Intake in the planner's first turn.
  An accepted stable task receipt is sufficient. Do not add a bootstrap-only
  turn, effective-profile readback, identity self-attestation, title
  reconciliation, execution-target comparison, goal, or replacement protocol.
  Inspect the same task effect once only when creation is genuinely ambiguous.
  Repository and source identity are verified later as Intake evidence.
- Keep Implement scheduling body-backed and evidence-driven. Inspect selected
  and unselected declared prerequisites without expanding the requested Feature
  set. Exclude Features already owned by an observed active lane, use
  change-driven reconciliation when only active lanes remain, and never create
  a duplicate lane for the same active Feature.
- Keep orchestrator placement and worker targeting independently verifiable.
  Reuse the invoking visible task only when stable identity, intended home, and
  exact Feature selection correlate; otherwise create one visible orchestrator.
  Verify each worker's repository, remote, isolated worktree, branch, and full
  starting SHA before mutation. Titles and project grouping are diagnostic only.
  Use configured model and reasoning defaults for the orchestrator and workers
  unless the caller explicitly requests an override. Keep candidate-review
  operations, fixed profile, lifecycle, and convergence in their routed runtime
  reference, their value registry in `references/states.md`, and the indexed
  profile projection synchronized without duplicating those contracts here.
- Keep pull-request review exact-head and hosted. A newly published draft is an
  intermediate state. Once the candidate is stable, make the PR ready, read
  back its full HEAD, actual base, body identity, and topology, and wait once for
  the automatic hosted review. A Feature permits only two review-driven repair
  or rebuttal revisions across local and hosted review combined. Actionable
  findings return to the same trustworthy worker; a repaired HEAD updates the
  same PR and uses one explicit hosted re-review request. Evidence-backed
  non-actionable findings require G disposition and a fresh local rebuttal
  review, never an empty commit. Reconcile ambiguous transitions or requests
  before retry and never toggle draft state or duplicate a same-head request.
- Keep Implement completion closed to a current ready exact-head PR whose
  actual base, body, and standalone or stacked topology match reviewed intent,
  with an admissible independent candidate-review receipt, required validation
  and CI, and either provider-clean hosted evidence or explicitly reported
  adjudicated-clean evidence; alternatively require proof that the Feature is
  already incorporated into its integration base. Complete only after exact
  whole-group claim release and unclaimed readback. A caller-required draft PR
  defers completion. Merge, deploy, release, issue closure, destructive
  recovery, and unrelated cleanup remain outside invocation authority.
- Feature requests its planner title when supported but never reads, corrects,
  or gates on it. Implement titles are useful diagnostics but never identity or
  correctness evidence.
- Keep task prompts as flat semantic handoffs. Preserve bounded intent,
  constraints, source references, destination, validation, and return evidence,
  but unwrap raw task/delegation transport envelopes, escaped wrapper markup,
  parent prompts, and transcripts before creating a child task. Never use a
  transport wrapper as user intent or durable evidence.
- Keep Idea capture independent from Feature Plan and Implement semantics while
  using the shared workflow-graph vocabulary. Session context may be assembled
  in transient run state, but only an explicitly published hosted issue is
  durable; Idea must not write project memory or create application tasks.
- Keep Idea hosted output behind the G-owned issue workflow and the shared
  fail-closed dependency gate. Never add a direct tracker transport or a
  compatibility alias for a missing dependency.
- Keep internal orchestration records distinct from hosted content. Internal
  records may retain local task/project/worktree facts; every hosted projection
  must pass references/hosted-content-safety.md immediately before write,
  including worker/tool-originated content. Correct or remove local paths before
  transport; if readback still exposes one, attempt one bounded update of the
  same artifact and retain a non-blocking warning when repair is unavailable,
  failed, or ambiguous.
- Keep hosted titles as exact non-empty single-line semantic values. Remove
  only serialization-added final line terminators before G transport, reject
  interior line breaks, and leave intentional multiline body content intact.
- Keep Feature preview local-only. Route Feature maintenance or existing-source
  hosted Plan Set rehydration through the shared G dependency gate before
  hosted reads, and route default publication through the single publication
  adapter and G-owned issue workflow before any hosted mutation. Publication
  creates every sibling parent Feature and every local child Macro Task without
  a container issue, then reconciles each parent body in place with the final
  set registry and exact child mappings before readback. After identities are
  final, attempt every exact native Feature and same-parent Macro dependency
  through `g:github-issues`, recording one verified, no-op, failed, unavailable,
  or unknown result per edge. Existing-source maintenance also removes only
  prior SE-owned native edges explicitly removed from the revised semantic
  graph and preserves foreign edges. A missing attempt or result blocks; a
  recorded native failure does not downgrade a complete semantic publication.
  Any explicitly requested downstream handoff must also have a reconciled
  terminal result before completion. Classification
  is optional after semantic readback; when used, delegate label and native type
  selection to `g:github-tagger` and never preselect metadata values. Preserve
  the tagger's smallest-set policy: zero or more relevant labels and zero or one
  relevant type, with empty selections valid. Classification never gates
  completion. Preview is opt-in and must never be selected implicitly
  when publish authority or G is unavailable.
- Keep Audit strictly observational. Attribute SE use only from task-visible
  evidence, treat missing visibility as indeterminate, and never add task
  contact, repository/GitHub mutation, delegation, or persistent audit state.
- Keep repository context discovery rooted at AGENTS.md hierarchy and generic:
  do not add a global context-document taxonomy. Feature records normative
  context separately from the critic analyst's independent first pass and
  reports conflicts rather than silently overriding repository instructions.
- Keep node IDs lower-kebab-case, unique, and consistent across front matter,
  each skill registry, Mermaid node names, and transition targets.
- Treat the node header and registry as the structural contract. Mermaid is a
  maintained projection of that contract, not an independent source of edges.
- Any committed change under this plugin requires a semantic version update in
  .codex-plugin/plugin.json.

## Validation

- Follow the repository testing rule: Python tests must exercise executable
  behavior or structured always-loaded metadata. Never assert Markdown wording,
  heading names, table layout, section placement, or moved prose. Use a bounded
  forward-model check when semantic workflow behavior cannot be established by
  executable tests or structured validation.
- Parse the plugin manifest as JSON.
- Validate the Idea skill front matter and UI metadata, canonical references,
  explicit-only invocation, and independent hosted-output boundary.
- Validate that every table-owned registry row matches its declared field order
  and arity, every registered local node exists, every local transition targets
  a registered node, and every step has the standard front matter.
- Validate Learn, Grilling, and Idea registry/projection reconciliation,
  terminal reachability, and the absence of outgoing transitions from terminal
  nodes.
- Validate Learn's invocation preflight, canonical AGENTS.md pointer shape,
  root-first monorepo routing, local context ownership and migration,
  evolution-rule projection, and no-dangling-pointer rule.
- Validate Feature Plan Set graph reachability, genuinely distinct sibling
  Feature boundaries, Feature registry coverage, Feature-level acyclic
  planning relations, each closed local Macro Task registry, same-parent-only
  macro relations, material-question routing and nonterminal waits, optional
  delegation with serial fallback, mandatory post-draft structural Review,
  progress-bounded revision and review clarification, G preflight before hosted
  source reads or publication, final in-place parent-body reconciliation,
  parent/child publication and readback,
  mandatory native-dependency attempts for every canonical edge, non-blocking
  native failure outcomes, maintenance removal of only explicitly retired
  SE-owned edges, requested-handoff reconciliation, reconciliation to
  `complete` or `blocked`, and the
  absence of side effects or outgoing edges on terminal nodes.
- Validate Idea default-publish/explicit-preview routing, Learn's local-only
  boundary, and Implement's mandatory hosted-source and PR-output path.
- Validate Implement registry/projection reconciliation, registered transition
  targets, terminal reachability, terminal nodes without outgoing edges,
  exact selected-Feature scope, body-backed dependency scheduling, visible
  orchestrator placement, serial worker reuse, bounded concurrent lanes,
  same-repository stacks, cross-repository scheduling, mandatory independent
  candidate review with Sol/xhigh, receipt admission, checkout cleanup,
  exact-base/full-HEAD invalidation, the shared two-revision budget,
  provider-clean or adjudicated-clean hosted acceptance, actual PR topology,
  completion-time claim release, resume reconstruction through `reconcile`,
  claim conflicts, and mutation boundaries.
- Validate that every bundled skill routes to `references/states.md`, every
  graph node appears in its skill's state table, and Implement's workflow
  registry, transition conditions, and Mermaid projection agree while every
  workflow node remains absent from
  repository-claim storage.
- Run scripts/validate-hosted-content-safety and validate that Idea, Feature,
  Implement, and their write-owning references route through
  the one canonical hosted-content owner without duplicate Idea doctrine.
  Include exact single-line title artifacts without serialization-added
  terminators.
- Validate that Feature explicitly requests its planner's model and reasoning
  once, accepts a stable creation or resume receipt, and begins Intake in the
  planner's first turn without assigned-task bootstrap, effective-profile
  readback, title reconciliation, execution-target comparison, or a goal.
  Require at most one readback only for a genuinely ambiguous creation effect.
- Validate flat prompt projection and removal of nested or escaped transport
  envelopes without losing semantic constraints. Task titles remain diagnostic
  only, and Feature title metadata never gates its planner.
- Validate the canonical bracketed Feature acceptance syntax, monotonic
  high-water marks, plan publication/readback, malformed and legacy-checkbox
  rejection, question-batch completeness, and Implement evidence bound to the
  current candidate SHA.
- Validate that optional Feature classification runs only after exact issue
  readback, never presets metadata values, preserves the tagger cardinalities
  of zero or more labels and zero or one type, and never gates semantic
  completion.
- Validate Audit explicit-only metadata, frozen-cohort and stopping rules,
  registry/projection reconciliation, exact transition-condition coverage, the
  intentional refresh loop, terminal reachability, exhaustive stable inventory
  traversal before complete coverage, explicit partial coverage at capped or
  untraversable boundaries, evidence classifications, and prohibited mutation
  behavior.
- Run `python3 -m unittest discover -s plugins/se -v` and require the package
  aggregator to execute both Implement repository-claims and runtime-alignment
  suites. Also run CLI help, version, and read-only absent doctor. Validate
  structured read-only parser failures, atomic overlap rollback,
  same-token acquisition reuse, immutable repository sets, exact whole-group
  bind and release, corruption detection, file permissions, and the absence of
  WAL, TTL, heartbeat, force-release, and execution-state storage.
- Use bounded forward-model scenarios to validate Implement selection
  scope, workflow-graph traversal, visible orchestrator placement,
  orchestrator-owned concurrency, serial worker reuse, same-repository stacks,
  cross-repository scheduling, candidate-review clean/findings/indeterminate
  paths, receipt admission, profile enforcement, checkout cleanup, one proved
  non-execution retry, the combined review-revision budget, actionable and
  adjudicated hosted findings, wait and provider failures, final PR topology,
  completion-time claim release, blocked/deferred claim retention, resume
  reconstruction through `reconcile`, claim conflicts, and mutation boundaries.
- Check that the marketplace path and plugin metadata point to this package.
- Scan for retired delivery-skill identifiers and removed legacy task contracts
  before handoff.
- Validate Learn front matter, UI metadata, routed references, implicit
  hard-rule selection, setup-first capture, monorepo root/local ownership and
  migration, and the absence of retired compatibility surfaces.
- Validate Grilling front matter, explicit-only UI metadata, Learn-first
  read-only context inspection, one-question-per-turn interaction with a
  concrete recommended answer, refined handoff output, and the absence of
  writes, task creation, or delegation.
- Validate Study front matter, explicit-only UI metadata, bundled Grilling
  composition without a cross-package dependency preflight, routing through
  the shared Codex surface contract, the shared curated handoff, immediate
  surface-local Grilling,
  App-only Sol/medium controller placement, inherited CLI controller settings,
  shared native Luna/max subagents, zero-worker focused analysis, the
  five-worker cap, no-replacement behavior, absence of visible App worker
  tasks, model index ownership, surface-aware reporting, and read-only
  outcomes.
- Scan Idea sources for direct provider access, durable-memory routing, model
  profile selection, and dependencies on the other plugin's Idea surface.
- Scan Learn sources for direct provider or tracker access, task/profile
  selection, stale legacy invocation names, and unowned local references.
- Run git diff --check before handoff.
