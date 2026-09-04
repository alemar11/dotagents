---
name: learn
description: "Capture and maintain durable repository knowledge, including project context, hard rules, decisions, localization guidance, and code review rules. Use when the user explicitly asks to remember, save, or preserve a repository rule or other durable knowledge; make only authorized local changes."
---

# Learn Project Context

## Purpose and boundary

Use $se:learn as the single public entry point for durable repository
context:

- always-active operating rules, ownership boundaries, essential verification,
  and the exact ## Code Review Rules section in the closest applicable
  AGENTS.md;
- root-first routing through CONTEXT.md;
- conditional topic files and accepted ADRs under the nearest context-owning
  root or first-class monorepo subproject;
- optional TRANSLATION.md sidecars when localization rules are evidenced;
- confirmed durable corrections, preferences, and accepted decisions;
- explicit requests to remember, save, or preserve an always-active or "hard"
  repository rule;
- explicit, proposal-first compaction of an applicable AGENTS.md chain.

The skill owns repository knowledge only. Tracker routing, issue metadata,
publication, delivery policy, branches, pull requests, provider transport,
task graphs, and worker configuration belong to their own workflows and must
never be stored in project-context/.

Learn is local-repository-only. It may inspect and, when authorized, modify
the selected repository's context files, AGENTS.md surfaces, ADRs, and related
local documentation. It never contacts GitHub or another hosted provider, does
not load the G dependency preflight, and has no publish or preview delivery
mode.

Use the smallest requested memory_slice. Load
references/options.md before resolving a branch and reject noncanonical
structured fields or values. This is an independently maintained SE skill: it
does not import, alias, synchronize with, or depend on a retired workflow
package.

## Invocation preflight

After loading `references/options.md` and before executing any selected branch,
run a local Project Context routing preflight. Resolve the actual
root-to-target `AGENTS.md` chain, read the root `CONTEXT.md` first when it
exists, and inspect the canonical Project Context pointer in the applicable
`AGENTS.md`. The pointer must direct agents to `CONTEXT.md` and carry the
compact evolution rule defined in `references/setup-workflow.md`.

Treat a missing, stale, duplicated, or over-copied pointer as an
`agents-pointers` finding even when another `memory_slice` was requested. For
an authorized context setup, update, closeout, or confirmed capture, reconcile
that pointer as a companion local change. In review, proposal, or otherwise
read-only work, report the exact pointer change without writing it. This
preflight derives run facts; it never grants write authority or changes the
selected memory slice.

For an explicit request to remember, save, or preserve a specific repository
rule, select `durable-capture` even when the user does not name Learn. Treat the
request itself as capture authority when the rule, repository scope, and
narrowest destination are unambiguous. If the repository root or selected
first-class subproject lacks its required `CONTEXT.md` or canonical Project
Context pointer, include the smallest evidence-backed bootstrap prerequisite in
the same authorized run, following the `setup-bootstrap` semantics without
changing the selected memory slice:
create or repair the root-first context chain and pointers, then capture the
rule in the closest applicable `AGENTS.md`. Do not turn this prerequisite into
`full-setup`, create empty topic or ADR trees, or widen the repository scope.
When wording, scope, destination, or a conflict remains material, show the exact
proposal and wait for confirmation before either setup or capture.

When an authorized context-bearing run carries accepted landed changes that
alter shared purpose, vocabulary, durable project rules, boundaries, stable
routing, known state, or explicit unknowns, update the smallest applicable
`CONTEXT.md` surface and its topic/ADR indexes in the same run. For an
unrelated selected slice, report the candidate for `domain-memory` instead of
silently widening the run. File churn alone is not durable context evidence.

## Workflow graph

Read the shared [workflow-graph.md](../../references/workflow-graph.md) before
using this registry. Read [references/states.md](references/states.md) for the
human-readable distinction between workflow nodes, selectable fields, derived
facts, result values, and persisted domain state. Learn owns the registry
below; its routed references own operation-specific detail. The registry is the
structural source of truth and Mermaid is its projection.

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

~~~mermaid
flowchart TD
    scope --> inspect --> draft
    scope --> blocked
    inspect --> blocked
    draft --> reported
    draft --> confirm
    confirm --> apply --> verify
    confirm --> deferred
    confirm --> blocked
    apply --> blocked
    verify --> complete
    verify --> blocked
~~~

## Surfaces and ownership

| Surface | Owns | Always active? |
| --- | --- | --- |
| AGENTS.md | Operating invariants, safety, ownership, essential verification, short pointers, and the minimum Code Review Rules contract. | Yes |
| CONTEXT.md | Shared overview, vocabulary, known state, explicit unknowns, scope routing, and the index of conditional context files. | No; entry point when context is needed |
| project-context/<topic>.md | Conditional details, examples, rationale, domain contracts, and operational notes. | No; each file declares Read when |
| project-context/adr/index.md | Canonical index of accepted ADRs. Created with the first ADR. | No |
| project-context/adr/ADR-*.md | Accepted load-bearing decisions and consequences. | No |
| TRANSLATION.md | Evidence-backed localization and language conventions beside its owning context. | No |

Keep topic files flat and lowercase. `project-context/adr/` is the only initial
subdirectory within each context-owning scope. In a monorepo, the Git root owns
shared rules, context, routing, and cross-project decisions. Each evidenced
first-class subproject may own a local `AGENTS.md`, `CONTEXT.md`, optional
`TRANSLATION.md`, and `project-context/` for subproject-only knowledge. Do not
create this tree for incidental folders or packages without an independent
product, service, build, deployment, documentation, or ownership boundary.

During an authorized monorepo setup or update, classify existing knowledge by
scope. Keep shared material at the repository root; create or update local
subproject surfaces and move subproject-only material there. Update root routes,
indexes, and links in the same change, and do not leave normative duplicates.

AGENTS.md is the source of always-active normative rules. A topic file may
contain conditional detail, but it must not replace a rule that applies to
every task.

## Operations

| memory_slice | Owns |
| --- | --- |
| domain-memory | Root/subproject context routing, topic setup, ADR setup, inline update, implementation closeout, or periodic review. |
| durable-capture | Manual capture of a confirmed correction, preference, rule, localization convention, or accepted decision. |
| translation-memory | Localization memory only. |
| agents-pointers | Preflight and maintain the concise Project Context pointer and evolution rule in the applicable AGENTS.md; detect missing, stale, duplicated, or over-copied routing. |
| agents-compaction | Measurement, classification, proposal, and authorized compaction of an applicable AGENTS.md chain. |
| code-review-rules | Evidence-backed rules in the exact ## Code Review Rules section of the closest applicable AGENTS.md. |
| full-setup | All applicable context slices, only when explicitly requested. |

For memory_slice=domain-memory, resolve domain_operation from
references/domain-modeling.md: setup-bootstrap, inline-update,
implementation-closeout, or periodic-review.

## Write authority

There is no durable configuration file and no persisted write preference.
Resolve authority from the current request and caller data:

- inspection, review, proposal, dry-run, or indirect suggestion: read-only;
- explicit setup, initialize, update, or refresh: write only the selected
  surfaces in the requested repository scope;
- direct durable-capture: an explicit request to remember, save, or preserve a
  specific rule or other durable item authorizes the unambiguous scoped write;
  otherwise propose the exact target, section, wording, and before/after block,
  then wait for affirmative confirmation before writing;
- a composed domain-memory handoff: write only when the caller supplies
  accepted durable knowledge, named targets, and explicit capture authority;
- agents-compaction: always show measurement and the before/after proposal;
  apply only after an explicit target and confirmation.

Never infer durable capture from ordinary conversation, tentative ideas, raw
session text, secrets, or generic advice. Preserve unrelated custom prose,
comments, overrides, context files, ADRs, and localization data.

The invocation preflight only detects a companion `AGENTS.md` pointer change.
It may apply that change when the current run already authorizes the relevant
local context write; otherwise it remains a reported proposal.

## Non-negotiable rules

- Resolve the current Git repository as the default scope. Cross-repository work
  requires explicitly authorized identities and candidate roots verified
  one-to-one by the caller.
- Never fabricate paths from issue references, saved projects, common parents,
  or path proximity. Reject extra or unmatched roots.
- During authorized setup/bootstrap, create or update root CONTEXT.md at every
  selected Git root, even when only a minimal entry point is supported.
- During authorized full monorepo setup or hierarchy update, create or update a
  minimal local `AGENTS.md` and `CONTEXT.md` for every evidenced first-class
  subproject in scope. Create its `project-context/` only when local topic or ADR
  content exists, and create `TRANSLATION.md` only when localization is
  evidenced or explicitly confirmed.
- Create TRANSLATION.md only when localization support or durable translation
  rules are evidenced or explicitly confirmed. Do not create empty ADR trees.
- Put accepted load-bearing decisions in ADRs, not in a growing AGENTS.md.
- For Code Review Rules, write only invariant, consequence, and safe path under
  the exact ## Code Review Rules heading in the closest applicable AGENTS.md.
- Never create tracker, publication, delivery, provider, branch, or worker
  configuration under project-context/.
- Verify links, target existence, duplicate normative content, preserved custom
  text, and the documentation diff after every authorized write.

## Reference loading matrix

Load `options.md` and `setup-workflow.md` for the invocation preflight, then
load only the selected branch:

| Work | Required references |
| --- | --- |
| Domain setup/bootstrap | domain.md, domain-modeling.md, context-seed.md, and setup-workflow.md; add session-history.md only for accepted existing-project evidence. |
| Domain inline update / closeout / review | domain-modeling.md; add domain.md for layout ambiguity and documentation-shapes.md when no stronger local shape exists. |
| Durable capture | durable-capture.md; add domain-modeling.md, documentation-shapes.md, or translation.md for the selected destination. |
| Translation | translation.md and setup-workflow.md. |
| Pointers | setup-workflow.md. |
| AGENTS compaction | agents-compaction.md, documentation-shapes.md, and domain.md when the context index needs updating. |
| Code Review Rules | code-review-rules.md; add its evidence, evaluation, or official-documentation references only when routed by that file. |

Do not load domain, localization, or session-history evidence for a
Code-Review-only request unless the selected reference explicitly routes to
it. Load setup-questions.md only when repository evidence and documented
defaults leave a material ambiguity.

## Workflow

1. Resolve the smallest memory_slice, its operation when required, the
   repository scope, the caller's authority, and whether minimal setup must
   precede the selected capture.
2. Inspect the applicable AGENTS.md chain, root CONTEXT.md, matched subproject
   contexts, indexed topics, relevant ADRs, and only the evidence needed for
   the selected operation.
3. Draft the exact intended targets, wording, evidence, unknowns, and links.
4. For inspection, review, proposal, or dry-run work, transition to reported.
   For a durable write without direct scoped authority, transition to confirm
   and show the exact target, section, wording, and before/after block. Never
   turn a proposal into an apply operation because the user did not object.
5. After direct scoped authority or affirmative confirmation, apply only the
   selected surfaces, performing any required minimal setup before capture. Read
   targets back, verify links and indexes, scan for duplicate normative
   wording, run git diff --check, and transition to complete or blocked.
   Report the capture result separately from the knowledge data.

## Durable capture and compaction

Use references/durable-capture.md for corrections, preferences, rules,
localization conventions, and decisions. Determine the narrowest destination,
propose exact wording, wait for confirmation, handle duplicates or conflicts,
and verify the final diff.

Use references/agents-compaction.md only for an explicit compaction request or
context-size review. Measure the actual chain, preserve always-active
invariants and the minimum Code Review Rules block, propose conditional
material as flat topic files, and apply only after approval.

## Independence and runtime boundary

This skill runs in the invoking task and owns no task profile, model selection,
worker delegation, GitHub transport, or external publication. It may write
consumer-repository context only when the current request authorizes the
selected surface. It must remain independent from the other workflow
implementations and must report unavailable evidence or ambiguous authority
instead of guessing.

## Reference responsibilities

- states.md: workflow-node and field-qualified state inventory.
- options.md: canonical fields and values.
- domain.md: repository-root and scoped-context discovery, layout, and ADR
  ownership.
- domain-modeling.md: context, topic, ADR, inline-update, closeout, and review
  semantics.
- durable-capture.md: classification and confirmation for durable capture.
- agents-compaction.md: measurement, proposal, section split, and verification.
- setup-workflow.md: setup defaults, pointers, write checklist, and completion
  report.
- code-review-rules.md: evidence, evaluation, rendering, and exact AGENTS.md
  update semantics.
- documentation-shapes.md: fallback shapes when a consumer repository has no
  stronger local format.
- context-seed.md and session-history.md: initial and accepted session-backed
  evidence.
- translation.md: optional localization memory.
