# Feature Specification Contract

Read before authoring, reviewing, saving, or consuming a spec. This file owns
content and identity; templates render it, and output references own transport.

## Main specification

Every spec and task in an invocation belongs to one selected repository; an
explicit batch may contain several independent specs there. Return work for
other repositories as out of scope without silently dropping its requirements
or claiming full coverage. Do not create parent issues, task issues, set
registries, companion specs in other repositories, or cross-repository issue
references. Historical references follow [existing-specs.md](existing-specs.md).

A complete spec records:

- the problem, affected actors, expected behavior, scope, and non-goals;
- representative user or caller usage that makes the proposed behavior concrete;
- important failure cases, compatibility obligations, constraints, and risks;
- accepted decisions, relevant repository evidence, and explicit assumptions;
- ownership, domain invariants, and boundary contracts where the change affects
  them, with rationale and material tradeoffs rather than an exhaustive code plan;
- observable feature acceptance criteria covered by task verification checks;
- an ordered task index and each task's embedded or linked detailed contract;
- prerequisites outside the selected spec when relevant, with exact source
  references and the evidence required to satisfy them.

Use project vocabulary and proportional detail: a small change may express
usage and design within the behavior section. User stories, diagrams, API
sketches and alternatives are not mandatory formats. Design reasoning follows
[design.md](design.md) when relevant to changed boundaries.

## Interfaces and readiness

Record accepted interfaces, failure semantics and compatibility assumptions;
API/schema documentation may supply evidence. Describe required external
capabilities as inputs, without planning another repository's work or linking
its issues. Missing implementation does not block planning against an agreed
contract; resolve material interface uncertainty before calling the plan ready.

State the checks and inputs required for PR readiness separately from rollout
conditions. Require real integration only when the accepted criteria call for
it, and never present fixture tests as provider verification.

## Identity and authority

| Field | Meaning |
| --- | --- |
| `spec_revision` | Positive integer, incremented once for each accepted semantic revision. |
| `owner_repository` | The single verified repository that owns the spec and all its implementation tasks. |

A published spec is identified by its exact issue URL in the verified owner
repository. An existing local source is identified by its repository and path;
an unpublished conversational draft needs no separate identifier. Titles and
list positions are display metadata. Use exact saved references within the
selected repository when referring to another spec; do not resolve a
prerequisite by a bare title or issue number.

Acceptance criteria are plain bullets describing observable success, without
checkboxes, assigned IDs, short titles, or mandatory per-criterion verification
lines. Task acceptance references quote the applicable criterion text rather
than list positions. When wording changes, update affected references together
and preserve the accepted obligation; record material replacements or removals
in a compact revision note. Keep source links beside supported claims.

New and consolidated specs keep all content in one authoritative GitHub issue.
Legacy specs may retain separate task issues under [existing-specs.md](existing-specs.md);
targeted revisions do not require migration. Tasks inherit the owner repository
and own acceptance links and task prerequisites. Related specs use ordinary
links; prerequisites remain in bodies. Architect never manages native GitHub
blocking relationships; explicit requests use `gh` outside this contract.

Spec-level prerequisites name exact same-repository references, required outcomes
or evidence, and the activity and scope gated: implementation, integration,
publication, merge or deployment. Shared scope or recommended order is not a
dependency. An agreed interface may permit parallel implementation; a usable
candidate may satisfy integration without issue closure or merge. Preserve
explicit merge or deployment requirements. Task-specific prerequisites stay
with their tasks; the executor checks both without expanding selection.

Preserve executor-owned progress and provider status; neither advances
`spec_revision`. Requirements, decisions and task contracts do. Implementation
readiness metadata belongs to the execution caller, and a completed spec proves
no implementation. Revision rules live in [existing-specs.md](existing-specs.md).

## Task contract

Tasks are actionable implementation handoffs. A fresh session must be able to
read the main spec plus one task and understand its outcome, limits,
prerequisites, and completion checks without the drafting conversation.

| Field | Meaning |
| --- | --- |
| `task_id` | Stable lower-kebab identity within this spec; never reused after retirement. |
| `title` | Concise description of the task outcome. |
| `outcome` | Observable capability or enabling result delivered by this task. |
| `scope` | Included work and relevant exclusions. |
| `acceptance_refs` | Exact text of existing acceptance criteria to which this task contributes; contribution alone does not prove a criterion satisfied. |
| `checks` | Each check pairs an observable completion condition with its test or observation; include assembled integration evidence where needed. |
| `blocked_by` | Other task IDs in this spec that supply real prerequisites, each with the required outcome or evidence. |
| `external_prerequisites` | Prerequisites outside this spec but within its repository, with exact artifact references and required evidence, or none. The established field name is retained; it does not permit cross-repository issue links or expand selection. |

The ordered index owns task membership and recommended order, listing only IDs,
titles matching their details, and detail links. Task details own other fields;
read every task to establish coverage and the full dependency graph.

A task is identified by its containing spec reference plus `task_id`; within
one spec, `task_id` is sufficient. Display position may change independently.
All local dependency targets must exist and the graph must be acyclic. Retain
retired task IDs in a compact revision note.

Every task contributes to at least one feature criterion, and the complete
task plan covers every criterion. Preparatory work records the criteria it
enables and its own independently verifiable completion checks. Do not invent
a new feature criterion merely to justify an unrelated task.

Read [task-decomposition.md](task-decomposition.md) when creating or changing
task boundaries, recommended order, or prerequisites.

## Decisions and validation

Review usage against interfaces and failure semantics, and ownership and
invariants across tasks. Callers must not coordinate hidden implementation
steps. A dependent decision is not ready while essential empirical evidence is
missing; name the required observation and continue independent work.

Preserve accepted API, schema, compatibility, ownership, security, architecture,
migration and testing decisions. Record their consequences and evidence or
authority; distinguish them from safe assumptions and replaceable implementation
suggestions. A source's proposal is not an accepted requirement without authority.
Clarification follows the entrypoint; do not invent decisions to fill a template.

Use precise interfaces or a compact schema/state example when prose would lose
an accepted contract. Relevant repository-relative paths may cite current
evidence; they are not an exhaustive edit list. Leave incidental helpers,
commands, worker assignment, and Git operations to implementation.

Task checks must collectively prove the feature criteria, including assembled
behavior where needed. Cite current behavior when scope, regression preservation,
migration, feasibility or verification depends on it; no per-criterion baseline
field is required. Investigate material unknown baselines, never invent failure
evidence, and distinguish preservation obligations from new behavior.

Prefer an existing verification boundary that exercises the relevant external
behavior. Propose a new boundary only with a concrete adequacy reason. When the
choice materially affects confidence, explain what it proves and which risks
need another boundary. Routine boundary choices need no separate approval.
Task completion, especially preparatory work, alone never proves the assembled
feature works.

## Rendering

Templates are presentation guides, not text to publish verbatim. Omit empty
optional sections and authoring instructions. Keep required task metadata and
explicit `none` prerequisites so missing information is distinguishable from
no dependency. Lead with the problem and observable behavior; put compact identity
metadata at the end. Use concrete WHEN / THEN scenarios only where they clarify
a criterion, not as a second mandatory requirements list. Keep the task index
free of progress checkboxes and do not seed an execution progress section during
planning. New or consolidated issue bodies embed tasks under `## Task details`;
legacy indexes retain links to existing task artifacts until consolidation.
For embedded tasks, use `<a id="task-<task_id>"></a>`, H3 task titles and H4
subsections, with a fixed `spec` anchor for back-links; the index links to these
task anchors. GitHub output owns transport and metadata.
