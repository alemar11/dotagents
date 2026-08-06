---
name: feature
description: "Analyze one or more related feature inputs, converge their repository-owned outcomes, surface one consolidated batch of user questions, and produce a structured textual Feature Plan that se2:implement can execute; use optional read-only analyst workers when available, publish the plan to GitHub by default, and never implement code."
---

# Feature Planning

## Purpose and invocation

Use this skill only for an explicit SE2 Feature-planning request. Accept a
new request, a set of related source issues, or an explicit plan-maintenance
request for an existing published plan.

The result is a Feature Plan, not an implementation graph. For every
repository-owned plan member, converge:

- the bounded product or capability outcome;
- the source-issue relationship and multi-issue consolidation rationale;
- the problem analysis, scope, non-goals, and repository context;
- stable Feature acceptance criteria;
- constraints, assumptions, risks, and validation intent;
- one complete batch of material questions for the user when decisions remain;
- a narrative plan that is clear enough for se2:implement to derive execution
  work without invoking se2:feature for technical decomposition.

For a multi-repository request, produce one linked plan member per affected
repository. Keep repository context and source evidence separate per member.
Do not create an artificial integration issue.

This skill never writes repository code, derives implementation execution units
or an execution graph, schedules implementation workers, creates worktrees, chooses code
design, merges changes, or decides delivery completion. Its terminal product is
the plan and its optional GitHub projection.

## Application task, delegation, and goal

For a task-managed run, load the skill-owned task profile and the shared task
preflight before creating, resuming, or monitoring the planner task. The
application task is an execution envelope for the current planning run; it is
not a Feature graph node.

The planner is required. Read-only analysis-worker and critic-analyst roles
are optional capability-conditioned roles. When delegation is available, the
planner may dispatch bounded workers with non-overlapping analytical
responsibilities. When it is unavailable, the planner performs the same
analysis serially. Delegation unavailability never changes the plan contract
and never blocks planning.

The planner must use the invoking session's exact saved local project and
local environment. It must not create or use a Git worktree, isolated
checkout, or task fork. If the destination cannot be independently verified,
stop before creating, resuming, or monitoring the task.

When goal tools are available, create or adopt one goal for the whole Feature
Plan run after the task preflight is ready. Keep that goal active while the
task waits for the user's question batch. Complete it only after the plan is
published or an explicitly requested preview is complete. Do not mark the goal
blocked merely because the plan is awaiting user input; the plan run-state
owns awaiting-user-input separately. If goal tools are unavailable, preserve
the same objective in the task report and continue.

The shared task preflight must verify required task creation, observation,
monitoring, and relay capabilities. It records delegation and goal
capabilities as optional runtime facts. A missing optional capability selects
the documented fallback; it does not authorize a replacement planner task.

## Analysis worker contract

The planner is the sole reducer and owner of the canonical plan. Workers
return evidence and proposals only; they do not edit the plan, create hosted
issues, ask the user directly, publish, or invoke se2:implement.

The optional analytical roles are:

- intent-analyst: normalize source issues and identify the requested outcome;
- context-analyst: inspect repository instructions, code, documentation, and
  ownership facts needed for a grounded plan;
- boundary-analyst: compare related issues and test whether outcomes should be
  consolidated or separated;
- question-analyst: collect missing decisions, assumptions, risks, and
  acceptance gaps;
- critic-analyst: study the original problem independently and challenge
  anchoring, unnecessary constraints, missing outcomes, and context conflicts.

All workers receive the same immutable user intent and source set. The
critic-analyst receives no preliminary planner plan and no context-derived
requirements during its first pass. It may later inspect repository
instructions as evidence of a possible conflict, but independence is not an
authority bypass: global safety rules and read-only behavior still apply.

The parent must preserve worker provenance, separate evidence from
speculation, deduplicate questions, and reconcile conflicting analyses before
plan composition. Worker count is selected from available capacity and useful
analytical partitions; configured capacity is not evidence that a worker
started.

## Repository context and source routes

Resolve the affected repository set and source route during Intake. For every
repository, read the applicable AGENTS.md hierarchy and the documents and
paths it requires. The main planner uses that hierarchy as normative planning
context and records the sources and facts used.

The critic-analyst is deliberately independent from those context-derived
constraints during its first-pass problem study. If the critic identifies a
rule that appears to obstruct the requested outcome, retain the conflict as
evidence and surface it as a decision or question. Do not silently override
AGENTS.md and do not silently let it erase the user problem.

Source routes are:

- new-source: build a plan from explicit intent and source issues;
- existing-source: rehydrate one published plan or linked plan set and apply
  only an explicit semantic maintenance request.

An Idea source is tentative evidence. Preserve its open questions and derive
every plan field independently. Do not promote Idea fields into requirements
without fresh evidence.

## Consolidation and multi-issue semantics

Treat issue titles, headings, requested counts, and proposed splits as
candidate evidence. Consolidate sources when they describe one independently
deliverable outcome. Keep separate plan members when an exclusive outcome,
acceptance obligation, usable landing state, or delivery reason remains.

Multiple source issues may map to one plan member. Independently deliverable
outcomes become separate plan members in the same plan set or separate
explicit planning runs. Multi-repository work produces one linked plan member
per repository. Source mapping and the consolidation decision remain visible
in the final plan.

Do not create implementation units, dependency IDs, execution waves,
allowed-path claims, or tracker-specific execution relations in Feature planning.
se2:implement derives those from the complete plan.

## Question batch

Analysis must collect all material questions before asking the user. The
clarification phase presents one consolidated batch, not one question per
turn. Each question records:

- a stable question ID;
- the decision requested;
- why it matters;
- affected outcome, scope, acceptance, or ownership;
- available options and the recommended answer;
- blocking or non-blocking status;
- provenance from the analysis that raised it.

Questions that change the product outcome, repository ownership, scope,
acceptance, or plan boundaries are blocking. The task remains
awaiting-user-input until the user answers the batch. Non-blocking questions
become explicit assumptions with their impact. Technical implementation
questions belong to se2:implement and do not restart Feature planning.

## Feature Plan contract

The Feature Plan is the canonical semantic content. When published, a GitHub
issue of type Feature is its hosted projection and authoritative durable copy;
the type is metadata and does not carry the semantics.

The plan must contain:

- plan identity and source-issue mapping;
- shared outcome, problem statement, and analysis;
- explicit scope and non-goals;
- affected repository members and links;
- repository-context sources and relevant facts;
- stable Feature acceptance criteria rendered as F-AC-NN list items;
- constraints, assumptions, risks, and validation intent;
- the critic-analyst findings and accepted or rejected challenges;
- the resolved question batch, or the current awaiting-user-input batch;
- implementation considerations and evidence without prescribing code design;
- the handoff statement for se2:implement;
- selected operation and publication evidence.

Feature criteria use stable F-AC-NN identities and a monotonic
feature_acceptance_high_water. They are contract identity, not Markdown
checkbox state. This workflow does not assign T-AC-NN identities or an
execution-unit acceptance high-water; those belong to the execution plan derived by
se2:implement.

## Workflow graph

The graph contains planning milestones and one publication adapter. Its
publication node loads the shared G dependency and hosted-content contracts
internally; transport and read-after-write safeguards remain mandatory but do
not become planning nodes.

Before the first hosted operation in plan-publication, load the shared
[hosted-content-safety.md](../../references/hosted-content-safety.md) contract
for the exact projected content.

~~~mermaid
flowchart TD
    intake -->|normalized source set| analysis
    maintenance -->|rehydrated plan evidence| analysis
    intake -->|invalid scope or identity| blocked
    maintenance -->|conflict or missing target| blocked
    analysis -->|material questions| clarification
    analysis -->|sufficient evidence| convergence
    analysis -->|missing context or failed analysis| blocked
    clarification -->|answer batch received| convergence
    clarification -->|unresolved or declined decision| blocked
    convergence -->|bounded plan members| plan
    convergence -->|independent scope cannot be resolved| blocked
    plan -->|draft complete| plan-validation
    plan -->|missing required content| blocked
    plan-validation -->|plan-ready| plan-publication
    plan-validation -->|invalid or contradictory plan| blocked
    plan-publication -->|preview or verified publish| complete
    plan-publication -->|operation or reconciliation failure| blocked
~~~

Only the following files are graph nodes:

| node_id | file | kind | entry condition | transitions |
| --- | --- | --- | --- | --- |
| maintenance | steps/maintenance.md | action | explicit maintenance request and existing plan evidence | analysis, blocked |
| intake | steps/intake.md | action | explicit Feature intent or source issue set | analysis, blocked |
| analysis | steps/analysis.md | action | normalized source set and repository targets | clarification, convergence, blocked |
| clarification | steps/clarification.md | decision | consolidated material question batch | convergence, blocked |
| convergence | steps/convergence.md | action | evidence and answered questions are available | plan, blocked |
| plan | steps/plan.md | action | bounded plan members are resolved | plan-validation, blocked |
| plan-validation | steps/plan-validation.md | validation | textual plan draft is complete | plan-publication, blocked |
| plan-publication | steps/plan-publication.md | action | plan is ready and operation mode is resolved | complete, blocked |
| complete | steps/complete.md | terminal | preview is frozen or publication is verified | none |
| blocked | steps/blocked.md | terminal | a required planning or publication contract cannot be satisfied | none |

The application task and optional analysis workers are execution envelopes,
not graph nodes. A question batch is a user-facing wait state inside
clarification, not a separate node for each question.

## Workflow rules

### Intake and maintenance

Normalize the explicit source issue set, preserve the original intent, and
resolve repository identities without inventing scope. Maintenance rehydrates
the existing plan projection and carries only the explicit semantic change
into the same analysis and convergence flow. It never creates a second plan
identity and it never starts an implementation worker.

### Analysis

Run the bounded analyst roles when delegation is available and otherwise run
their assignments serially in the planner. Freeze the input context for the
run. Collect repository facts, outcome alternatives, boundary evidence,
critic challenges, assumptions, and the complete question candidate set.

### Convergence

Resolve one or more repository-owned plan members from the evidence. Preserve
source provenance and explain every consolidation or separation. Do not
manufacture distinctions merely to preserve issue counts. A plan is ready for
composition only when each member has a coherent outcome and a clear
ownership boundary.

### Plan composition and validation

Write the narrative plan from confirmed evidence, accepted assumptions, and
answered questions. Keep implementation considerations useful to Implement
without turning them into an execution graph or prescribing code design.

Validate only the plan contract: outcome, scope, non-goals, repository
identity, acceptance criteria, source mapping, context evidence, assumptions,
risks, validation intent, question status, critic reconciliation, and
Implement handoff clarity. Do not validate execution graphs, worker scheduling,
current Git HEADs, or implementation readiness here.

### Plan publication

Resolve run_mode once after plan validation. Omitted run_mode means publish;
preview is accepted only when explicitly requested. Preview retains the
complete plan as local report data and performs no hosted reads for a new
source. Publish loads the G dependency preflight and hosted-content-safety
contract immediately before the first hosted operation, publishes one Feature
plan issue per repository member through the G-owned workflow, and verifies
every result with authoritative read-after-write evidence. A hosted failure
does not silently fall back to preview; retain the calculated plan and report
the blocker.

When one exact hosted Idea was the source and the Feature Plan publishes
successfully, close that source Idea as completed only after the plan
publication and its readback are verified. Preview and ambiguous source
identity never close an Idea.

### Implement handoff

Only a complete published plan is an implementation input. Implement reads
the authoritative plan, derives execution units and their dependencies,
path envelopes, and runtime waves in its own control plane, then creates its
orchestrator and Feature Workers. Technical interpretation remains in
Implement. A product-level contradiction is reported to the user as a
bounded plan question; Implement must not create an automatic plan-repair
planner for ordinary implementation detail.

## Transient state and terminal report

Keep current_node_id, entry_route, source_route, run_mode, source issue
identities, repository plan members, analysis evidence, worker provenance,
question batch, assumptions, artifacts, publication evidence, blockers, and
terminal state explicit and transient. Do not store runtime state in Markdown.

A complete report contains:

- every plan member and repository identity;
- source issues, consolidation and separation rationale;
- problem analysis, outcome, scope, non-goals, and context sources;
- Feature acceptance criteria and high-water evidence;
- assumptions, risks, validation intent, and critic findings;
- the full question batch and the user's resolutions;
- the complete textual plan and Implement handoff;
- preview or publication operation evidence;
- source-Idea lifecycle evidence when applicable;
- retained identities, no-op operations, and unresolved blockers when
  applicable.

Terminal states:

- complete: the plan is complete and preview-frozen or published with required
  read-after-write evidence;
- blocked: the exact planning, authority, capability, or publication blocker
  and the smallest recovery input are reported.
