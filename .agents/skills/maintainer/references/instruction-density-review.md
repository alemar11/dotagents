# Instruction Density Review Playbook

Use this playbook when the user asks whether one or more skills can preserve the
same behavior with fewer instructions, asks for an instruction-density review, or
asks for compaction opportunities before refactoring.

## Purpose
- Find places where a skill's runtime behavior can be achieved with fewer,
  clearer, or better-routed instructions.
- Preserve the target's trigger rules, workflow guarantees, guardrails,
  validation expectations, and portability/Codex-dependency boundaries.
- Return a read-only proposal first, then wait for explicit user approval before
  editing, refactoring, staging, committing, or moving content.

## Task Boundary
- Default scope per target skill:
  - `SKILL.md`
  - `SKILL.md` frontmatter descriptions when they duplicate trigger rules, workflow details, or guardrails
  - directly referenced `references/*.md`
  - `agents/openai.yaml` when metadata wording contributes to duplicated or
    conflicting runtime instructions
  - `README.md` or `AGENTS.md` only when repo docs duplicate target-specific
    runtime behavior or create contradictory guidance
- For plugin or bundled-skill targets, include the owning plugin manifest only
  when package metadata contributes to instruction duplication or target
  confusion.
- This playbook is not a content refresh. Do not update domain guidance,
  upstream docs, generated assets, or runtime scripts unless the user separately
  approves that maintenance work.

## Review Workflow
1. Resolve the target skill, plugin, or bundled skill. If no target is named,
   ask whether the user wants a repo-wide scan or a specific high-value target.
2. Read the target entrypoint and only the references needed to understand
   duplicated behavior, routing, or guardrails.
3. Identify the behavior each dense section protects:
   - trigger or invocation boundary
   - workflow order
   - safety or mutation guardrail
   - output contract
   - metadata or repo-doc alignment
   - description selection value and prompt-budget pressure
   - optional-tool or portability boundary
4. Measure entrypoint size and representative invoked-path cost using
   `skill-health.md`. When the entrypoint is outside `normal`, descriptions or
   overlaps are suspect, instruction sprawl is visible, or runtime behavior is
   in question, invoke `$skill-audit` read-only for deeper evidence. Treat size
   as diagnostic, never as a standalone failure.
5. Classify every candidate:
   - `safe trim`: remove redundant wording without changing behavior
   - `move to reference`: keep behavior but route dense detail out of `SKILL.md`
   - `behavior-risk`: compaction could weaken a trigger, guardrail, or contract
   - `leave as-is`: verbosity is load-bearing or cheaper than indirection
6. Recommend the smallest refactor that preserves behavior. Prefer a scoped
   section rewrite or reference extraction over a whole-file rewrite.
7. Stop after the proposal. Ask for explicit approval before applying any
   compaction refactor. Treat approved follow-up refactors as targeted
   maintenance using `skill-upgrade.md`.

## Proposal Output
Report:
- Scope reviewed
- Behavior that must be preserved
- Candidate changes grouped by `safe trim`, `move to reference`,
  `behavior-risk`, and `leave as-is`
- Expected line-count or prompt-weight reduction when it is easy to estimate
- Files that would be touched if approved
- Specific approval question before edits

## Refactor Rules After Approval
- Re-read the whole target `SKILL.md` before editing.
- Preserve behavior first; shorter text is not a win if it makes invocation,
  safety, or output contracts ambiguous.
- Keep `SKILL.md` as the entrypoint and move long-form detail to `references/`
  only when the reference remains discoverable from the entrypoint.
- Update `agents/openai.yaml`, `README.md`, or `AGENTS.md` only when the wording
  or durable repo guidance actually changes.
- Run the focused checks from `skill-health.md` and finish with
  `release-checklist.md` for any approved edit pass.
