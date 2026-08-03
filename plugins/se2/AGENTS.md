# SE2 Plugin Maintenance

plugins/se2/ is an experimental graph-first workflow package. Learn, Idea, and
Feature expose distinct workflow graphs; Feature additionally owns the
Feature/Task graph. SE2 is independent from plugins/se/; do not silently merge
its graph contract into the existing SE plugin.

## Ownership map

- .codex-plugin/plugin.json owns SE2 identity, version, discovery metadata,
  and bundled-skill exposure.
- references/task-preflight.md owns the root-level live task capability,
  destination, observation, authorization, update-relay, and recovery gates.
- references/task-handoff.md owns the shared task assignment, observation,
  partial/final relay, deterministic emoji title grammar, reconciliation, and
  terminal-report evidence.
- references/workflow-contract.md owns the semantic Idea marker and hosted
  shape for SE2 Idea capture.
- references/workflow-graph.md owns the shared workflow-graph vocabulary,
  registry rules, terminal meanings, authority boundaries, and validation
  expectations. It does not own Idea hosted metadata or Feature/Task semantics.
- references/codex-dependency-preflight.md owns the fail-closed availability
  gate before an Idea publish run uses the G-owned issue workflow.
- skills/learn/SKILL.md owns independent durable repository-context routing,
  capture, localization, Code Review Rules, and AGENTS.md compaction
  proposals and its workflow registry; its references own branch-specific
  detail.
- skills/feature/SKILL.md owns the graph manifest, Mermaid overview, node
  registry, Feature/Task invariants, and terminal states.
- skills/feature/references/task-profile.md owns the principal Feature planner
  role and its model, reasoning, and topology selection.
- skills/feature/steps/ owns the Markdown node contracts. Every step file
  keeps the standard front matter and its declared transitions synchronized.
- skills/feature/templates/ owns reusable authoring templates and is not a
  node namespace.
- skills/implement/SKILL.md and skills/implement/references/task-profile.md
  own the implementation workflow, its orchestrator/worker roles, and its
  model, reasoning, and topology selection; they consume the Feature bundle
  and root task contracts without redefining them.
- skills/idea/SKILL.md owns explicit session capture, the transient Idea bundle,
  workflow registry, preview/publish routing, and the capture-only terminal
  boundary. Its references own the canonical body, Idea source handoff, and
  publication recovery details.
- .agents/plugins/marketplace.json owns repo-local discovery registration.

## Maintenance contract

- Keep Feature planning free of implementation authority. The separate
  Implement skill may execute an explicitly selected Task, but it must not
  silently change the Feature graph or inherit its task profile. External
  issue publication is allowed only through an explicit publish run and must
  remain separate from node planning semantics.
- Keep Idea capture independent from Feature/Task and Implement semantics while
  using the shared workflow-graph vocabulary. Session context may be assembled
  in transient run state, but only an explicitly published hosted issue is
  durable; Idea must not write project memory or create application tasks.
- Keep Idea hosted output behind the G-owned issue workflow and the shared
  fail-closed dependency gate. Never add a direct tracker transport or a
  compatibility alias for a missing dependency.
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
- Validate that every registered local node exists, every local transition
  targets a registered node, and every step has the standard front matter.
- Validate Learn and Idea registry/projection reconciliation, terminal
  reachability, and the absence of outgoing transitions from terminal nodes.
- Check that the marketplace path and plugin metadata point to this package.
- Validate Learn front matter, UI metadata, routed references, explicit-only
  invocation, and independence from the existing SE Learn package.
- Scan Idea sources for direct provider access, durable-memory routing, model
  profile selection, and dependencies on the other plugin's Idea surface.
- Scan Learn sources for direct provider or tracker access, task/profile
  selection, stale legacy invocation names, and unowned local references.
- Run git diff --check before handoff.
