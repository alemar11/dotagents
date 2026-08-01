# Project Context Maintenance

`skills/project-context/` is the reusable owner of durable project context,
localization memory, ADR routing, confirmed durable capture, AGENTS.md
compaction proposals, and evidence-backed Code Review Rules. Runtime behavior
belongs in `SKILL.md` and the routed references.

## Ownership map

- `references/options.md` owns canonical selectable fields and values; do not
  add execution context, confirmation state, or capture results as options.
- `references/domain.md`, `domain-modeling.md`, `durable-capture.md`,
  `agents-compaction.md`, `code-review-rules.md`, and
  `documentation-shapes.md` own their respective workflows and shapes.
- Consumer repositories own root/scoped `CONTEXT.md`, optional
  `TRANSLATION.md`, `project-context/`, and the closest applicable
  `AGENTS.md`. This package must not invent repository paths or copy durable
  facts without evidence and authority.
- `scripts/extract_recent_transcript.py` is an optional Codex-session evidence
  helper. It emits JSON, writes no config, and is not a source of durable truth.
- The skill has no persistent configuration and no tracker or publication
  contract. Use focused Markdown, path, helper, stale-vocabulary, and
  documentation-diff checks for maintenance.

## Durable-boundary rules

- Keep runtime guidance separate from maintainer routing. Preserve unrelated
  project prose when updating pointers, Code Review Rules, or compaction
  proposals.
- Keep evidence, evaluation matrices, history, and before/after proposals in
  references or run reports; write only the exact named durable surfaces
  authorized by the caller or confirmed by the user.
- Keep always-active invariants in `AGENTS.md`; conditional detail belongs in
  indexed flat topic files under the consumer repository's `project-context/`.
