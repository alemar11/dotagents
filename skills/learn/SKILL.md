---
name: learn
description: "Maintain AGENTS.md and durable repository knowledge when requested or when the user states hard repository rules or important assumptions intended to guide future work."
---

# Learn Project Context

## Purpose and boundary

Use `$learn` for durable, local repository knowledge: always-active rules in
`AGENTS.md`, root-first `CONTEXT.md` routing, conditional topic files, accepted
ADRs, localization guidance, and Code Review Rules. Create, update, review, or
refactor `AGENTS.md` within the requested scope.

Learn never owns tracker content, delivery state, branches, pull requests,
provider transport, task graphs, or worker configuration. It may inspect local
evidence and modify only authorized context surfaces. It never contacts a
hosted provider and has no publish mode. Work in the invoking session, without
creating tasks or subagents, whether invoked directly or by another skill.

## Trigger selection

Also select Learn when the user states a hard repository rule or an important
repository assumption intended to guide future work, even without `$learn` or
a request to remember it. Route these statements to durable capture. For
example, “Hard rule: all database access goes through the repository layer”
or “This repository assumes one tenant per deployment” qualifies when stated
as an established constraint. Preserve assumptions as assumptions, not verified
facts. One-task instructions, quoted examples, and tentative ideas do not
qualify. Selection alone does not authorize a write; apply the authority rules
below.

## Select and load one branch

Select the smallest route below. Read [options.md](references/options.md) when
normalizing a composed handoff or resolving an ambiguous branch. AGENTS.md-only
work needs its writing guidance and applicable instruction chain; context-bearing
work uses [context-preflight.md](references/context-preflight.md) for relevant
context and pointer checks. Read setup templates only when setup
or a pointer change is part of the selected work.

| Work | Read |
| --- | --- |
| Domain setup/bootstrap | [domain.md](references/domain.md), [domain-modeling.md](references/domain-modeling.md), [context-seed.md](references/context-seed.md), and [setup-workflow.md](references/setup-workflow.md) |
| Domain inline update, implementation closeout, or periodic review | [domain-modeling.md](references/domain-modeling.md); add domain.md only for layout ambiguity and [documentation-shapes.md](references/documentation-shapes.md) only when no stronger local shape exists |
| Durable capture | [durable-capture.md](references/durable-capture.md); add only the destination-specific domain, documentation-shape, or translation reference it routes to |
| AGENTS.md creation, rule updates, review, or refactoring | [agents-guidance.md](references/agents-guidance.md) |
| Translation memory | [translation.md](references/translation.md) and [setup-workflow.md](references/setup-workflow.md) |
| AGENTS.md pointers | [setup-workflow.md](references/setup-workflow.md) |
| AGENTS.md chain-size review or compaction | agents-guidance.md and [agents-compaction.md](references/agents-compaction.md); add documentation-shapes.md and domain.md only when extracting context |
| Code Review Rules | [code-review-rules.md](references/code-review-rules.md) and only the evidence or evaluation references it routes to |
| Explicit full setup | domain.md, domain-modeling.md, context-seed.md, [setup-workflow.md](references/setup-workflow.md), and only evidenced optional branches |

Load [session-history.md](references/session-history.md) only for accepted
existing-project evidence. Load [setup-questions.md](references/setup-questions.md)
only when repository evidence and documented defaults leave one material
ambiguity.

## Invocation preflight and authority

The context preflight derives state; it never grants write authority.

Apply these authority rules:

- Requests limited to inspection, review, proposal, or dry-run are read-only.
- Explicit setup, initialization, update, or refresh authorizes only the named
  local context scope.
- An explicit request to remember, save, or preserve one unambiguous durable
  item authorizes that item and its smallest required context bootstrap.
- A composed handoff writes only accepted knowledge with named targets and
  explicit inline-capture authority.
- For AGENTS.md authoring or refactoring, prepare an exact before/after change.
  Apply it when authorized; a review-only request stays read-only.

Use established user or caller authority without asking again. When scope,
wording, destination, or a conflict leaves a material decision unresolved, draft
the exact change and ask only about that decision; continue unaffected work.
Never infer write authority from trigger selection, tentative ideas, raw session
text, secrets, or file churn.

## Workflow graph

Read [states.md](references/states.md) before interpreting workflow, option,
derived, result, or persisted state. The registry owns node meanings; the table
below owns entry conditions and edges for this entrypoint.

| node_id | kind | entry condition | transitions | terminal state |
| --- | --- | --- | --- | --- |
| scope | action | repository-knowledge request or qualifying user-stated rule or assumption | inspect, blocked | none |
| inspect | action | repository scope and memory slice resolved | draft, blocked | none |
| draft | decision | evidence and intended target are known | reported, apply, confirm | none |
| confirm | decision | a material decision or write authority remains unresolved | apply, deferred, blocked | none |
| apply | action | exact target and authority confirmed | verify, blocked | none |
| verify | validation | selected surface was applied | complete, blocked | none |
| reported | terminal | read-only or non-durable result is ready | none | reported |
| deferred | terminal | user decision or confirmation is required | none | deferred |
| complete | terminal | authorized write was verified | none | complete |
| blocked | terminal | required evidence, authority, or verification is unavailable | none | blocked |

## Execution and result

Draft exact targets, wording, evidence, unknowns and links. Report read-only
work; apply authorized changes only after any required decision, then read them
back and verify links, indexes, preserved content and the diff. Finish once the
requested surfaces are verified. Report the changed files, outcome, and material
limitations concisely. Include canonical state and result fields for composed
handoffs; omit unrelated branch fields from ordinary user-facing reports.

Use the current Git repository as the default scope. Cross-repository work
requires explicitly authorized identities and candidate roots verified
one-to-one. Preserve unrelated content. Learn has no persisted workflow
checkpoint, run ledger, generic run mode, or stored write preference.
