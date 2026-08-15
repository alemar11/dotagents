---
name: feature
description: "Turn one or more related requests into a clear, evidence-backed Feature Plan Set. Describe each Feature's problem, desired outcome, scope, and acceptance criteria, split it into practical Macro Tasks using vertical slices when the outcome supports them, publish semantic and native GitHub dependency projections by default, delegate optional issue label and type classification, and never implement code."
---

# Feature Planning

## Purpose and invocation

Use this skill only for an explicit SE Feature-planning request. Accept a
new request, a set of related source issues, or an explicit plan-maintenance
request for an existing published plan.

The result is a Feature Plan Set with one or more repository-owned Feature
members and a durable macro-planning projection, not a technical
implementation graph. For every Feature member, converge:

- an evidence-backed description of the problem, affected users, actors, or
  systems, and bounded product or capability outcome;
- the source-issue relationship and multi-issue consolidation rationale;
- the problem analysis, scope, non-goals, and repository context;
- stable Feature acceptance criteria;
- an observable usable landing state, ownership boundary, and delivery reason;
- a closed set of Macro Task areas that collectively cover the Feature outcome
  and its acceptance criteria, using vertical slices when the outcome supports
  them;
- macro planning dependencies or `blocked_by` relations between those areas;
- Feature-level `blocked_by` relations to other Feature members only for hard
  outcome dependencies, with repository identity preserved for Implement's
  deterministic stack-or-scheduling projection;
- constraints, assumptions, risks, and validation intent;
- one complete batch of material questions for the user when decisions remain;
- a narrative plan that is clear enough for se:implement to derive execution
  work without invoking se:feature for technical decomposition.

For a multi-repository request, produce one or more linked Feature members per
affected repository. Keep repository context and source evidence separate per
member. Do not create an artificial Feature container or integration issue.

This skill never writes repository code, derives technical implementation
execution units or an execution graph, schedules implementation workers,
creates worktrees, chooses code design, merges changes, or decides delivery
completion. It does create the Feature-owned macro Task projections and their
non-operational planning relations. Its terminal product is the complete Plan
Set, one closed Macro Task registry per Feature, and their optional GitHub
projections.

## Application task, delegation, and goal

For a task-managed run, read
[task-profile.md](references/task-profile.md), the shared
[task preflight](../../references/task-preflight.md), and the shared
[task handoff](../../references/task-handoff.md) before creating, resuming, or
monitoring the planner.
The task profile owns the required planner and optional analyst roles, their
model/reasoning profiles, and topology selection. The shared task preflight and
handoff own capability and recovery gates plus typed bootstrap, identity, and
execution-target verification. Apply all three contracts in full; never rely
on ambient profile inheritance or create a replacement after an identity,
profile, or execution-target mismatch.

The planner is the sole reducer and owner of the canonical plan. Optional
workers return bounded read-only evidence and proposals only; they never edit
or publish the plan, ask the user directly, or invoke se:implement. When those
roles cannot be instantiated, the planner runs the same analytical lenses
serially. The application task and workers are execution envelopes, not
Feature graph nodes.

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
deliverable outcome. Keep separate Feature members when an exclusive outcome,
acceptance obligation, usable landing state, or delivery reason remains.

Multiple source issues may map to one Feature member. Independently
deliverable outcomes become separate sibling Feature members in the same Plan
Set or separate explicit planning runs. Multi-repository work may produce one
or more Feature members per repository. Source mapping and the consolidation
or separation decision remain visible in the final plan.

Create separate Feature members only when the user outcome, acceptance
criteria, usable landing state, ownership, or delivery reason is genuinely
independent. A shared integration narrative is not a reason to create a
Feature container. If an acceptance criterion inherently spans distinct
Features, keep the outcome in one Feature or decompose the criterion into
Feature-local criteria; never invent a cross-Feature integration Feature.

After each Feature member has one coherent outcome, define its closed set of
Macro Tasks and decide whether that outcome admits clean vertical slicing. When
it does, make each Macro Task a
bounded vertical view of one slice of the same Feature outcome, not an optional
deliverable or a technical execution unit. When it does not, keep fewer
coherent Macro Tasks and explain the boundary rather than forcing a vertical
split. Macro Tasks may cross repository layers when those layers serve one
coherent outcome. Do not split only into backend, frontend, tests, or other
technical layers. The complete set must cover the Feature acceptance criteria
and must not introduce scope outside the Feature.

Feature-level `blocked_by` relations connect distinct Feature IDs in the same
Plan Set and express a hard outcome dependency, never preferred order alone.
Repository identity gives the relation a deterministic Implement projection:
a same-repository edge is mandatory stack intent, while a cross-repository
edge remains scheduling-only because no Git ancestry can span repositories.
After every parent issue identity is known, publication must mirror each edge
as an exact native GitHub `blocked by` relationship from the dependent Feature
issue to the blocking Feature issue. Cross-repository Feature dependencies use
exact issue URLs. The Plan Set remains semantic authority; the native edge is
an expected provider projection that publication must always attempt. A
verified edge is preferred, but a failed, unavailable, or unknown native result
is reported and does not block the body-backed semantic publication.
This projection does not make Feature the owner of branches, exact heads,
technical execution edges, or worker scheduling. Record non-blocking preferred
order as prose instead of `blocked_by`.

A Macro Task `blocked_by` relation is narrower: it may reference only a Macro
Task whose `parent_feature_id` is exactly the current Feature ID.
Cross-Feature Task-to-Task edges are invalid, including when the Features
share a repository. After all child issue identities are known, publication
must mirror every valid macro-local edge as a native GitHub `blocked by`
relationship from the dependent child Task to the blocking child Task. A
native Task dependency may never cross parent Features.

Macro Task `blocked_by` relations are planning structure and sequencing
context. They are not Implement execution edges, worker gates, PR boundaries,
or stack instructions. Implement may combine, reorder, or internalize them in
its technical execution graph, but it must preserve every Macro Task outcome
and Feature acceptance criterion.

Do not create technical implementation units, allowed-path claims, execution
waves, worker assignments, or technical dependency IDs in Feature planning.
se:implement derives those from the complete Feature Plan Set and each
Feature's Macro Task registry.

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
questions belong to se:implement and do not restart Feature planning.

## Feature Plan contract

The Feature Plan Set is the canonical semantic content. When published, each
Feature member becomes one GitHub parent issue. There is no hosted container
issue. Each parent Feature carries the common Plan Set identity and revision,
the set-membership manifest, its own Feature identity, and its own closed Macro
Task registry. Repository labels and native GitHub Issue Types are optional
metadata and do not carry these semantics. Feature never preselects their
values. After each final hosted issue projection and exact identity are
verified, delegate classification and authorized application to
`$g:github-tagger`. Instruct it to choose the smallest relevant set of existing
labels, including none, and zero or one available native issue type for that
exact issue.

The plan must contain:

- Feature Plan Set identity, revision, and source-issue mapping;
- one Feature identity, evidence-backed problem statement, affected users,
  actors, or systems, desired outcome, and analysis per member;
- explicit scope and non-goals;
- affected Feature members, repositories, and parent-issue identities;
- repository-context sources and relevant facts per Feature member;
- stable Feature acceptance criteria rendered as F-AC-NN list items per
  Feature member;
- a Feature Plan Set registry that maps every Feature identity to its parent
  Feature issue, Feature-level `blocked_by` refs, and local Macro Task
  registry;
- the repository-sensitive projection rule that same-repository Feature
  `blocked_by` is mandatory stack intent and cross-repository `blocked_by` is
  scheduling-only;
- one native GitHub `blocked by` operation and readback attempt for every
  Feature-level dependency, including cross-repository edges, with its
  verified, no-op, failed, unavailable, or unknown outcome;
- one hosted child Task projection for every Macro Task, linked to its own
  parent Feature issue;
- Macro `blocked_by` relations that reference only Macro Tasks with the same
  `parent_feature_id` and remain planning-only;
- one native GitHub `blocked by` operation and readback attempt for every
  macro-local dependency, with its outcome and no cross-Feature Task edge;
- the per-Feature closure policy that each parent Feature and only its own
  associated Macro Tasks belong to that Feature's final implementation
  closing set;
- constraints, assumptions, risks, and validation intent;
- the critic-analyst findings and accepted or rejected challenges;
- the resolved question batch, or the current awaiting-user-input batch;
- implementation considerations and evidence without prescribing code design;
- the handoff statement for se:implement;
- selected operation and publication evidence.

Feature identities use stable lower-kebab `feature_id` values within the
`feature_plan_set_id`. Feature criteria use stable F-AC-NN identities and a
monotonic feature_acceptance_high_water per Feature member. They are contract
identity, not Markdown checkbox state. Macro Tasks use stable lower-kebab
`macro_task_id` values scoped by `parent_feature_id` and map to one or more
F-AC-NN identities. This workflow does not assign T-AC-NN identities or an
execution-unit acceptance high-water; those belong to the technical
execution evidence derived by se:implement.

The canonical Feature Plan Set registry contains one entry per Feature:

- `feature_plan_set_id`: stable identity for the sibling Feature set;
- `feature_plan_set_revision`: monotonic set revision;
- `feature_id`: stable lower-kebab identity within the set;
- `repository_identity`: the repository owned by this Feature;
- `parent_issue_ref`: the authoritative hosted Feature issue after publication;
- `blocked_by`: zero or more Feature IDs in the same set;
- `macro_tasks`: the complete local Macro Task registry for this Feature.

Each Macro Task entry contains:

- `parent_feature_id`: the Feature identity that owns the Macro Task;
- `macro_task_id`: stable lower-kebab identity within that Feature;
- `macro_outcome`, `scope`, and `feature_acceptance_refs`;
- `blocked_by`: zero or more Macro Task IDs whose `parent_feature_id` is the
  same value;
- `macro_status` and `child_issue_ref` after publication.

The set registry is closed. Every Feature identity has exactly one parent
issue and every Macro Task has exactly one parent Feature and one child Task.
The registry is projected into every parent Feature issue with the same set
identity and revision; authoritative readback must reconcile those
projections. No child issue, title, or narrative text can add a sibling,
Feature dependency, or Macro Task to the registry.

## Workflow graph

The graph contains planning milestones and one publication adapter. Its
publication node loads the shared
[G dependency preflight](../../references/codex-dependency-preflight.md) and
hosted-content contracts internally; transport and read-after-write safeguards
remain mandatory but do not become planning nodes.

Read [states.md](references/states.md) for the human-readable meaning of every
workflow node and for the separate plan, report, domain, and external state
registries. That reference also defines the runtime-checkpoint boundary.

Before every hosted write in plan-publication, load the shared
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
    convergence -->|bounded Feature members| plan
    convergence -->|independent scope cannot be resolved| blocked
    plan -->|draft complete| plan-validation
    plan -->|missing required content| blocked
    plan-validation -->|plan-ready| plan-publication
    plan-validation -->|invalid or contradictory plan| blocked
    plan-publication -->|preview or verified semantic publish with dependency attempt results| complete
    plan-publication -->|semantic publication failure or missing dependency attempt result| blocked
~~~

Only the following files are graph nodes:

| node_id | file | kind | entry condition | transitions |
| --- | --- | --- | --- | --- |
| maintenance | steps/maintenance.md | action | explicit maintenance request and existing plan evidence | analysis, blocked |
| intake | steps/intake.md | action | explicit Feature intent or source issue set | analysis, blocked |
| analysis | steps/analysis.md | action | normalized source set and repository targets | clarification, convergence, blocked |
| clarification | steps/clarification.md | decision | consolidated material question batch | convergence, blocked |
| convergence | steps/convergence.md | action | evidence and answered questions are available | plan, blocked |
| plan | steps/plan.md | action | bounded Feature members are resolved | plan-validation, blocked |
| plan-validation | steps/plan-validation.md | validation | textual plan draft is complete | plan-publication, blocked |
| plan-publication | steps/plan-publication.md | action | plan is ready and operation mode is resolved | complete, blocked |
| complete | steps/complete.md | terminal | preview is frozen or publication is verified | none |
| blocked | steps/blocked.md | terminal | a required planning or publication contract cannot be satisfied | none |

The application task and optional analysis workers are execution envelopes,
not workflow graph nodes. The durable Feature Plan Set registry and its
Feature/Macro Task relations are planning projections, not workflow nodes or
the Implement runtime graph. A question batch is a user-facing wait state
inside clarification, not a separate node for each question.

## Workflow rules

Before executing a node, read its registered `steps/<node-id>.md` contract.
Those files own node-specific inputs, stop conditions, detailed behavior,
side effects, and transitions. Follow the graph and registry above as the
canonical order; do not skip `plan-validation`, enter `plan-publication`
early, or infer a transition from prose. In particular, the publication step
owns preview selection, the G dependency handoff, hosted-content projection,
native dependency attempts, optional tagging, readback, and recovery. Do not
create a Feature Plan Set container. When one exact hosted Idea is the source,
close that source Idea as completed only after the complete Plan Set and all
required publication results reconcile; preview and ambiguous identity never
close it.

### Implement handoff

Feature must publish and reconcile the complete Feature Plan Set and every
planned child projection before it can report its own workflow complete. At
the Implement handoff, however, each published parent Feature issue is the
required semantic contract; its Macro Task children are useful planning
projections rather than an implementation gate. Implement may classify those
projections as `complete`, `partial`, or `absent`, report any degradation, and
derive missing execution coverage from outcome, scope, and F-AC without
creating or repairing Task issues. Implement reads the authoritative set,
projects same-repository Feature `blocked_by` as mandatory stack intent and
cross-repository Feature `blocked_by` as scheduling-only, re-evaluates real
technical prerequisites, and derives technical execution units, stable
assignment-scoped T-AC criteria, path envelopes, and runtime waves in its own
control plane. It may combine, reorder, or internalize available Macro Task
dependencies while preserving every Feature criterion and available Macro
outcome. A T-AC may specialize an F-AC but never replace, weaken, or change it.
It creates one Feature Worker and one PR per
implementation-eligible Feature member. A same-repository child may start from
its parent's verified `candidate-published` exact HEAD before that parent is
delivery-ready only when no applicable current-head CI check is confirmed
failing; pending CI remains non-blocking, and Implement may exempt only a
G-verified infrastructure or flaky failure unrelated to candidate correctness.
Technical interpretation remains in Implement. A product-level
contradiction that cannot be resolved without changing outcome, scope, F-AC,
or Feature dependencies is reported to the user as a bounded plan question;
missing task decomposition, technical ambiguity, and acceptance specificity
remain autonomous Implement work. Implement must not create an automatic
plan-repair planner for ordinary implementation detail.

## Transient state and terminal report

Keep current_node_id, entry_route, source_route, run_mode, source issue
identities, Feature Plan Set and Feature members, analysis evidence, worker
provenance, question batch, assumptions, artifacts, publication evidence,
blockers, and terminal state explicit and transient. Do not store runtime
state in Markdown.

A complete report contains:

- the Feature Plan Set identity and every Feature member/repository identity;
- source issues, consolidation and separation rationale;
- problem analysis, outcome, scope, non-goals, and context sources;
- Feature acceptance criteria and high-water evidence;
- the complete Feature registry, Feature-level dependency relations, every
  local Macro Task registry, and projected parent/child issue identities when
  published;
- native GitHub dependency attempt and `blockedBy`/reciprocal `blocking`
  readback or failure evidence for every published Feature-level and
  macro-local edge;
- assumptions, risks, validation intent, and critic findings;
- the full question batch and the user's resolutions;
- the complete textual plan and Implement handoff;
- preview or publication operation evidence, including each reconciled tagger
  result when published;
- source-Idea lifecycle evidence when applicable;
- retained identities, no-op operations, and unresolved blockers when
  applicable.

Terminal states:

- complete: the plan is complete and preview-frozen or published with required
  read-after-write evidence;
- blocked: the exact planning, authority, capability, or publication blocker
  and the smallest recovery input are reported.
