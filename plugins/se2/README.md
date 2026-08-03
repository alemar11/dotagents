# SE2

SE2 is an experimental issue-first, graph-first Feature planning plugin.

Its initial feature skill is deliberately small:

- SKILL.md is the graph manifest and Mermaid overview.
- steps/*.md are workflow nodes with a shared front matter contract.
- templates/ contains authoring resources, not executable nodes.
- repository context starts at AGENTS.md and follows the repository's own
  instruction hierarchy; no documentation system is imposed.
- the prototype returns one Feature plus vertical Task dependency graphs,
  including multi-repository Feature links and local dependency waves, without
  implementing code; GitHub publication is the internal final operation and
  requires explicit authorization plus read-after-write verification.
- Feature maintenance is an alternate entry into the same graph: it rehydrates
  the current Feature/Task bundle, reconciles it, and emits a lateral Feature
  changelog comment for each significant published change.

SE2 is a parallel design surface and does not replace or mutate the existing
se plugin.
