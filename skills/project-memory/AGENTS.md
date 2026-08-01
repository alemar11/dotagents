# Project Memory Maintenance

`skills/project-memory/` is the reusable owner of tracker routing, domain
memory, localization memory, ADR routing, and evidence-backed Code Review Rules.
Its runtime behavior belongs in `SKILL.md` and the routed references.

## Ownership map

- `references/options.md` owns the four genuine controls and canonical values;
  do not add execution context or result state as options.
- `references/domain-modeling.md`, `code-review-rules.md`, and
  `documentation-shapes.md` own their respective durable-document workflows.
- Consumer repositories own their root `CONTEXT.md`, `project-memory/`, and
  closest applicable `AGENTS.md`; this package must not invent repository paths
  or copy durable project facts without evidence and authority.
- The skill has no shipped executable or test runner. Use focused Markdown,
  path, stale-vocabulary, and documentation-diff checks for maintenance.

## Durable-boundary rules

- Keep runtime guidance separate from maintainer routing. Preserve unrelated
  project prose when updating generated pointers or Code Review Rules.
- Keep evidence, evaluation matrices, and history in the references or run
  report; write only the exact named durable surfaces authorized by the caller.
