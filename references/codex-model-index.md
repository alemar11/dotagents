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
| [`$se:chief-of-staff`](../plugins/se/skills/chief-of-staff/SKILL.md) | `configured/default` | `configured/default` | Invoking coordinator retains its settings; new visible Deliver tasks inherit App defaults and reused tasks retain settings unless explicitly overridden by the user. |
| [`$se:explore`](../plugins/se/skills/explore/SKILL.md) | `configured/default` | `configured/default` | Invoking App task or CLI session acting as the read-only Explore controller; its active model and reasoning are intentionally retained. |
| [`$se:explore`](../plugins/se/skills/explore/SKILL.md), [`$se:spec`](../plugins/se/skills/spec/SKILL.md) | `gpt-5.6-luna` | `max` | Shared [`evidence-researcher`](../plugins/se/references/subagents/evidence-researcher.md) role. Calling skills own selection, concurrency, lifecycle, and fallback. |
| [`$se:spec`](../plugins/se/skills/spec/SKILL.md) | Inherit | Inherit | The invoking session owns drafting and review with its configured model and reasoning; no separate planner. Optional helpers use the shared roles below. |
| [`$se:spec`](../plugins/se/skills/spec/SKILL.md) | `gpt-5.6-sol` | `xhigh` | Optional shared [`spec-reviewer`](../plugins/se/references/subagents/spec-reviewer.md) role for the complete draft and task plan; Spec owns review criteria and disposition. |
| [`$se:adversarial-review`](../plugins/se/skills/adversarial-review/SKILL.md) | `configured/default` | `configured/default` | Independent read-only reviewer profile supplied by the caller or composed workflow; the skill does not select a model or reasoning value. |
| [`$se:deliver`](../plugins/se/skills/deliver/SKILL.md) | `gpt-6-astra` | `configured/default` | Intended current-task delivery lead and orchestrator under its entrypoint; caller reasoning and explicit profile overrides are retained without changing task settings. |
| [`$se:deliver`](../plugins/se/skills/deliver/SKILL.md) | `gpt-5.6-luna` | `max` | Local [worker contract](../plugins/se/skills/deliver/references/workers.md) owns contribution, integration and PR delivery assignments where the runtime permits skill-selected profiles; explicit user overrides win. |
| [`$se:deliver`](../plugins/se/skills/deliver/SKILL.md) | `configured/default` | `configured/default` | Intentional worker inheritance when runtime profile selection requires an explicit user request, under the [worker contract](../plugins/se/skills/deliver/references/workers.md). |
| [`$se:deliver`](../plugins/se/skills/deliver/SKILL.md) | `gpt-6-astra` | `medium` | Worker-launched single read-only [candidate review](../plugins/se/skills/deliver/references/workers.md#candidate-review) under the shared code-reviewer role, where runtime profile selection is permitted. |
| [`$se:deliver`](../plugins/se/skills/deliver/SKILL.md) | `configured/default` | `configured/default` | Intentional candidate-reviewer inheritance when runtime profile overrides are unavailable, under the [candidate review contract](../plugins/se/skills/deliver/references/workers.md#candidate-review). |
| [`$se:implement`](../plugins/se/skills/implement/SKILL.md) | `configured/default` | `configured/default` | Executes in the current task or caller-selected developer subagent; does not select or change its profile. |

| [`$se:implement`](../plugins/se/skills/implement/SKILL.md) | `gpt-6-astra` | `low` | Optional read-only [UI designer](../plugins/se/references/subagents/designer.md), selected and managed by the executing worker in standalone or composed implementation. |

Remote Codex review requests or skills that merely execute in the current task
without owning a model/reasoning profile are not separate rows unless they gain
skill-level selection or delegation behavior.
