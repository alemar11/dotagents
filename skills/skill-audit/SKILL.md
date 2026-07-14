---
name: skill-audit
description: Audit installed Codex skills, plugins, and bundled plugin skills for usage, overlap, prompt budget, and improvement roadmap.
---

# Skill Audit

## Overview

Audit installed standalone skills, plugin packages, and bundled plugin skills
before proposing new surfaces. Prefer improving, merging, or disabling an
existing owner when the evidence supports it.

This skill is Codex-dependent. Repo files and installed manifests are the
editable source of truth; Codex memory, rollout summaries, session JSONL, and
cache copies are evidence only.

## Non-negotiables

- Audits are read-only. Record findings; edit, commit, or publish only after the
  user explicitly switches the named target to implementation mode.
- Never edit session archives or `~/.codex/plugins/cache/...`.
- Named targets are the primary and normally exclusive scope. Include another
  target only to explain a concrete overlap or ownership conflict.
- Self-audit is opt-in: include `skill-audit` only when the user names it. For a
  full-portfolio audit, exclude it and offer a separate follow-up.
- Keep findings decision-oriented and evidence-backed.

## Target Resolution

1. Resolve each named target before broader discovery.
2. Classify it as `standalone skill`, `plugin package`, or `bundled plugin
   skill`.
3. If a target cannot be resolved, report the miss; do not substitute a near
   match.
4. For an unnamed portfolio audit, start from the current workflow and relevant
   installed surfaces, then widen only when the question requires it.

## Reference Routing

Open only the branch needed for the current question:

| Question | Reference |
| --- | --- |
| Standalone skill | `references/standalone-skills.md` |
| Plugin package | `references/plugins.md` |
| Bundled plugin skill | `references/bundled-plugin-skills.md` plus the owning manifest |
| Cached or unclear editable owner | `references/cache-resolution.md` |
| Merge, disable, duplicate, usage, or prompt-budget decision | `references/portfolio-hygiene.md` |
| Trigger clarity or instruction-density review | `references/writing-style-review.md` |

## Evidence Workflow

1. Read the target's current discovery metadata, entrypoint, directly relevant
   references, owning manifest, and adjacent repo docs.
2. Check cheap history and consistency evidence such as `git log` before deep
   session scans.
3. Search the memory index first, then open only the one to three most relevant
   rollout summaries.
4. When claiming runtime behavior, false triggers, missed triggers, correctness,
   or low value, inspect a representative raw session when practical. If none is
   available, state that limitation.
5. Use the helpers below instead of ad hoc parsers for repeated session or
   portfolio checks. Treat their output as evidence, not automatic cleanup
   authority.

### Session evidence

Run from the resolved skill root:

```bash
scripts/session-evidence \
  --target my-skill \
  --target-path /path/to/my-skill/SKILL.md \
  --runtime-pattern 'my-skill=my-tool|my-command' \
  --root "$CODEX_HOME/sessions" \
  --since 2026-04-01 \
  --include-zero
```

It reports `explicit-user`, `skill-injection`, `opened-skill-doc`, and
`runtime-command` buckets from direct function calls and code-mode custom tool
calls. Examples also record transport, `thread_source`, `parent_thread_id`, and
the raw `forked_from_id` when present so worker-thread evidence can be
attributed across supported session metadata shapes without counting tool
outputs or tool discovery as usage. Read a representative trace before making
a high-risk behavior claim.

### Portfolio health

```bash
scripts/portfolio-health --help
scripts/portfolio-health --version
scripts/portfolio-health --json doctor
scripts/portfolio-health scan --months 3
```

Use `references/portfolio-hygiene.md` to interpret its inventory, duplicate,
prompt-budget, root, and heuristic usage signals. No recent usage alone is not
enough to delete, disable, or rewrite a surface.

## Output Expectations

Return a compact audit using the format in
`references/output-format.md`.

## CLI Maintenance

- Keep normal runtime execution on `scripts/session-evidence` and
  `scripts/portfolio-health`.
- Both helpers are Python standard-library scripts shipped directly under
  `scripts/`.
- Keep each helper's `--version` output as its semver source of truth.
- Re-verify touched helpers with `--help`, `--version`, and `--json doctor`
  before relying on them in an audit.

## Follow-up

If the user asks to create a brand-new skill or substantially reshape one,
switch to `$skill-creator` and implement that change rather than continuing the
audit.

If the user asks to update an existing plugin package, bundled plugin skill, or
standalone skill, leave audit mode and switch into implementation mode using
the owning project's maintenance workflow.
