# Codex Model and Reasoning Index

This is the repository-wide inventory of skill-level Codex execution profiles.
Keep it synchronized with the linked runtime contracts; it is an index, not a
runtime policy source. Skills that only run in the current task without
selecting or delegating another Codex execution are omitted. A
`configured/default` value records intentional inheritance from the caller or
active runtime.

| skill | model | reason | description |
| --- | --- | --- | --- |
| [`$codex-cli`](../skills/codex-cli/SKILL.md) | `gpt-5.6-sol` | `medium` default; `low`/`medium`/`high`/`xhigh`/`max`/`ultra` supported | One-shot delegated Codex CLI task. The full selection and task-profile matrix lives in [`references/model-policy.md`](../skills/codex-cli/references/model-policy.md). |
| [`$codex-cli`](../skills/codex-cli/SKILL.md) | `gpt-5.6-terra` | `high` default; `low`/`medium`/`high`/`xhigh`/`max`/`ultra` supported | Explicit Terra selection for one-shot Codex CLI delegation; see the [canonical model policy](../skills/codex-cli/references/model-policy.md). |
| [`$codex-cli`](../skills/codex-cli/SKILL.md) | `gpt-5.6-luna` | `max` default; `low`/`medium`/`high`/`xhigh`/`max` supported | Explicit Luna selection for one-shot Codex CLI delegation; extreme profiles cap at `max` because Luna has no `ultra`; see the [canonical model policy](../skills/codex-cli/references/model-policy.md). |
| [`$focus`](../skills/focus/SKILL.md) | `configured/default` | `configured/default` | Creates one focused Codex App task and intentionally omits `model` and `thinking`, so the caller's configured defaults apply. |
| [`$study`](../skills/study/SKILL.md) | `gpt-5.6-sol` | `medium` | Visible read-only Study orchestrator in the current saved local project. |
| [`$study`](../skills/study/SKILL.md) | `gpt-5.6-luna` | `max` | Up to five visible read-only Study workers in the same project; the worker cap and topology are owned by [`skills/study/SKILL.md`](../skills/study/SKILL.md). |
| [`$se:feature`](../plugins/se/skills/feature/SKILL.md) | `gpt-5.6-sol` | `medium` | Required Feature Plan planner and reducer; the profile is owned by [`skills/feature/references/task-profile.md`](../plugins/se/skills/feature/references/task-profile.md), while the root preflight verifies required task capabilities and records optional delegation and goal facts. |
| [`$se:feature`](../plugins/se/skills/feature/SKILL.md) | `gpt-5.6-sol` | `medium` | Optional bounded analysis-worker roles for intent, context, boundary, question, and evidence analysis; when delegation is unavailable, the parent planner performs the same work serially. |
| [`$se:feature`](../plugins/se/skills/feature/SKILL.md) | `gpt-5.6-sol` | `medium` | Optional independent critic-analyst role; it receives the original problem without the planner draft or context-derived requirements during its first pass and returns read-only challenges to the parent reducer. |
| [`$se:implement`](../plugins/se/skills/implement/SKILL.md) | `gpt-5.6-sol` | `medium` | Multi-Feature Implement orchestrator and control-plane role; the required and optional profiles are owned by [`skills/implement/references/task-profile.md`](../plugins/se/skills/implement/references/task-profile.md). |
| [`$se:implement`](../plugins/se/skills/implement/SKILL.md) | `gpt-5.6-sol` | `medium`/`high`/`xhigh` adaptive | One Feature Worker per implementation-eligible Feature in the Plan Set; it derives execution units from that Feature's textual plan and local Macro Task registry, implements them in one worktree, and performs exact-HEAD in-session review with the same resolved reasoning. |
| [`$se:implement`](../plugins/se/skills/implement/SKILL.md) | `gpt-5.6-sol` | `medium`/`high`/`xhigh` adaptive | Optional bounded Feature Worker support assignments for code analysis, execution-unit assistance, validation, and critique; delegation is capability-conditioned and falls back to serial parent execution. |
| [`$code-wiki`](../skills/code-wiki/SKILL.md) | `configured/default` | `configured/default` | May use Codex subagents for parallel read-only repository study when the active runtime policy permits delegation; the skill does not select a profile. |

Remote Codex review requests or skills that merely execute in the current task
without owning a model/reasoning profile are not separate rows unless they gain
skill-level selection or delegation behavior.
