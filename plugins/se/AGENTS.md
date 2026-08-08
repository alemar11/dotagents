# SE Plugin Maintenance

plugins/se/ is the repository's graph-first workflow package. Learn, Idea,
Feature, Implement, and Audit expose distinct workflow graphs; Feature owns the
repository-scoped textual Feature Plan Set graph. Keep SE as the sole active
owner of these workflow contracts; do not reintroduce a retired compatibility
surface.

## Ownership map

- .codex-plugin/plugin.json owns SE identity, version, discovery metadata,
  and bundled-skill exposure.
- references/task-preflight.md owns the root-level live task capability,
  effective-role-readback capability, destination, observation, authorization,
  display-title capability, update-relay, and recovery gates.
- references/task-handoff.md owns the shared task assignment, typed requested
  versus effective role observation, partial/final relay, deterministic emoji
  title grammar, bounded title reconciliation, and terminal-report evidence.
- references/workflow-contract.md owns the semantic Idea hosted shape for SE
  Idea capture.
- references/workflow-graph.md owns the shared workflow-graph vocabulary,
  registry rules, terminal meanings, authority boundaries, and validation
  expectations. It does not own Idea hosted metadata or Feature Plan semantics.
- references/codex-dependency-preflight.md owns the fail-closed availability
  gate before any SE workflow uses a required G-owned GitHub workflow.
- references/hosted-content-safety.md owns the final portable-content projection
  and fail-closed gate immediately before every hosted write produced by Idea,
  Feature, or Implement. G owns transport and readback, not semantic cleanup.
- scripts/validate-hosted-content-safety owns the static owner-routing,
  duplicate-doctrine, and hosted-template path checks for that contract.
- skills/learn/SKILL.md owns independent durable repository-context routing,
  capture, localization, Code Review Rules, concise AGENTS.md Project Context
  pointer reconciliation, and AGENTS.md compaction proposals and its workflow
  registry; its references own branch-specific detail.
- skills/feature/SKILL.md owns the workflow graph manifest, Mermaid overview,
  node registry, Feature Plan Set, Feature identity, Feature-level dependency,
  and local Macro Task contracts, question-batch rules, optional analysis
  roles, publication adapter, and terminal states.
- skills/feature/references/task-profile.md owns the required Feature planner,
  optional analyst roles, model/reasoning profiles, and topology selection.
- skills/feature/steps/ owns the Markdown node contracts. Every step file
  keeps the standard front matter and its declared transitions synchronized.
- skills/feature/templates/ owns reusable authoring templates and is not a
  node namespace.
- skills/implement/SKILL.md owns the GitHub-Feature-to-PR workflow registry and
  Mermaid projection. Its references own multi-Feature orchestration,
  execution and delivery topology, orchestrator/worker profiles, optional
  Feature Worker support delegation, worker-session review, standalone and
  stacked delivery, stack reconciliation, and the SQLite WAL run-state
  contract.
- skills/implement/scripts/run-state is the shipped checkpoint and idempotency
  CLI. Its version constants and schema are runtime sources of truth; focused
  tests live under skills/implement/tests/.
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
  sibling Features, each with a closed set of durable macro-vertical Task
  projections. Feature-level `blocked_by` remains a planning-owned relation,
  but repository identity gives it a deterministic Implement projection: a
  same-repository edge is mandatory stack intent and a cross-repository edge
  is scheduling-only. Macro-local `blocked_by` remains planning-only and may be
  internalized by Implement while preserving every Macro Task outcome.
  Implement consumes the verified set, derives technical execution units
  internally, and returns a verified standalone or stacked PR topology.
  Implement must not create an automatic plan-repair planner for ordinary
  technical interpretation.
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
  and the durable parent/child projection. Implement owns technical
  execution-unit decomposition, exact-head implementation evidence, and one
  registry-derived closing set per Feature. Macro Tasks are planning views of
  the same Feature outcome and are always included with that parent Feature;
  sibling Features and their Tasks are never included. The uppercase
  bracketed IDs are an explicit rendered-contract syntax exception to
  lower-kebab values.
- Keep Implement execution waves separate from PR delivery topology.
  Serialization, capacity, and path overlap do not create a stack. Every
  same-repository Feature `blocked_by` edge does create mandatory stack intent,
  independently of whether implementation otherwise runs serially or in
  parallel. Cross-repository edges remain scheduling-only. A stacked child may
  start from a verified `candidate-published` parent branch and exact HEAD
  before that parent is delivery-ready; multi-parent work remains blocked until
  one immediate parent candidate contains every required same-repository
  prerequisite HEAD. G owns publication and pairwise stack linking. Parent
  drift invalidates descendant evidence, and each worker owns its own
  bottom-to-top rebase and review cycle.
- Keep Feature Worker support delegation subordinate to the parent Worker.
  Delegation is optional and must fall back to serial parent execution when
  unavailable, unknown, or capacityless. Support assignments may return
  bounded evidence or scoped changes, but never own a Feature member, final
  candidate, PR, Feature Plan Set, GitHub mutation, or ledger state. Do not run
  overlapping writes in one worktree.
- Keep the Implement ledger a minimal recovery index, not a second workflow
  engine. Preserve five tables, including exclusive active Feature claims,
  SQLite WAL, explicit drop-and-recreate, and the boundary against prompts,
  message logs, findings, and routine worker state. The orchestrator is its only
  runtime client; workers supply evidence but never access the ledger.
- Keep Feature-level scheduling and derived execution-unit dependency edges
  separate. A Feature `blocked_by` edge may cross repositories. Implement maps
  every same-repository edge to mandatory stack intent and every
  cross-repository edge to scheduling-only context; it never treats capacity,
  path overlap, or preferred order as stack authority. A downstream stacked
  candidate must contain every exact same-repository prerequisite HEAD through
  one verified immediate-parent ancestry chain. `candidate-published`, not PR
  readiness, is the development-unblock boundary. Macro Task `blocked_by`
  relations remain planning context: Implement may combine, reorder, or
  internalize them only while preserving every Macro Task outcome and Feature
  acceptance criterion.
- Keep PR observation centralized in the Implement orchestrator. After
  `candidate-published`, the Feature Worker becomes inactive but resumable and
  the assignment remains `delivery-pending`; the orchestrator monitors exact
  PR heads, hosted review, CI, delivery status, and parent drift. It contacts
  the same Worker only for actionable fixes, evidence repair, or rebase, and
  retains sole ledger and aggregate-completion authority.
- Keep deterministic task-title initialization shared by every task-managed
  SE skill. After stable identity readback, require one bounded reconciliation
  outcome before monitoring: exact verification or an explicit
  `title-unverified`/`title-drift` warning. Never use a title as identity,
  repeat an adjustment, or create a replacement task for title failure.
- Keep effective task-profile verification shared by every task-managed SE
  skill. The invoking skill owns requested role, model, reasoning, and topology;
  the shared preflight owns authoritative-readback capability; and the shared
  handoff owns one typed assignment-specific comparison bound to the observed
  task identity. Reuse existing workflow outcomes, never persist this evidence
  in the Implement ledger, and never create a replacement after a mismatch or
  unobservable required profile.
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
  including worker/tool-originated content, and fail closed when portable
  identity cannot be established.
- Keep Feature preview local-only. Route Feature maintenance or existing-source
  hosted Plan Set rehydration through the shared G dependency gate before
  hosted reads, and route default publication through the single publication
  adapter and G-owned issue workflow before any hosted mutation. Publication
  creates every sibling parent Feature, every local child Macro Task, their
  planning relations, and the final set registry readback without a container
  issue. Preview is opt-in and must never be selected implicitly when publish
  authority or G is unavailable.
- Keep Implement GitHub-backed end to end. It accepts authoritative published
  Feature Plan Sets with verified sibling/Macro projections, derives its
  technical execution units in the Implement control plane, and returns one
  verified hosted PR topology per Feature whose `closing_issue_refs` contains
  only that Feature's parent and every associated local Macro Task. It has no
  local-only or preview implementation mode.
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

- Parse the plugin manifest as JSON.
- Validate the Idea skill front matter and UI metadata, canonical references,
  explicit-only invocation, and independent hosted-output boundary.
- Validate that every table-owned registry row matches its declared field order
  and arity, every registered local node exists, every local transition targets
  a registered node, and every step has the standard front matter.
- Validate Learn and Idea registry/projection reconciliation, terminal
  reachability, and the absence of outgoing transitions from terminal nodes.
- Validate Learn's invocation preflight, canonical AGENTS.md pointer shape,
  read-first routing, evolution-rule projection, and no-dangling-pointer rule.
- Validate Feature Plan Set graph reachability, genuinely distinct sibling
  Feature boundaries, Feature registry coverage, Feature-level acyclic
  planning relations, each local Macro Task registry, same-parent-only macro
  relations, the question-batch wait boundary, optional delegation fallback,
  publication-before-hosted-access, parent/child publication and readback,
  reconciliation to `complete` or `blocked`, and the absence of side effects
  or outgoing edges on terminal nodes.
- Validate Idea default-publish/explicit-preview routing, Learn's local-only
  boundary, and Implement's mandatory hosted-source and PR-output path.
- Validate Implement registry/projection reconciliation, registered transition
  targets, terminal reachability, terminal nodes without outgoing edges, and
  the delivery gate, Feature-level scheduling, optional Feature Worker
  delegation fallback, exact sibling/Macro Task readback, per-Feature
  registry-derived closing sets, deterministic same-repository stack intent,
  `candidate-published` child unblocking, orchestrator-owned delivery
  monitoring, resumable Worker repair, and stack-reconcile paths.
- Validate that every bundled skill routes to `references/states.md`, every
  graph node appears in its skill's state table, and Implement's documented
  persisted values exactly match the run-state capability registry.
- Run scripts/validate-hosted-content-safety and validate that Idea, Feature,
  Implement, and their write-owning references route through the one canonical
  hosted-content owner without duplicate Idea doctrine.
- Validate that Feature and Implement both route every created task through the
  shared typed effective-role observation and title-reconciliation outcome
  before normal monitoring or update relay, and that resume paths cannot repeat
  an uncertain adjustment or create a replacement after profile mismatch.
- Validate the canonical bracketed Feature acceptance syntax, monotonic
  high-water marks, plan publication/readback, malformed and legacy-checkbox
  rejection, question-batch completeness, and Implement evidence bound to the
  current candidate SHA.
- Validate Audit explicit-only metadata, frozen-cohort and stopping rules,
  registry/projection reconciliation, exact transition-condition coverage, the
  intentional refresh loop, terminal reachability, evidence classifications,
  and prohibited mutation behavior.
- Run the Implement run-state CLI help, version, read-only doctor, and focused
  standard-library tests against temporary databases.
- Check that the marketplace path and plugin metadata point to this package.
- Validate Learn front matter, UI metadata, routed references, explicit-only
  invocation, and the absence of retired compatibility surfaces.
- Scan Idea sources for direct provider access, durable-memory routing, model
  profile selection, and dependencies on the other plugin's Idea surface.
- Scan Learn sources for direct provider or tracker access, task/profile
  selection, stale legacy invocation names, and unowned local references.
- Run git diff --check before handoff.
