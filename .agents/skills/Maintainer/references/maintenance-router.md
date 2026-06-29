# Maintenance Router

Use this file first to route maintenance requests to the right playbook.

## Request Types
- `maintain`: inspect one or more existing skills or plugins, detect drift, and apply the right maintenance mode
- `codex-deps`: audit which skills are Codex-dependent versus portable and tighten Codex-tool/runtime wording
- `codex-tool-surface`: check current Codex subagent and Codex App thread tool surfaces and update dependent skill contracts
- `audit`: run consistency/release checks
- `instruction-density`: review whether the same skill behavior can be achieved with fewer instructions before any refactor
- `description-review`: inspect skill descriptions for prompt-budget pressure, selection value, and metadata alignment
- `refresh`: refresh domain best-practices content or bundled skill reference content
- `okf-spec`: refresh the bundled official OKF spec copy and validate the runtime OKF skill

## Decision Tree
1. If the user invokes `$Maintainer` generically with a bare imperative such as `run`, `run your tasks`, or `do a maintenance pass` and does not name a task, classify as `maintain` and use `run-maintenance.md`.
   - Deterministic default flow:
     - inspect local skills and plugins
     - shortlist clear actionable drift
     - upgrade the selected targets
     - sync touched docs
     - audit consistency
     - finish with `release-checklist.md`
   - Do not infer `refresh` or new-skill creation.
2. If the user asks to maintain, upgrade, modernize, tighten, or improve one or more named existing skills or plugins, classify as `maintain` and use `skill-upgrade.md`.
   - If the named target is `okf`, run
     `python3 .agents/skills/Maintainer/scripts/okf_spec_refresh.py --check-stale`
     as part of inspection and report whether the official spec changed.
   - Do not refresh the bundled OKF spec during targeted `maintain okf`
     unless the user explicitly asked for refresh or approved the update.
3. If the user explicitly asks to align or sync skill metadata/docs, classify as `maintain` and use `metadata-sync.md`.
4. If the user asks to review, shorten, compact, or align skill descriptions, classify as `description-review` and use `metadata-sync.md`.
   - If the request is only a review, report proposed wording first.
   - If the user explicitly approves description edits, apply safe metadata trims directly.
   - If a trim could weaken invocation boundaries or workflow guarantees, run `instruction-density-review.md` first.
5. If the user asks which skills are Codex-dependent versus portable, or asks to verify that Codex-dependent skills explicitly use the right Codex tools/runtime contracts, classify as `codex-deps` and use `codex-dependency-audit.md`.
6. If the user asks to check, refresh, or update the Codex tool surface for spawning subagents, managing subagent lifecycle, creating Codex App threads, or keeping `codex-orchestrator` worker/thread contracts current, classify as `codex-tool-surface` and use `codex-tool-surface-refresh.md`.
7. If the user asks whether skill behavior can be achieved with fewer instructions, asks for an instruction-density review, or asks to find compaction opportunities while preserving behavior, classify as `instruction-density` and use `instruction-density-review.md`.
   - This route is read-only by default. Return proposed trims or refactors first, then wait for explicit user approval before editing.
8. If the user asks for repo health, policy compliance, structure checks, or pre-release validation, classify as `audit` and use `doc-consistency.md` plus `release-checklist.md`.
9. If the user asks to refresh bundled Swift-DocC references, review the `swift-docc` manifest, or re-sync the local DocC asset tree against upstream, classify as `refresh` and use `swift-docc-refresh.md`.
10. If the user asks to refresh bundled Swift API Design references, review the `swift-api-design` manifest, or re-sync the local guideline source against upstream, classify as `refresh` and use `swift-api-design-refresh.md`.
11. If the user asks to review, refresh, or periodically re-check TanStack Intent coverage for `skills/tanstack/`, classify as `refresh` and use `tanstack-intent-refresh.md`.
12. If the user asks to review, refresh, align, or periodically re-check TanStack skills coverage against `tanstack-skills/tanstack-skills`, classify as `refresh` and use `tanstack-skills-alignment.md`.
13. If the user asks to refresh, align, or check `skills/okf/` against the latest official OKF spec from `GoogleCloudPlatform/knowledge-catalog`, classify as `okf-spec` and use `okf-spec-refresh.md`.
14. If the user asks to create or bootstrap a brand-new skill, route skill creation through `$skill-creator` first. Return to this maintainer skill only for repo integration or follow-up maintenance after the scaffold exists.
15. If a request mixes categories, run in this deterministic order:
   - `maintain` -> `run-maintenance.md`, `skill-upgrade.md`, or `metadata-sync.md` according to scope
   - `description-review` -> `metadata-sync.md`, with `instruction-density-review.md` first when behavior-sensitive
   - `instruction-density` -> `instruction-density-review.md`, then stop before edits; approved follow-up refactors route through targeted maintenance
   - `codex-deps` -> `codex-dependency-audit.md`
   - `codex-tool-surface` -> `codex-tool-surface-refresh.md`
   - `refresh` -> the specific routed refresh playbook (`swift-docc-refresh.md`, `swift-api-design-refresh.md`, `tanstack-intent-refresh.md`, or `tanstack-skills-alignment.md`)
   - `okf-spec` -> `okf-spec-refresh.md`
   - `audit` -> `doc-consistency.md`, then `release-checklist.md`
16. Always end with `release-checklist.md` for mixed or multi-step maintenance tasks.

## Task Isolation Rule
- Generic bare imperatives map only to the repo-wide mode of `maintain`.
- Run only the routed task playbook unless the user explicitly requests a mixed workflow.
- Do not silently expand generic maintenance into `refresh` or new-skill creation.
- Do not silently expand generic maintenance into `okf-spec` or any other network-backed spec refresh.
- Do not silently expand targeted maintenance into repo-wide `refresh`.
- Do not silently expand metadata-only maintenance into `audit` or `refresh`.
- Do not silently convert an instruction-density review into a refactor. Ask for explicit approval after the proposal before editing.
- Do not silently run `codex-tool-surface`; it is an explicit task because Codex tool availability is runtime-dependent.

## Parallel Delegation Rule
- If subagent tools are available and the user explicitly asked for delegation or parallel agent work, spawn multiple subagents only after the request has been routed to a concrete playbook.
- Prefer explorer subagents for independent read-only inspections and worker subagents only when write ownership is clearly separated.
- Keep routing, playbook selection, final synthesis, and final report assembly in the main agent.

## Output Contract
For every routed workflow, report:
- Scope covered
- Checks executed
- Findings grouped by severity
- Exact files touched (if any)
- Any deferred work
- Use `release-checklist.md` final report fields (`Scope`, `Commands run`, `Files changed`, `Why changed`, `Result`).
