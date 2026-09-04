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
| [`$se:study`](../plugins/se/skills/study/SKILL.md) | `gpt-5.6-sol` | `medium` | Separate visible read-only Study controller on the App surface in the exact saved local project. |
| [`$se:study`](../plugins/se/skills/study/SKILL.md) | `configured/default` | `configured/default` | Current CLI session acting as the read-only Study controller; its active model and reasoning are intentionally retained. |
| [`$se:study`](../plugins/se/skills/study/SKILL.md) | `gpt-5.6-luna` | `max` | Up to five visible App worker tasks or native CLI subagents. The cap and transport routing are owned by [`plugins/se/skills/study/SKILL.md`](../plugins/se/skills/study/SKILL.md). |
| [`$se:feature`](../plugins/se/skills/feature/SKILL.md) | `gpt-5.6-sol` | `high` | One visible Feature Plan planner and reducer. The profile is passed explicitly once at task creation or resume; the accepted stable receipt starts Intake without post-effect profile readback, self-attestation, title reconciliation, or execution-target gating. Optional read-only helpers are subordinate and fall back to serial planner work. |
| [`$se:implement`](../plugins/se/skills/implement/SKILL.md) | `configured/default` | `configured/default` | One visible graph orchestrator in the single involved project or the caller-selected coordination project; the skill intentionally inherits the configured profile unless the caller explicitly overrides it. |
| [`$se:implement`](../plugins/se/skills/implement/SKILL.md) | `configured/default` | `configured/default` | Reusable repository-bound worker lanes in isolated worktrees; the orchestrator chooses serial reuse or concurrent lanes without selecting a fixed profile. |

Remote Codex review requests or skills that merely execute in the current task
without owning a model/reasoning profile are not separate rows unless they gain
skill-level selection or delegation behavior.
