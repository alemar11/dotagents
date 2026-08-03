# SE2 Learn Project Context Maintenance

plugins/se2/skills/learn/ owns durable project context, ADR routing, optional
localization memory, confirmed durable capture, Code Review Rules, and explicit
AGENTS.md compaction proposals. Runtime behavior stays in SKILL.md and the
routed references.

## Ownership map

- references/options.md owns the complete selectable-field registry. Keep
  execution context, authority, confirmation, evidence, and results as data.
- references/domain.md, domain-modeling.md, durable-capture.md,
  agents-compaction.md, code-review-rules.md, and documentation-shapes.md own
  their named workflows and shapes.
- Consumer repositories own root/scoped CONTEXT.md, optional TRANSLATION.md,
  project-context/, and the closest applicable AGENTS.md. This package must not
  invent repository paths or copy facts without evidence and authority.

## Maintenance contract

- This package has no persistent configuration and no tracker, publication,
  delivery, provider, or worker-orchestration contract. Never reintroduce
  project-context/config/ or move workflow-owned metadata here.
- Keep the consumer structure canonical: one repository-root project-context/
  with flat topic files and adr/ for accepted decisions; root CONTEXT.md is the
  entry point and TRANSLATION.md is optional.
- Keep always-active invariants and the minimum normative Code Review Rules in
  the closest AGENTS.md; conditional detail, matrices, history, and provenance
  belong in indexed context files or these references.
- Durable capture and compaction are proposal-first unless the caller supplies
  explicit scoped authority. Preserve unrelated content and verify links,
  indexes, targets, and the final diff.
- Keep this package independent from plugins/se/skills/learn/. Do not add an
  import, alias, compatibility wrapper, or automatic synchronization path.
- Do not add model selection, task profiles, application-task delegation, or
  GitHub transport to this runtime skill.

## Validation

- Parse front matter and UI metadata, verify every routed reference, and check
  the package-local ownership map.
- Scan for stale legacy SE Learn invocations, imports or aliases to the SE package,
  direct provider/tracker behavior, task profiles, and unowned links.
- Preserve unrelated plugin docs and run git diff --check.
