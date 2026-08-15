# Codex Dependency Audit Playbook

Use this playbook when the user asks to audit which skills are Codex-dependent versus portable, or to tighten how Codex-specific runtime tools and contracts are documented.

## Purpose
- Keep each targeted skill's portability contract accurate in its `SKILL.md`.
- Keep package-specific maintenance implications in the nearest local
  `AGENTS.md` when that contract is needed; do not turn the root `AGENTS.md`
  into a per-skill inventory.
- Ensure Codex-dependent skills explicitly describe the semantic runtime
  capabilities, artifacts, or filesystem contracts they require.
- Ensure portable skills keep Codex-only helpers optional and provide a generic fallback path.

## Classification Rules
- `Codex-dependent`
  - The skill cannot run seamlessly in another agent runtime without
    adaptation because it requires Codex-branded runtime outcomes, paths, or
    artifacts.
  - Common signals:
    - Codex CLI or Codex App version discovery
    - `~/.codex/*`, `$CODEX_HOME`, Codex memory/session files, or Codex-only repo contracts
    - Codex-only task lifecycle or maintainer capabilities with no generic
      fallback
- `Codex-aware but portable`
  - The skill may mention Codex-only helpers, but they are optional accelerators and the skill still describes a generic fallback.
  - Common signals:
    - optional structured interaction with a normal chat fallback
    - optional subagent review with a local review fallback
- `Portable`
  - The skill's workflow is expressed in general shell, git, docs, or project-local terms and does not materially depend on Codex-specific runtime features.

## Workflow
1. Inspect the targeted skills' `SKILL.md` files, nearest local `AGENTS.md`
   when present, and directly coupled docs for:
   - Codex-branded runtime capability mentions
   - Codex filesystem or memory/session path assumptions
   - whether those dependencies are required or optional
   - whether a generic fallback exists when Codex-only helpers are mentioned
2. Classify each targeted skill as `Codex-dependent`, `Codex-aware but portable`, or `Portable`.
3. If the classification changed, update the targeted skill's `SKILL.md`; update
   its local `AGENTS.md` only when the maintenance contract also changes.
4. For Codex-dependent skills, tighten wording so the required outcome,
   topology, authorization, lifecycle, verification, and recovery contract is
   explicit without encoding live callable names or payload shapes.
5. For portable skills, rewrite Codex-only helper mentions so they stay explicitly optional and keep a generic fallback.
6. Run `metadata-sync.md` if any repo-facing descriptions changed.
7. Run the relevant checks from `skill-health.md` and finish with
   `release-checklist.md`.

## Quality Gates
- Every Codex-dependent skill clearly states the semantic Codex runtime
  contract it requires.
- No portable skill accidentally hard-requires a Codex-only helper.
- `result=pass` with `change_state=no-change` is valid when the inventory and
  wording are already correct.

## Branch Report Additions

Add the audited skills and classification result per skill to the common final
report owned by `release-checklist.md`.
