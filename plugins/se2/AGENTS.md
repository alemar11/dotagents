# SE2 Plugin Maintenance

plugins/se2/ is an experimental graph-first Feature planning package. It is
independent from plugins/se/; do not silently merge its graph contract into
the existing SE plugin.

## Ownership map

- .codex-plugin/plugin.json owns SE2 identity, version, discovery metadata,
  and bundled-skill exposure.
- references/task-preflight.md owns the root-level live task capability,
  destination, observation, authorization, update-relay, and recovery gates.
- references/task-handoff.md owns the shared task assignment, observation,
  partial/final relay, deterministic emoji title grammar, reconciliation, and
  terminal-report evidence.
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
- scripts/validate-task-contract.sh owns static package validation only. It
  must never be used as evidence that the live application can create or
  monitor a task.
- .agents/plugins/marketplace.json owns repo-local discovery registration.

## Maintenance contract

- Keep Feature planning free of implementation authority. The separate
  Implement skill may execute an explicitly selected Task, but it must not
  silently change the Feature graph or inherit its task profile. External
  issue publication is allowed only through an explicit publish run and must
  remain separate from node planning semantics.
- Keep repository context discovery rooted at AGENTS.md hierarchy and generic:
  do not add a global context-document taxonomy or encode context discovery as
  graph nodes. Keep future tracker capabilities separate from the initial
  Feature, Task, relation, and dependency contract.
- Keep node IDs lower-kebab-case, unique, and consistent across front matter,
  the registry, Mermaid node names, and transition targets.
- Treat the node header and registry as the structural contract. Mermaid is a
  maintained projection of that contract, not an independent source of edges.
- Any committed change under this plugin requires a semantic version update in
  .codex-plugin/plugin.json.

## Validation

- Parse the plugin manifest as JSON.
- Validate that every registered local node exists, every local transition
  targets a registered node, and every step has the standard front matter.
- Check that the marketplace path and plugin metadata point to this package.
- Run scripts/validate-task-contract.sh for static package checks only; its
  success is not live application or monitoring evidence.
- Run git diff --check before handoff.
