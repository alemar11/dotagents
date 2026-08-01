---
name: maintainer
description: Manually audit, maintain, and re-engineer existing repo skills and plugins through health checks, targeted upgrades, workflow hardening, package lifecycle work, validation, and explicit refreshes.
---

# Maintainer

## Goal

Use this project-maintainer skill only after the user explicitly invokes
`$maintainer`, asks to run Maintainer, or an explicitly invoked parent workflow
routes here. This skill is manual-only. Do not auto-select it for ordinary
skill, plugin, metadata, docs, or repository change requests.

Maintain existing skill and plugin packages through one routed control plane:

- A bare `run`, `run your tasks`, or equivalent imperative starts a
  conservative repo-wide maintenance pass.
- Named packages stay targeted; explicit metadata wording stays metadata-only.
- Health and instruction-density audits are read-only evidence passes.
- Runtime failures, package lifecycle work, and domain refreshes use their
  explicit routes and never expand from a bare run.
- Brand-new skills start with `$skill-creator`. Substantial public skill or
  plugin reshapes start with `$skill-creator` or `$plugin-creator`, then return
  here for integration, validation, and cleanup.

## Runtime Dependencies

This project-local skill is Codex-dependent. Use `$skill-audit` read-only when
health or workflow-family claims require portfolio, writing-quality, prompt-cost,
or session evidence. Use `$skill-creator` or `$plugin-creator` for substantial
public reshapes and native `codex review` for non-trivial implementation closeout. The
remaining workflows rely on the local repository filesystem, shell, and `git`.

## Routing And Progressive Disclosure

Always open [references/maintenance-router.md](references/maintenance-router.md)
first. It owns request routing,
mixed-route order, task isolation, delegation, and common output handling. Open
only the branch references whose conditions match the routed request:

| Condition | Required reference |
| --- | --- |
| The user asks what Maintainer can do | [task-menu.md](references/task-menu.md) |
| Bare or repo-wide maintenance pass | [run-maintenance.md](references/run-maintenance.md) |
| One or more named existing packages | [skill-upgrade.md](references/skill-upgrade.md) |
| Metadata, descriptions, or repo-doc alignment | [metadata-sync.md](references/metadata-sync.md) |
| Editing `agents/openai.yaml` fields | [skill_openai_metadata.md](references/skill_openai_metadata.md) |
| Skill or repository health, policy compliance, or pre-release audit | [skill-health.md](references/skill-health.md) |
| Behavior-preserving compaction or instruction-density review | [instruction-density-review.md](references/instruction-density-review.md) |
| Runtime evidence exposes a connected workflow defect | [workflow-family-hardening.md](references/workflow-family-hardening.md) |
| Merge, rename, move, bundle, replace, or retire a package | [package-lifecycle.md](references/package-lifecycle.md) |
| Codex-dependency or portability-boundary audit | [codex-dependency-audit.md](references/codex-dependency-audit.md) |
| Swift-DocC asset refresh | [swift-docc-refresh.md](references/swift-docc-refresh.md) and [swift-docc-runbook.md](references/swift-docc-runbook.md) |
| Swift API Design source refresh | [swift-api-design-refresh.md](references/swift-api-design-refresh.md) and [swift-api-design-runbook.md](references/swift-api-design-runbook.md) |
| TanStack Intent coverage refresh | [tanstack-intent-refresh.md](references/tanstack-intent-refresh.md) |
| TanStack skills coverage alignment | [tanstack-skills-alignment.md](references/tanstack-skills-alignment.md) |
| Codex worker/thread tool-surface refresh | [codex-tool-surface-refresh.md](references/codex-tool-surface-refresh.md) |
| OKF official-spec refresh | [okf-spec-refresh.md](references/okf-spec-refresh.md) and [okf-spec-runbook.md](references/okf-spec-runbook.md) |

Before closeout, load [options.md](references/options.md), select every
applicable lane from [validation-matrix.md](references/validation-matrix.md),
and finish with [release-checklist.md](references/release-checklist.md). Emit
canonical `result` and `change_state` values and actionable findings.

## Execution Boundaries

- Direct `audit` and instruction-density routes remain read-only. `$skill-audit`
  findings are evidence, not automatic cleanup authority.
- A bare maintenance run may apply only safe, low-ambiguity improvements with a
  concrete rationale. Report strategic, behavior-sensitive, or high-ambiguity
  candidates for approval.
- Keep refresh, workflow hardening, package lifecycle, and new-skill creation
  explicit.
- Resolve commit, push, PR, and other publication authority independently; do
  not infer Git mutations from maintenance authority.
- Keep changes scoped to the selected or discovered packages and preserve
  unrelated dirty worktree state.
- If no meaningful update is needed, return `result=pass` and
  `change_state=no-change` without persistent edits.
