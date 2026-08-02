# Project Context Maintenance

`plugins/software-project/skills/project-context/` owns durable project context, ADR routing, optional
localization memory, confirmed durable capture, Code Review Rules, and
explicit `AGENTS.md` compaction proposals. Runtime behavior stays in `SKILL.md`
and routed references.

## Ownership map

- `references/options.md` owns the complete selectable-field registry. Keep
  execution context, write authority, confirmation, evidence, and capture
  results as data rather than options.
- `references/domain.md`, `domain-modeling.md`, `durable-capture.md`,
  `agents-compaction.md`, `code-review-rules.md`, and
  `documentation-shapes.md` own their named workflows and shapes.
- Consumer repositories own root/scoped `CONTEXT.md`, optional
  `TRANSLATION.md`, `project-context/`, and the closest applicable
  `AGENTS.md`. This package must not invent repository paths or copy facts
  without evidence and authority.
## Maintenance contract

- The skill has no persistent configuration and no tracker, publication,
  delivery, or worker-orchestration contract. Do not reintroduce
  `project-context/config/` or move workflow-owned metadata here.
- Keep the consumer structure canonical: one repository-root
  `project-context/` with flat topic files and `adr/` for accepted decisions;
  root `CONTEXT.md` is the entry point, `TRANSLATION.md` is optional and
  evidence-backed, and nested context roots are not created for monorepo
  scopes.
- Keep always-active invariants and the minimum normative Code Review Rules in
  the closest `AGENTS.md`; conditional detail, matrices, history, and
  provenance belong in indexed context files or references.
- Durable capture and compaction are proposal-first unless the caller supplies
  explicit scoped authority. Preserve unrelated text, show exact target and
  wording, require affirmative confirmation where the runtime contract says
  so, and suffix inserted AGENTS learning bullets with ` (Codex learning)`.
- Keep the Software Project workflow contract as the feature metadata owner and
  GitStack as transport owner. Project Context may route to those contracts but
  must not duplicate their values or publication rules.

## Validation

- Run focused Markdown, link, stale-vocabulary, and documentation-diff checks
  for reference changes. Validate context pointers, ADR indexes, and absence
  of duplicate normative rules for surface changes.
