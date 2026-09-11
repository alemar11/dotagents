# Codex Model and Reasoning Index

This is the repository-wide inventory of skill-level Codex execution profiles.
Keep it synchronized with the linked runtime contracts; it is an index, not a
runtime policy source. Skills that only run in the current task without
selecting or delegating another Codex execution are omitted unless an explicit
composition boundary defines profile inheritance. A
`configured/default` value records intentional inheritance from the caller or
active runtime.

| skill | model | reason | description |
| --- | --- | --- | --- |
| [`$explore`](../skills/explore/SKILL.md) | `configured/default` | `configured/default` | Invoking App task or CLI session acting as the read-only Explore controller; its active model and reasoning are intentionally retained. |
| [`$spec`](../skills/spec/SKILL.md) | Inherit | Inherit | The invoking session owns drafting and review with its configured model and reasoning; no separate planner. Optional helpers follow the skill-local briefs. |
| [`$adversarial-review`](../skills/adversarial-review/SKILL.md) | `configured/default` | `configured/default` | Independent read-only reviewer profile supplied by the caller or composed workflow; the skill does not select a model or reasoning value. |
| [`$implement`](../skills/implement/SKILL.md) | `configured/default` | `configured/default` | Executes in the current task or caller-selected developer subagent; does not select or change its profile. |
| Explore research helpers | `configured/default` | `configured/default` | [Research delegation](../skills/explore/references/orchestration.md) inherits host defaults or explicit user choices. |
| Spec research and review helpers | `configured/default` | `configured/default` | [Specification helpers](../skills/spec/references/subagents.md) prescribe no model or reasoning level. |
| Implement design helper | `configured/default` | `configured/default` | [Designer role](../skills/implement/references/designer.md) inherits host defaults or explicit user choices. |


Remote Codex review requests or skills that merely execute in the current task
without owning a model/reasoning profile are not separate rows unless they gain
skill-level selection or delegation behavior.
