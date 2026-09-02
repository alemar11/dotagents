---
name: feature
description: "Turn one or more related requests into an evidence-backed Feature Plan Set with stable acceptance criteria, coherent Macro Tasks, and explicit dependency intent. Use for new planning or bounded maintenance, publish by default, and never implement code."
---

# Feature Planning

## Purpose and boundary

Use this skill only for an explicit SE Feature-planning request. Accept a new
request, related source issues, an Idea source, or an explicit revision of an
existing published Feature Plan Set.

Produce one complete textual Plan Set containing only genuinely distinct
repository-owned Features. Every Feature has a bounded outcome, stable
`F-AC-NN` acceptance criteria, and a closed set of coherent Macro Tasks. The
Plan Set records hard Feature dependencies and same-parent Macro planning
dependencies without turning either into a technical execution graph.

Feature never writes product code, chooses code design, creates branches or
worktrees, schedules implementation workers, defines technical execution
units, assigns `T-AC-NN` criteria, creates pull requests, merges, deploys, or
releases. Those responsibilities belong to Implement.

## Planner task

Read [task-profile.md](references/task-profile.md) before creating or resuming
the planner. Explicit invocation authorizes exactly one visible planner task.
Pass the profile's model and reasoning effort explicitly and use a direct local
project checkout, never an isolated worktree or task fork.

An accepted creation or resume receipt with a stable task identity is enough to
start work. The planner begins at `intake` in its first turn. Do not add a
bootstrap-only turn, ask the planner to rediscover its task identity or
effective profile, compare task metadata with the request, gate on title
readback, or add an assigned-task preflight or handoff contract.
Request a useful title when supported, but treat it as display metadata only.

If the creation effect is genuinely ambiguous, inspect that same attempt once.
Resume the observed task when it exists; create another only after authoritative
evidence proves the first effect did not apply. A rejected creation request or
an ambiguity that cannot be reconciled is a real launch blocker.

The planner is the sole owner of the canonical plan and publication decision.
It may use bounded read-only helpers for repository study or review when useful.
Helpers never publish, edit the plan, ask the user directly, or become required
application tasks. When delegation is unavailable or prohibited, the planner
performs the same work serially.

## Feature Plan Set contract

For every affected repository, read the applicable `AGENTS.md` hierarchy and
the sources it requires. Treat repository and source identity as planning
evidence gathered during Intake, not application-task metadata. A planner task
may read every repository explicitly in scope; its application project does not
create a primary-repository or correctness boundary.

When Intake receives a typed Idea source, validate it against the canonical
[idea-source.md](../idea/references/idea-source.md) handoff before deriving any
Feature fields.

The Plan Set contains:

- a stable lower-kebab `feature_plan_set_id`, monotonic revision, source map,
  and selected `preview` or `publish` operation;
- one entry per genuinely independent Feature with a stable lower-kebab
  `feature_id`, repository identity, problem, observable outcome, scope,
  non-goals, context evidence, constraints, assumptions, risks, and validation
  intent;
- ordinary list-item acceptance criteria with stable bracketed `F-AC-NN`
  identities and a monotonic high-water mark per Feature;
- a closed Macro Task registry per Feature. Each lower-kebab `macro_task_id`
  describes a coherent outcome or vertical slice, maps to one or more F-ACs,
  and never acts as an implementation unit or PR boundary;
- hard-outcome Feature `blocked_by` edges and same-parent Macro `blocked_by`
  edges, both acyclic;
- resolved material questions and explicit assumptions;
- review findings and dispositions when they materially changed the plan;
- an implementation-neutral handoff that lets Implement
  derive technical work while preserving every Feature criterion and available
  Macro outcome.

Multiple source issues may converge into one Feature. Create siblings only
when a distinct usable landing state, acceptance obligation, ownership
boundary, or delivery reason remains. Never create a container or integration
Feature merely to group the set.

A Feature dependency may reference only another Feature in the same Plan Set.
Implementation workflows project a same-repository edge as mandatory stack
intent and a cross-repository edge as scheduling-only because Git ancestry
cannot cross repositories. Preferred order is prose, not `blocked_by`.

A Macro dependency may reference only another Macro Task owned by the same
`parent_feature_id`. Macro edges are planning context; an implementation
workflow may combine, reorder, or internalize them while preserving their
outcomes and F-AC coverage. Cross-Feature Task-to-Task edges are invalid.

For an existing-source revision, retain the exact Plan Set, Feature, Macro, and
hosted issue identities. Apply the smallest semantic patch, increment the
revision, preserve every unaffected field and executor-owned progress, and
state what a later Implement run must reconsider. Never
silently create a replacement plan.

Use [plan.md](templates/plan.md) for the canonical plan,
[macro-task.md](templates/macro-task.md) for child projections, and
[plan-report.md](templates/plan-report.md) for the terminal report.

## Questions and review

Ask only when a material product decision remains after evidence gathering.
Collect all such decisions into one concise batch with recommendations. The
planner may continue without questions when the request is already complete,
the user delegated the choice, or remaining uncertainty is safe as an explicit
assumption. Technical implementation choices belong to the later implementation
workflow.

Clarification is a nonterminal wait. After answers arrive, return to Analysis
and incorporate them. If the user declines a required decision, report the
smallest unresolved blocker rather than guessing.

Review every complete draft. Use an independent read-only helper when useful
and available, otherwise a separate serial review lens. Review must verify the
semantic content and these structural invariants:

- stable identities and monotonic revisions/high-water marks;
- genuinely distinct Feature boundaries and no container Feature;
- observable, non-duplicative F-ACs covered by the closed Macro registries;
- no scope added by Macro Tasks;
- valid, acyclic Feature and same-parent Macro dependency graphs;
- complete source provenance, repository mapping, and publication projections;
- correct same-repository stack and cross-repository scheduling semantics;
- preservation of existing identities, unaffected content, and executor-owned
  progress during maintenance.

Return correctable findings to Plan while revisions are making progress. A
newly exposed material decision returns to Clarification. Repeated unresolved
findings, no-progress revision, or a genuinely unavailable required decision
blocks publication. A separate Plan Validation node or review-round state
machine is not required.

## Workflow graph

The node table is the structural source of truth. Mermaid is its maintained
projection. Read [states.md](references/states.md) before interpreting nodes or
reported values. Before executing a node, read its registered step file.

| node_id | file | kind | entry condition | transitions |
| --- | --- | --- | --- | --- |
| intake | steps/intake.md | action | explicit Feature intent, source set, or revision request | analysis, blocked |
| analysis | steps/analysis.md | action | sources and affected repositories are resolved | clarification, plan, blocked |
| clarification | steps/clarification.md | decision | one or more material product decisions remain | analysis, blocked |
| plan | steps/plan.md | action | evidence and required decisions are available | review, blocked |
| review | steps/review.md | validation | a complete textual Plan Set draft exists | plan, clarification, publish, blocked |
| publish | steps/publish.md | action | review is clean and operation authority is resolved | complete, blocked |
| complete | steps/complete.md | terminal | preview is frozen, or semantic publication, required dependency attempts, and any requested handoff are verified | none |
| blocked | steps/blocked.md | terminal | no responsible transition remains | none |

~~~mermaid
flowchart TD
    intake -->|sources and repositories resolved| analysis
    intake -->|invalid or inaccessible scope| blocked
    analysis -->|material decision remains| clarification
    analysis -->|evidence is sufficient| plan
    analysis -->|required evidence unavailable| blocked
    clarification -->|answers received| analysis
    clarification -->|required decision declined or unavailable| blocked
    plan -->|complete Plan Set draft| review
    plan -->|contract cannot be completed| blocked
    review -->|correctable findings with progress| plan
    review -->|new material decision| clarification
    review -->|clean semantic and structural result| publish
    review -->|repeated unresolved or no-progress finding| blocked
    publish -->|preview frozen or all required publication results reconciled| complete
    publish -->|authority, attempt, handoff, or required write unresolved| blocked
~~~

Workflow position is transient. Do not persist a queue, current node,
checkpoint, task bootstrap, review-round machine, or recovery ledger. Resume
from the current conversation and authoritative published Plan Set, then choose
the next edge from live evidence.

## Publication and result

Publication is the default. Preview is selected only when the user explicitly
requests a local, non-durable result. Never silently downgrade publish to
preview because a dependency, permission, or provider is unavailable.

Intake applies the G dependency check before any hosted source read. The
Publish node owns the same check for hosted publication, hosted-content
projection, parent/child issue operations, relationship and dependency
attempts, exact readback, optional classification, existing-source updates,
and any explicitly requested post-publication handoff. Provider transport
details stay with the focused G workflows. Immediately before every hosted write,
apply the canonical
[hosted-content-safety.md](../../references/hosted-content-safety.md) contract.

Issue identity and semantic body readback are mandatory. Reconcile a genuinely
ambiguous write against the same intended artifact before retrying. The Plan
Set bodies and registries are semantic authority. After exact parent and child
identities exist, reconcile every parent body in place and read the complete
projection back. Record one native dependency attempt and observable result per
canonical edge. A confirmed failed, unavailable, or unknown result is a warning,
but a missing attempt or result blocks. Reconcile any explicitly requested
post-publication handoff before completion. Optional labels and native Issue
Types never gate completion.

Report the Plan Set identity and revision, Feature/repository mapping, F-ACs,
Macro registries, dependency semantics, material questions and assumptions,
review outcome, preview or hosted issue identities, publication/readback
evidence, warnings, and the implementation-neutral handoff. On failure, report
the exact blocker and smallest recovery input without claiming a partial plan
complete.

## Skill Dependencies

Any hosted source read or hosted write requires the installed reusable `$g`
skill for GitHub issue operations and optional classification. A local
new-source preview needs no G workflow. This skill never installs, refreshes,
or substitutes that dependency.
