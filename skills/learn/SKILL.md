---
name: learn
description: "Save or maintain durable repository knowledge when explicitly requested; make only authorized local changes."
---

# Learn Project Context

## Purpose and boundary

Use `$learn` for durable, local repository knowledge: always-active rules in
`AGENTS.md`, root-first `CONTEXT.md` routing, conditional topic files, accepted
ADRs, localization guidance, Code Review Rules, and explicit AGENTS.md
compaction proposals.

Learn never owns tracker content, delivery state, branches, pull requests,
provider transport, task graphs, or worker configuration. It may inspect local
evidence and modify only authorized context surfaces. It never contacts a
hosted provider and has no publish mode. Work in the invoking session, without
creating tasks or subagents, whether invoked directly or by another skill.

## Select and load one branch

Read [options.md](references/options.md) to resolve the smallest canonical
`memory_slice`. Apply [context-preflight.md](references/context-preflight.md)
for the shared context/pointer checks, then load only the selected branch.
Read setup details only on the routes below or when the preflight identifies a
pointer change that needs their templates.

| Work | Read |
| --- | --- |
| Domain setup/bootstrap | [domain.md](references/domain.md), [domain-modeling.md](references/domain-modeling.md), [context-seed.md](references/context-seed.md), and [setup-workflow.md](references/setup-workflow.md) |
| Domain inline update, implementation closeout, or periodic review | [domain-modeling.md](references/domain-modeling.md); add domain.md only for layout ambiguity and [documentation-shapes.md](references/documentation-shapes.md) only when no stronger local shape exists |
| Durable capture | [durable-capture.md](references/durable-capture.md); add only the destination-specific domain, documentation-shape, or translation reference it routes to |
| Translation memory | [translation.md](references/translation.md) and [setup-workflow.md](references/setup-workflow.md) |
| AGENTS.md pointers | [setup-workflow.md](references/setup-workflow.md) |
| AGENTS.md compaction | [agents-compaction.md](references/agents-compaction.md), documentation-shapes.md, and domain.md only when the context index changes |
| Code Review Rules | [code-review-rules.md](references/code-review-rules.md) and only the evidence or evaluation references it routes to |
| Explicit full setup | domain.md, domain-modeling.md, context-seed.md, [setup-workflow.md](references/setup-workflow.md), and only evidenced optional branches |

Load [session-history.md](references/session-history.md) only for accepted
existing-project evidence. Load [setup-questions.md](references/setup-questions.md)
only when repository evidence and documented defaults leave one material
ambiguity.

## Invocation preflight and authority

The context preflight derives state; it never grants write authority.

Apply these authority rules:

- Inspection, review, proposal, and dry-run requests are read-only.
- Explicit setup, initialization, update, or refresh authorizes only the named
  local context scope.
- An explicit request to remember, save, or preserve one unambiguous durable
  item authorizes that item and its smallest required context bootstrap.
- A composed handoff writes only accepted knowledge with named targets and
  explicit inline-capture authority.
- For AGENTS.md compaction, prepare an exact before/after change. Apply it
  when the request authorizes the edit; a review-only request stays read-only.

When scope, wording, destination, or a conflict remains material, draft the
exact change and stop for confirmation. Never infer capture from ordinary
conversation, tentative ideas, raw session text, secrets, or file churn.

## Workflow graph

Read [states.md](references/states.md) before interpreting workflow, option,
derived, result, or persisted state. The registry owns node meanings; the table
below owns entry conditions and edges for this entrypoint.

| node_id | kind | entry condition | transitions | terminal state |
| --- | --- | --- | --- | --- |
| scope | action | explicit repository-knowledge request | inspect, blocked | none |
| inspect | action | repository scope and memory slice resolved | draft, blocked | none |
| draft | decision | evidence and intended target are known | reported, confirm | none |
| confirm | decision | durable write is requested | apply, deferred, blocked | none |
| apply | action | exact target and authority confirmed | verify, blocked | none |
| verify | validation | selected surface was applied | complete, blocked | none |
| reported | terminal | read-only or non-durable result is ready | none | reported |
| deferred | terminal | user decision or confirmation is required | none | deferred |
| complete | terminal | authorized write was verified | none | complete |
| blocked | terminal | required evidence, authority, or verification is unavailable | none | blocked |

## Execution and result

Draft exact targets, wording, evidence, unknowns and links. Report read-only
work; apply authorized changes only after any required decision, then read them
back and verify links, indexes, preserved content and the diff. Return the
terminal state, changed files, capture outcome, pointer state, context ownership
and only the selected branch's additional fields.

Use the current Git repository as the default scope. Cross-repository work
requires explicitly authorized identities and candidate roots verified
one-to-one. Preserve unrelated content. Learn has no persisted workflow
checkpoint, run ledger, generic run mode, or stored write preference.
