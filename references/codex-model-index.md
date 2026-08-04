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
| [`$se:implement`](../plugins/se/skills/implement/SKILL.md) | `gpt-5.6-sol` | `medium` | Visible root/controller task for an explicit implementation run. The fixed controller profile is owned by [`task-model-policy.md`](../plugins/se/skills/implement/references/task-model-policy.md). |
| [`$se:implement`](../plugins/se/skills/implement/SKILL.md) | `gpt-5.6-sol` | `medium`/`high`/`xhigh` adaptive | Implementation workers resolve one thinking level per eligible Feature Spec; the resolved value is also passed to native Codex review. See the [worker policy](../plugins/se/skills/implement/references/task-model-policy.md). |
| [`$se2:feature`](../plugins/se2/skills/feature/SKILL.md) | `gpt-5.6-sol` | `medium` | Principal Feature planner task; the profile is owned by [`skills/feature/references/task-profile.md`](../plugins/se2/skills/feature/references/task-profile.md), while the root preflight only verifies supplied runtime capabilities. |
| [`$se2:implement`](../plugins/se2/skills/implement/SKILL.md) | `gpt-5.6-sol` | `medium` | Multi-Feature Implement orchestrator and control-plane role; the two-role profile is owned by [`skills/implement/references/task-profile.md`](../plugins/se2/skills/implement/references/task-profile.md). |
| [`$se2:implement`](../plugins/se2/skills/implement/SKILL.md) | `gpt-5.6-sol` | `medium`/`high`/`xhigh` adaptive | One Feature Worker per implementation-eligible Feature; it serially executes the complete Task DAG in one worktree and performs exact-HEAD in-session review with the same resolved reasoning. |
| [`$code-wiki`](../skills/code-wiki/SKILL.md) | `configured/default` | `configured/default` | May use Codex subagents for parallel read-only repository study when the active runtime policy permits delegation; the skill does not select a profile. |

Remote Codex review requests or skills that merely execute in the current task
without owning a model/reasoning profile are not separate rows unless they gain
skill-level selection or delegation behavior.
