---
name: skill-audit
description: Audit installed or user-specified Codex skills, plugins, or bundled plugin skills using project history, repo evidence, memory, sessions, and current context to plan updates, additions, merges, or disables. Use when a user asks how their installed Codex surfaces are performing, wants a one-by-one refinement roadmap, asks to audit a skill, a plugin, or a bundled plugin skill, or wants evidence-based recommendations before changing those surfaces.
---

# Skill Audit

## Overview

Audit installed Codex surfaces before proposing new ones.

Treat the installed surface portfolio as the primary subject by default.
Supported target kinds are:

- standalone skill
- plugin package
- bundled plugin skill

Prefer updating, merging, or disabling existing surfaces before recommending
new ones. Treat project-local specializations as a last resort.

Default full-scope audits should stay workflow-first and mixed. Start from the
current workflow, repo docs, named tasks, and relevant local surfaces, then
widen only when the workflow or named target requires it.

This skill is Codex-dependent. It may use Codex prompt context, Codex memory
artifacts, rollout summaries, and session JSONL when those are available.
Treat those surfaces as evidence only; the editable source of truth lives in
the owning checkout or install root.
When raw session behavior matters, the skill-owned helper
`scripts/session-evidence` can extract target-specific invocation evidence
from Codex session JSONL files. It is a shipped runtime helper for audit work;
do not edit or route fixes to session archives themselves.

If the user explicitly names one or more targets, such as `audit skill
$my-skill`, `audit plugin $my-plugin`, or `audit [$my-plugin:publish](...)`,
treat those named targets as the required audit scope and resolve them before
any broader workflow discovery.

Treat `skill-audit` self-audit as opt-in only. Unless the user explicitly
names `skill-audit`, do not audit it, do not add it implicitly because it
appears relevant, and do not include it in the audited set.

In full-portfolio audits, exclude `skill-audit` from the audited set by
default. After presenting the suggestions for the other audited targets,
explicitly ask the user whether they want a follow-up audit of `skill-audit`
too.

## Target Resolution

- Resolve user-provided scope first.
  - If the user names one or more targets explicitly, those names define the
    primary audit target set.
  - Accept singular or plural phrasing such as `audit skill $my-skill`, `audit
    plugin $my-plugin`, `audit [$my-plugin:publish](...)`, or `review only
    $my-skill`.
- Detect target kind before going deep.
  - Treat a standalone skill root or skill path as `skill`.
  - Treat a plugin root or plugin name as `plugin`.
  - Treat a bundled skill under a plugin package or cache snapshot as
    `bundled plugin skill`.
- Keep targeted audits targeted.
  - If the user names specific targets, do not expand to a wider portfolio
    scan.
  - In that mode, never auto-include `skill-audit`; include it only when it
    was explicitly requested.
  - Only bring in non-requested targets when needed to explain overlap, merge
    candidates, or ownership conflicts.
- Keep full-portfolio audits scoped too.
  - When auditing the installed portfolio, do not auto-include `skill-audit`
    in the findings.
  - After presenting the non-`skill-audit` recommendations, ask the user
    whether they want to audit `skill-audit` too.
- Be explicit about misses.
  - If a named target cannot be resolved, say so clearly.
  - Do not silently substitute a near match or widen the audit scope.

## Reference Routing

After detecting the target kind, open the matching workflow reference:

- `references/standalone-skills.md`
  - Use for standalone project-local, shared, or global skills.
- `references/plugins.md`
  - Use for plugin package audits.
- `references/bundled-plugin-skills.md`
  - Use for bundled plugin skills.
  - When auditing a bundled plugin skill, also inspect the owning plugin
    package, including `.codex-plugin/plugin.json`.
- `references/cache-resolution.md`
  - Use whenever a target path lives under `~/.codex/plugins/cache/...` or when
    a bundled target's editable owner is unclear.

Open only the references needed for the current target and questions. Do not
bulk-load all reference files by default.

## Session Evidence Helper

Use `scripts/session-evidence` when a raw-session scan would otherwise require
custom parsing. Keep targets explicit and pass concrete paths from the skill,
plugin, workspace, or installed cache being audited:

```bash
scripts/session-evidence \
  --target my-skill \
  --target-path /path/to/my-skill/SKILL.md \
  --runtime-pattern 'my-skill=my-tool|my-command' \
  --root "$CODEX_HOME/sessions" \
  --since 2026-04-01 \
  --include-zero
```

The helper reports `explicit-user`, `skill-injection`, `opened-skill-doc`, and
`runtime-command` buckets. Treat its output as evidence to interpret, not as a
replacement for reading a representative trace when a claim is high-risk.

## Shared Evidence Rules

- Start from relevant local surfaces first, then widen only when needed.
- Search the memory index first, then open only the 1-3 most relevant rollout
  summaries.
- Check cheap maintenance signals such as `git log` and adjacent docs before
  deep session scans.
- Treat audits as read-only by default.
  - Do not modify files under the audited target (including its `SKILL.md` or
    `references/*`) while performing an audit.
  - Record findings in the audit output; make file changes only after the user
    explicitly asks to apply updates to that specific target.
- If the audit is making a behavior, correctness, false-positive,
  false-negative, or low-value claim and raw sessions exist, inspect at least
  one representative session trace when practical.
- For repeated or portfolio-style raw-session checks, prefer
  `scripts/session-evidence` before ad hoc shell scripts. Pass explicit
  `--target` values, optional `--target-path` values for installed or cached
  `SKILL.md` files, and target-bound `--runtime-pattern TARGET=REGEX`
  arguments only for runtime commands that are truly meaningful for the
  audited surface.
- If representative invocation evidence cannot be found, say that explicitly
  instead of implying runtime behavior from docs or summaries alone.
- Treat cache copies as verification-only evidence. Never route fixes to
  `~/.codex/plugins/cache/...`.

## Output Expectations

Return a compact audit with these sections:

1. `Audited targets`
   List the audited targets and the role each one plays.
2. `Evidence summary`
   Summarize the strongest repo, memory, session, cache-verification, and
   live-context signals that informed the audit.
3. `Per-target update roadmap`
   For each audited target, include:
   - target name
   - target kind: `skill`, `plugin`, or `bundled plugin skill`
   - observed strengths
   - missing or weak behavior
   - behavior evidence status: session-confirmed, summary-only, or no
     invocation evidence found
   - evidence source
   - highest-value next update
   - owning surface for the fix: `skill`, `bundled plugin skill`, `plugin`,
     or `docs`
4. `Add / merge / disable candidates`
   List only candidates justified by evidence after reviewing the audited
   scope.
5. `Priority order`
   Rank the top recommendations by expected value.
6. `Follow-up question`
   In full-portfolio audits where `skill-audit` was not explicitly requested,
   end by asking whether the user wants a follow-up audit of `skill-audit`
   too.

## Decision Rules

- Audit installed surfaces before proposing new ones.
- Audit project-local surfaces before widening to shared/global surfaces.
- Keep default full-scope audits workflow-first and mixed.
- Treat `skill-audit` self-audit as explicit-scope only; never include it
  unless the user names it.
- When the user names specific targets, treat those named targets as the
  primary and usually exclusive audit scope.
- Prefer improving an existing installed surface before adding a new one.
- Prefer improving a bundled plugin skill or repo docs when the problem does
  not justify a plugin-level change.
- Recommend a new surface only after checking whether an audited installed
  surface could own the workflow cleanly.
- If auditing a bundled plugin skill, inspect both the bundled skill contract
  and the owning plugin package.

## Failure Shields

- Do not invent recurring patterns without repo, memory, or session evidence.
- Do not confuse recurrence with effectiveness.
- Do not claim runtime behavior, correctness, or low-value triggering from docs
  or rollout summaries alone when raw session evidence is available.
- Do not “fix as you audit”.
  - Audits should not create PRs/commits or edit audited target docs unless the
    user explicitly transitions the request from *audit* to *implementation*.
- When implementing changes to an audited target, avoid “append-only” edits.
  - Re-read the whole `SKILL.md` and reorganize sections if needed so it stays
    a compact entrypoint.
  - Prefer moving long-form guidance into `references/*` and linking to it from
    `SKILL.md` rather than growing `SKILL.md` indefinitely.
- Do not flatten skill, bundled plugin skill, plugin, and docs issues into one
  bucket; keep ownership decisions explicit.
- Do not jump to new-surface recommendations before evaluating existing
  installed surfaces as possible owners.
- Do not audit `skill-audit` unless the user explicitly requested
  `skill-audit` in scope.
- Do not bulk-load all rollout summaries or raw sessions; stay targeted.
- Do not silently expand a user-targeted audit into a wider portfolio review.
- Do not bloat audited docs through audit output.
  - Keep audit findings compact and decision-oriented.
  - If an audited target needs substantial new guidance, prefer putting the
    long-form content in a dedicated reference file under that target and keep
    its `SKILL.md` as an entrypoint.

## Follow-up

If the user asks to create a brand-new skill or substantially reshape one,
switch to `$skill-creator` and implement that change rather than continuing the
audit.

If the user asks to update an existing plugin package, bundled plugin skill, or
standalone skill, leave audit mode and switch into implementation mode using
the owning project's maintenance workflow.

## Examples

- "Audit the installed skills used in this workflow and tell me which ones
  should be updated first."
- "Audit plugin $my-plugin and suggest the highest-value improvements."
- "Audit [$my-plugin:publish](...) and tell me whether the bundled skill or the
  plugin package is the real owner of the problems."
- "Before we add a new skill, check whether an existing installed surface or
  repo docs should own this workflow instead."
- "Audit only $my-planning-skill and $skill-audit and call out any overlap or
  weak guardrails."
