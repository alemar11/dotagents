---
name: maintainer
description: Maintain and re-engineer existing repo skills and plugins through targeted upgrades, runtime-evidence workflow hardening, package migrations, metadata alignment, validation, and explicit refresh workflows.
---

# Maintainer

## Goal
Use this project-maintainer skill to maintain existing skills and plugins in this repository. Its primary job is to turn repository or runtime evidence into scoped package improvements and keep implementation, metadata, validation, and repo-level maintainer docs aligned.
Treat maintenance as one unified task:
- repo-wide pass when the user invokes `$maintainer` generically with a bare imperative such as `run` or `run your tasks`
- targeted maintenance when the user names one or more existing skills or plugins
- metadata-only maintenance when the user explicitly asks to align or sync docs/metadata
- workflow-family hardening when recent executions expose a cross-skill ownership, authority, closeout, or efficiency defect
- package lifecycle work when an existing skill or plugin must be merged, renamed, moved, bundled, replaced, or retired

For the repo-wide pass, inspect the local skills and plugins, choose the ones with clear actionable drift, apply safe scoped upgrades, then run sync, audit, and release-style checks.
Treat domain-refresh work as explicit tasks, not default behavior. For brand-new skills, start with `$skill-creator`; this skill is for maintaining and integrating existing skill and plugin packages.

## Runtime Dependencies

This project-local skill is Codex-dependent for its full maintenance contract.
Workflow-family hardening uses `$skill-audit` plus Codex memory/session evidence
when making portfolio or runtime invocation/routing/cost claims; reproducible
tests, supplied logs, or live failures may establish other defects directly.
Substantial reshapes require `$skill-creator` or `$plugin-creator`, and
non-trivial implementation closeout requires `$autoreview`. It also relies on
the local repository filesystem plus direct shell and `git` inspection.

## User-facing Capability Summary
If the user asks what this skill can do, answer with three capability groups:

1. Maintain existing skills or plugins through targeted package/docs/metadata
   updates, description and instruction-density reviews, consistency checks, and
   Codex-dependency audits.
2. Harden composed workflow families from representative runtime evidence, or
   migrate and retire existing skill/plugin packages with creator-first reshape
   routing and lifecycle validation.
3. Run explicit skill-specific refresh workflows for Swift-DocC, Swift API
   Design, TanStack coverage, Codex worker/thread surfaces, and OKF.

For the exact user-facing task menu, open `references/task-menu.md`.

## Trigger Rules
Use this skill when users ask to:
- Invoke `$maintainer` generically to maintain existing skills or plugins in this repository
- Maintain, upgrade, sync, tighten, or clean up one or more existing skills or plugins
- Maintain, upgrade, sync, tighten, or clean up repo-local plugins or shared repo structure around skills and plugins
- Optimize skill docs, metadata, workflow clarity, or maintainability
- Review, shorten, compact, or align skill descriptions, `agents/openai.yaml` short descriptions, or README skill one-liners
- Review whether skill behavior can be preserved with fewer instructions, or ask for an instruction-density review before refactoring
- Run a proactive skill maintenance pass before release
- Sync `SKILL.md`, `agents/openai.yaml`, and repository docs for one or more skills
- Audit which skills are Codex-dependent versus portable, or tighten Codex-tool/runtime wording for those skills
- Refresh bundled Swift-DocC references and bundled source assets
- Refresh bundled Swift API Design source and thin reference routes
- Refresh TanStack Intent coverage for the local `skills/tanstack/` skill when upstream alpha coverage changes
- Refresh the TanStack skill's `references/` layout or upstream-version fetch guidance when official TanStack Router, Start, CLI, or Intent surfaces change
- Refresh TanStack skills coverage for the local `skills/tanstack/` skill when the upstream `tanstack-skills/tanstack-skills` plugin tree changes
- Refresh or audit the Codex worker/thread tool surface, especially subagent spawning, subagent lifecycle, Codex App thread creation, visible worker behavior, or `codex-orchestrator` worker-surface contracts
- Refresh the bundled OKF spec or align `skills/okf/` with the latest official Open Knowledge Format spec from `GoogleCloudPlatform/knowledge-catalog`
- Integrate a newly scaffolded skill or plugin into repo metadata after `$skill-creator` or `$plugin-creator` has already created the package
- Harden a connected workflow family after sessions, logs, tests, or live failures expose recurring behavioral drift
- Merge, rename, move, bundle, replace, or retire an existing skill or plugin

## Workflow
1) Route the request with `references/maintenance-router.md`.
2) For unified maintenance requests, let the router choose the internal mode:
   - repo-wide pass -> `references/run-maintenance.md`
   - targeted maintenance -> `references/skill-upgrade.md`
   - metadata-only alignment -> `references/metadata-sync.md`
3) For runtime-evidence or composed-workflow hardening, follow `references/workflow-family-hardening.md`.
4) For package migrations, replacements, or retirements, follow `references/package-lifecycle.md`.
5) For structure and rules checks, follow `references/doc-consistency.md`.
6) For description alignment or compaction, follow `references/metadata-sync.md`; use `references/instruction-density-review.md` first when compaction could weaken behavior.
7) For instruction-density reviews, follow `references/instruction-density-review.md`.
8) For Codex dependency audits and portability-boundary checks, follow `references/codex-dependency-audit.md`.
9) For Swift-DocC bundled-reference refresh, follow `references/swift-docc-refresh.md`.
10) For Swift API Design bundled-reference refresh, follow `references/swift-api-design-refresh.md`.
11) For TanStack Intent coverage refresh on `skills/tanstack/`, follow `references/tanstack-intent-refresh.md`.
12) For TanStack skills coverage refresh on `skills/tanstack/`, follow `references/tanstack-skills-alignment.md`.
13) For Codex worker/thread tool surface refresh, follow `references/codex-tool-surface-refresh.md`.
14) For OKF official spec refresh on `skills/okf/`, follow `references/okf-spec-refresh.md`.
15) Before finishing, load `references/options.md`, select the applicable lanes
    from `references/validation-matrix.md`, then run
    `references/release-checklist.md` and report canonical `result` and
    `change_state` values with actionable findings.

## References

- `references/maintenance-router.md`: route the request to the correct maintenance workflow first.
- `references/task-menu.md`: exact user-facing task menu and capability details.
- `references/run-maintenance.md`: use for proactive repo maintenance across one or more existing skills or plugins.
- `references/skill-upgrade.md`: use for scoped improvements to one or more existing skills or plugins.
- `references/workflow-family-hardening.md`: use runtime evidence to harden ownership and handoffs across a connected workflow family.
- `references/package-lifecycle.md`: use for existing-package merges, renames, moves, bundling, replacements, and retirement.
- `references/options.md`: canonical maintainer closeout result options.
- `references/validation-matrix.md`: select validation by the changed package and behavior surface.
- `references/metadata-sync.md`: use for `SKILL.md`, `agents/openai.yaml`, and repo-doc alignment.
- `references/skill_openai_metadata.md`: field-shape reference for maintaining `agents/openai.yaml` UI metadata.
- `references/doc-consistency.md`: use for repository-wide structure and policy checks.
- `references/instruction-density-review.md`: use for read-only reviews that ask whether the same skill behavior can be achieved with fewer instructions before refactoring.
- `references/codex-dependency-audit.md`: use for Codex-dependency classification, portability-boundary checks, and Codex-tool wording audits.
- `references/swift-docc-refresh.md`: use for maintainer-only Swift-DocC bundled-reference refresh work.
- `references/swift-docc-runbook.md`: canonical refresh and review procedure for the `swift-docc` skill.
- `references/swift-api-design-refresh.md`: use for maintainer-only Swift API Design bundled-reference refresh work.
- `references/swift-api-design-runbook.md`: canonical refresh and review procedure for the `swift-api-design` skill.
- `references/tanstack-intent-refresh.md`: use for maintainer-only review of new TanStack Intent coverage relevant to `skills/tanstack/`.
- `references/tanstack-skills-alignment.md`: use for maintainer-only comparison of local `skills/tanstack/` coverage against `tanstack-skills/tanstack-skills/plugins`.
- `references/codex-tool-surface-refresh.md`: use for maintainer-only review of current Codex subagent and Codex App thread tool surfaces that affect `skills/codex-orchestrator/`.
- `references/okf-spec-refresh.md`: use for maintainer-only refresh of the bundled official OKF spec copy and runtime OKF validation layer.
- `references/okf-spec-runbook.md`: canonical refresh and review procedure for the `okf` skill.
- `references/release-checklist.md`: use at the end of mixed or multi-step maintenance tasks.

## Subagent Usage
- Use internal subagents for independent analysis slices or disjoint write scopes when the active runtime policy permits and delegation materially improves speed or quality.
- Ask before delegation only when runtime policy requires it or when creating visible user-owned Codex App threads.
- Prefer explorer subagents for read-only inspection and worker subagents only when file ownership is clearly split.
- Good candidates for parallel delegation in this skill:
  - unified maintenance: split reusable skills, project-local skills, coupled repo-doc inspection, or metadata-only verification into disjoint analysis buckets.
  - `audit`: split metadata drift, README/install prompt drift, and script/reference or policy checks.
  - targeted maintenance: split target skill packages from directly coupled repo docs only when write scopes do not overlap.
- Keep routing, final edit integration, final severity/result synthesis, and final git verification in the main agent.

## Guardrails
- Keep this skill focused on maintaining existing skills and plugins in this repository.
- Prefer concrete skill-level improvements over neutral orchestration language.
- Do not infer `refresh` or new-skill creation from generic maintenance requests.
- Use `$skill-creator` first when the user wants to create a brand-new skill.
- Use `$skill-creator` or `$plugin-creator` first for substantial public package reshapes; return here for repo integration, lifecycle cleanup, validation, and release checks.
- Keep changes scoped to the selected or discovered skills.
- Keep internal delegation within the active runtime policy and the user's scope; do not treat it as authority for external writes or broader maintenance.
- If no meaningful updates are needed, return `result=pass` and
  `change_state=no-change`, and avoid persistent file edits.
