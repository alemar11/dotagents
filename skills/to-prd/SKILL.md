---
name: to-prd
description: Convert clarified product or feature intent into a project-backed PRD. Use when the user asks for a PRD, wants to turn a grilled conversation into a product requirements document, or needs a PRD artifact before splitting work into implementation issues.
---

# To PRD

## Goal

Turn clarified feature, product, migration, cross-repo project, or workflow
intent into a practical PRD that can feed `$to-issues`.

Use this after requirements have been sharpened by conversation or
`$grill-me-with-context`. If the request is still too vague to produce a useful PRD,
ask the smallest blocking question set or recommend running `$grill-me-with-context`
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
- orchestrator workspace docs such as `projects/<project>/PROJECT.md` and
  `projects/<project>/repos/*.md`, when the tracker config uses orchestrator
  mode
- README, product docs, issue templates, and relevant source/tests

If setup files are missing, continue with repo evidence and say which project
memory files were unavailable.

### 2. Confirm the PRD source

Identify the source material:

- user conversation or pasted notes,
- output from `$grill-me-with-context`,
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

Do not include workflow status fields such as `Status: Draft` in the PRD body.
PRD readiness and lifecycle state belong in the issue tracker, mapped labels,
or the generated implementation issues, not in the PRD content itself.

### 4. Choose publication target

Read `project-memory/agents/issue-tracker.md` to determine where PRDs live:

- `Tracker mode: github`: publish only after confirmation through
  `$github-issues`, using the title format `PRD: <Feature Name>` and the
  mapped `feature` issue type when available.
- `Tracker mode: local-markdown`: write to the configured repo-local PRD path,
  normally `.scratch/<feature-slug>/PRD.md`, only after confirmation.
- `Tracker mode: orchestrator-local`: write to the configured orchestrator
  feature PRD path,
  `projects/<project-slug>/features/<feature-slug>/PRD.md`, only after
  confirmation. Derive or ask for `<project-slug>` before writing. `$to-prd`
  owns the PRD and may create or update
  `projects/<project-slug>/PROJECT.md`,
  `projects/<project-slug>/repos/<repo-slug>.md`, and
  `projects/<project-slug>/features/<feature-slug>/integration-gates.md` only
  from accepted project, repo, or PRD source material needed for planning.
- `Tracker mode: orchestrator-github`: publish the PRD parent issue in the
  configured coordination repo through `$github-issues`. Derive or ask for
  `<project-slug>`, ensure the GitHub label named exactly `<project-slug>`
  exists in the coordination repo, and apply it to the PRD parent issue. The
  PRD issue is the parent for vertical feature issues.
- Other tracker: follow the repo-specific instructions in
  `project-memory/agents/issue-tracker.md`.

For GitHub and GitHub coordination PRDs, derive `<Feature Name>` from the
accepted product name or short feature phrase in title case. Do not include
issue numbers, status labels, or implementation slice names in the PRD title.

For orchestrator workspace PRDs, include repository scope, cross-repo
contracts, integration gates, and release or validation order when those affect
issue splitting.

For GitHub coordination PRDs, treat the project label as required issue
metadata. It is separate from the mapped issue type and workflow-state labels.

Read `project-memory/agents/triage-labels.md` for the mapped `feature` type.
When GitHub issue types are available, create or update the PRD issue with that
mapped type, usually `Feature`. If issue types are disabled or unsupported,
publish the PRD without a type and keep the PRD title/body convention intact.
Use `$github-issues` for the GitHub create, type, label, and dry-run command
mechanics.

If a composing skill such as `$plan-feature` passes explicit write
authorization, use the configured target without re-asking unless this skill
finds a new blocker or unresolved question.

If the configured target is GitHub or GitHub coordination but external mutation
is not authorized for the current run, do not mutate GitHub. Ask
`$github-issues` for the exact draft publish command and return it with the PRD
body, or use the configured local dry-run target if
`project-memory/agents/issue-tracker.md` records one.

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
