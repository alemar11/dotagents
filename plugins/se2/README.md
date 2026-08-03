# SE2

SE2 is an experimental issue-first, graph-first Feature planning plugin.

Its skills are deliberately separated by responsibility:

- SKILL.md is the graph manifest and Mermaid overview.
- steps/*.md are workflow nodes with a shared front matter contract.
- templates/ contains authoring resources, not executable nodes.
- references/task-preflight.md and references/task-handoff.md are root-level
  contracts shared by task-managed Feature and Implement runs.
- task-handoff.md applies the established `se:implement` emoji-title grammar
  to planner, orchestrator, and worker tasks; titles remain display metadata.
- skills/implement/ is the Task execution entry point and owns its task
  profile and topology instead of inheriting the Feature profile; its required
  orchestrator and worker roles are checked before startup.
- scripts/validate-task-contract.sh checks the package statically; it never
  proves that the live ChatGPT/Codex application can create or monitor tasks.
- repository context starts at AGENTS.md and follows the repository's own
  instruction hierarchy; no documentation system is imposed.
- the prototype returns one Feature plus vertical Task dependency graphs,
  including multi-repository Feature links and local dependency waves, without
  implementing code; GitHub publication is the internal final operation and
  requires explicit authorization plus read-after-write verification.
- Feature maintenance is an alternate entry into the same graph: it rehydrates
  the current Feature/Task bundle, reconciles it, and emits a lateral Feature
  changelog comment for each significant published change.
- task-managed Feature and Implement runs pass their skill-owned profiles to
  the shared preflight; task creation authorization and GitHub mutation
  authorization remain independent, with no runtime fallback for a missing
  required role.

SE2 is a parallel design surface and does not replace or mutate the existing
se plugin.
