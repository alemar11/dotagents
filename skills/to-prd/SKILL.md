---
name: to-prd
description: Convert clarified product or feature intent into a repo-backed PRD. Use when the user asks for a PRD, wants to turn a grilled conversation into a product requirements document, or needs a PRD artifact before splitting work into implementation issues.
---

# To PRD

## Goal

Turn clarified feature, product, migration, or workflow intent into a practical
PRD that can feed `$to-issues`.

Use this after requirements have been sharpened by conversation or
`$grill-with-docs`. If the request is still too vague to produce a useful PRD,
ask the smallest blocking question set or recommend running `$grill-with-docs`
first.

## Boundaries

- Do not implement the feature.
- Do not split the PRD into implementation issues; use `$to-issues` for that.
- Do not invent requirements, users, constraints, or acceptance criteria that
  are not supported by user input, repo evidence, or project memory.
- Ask for confirmation before writing a PRD file or publishing to an issue
  tracker unless the user explicitly asked to write/publish or a composing
  skill passes explicit write authorization after resolving gates.

## Workflow

### 1. Ground in project memory

Inspect the current project context before drafting:

- `project-memory/agents/issue-tracker.md`
- `project-memory/agents/triage-labels.md`
- `project-memory/agents/domain.md`
- `CONTEXT.md` or `CONTEXT-MAP.md`
- `project-memory/adr/`
- README, product docs, issue templates, and relevant source/tests

If setup files are missing, continue with repo evidence and say which project
memory files were unavailable.

### 2. Confirm the PRD source

Identify the source material:

- user conversation or pasted notes,
- output from `$grill-with-docs`,
- an existing issue, doc, or planning note,
- repo behavior that needs to become a defined product surface.

If key facts are missing, ask only for decisions that would materially change
the PRD. Prefer defaults when the repo or project memory already implies them.

### 3. Draft the PRD

Use `references/prd-template.md` unless the repo has a stronger local PRD
format.

Keep the PRD implementation-facing:

- clear problem and target user,
- goals and non-goals,
- functional requirements,
- user workflow or system behavior,
- data, permissions, API, or integration constraints when relevant,
- acceptance criteria,
- risks and open questions,
- notes for later issue splitting.

### 4. Choose publication target

Read `project-memory/agents/issue-tracker.md` to determine where PRDs live:

- GitHub: publish only after confirmation, using `gh`, the title format
  `PRD: <Feature Name>`, and the mapped `feature` issue type when available.
- Local markdown: write to `.scratch/<feature-slug>/PRD.md` only after
  confirmation.
- Other tracker: follow the repo-specific instructions in
  `project-memory/agents/issue-tracker.md`.

For GitHub PRDs, derive `<Feature Name>` from the accepted product name or
short feature phrase in title case. Do not include issue numbers, status labels,
or implementation slice names in the PRD title.

Read `project-memory/agents/triage-labels.md` for the mapped `feature` type.
When GitHub issue types are available, create or update the PRD issue with that
mapped type, usually `Feature`. If issue types are disabled or unsupported,
publish the PRD without a type and keep the PRD title/body convention intact.

If a composing skill such as `$plan-feature` passes explicit write
authorization, use the configured target without re-asking unless this skill
finds a new blocker or unresolved question.

If no issue-tracker setup exists, return the PRD in chat and recommend running
`$setup-project-memory` before publishing.

### 5. Report completion

Return:

- PRD title,
- target location or "chat only",
- issue type applied, when the tracker supports it,
- any open questions,
- whether it is ready for `$to-issues`.

## Guardrails

- Do not hide uncertainty. Put unresolved decisions in `## Open Questions`.
- Do not make the PRD a broad architecture plan; keep implementation details at
  the level needed for issue splitting.
- Do not create issues from the PRD in this skill.
- Preserve existing PRD content when updating a local PRD file; revise only the
  sections needed for the current source material.

## References

- `references/prd-template.md`: default PRD shape.
