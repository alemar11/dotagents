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
| [`$se:feature`](../plugins/se/skills/feature/SKILL.md) | `gpt-5.6-sol` | `high` | One visible Feature Plan planner and reducer. The profile is passed explicitly once at task creation or resume; the accepted stable receipt starts Intake without post-effect profile readback, self-attestation, title reconciliation, or execution-target gating. Optional read-only helpers are subordinate and fall back to serial planner work. |
| [`$se:implement`](../plugins/se/skills/implement/SKILL.md) | `gpt-5.6-sol` | `medium` | Multi-Feature Implement orchestrator and control-plane role; its complete fixed profile is actively requested and never inherited. The required and optional profiles are owned by [`skills/implement/references/task-profile.md`](../plugins/se/skills/implement/references/task-profile.md). |
| [`$se:implement`](../plugins/se/skills/implement/SKILL.md) | `gpt-5.6-sol` | `medium`/`high`/`xhigh` adaptive | One Feature Worker per implementation-eligible Feature; its resolved profile is actively requested and never inherited before it derives execution units, implements them in one worktree, and performs exact-HEAD in-session review. |
| [`$se:implement`](../plugins/se/skills/implement/SKILL.md) | `gpt-5.6-sol` | `medium`/`high`/`xhigh` adaptive | Optional bounded Feature Worker support assignments for code analysis, execution-unit assistance, validation, and critique; any separately instantiated task receives the complete explicit profile, while unavailable delegation falls back to serial parent execution. |
| [`$se:implement-next`](../plugins/se/skills/implement-next/SKILL.md) | `configured/default` | `configured/default` | One visible graph orchestrator in the single involved project or the caller-selected coordination project; the skill intentionally inherits the configured profile unless the caller explicitly overrides it. |
| [`$se:implement-next`](../plugins/se/skills/implement-next/SKILL.md) | `configured/default` | `configured/default` | Reusable repository-bound worker lanes in isolated worktrees; the orchestrator chooses serial reuse or concurrent lanes without selecting a fixed profile. |
| [`$code-wiki`](../skills/code-wiki/SKILL.md) | `configured/default` | `configured/default` | May use Codex subagents for parallel read-only repository study when the active runtime policy permits delegation; the skill does not select a profile. |

Remote Codex review requests or skills that merely execute in the current task
without owning a model/reasoning profile are not separate rows unless they gain
skill-level selection or delegation behavior.
