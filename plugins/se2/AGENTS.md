# SE2 Plugin Maintenance

plugins/se2/ is an experimental graph-first workflow package. Learn, Idea,
Feature, Implement, and Audit expose distinct workflow graphs; Feature
additionally owns the Feature/Task graph. SE2 is independent from plugins/se/;
do not silently merge its graph contract into the existing SE plugin.

## Ownership map

- .codex-plugin/plugin.json owns SE2 identity, version, discovery metadata,
  and bundled-skill exposure.
- references/task-preflight.md owns the root-level live task capability,
  destination, observation, authorization, display-title capability,
  update-relay, and recovery gates.
- references/task-handoff.md owns the shared task assignment, observation,
  partial/final relay, deterministic emoji title grammar, bounded title
  reconciliation, and terminal-report evidence.
- references/workflow-contract.md owns the semantic Idea hosted shape for SE2
  Idea capture.
- references/workflow-graph.md owns the shared workflow-graph vocabulary,
  registry rules, terminal meanings, authority boundaries, and validation
  expectations. It does not own Idea hosted metadata or Feature/Task semantics.
- references/codex-dependency-preflight.md owns the fail-closed availability
  gate before any SE2 workflow uses a required G-owned GitHub workflow.
- references/hosted-content-safety.md owns the final portable-content projection
  and fail-closed gate immediately before every hosted write produced by Idea,
  Feature, or Implement. G owns transport and readback, not semantic cleanup.
- scripts/validate-hosted-content-safety owns the static owner-routing,
  duplicate-doctrine, and hosted-template path checks for that contract.
- skills/learn/SKILL.md owns independent durable repository-context routing,
  capture, localization, Code Review Rules, and AGENTS.md compaction
  proposals and its workflow registry; its references own branch-specific
  detail.
- skills/feature/SKILL.md owns the graph manifest, Mermaid overview, node
  registry, Feature/Task invariants, terminal-operation branches, and terminal
  states.
- skills/feature/references/task-profile.md owns the principal Feature planner
  role and its model, reasoning, and topology selection.
- skills/feature/steps/ owns the Markdown node contracts. Every step file
  keeps the standard front matter and its declared transitions synchronized.
- skills/feature/templates/ owns reusable authoring templates and is not a
  node namespace.
- skills/implement/SKILL.md owns the GitHub-Feature-to-PR workflow registry and
  Mermaid projection. Its references own multi-Feature orchestration,
  execution and delivery topology, orchestrator/worker profiles, Contract
  Repair, worker-session review, standalone and stacked delivery, stack
  reconciliation, and the SQLite WAL run-state contract.
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

- Keep Feature planning free of implementation authority. Implement accepts
  one or more complete authoritative GitHub Features, never an isolated Task
  or local draft, and returns a verified standalone or stacked PR topology.
  Contract Repair must re-enter Feature maintenance instead of silently
  rewriting the Feature graph or inheriting its planner profile.
- Keep acceptance criteria as ordinary list items with stable bracketed
  `F-AC-NN` and `T-AC-NN` identities, never Markdown checkbox state. Feature
  owns identity assignment, monotonic retirement high-water marks, and durable
  hosted coverage; workers own Task criterion proof at the exact candidate
  HEAD; the orchestrator aggregates Feature proof without rewriting issue
  bodies or adding criterion state to the ledger. The uppercase bracketed IDs
  are an explicit rendered-contract syntax exception to lower-kebab values.
- Keep Implement execution waves separate from PR delivery topology.
  Serialization, capacity, and path overlap do not create a stack. Stack only a
  true same-repository code dependency from one green exact-HEAD parent; keep
  parallel, unrelated, cross-repository, and multi-parent work standalone or
  blocked until it has one valid integration base. G owns publication and
  pairwise stack linking. Parent drift invalidates descendant evidence, and
  each worker owns its own bottom-to-top rebase and review cycle.
- Keep the Implement ledger a minimal recovery index, not a second workflow
  engine. Preserve five tables, including exclusive active Feature claims,
  SQLite WAL, explicit drop-and-recreate, and the boundary against prompts,
  message logs, findings, and routine worker state. The orchestrator is its only
  runtime client; workers supply evidence but never access the ledger.
- Keep Task dependency edges executable: a downstream candidate must contain
  every exact prerequisite HEAD through verified merged, stacked, or
  worker-composed ancestry. PR readiness alone never satisfies a dependency.
- Keep deterministic task-title initialization shared by every task-managed
  SE2 skill. After stable identity readback, require one bounded reconciliation
  outcome before monitoring: exact verification or an explicit
  `title-unverified`/`title-drift` warning. Never use a title as identity,
  repeat an adjustment, or create a replacement task for title failure.
- Keep Idea capture independent from Feature/Task and Implement semantics while
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
  hosted rehydration through the shared G dependency gate before hosted reads,
  and route the default Feature publication through its terminal preflight and
  G-owned issue workflow before any hosted mutation. Preview is opt-in and must
  never be selected implicitly when publish authority or G is unavailable.
- Keep Implement GitHub-backed end to end. It has no local-only or preview
  execution mode: authoritative hosted Features and Tasks are mandatory input,
  and a verified hosted PR topology is mandatory output.
- Keep Audit strictly observational. Attribute SE2 use only from task-visible
  evidence, treat missing visibility as indeterminate, and never add task
  contact, repository/GitHub mutation, delegation, or persistent audit state.
- Keep repository context discovery rooted at AGENTS.md hierarchy and generic:
  do not add a global context-document taxonomy or encode context discovery as
  graph nodes. Keep future tracker capabilities separate from the initial
  Feature, Task, relation, and dependency contract.
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
- Validate Feature terminal-operation preview/publish reachability, the
  preflight-before-hosted-access boundary, reconciliation to `complete` or
  `blocked`, and the absence of side effects or outgoing edges on terminal
  nodes.
- Validate Idea default-publish/explicit-preview routing, Learn's local-only
  boundary, and Implement's mandatory hosted-source and PR-output path.
- Validate Implement registry/projection reconciliation, registered transition
  targets, terminal reachability, terminal nodes without outgoing edges, and
  the delivery-gate and stack-reconcile paths.
- Run scripts/validate-hosted-content-safety and validate that Idea, Feature,
  Implement, their write-owning references, and Contract Repair route through
  the one canonical hosted-content owner without duplicate Idea doctrine.
- Validate that Feature and Implement both route every created task through the
  shared title-reconciliation outcome before normal monitoring or update relay,
  and that resume paths cannot repeat an uncertain adjustment.
- Validate the canonical bracketed acceptance syntax, Feature-local and
  bundle-wide uniqueness, monotonic high-water marks, hosted coverage
  publication/readback, malformed and legacy-checkbox rejection, and
  worker-task-report acceptance recovery bound to the current candidate SHA.
- Validate Audit explicit-only metadata, frozen-cohort and stopping rules,
  registry/projection reconciliation, exact transition-condition coverage, the
  intentional refresh loop, terminal reachability, evidence classifications,
  and prohibited mutation behavior.
- Run the Implement run-state CLI help, version, read-only doctor, and focused
  standard-library tests against temporary databases.
- Check that the marketplace path and plugin metadata point to this package.
- Validate Learn front matter, UI metadata, routed references, explicit-only
  invocation, and independence from the existing SE Learn package.
- Scan Idea sources for direct provider access, durable-memory routing, model
  profile selection, and dependencies on the other plugin's Idea surface.
- Scan Learn sources for direct provider or tracker access, task/profile
  selection, stale legacy invocation names, and unowned local references.
- Run git diff --check before handoff.
