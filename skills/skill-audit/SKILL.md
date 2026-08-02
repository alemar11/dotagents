---
name: skill-audit
description: Read-only audit of explicitly named installed Codex skills, plugins, and bundled plugin skills using historical evidence or active Codex App task monitoring. Use only when explicitly invoked as $skill-audit.
---

# Skill Audit

## Activation

Use this skill only after an explicit `$skill-audit` invocation or explicit
selection from the skill UI. Do not activate it merely because a request
mentions skill health, cost, usage, plugins, or auditing. If it was not
explicitly selected, keep the request on the normal workflow and do not load
this skill.

## Overview

Audit installed standalone skills, plugin packages, and bundled plugin skills
before proposing new surfaces. Prefer improving, merging, or disabling an
existing owner when the evidence supports it.

Use live monitoring when the user asks to observe active tasks, evaluate a
skill or plugin while it runs, or annotate defects from current behavior. Live
monitoring reads App task state directly and does not substitute session
archives for unavailable current evidence.

This skill is Codex-dependent. Repo files and installed manifests are the
editable source of truth; Codex memory, rollout summaries, session JSONL, and
cache copies are evidence only.

## Non-negotiables

- Audits are read-only. Record findings; edit, commit, or publish only after the
  user explicitly switches the named target to implementation mode.
- Live audits never message, steer, pause, archive, or otherwise mutate a
  monitored task. Keep annotations in the audit task unless the user separately
  authorizes another destination and workflow.
- Never edit session archives or `~/.codex/plugins/cache/...`.
- Named targets are the primary and normally exclusive scope. Include another
  target only to explain a concrete overlap or ownership conflict.
- Self-audit is opt-in: include `skill-audit` only when the user names it. For a
  full-portfolio audit, exclude it and offer a separate follow-up.
- Keep findings decision-oriented and evidence-backed.

## Canonical Audit DAG

Follow this directed acyclic workflow. References add branch-specific rules;
they do not replace or reorder these nodes.

1. Classify the request as `historical` or `live`.
2. Discover candidate targets:
   - historical named audit: use the named targets;
   - historical portfolio audit: discover relevant installed surfaces;
   - live audit: discover the selected active tasks, then attribute actual
     repository-owned skill or plugin use from task evidence.
3. Resolve each candidate to its editable owner. If resolution fails, report
   the miss; do not substitute a near match. For cached or unclear plugin
   paths, load `references/cache-resolution.md`.
4. Classify each resolved target and load exactly one target overlay:
   - `standalone-skill`: `references/standalone-skills.md`;
   - `plugin-package`: `references/plugins.md`;
   - `bundled-plugin-skill`: `references/bundled-plugin-skills.md` plus the owning
     manifest.
5. Collect behavior evidence through exactly one route:
   - historical: `references/historical-evidence.md`;
   - live: `references/live-monitoring.md`.
6. Load optional lenses only when their predicates match:
   - merge, disable, duplicate, usage, or prompt-budget decision:
     `references/portfolio-hygiene.md`;
   - trigger clarity or instruction-density review:
     `references/writing-style-review.md`.
7. Classify each finding by evidence strength and owning fix surface.
8. Return the historical or live branch from `references/output-format.md`.

Named targets remain the primary and normally exclusive scope. An unnamed
portfolio audit widens only as the question requires. A full-portfolio audit
excludes `skill-audit` unless the user explicitly opts into self-audit.

## Output Expectations

Return a compact audit using the format in
`references/output-format.md`. Live runs use its live-monitor format and retain
stable defect IDs for the duration of the monitor.

## Conditional Evidence Helpers

Do not run either helper for every audit. Select the smallest evidence route
that answers the explicit request:

- Use `scripts/session-evidence` for historical claims about actual invocation,
  runtime use, missed or false triggers, or orchestration behavior.
- Use `scripts/portfolio-health` only for portfolio-level health or cost
  questions such as inventory budget, entrypoint size, duplicates, descriptions,
  or heuristic recent usage.
- For static contract, trigger, ownership, or writing review, inspect the
  target files and references directly without a helper.
- For live audits, read current App task evidence directly; do not substitute
  either helper for live monitoring.

Treat helper output as evidence, not as permission to edit, delete, disable, or
publish. Run `--help`, `--version`, and `--json doctor` only when validating a
touched helper or diagnosing its availability.

- Both helpers are Python standard-library scripts shipped directly under
  `scripts/`.
- Keep each helper's `--version` output as its semver source of truth.
- Both helpers use the JSON envelope `{ok, version, command, data}`. Their v1
  contracts have no retired option or field aliases.
- Bump major for breaking flags or fields, minor for backward-compatible
  capabilities, and patch for backward-compatible fixes.

## Follow-up

If the user asks to create a brand-new skill or substantially reshape one,
switch to `$skill-creator` and implement that change rather than continuing the
audit.

If the user asks to update an existing plugin package, bundled plugin skill, or
standalone skill, leave audit mode and switch into implementation mode using
the owning project's maintenance workflow.
