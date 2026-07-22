# Standalone Skill Audits

Use this workflow for standalone skills under project-local, shared, or global
skill roots.

## Resolution

- Check project-local roots first:
  - `.agents/skills`
  - `.codex/skills`
  - `skills`
- Widen to shared/global roots only when needed:
  - `$CODEX_HOME/skills` when `$CODEX_HOME` is set
  - `~/.codex/skills`
  - `~/.agents/skills`
- If a root is a symlink farm, resolve the underlying skill once rather than
  double-counting both the symlinked view and the source.

## What To Inspect

- `SKILL.md`
- `agents/openai.yaml` when present
- directly coupled `references/*`, `scripts/*`, or `assets/*` only when needed
  to answer the audit question
- repo docs or adjacent docs that may have become the real source of truth

## What To Evaluate

- current role in the repo or workflow
- whether it matches recurring work actually seen in history
- whether its triggers are too weak, too broad, or stale
- whether its guardrails, validation steps, or paths are outdated
- whether `SKILL.md` and `agents/openai.yaml` drift from each other
- whether it duplicates or overlaps another installed or shared skill
- whether missing project-specific behavior should live in the reusable skill,
  in project docs or memory, or only as a last-resort project-maintained
  specialization
- whether it adds prompt weight without enough value when current context
  exposes that signal
- whether `references/writing-style-review.md` is needed to diagnose trigger
  clarity, prompt load, information hierarchy, or pruning issues

## Historical Evidence Hints

Use `references/historical-evidence.md` without changing its order. Useful
target-specific keys include skill name, `SKILL.md` and `agents/openai.yaml`
paths, exact `cwd`, repository basename, and specific failure text. Use
`git -C <skills-root> log -- <relative-skill-dir>` when the owning repository
is outside the current checkout.

## Ownership Guidance

- Put findings on `standalone-skill` when the problem is in the skill contract,
  references, scripts, or metadata.
- Put findings on `docs` when the missing context is project-specific but does
  not justify a skill change.
- If overlap exists with a bundled plugin skill or plugin package, call that
  out explicitly instead of forcing a skill-only conclusion.
