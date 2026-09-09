# Feature Specification Contract

Read before authoring, reviewing, saving, or consuming a Feature spec. This is
the canonical content and identity contract; templates project it into readable
Markdown. Output references own storage and transport, not feature meaning.

## Main specification

One invocation targets exactly one repository; every spec and task it produces
belongs there. An explicit batch may contain several independent specs in that
repository. Do not create parent issues, task issues, set registries, companion
specs in other repositories, or cross-repository issue references. Same-repository
spec links remain ordinary references, distinct from prerequisites.

When the request spans repositories, select the clearly intended local scope or
resolve the target before drafting. Return other repository work to the caller
as out of scope without planning or publishing it. Do not silently drop those
requirements or claim the local spec covers the complete cross-repository outcome.

A complete spec records:

- the problem, affected actors, expected behavior, scope, and non-goals;
- important failure cases, compatibility obligations, constraints, and risks;
- accepted decisions, relevant repository evidence, and explicit assumptions;
- observable feature acceptance criteria covered by task verification checks;
- an ordered task index and the detailed contract for every task;
- prerequisites outside the selected spec when relevant, with exact source
  references and the evidence required to satisfy them.

Use the project's vocabulary. Include user stories only when they clarify
behavior; a refactor or infrastructure spec can describe interfaces, invariants,
and operational outcomes directly. Omit empty optional sections.

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
| `spec_id` | Stable lower-kebab identity within the repository that owns the spec. |
| `spec_revision` | Positive integer, incremented once for each accepted semantic revision. |
| `owner_repository` | The single verified repository that owns the spec and all its implementation tasks. |

The spec's identity is its owner repository plus `spec_id`. Titles, list
positions, local paths, and hosted issue numbers are not substitutes. Use exact
saved references within the selected repository when referring to another spec;
do not resolve a prerequisite by a bare title or ID.

Acceptance criteria are plain bullets describing observable success, without
checkboxes, assigned IDs, short titles, or mandatory per-criterion verification
lines. Task acceptance references quote the applicable criterion text rather
than list positions. When wording changes, update affected references together
and preserve the accepted obligation; record material replacements or removals
in a compact revision note. Keep source links beside supported claims.

One GitHub issue is authoritative for each spec and
contains the spec, acceptance criteria, ordered task index, and every detailed
task contract. Task sections inherit the owner repository and own acceptance links and task
prerequisites. Related specs use ordinary links; prerequisites remain in the
body, including internal task dependencies. Spec never manages native GitHub
blocking relationships; explicit user requests belong to G, outside this contract.

Spec-level prerequisites identify exact same-repository spec references, required
implementation outcomes or evidence, and the activity and scope they gate.
Do not require issue closure or merge when a usable PR candidate supplies the
needed outcome. Preserve explicitly required merge or deployment conditions. Task-specific
prerequisites outside the spec stay with their tasks. Delivery checks both; a dependency
does not authorize implementing the prerequisite or expanding selection.

Revision rules live in [existing-specs.md](existing-specs.md).
Planning never overwrites executor-owned progress or claims implementation
completion from a drafted task list.

Delivery owns the separate execution section under
[progress.md](../../deliver-features/references/progress.md). That section and
provider status are excluded from semantic contract identity and do not advance
`spec_revision`; all requirements, decisions and task contracts remain included.
The shared [delivery readiness](../../../references/states.md) metadata is also
excluded: it records pickup eligibility or human handoff, not requirements.
Spec preserves either state during ordinary revisions.

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

The spec task index is an ordered list of task IDs, titles, and detail links.
It owns membership and recommended order; task details own all other task
fields. Do not duplicate acceptance links or dependency
descriptions in the index. Read every task to establish coverage and the full
dependency graph. Task titles in the index mirror their details.

A stable task identity is the qualified spec identity plus `task_id`; display
position may change independently. All local dependency targets must exist and
the graph must be acyclic. Retain retired task IDs in a compact revision note.

Every task contributes to at least one feature criterion, and the complete
task plan covers every criterion. Preparatory work records the criteria it
enables and its own independently verifiable completion checks. Do not invent
a new feature criterion merely to justify an unrelated task.

Read [task-decomposition.md](task-decomposition.md) when creating or changing
task boundaries, recommended order, or prerequisites.

## Decisions and validation

Preserve accepted public API, schema, compatibility, ownership, security,
architecture, migration, and testing decisions when they constrain the outcome.
Record the decision, consequence, and evidence or authority. Existing accepted
decisions, choices explicitly delegated to the planner, and safe explicit
assumptions may proceed without a new interview. Material unresolved choices
return through Grilling Session before saving a ready spec.

Distinguish binding decisions from implementation suggestions. Binding
decisions are part of the spec contract; suggestions are optional approaches
that an implementer may replace while preserving outcomes and constraints.
Never turn a source's proposed solution into an accepted requirement without
supporting authority. Do not fill a template by inventing decisions.

Use precise interfaces or a compact schema/state example when prose would lose
an accepted contract. Relevant repository-relative paths may cite current
evidence; they are not an exhaustive edit list. Leave incidental helpers,
commands, worker assignment, and Git operations to implementation.

Every acceptance criterion describes observable success. Task checks supply
credible verification methods and collectively cover all criteria, including
assembled feature behavior where needed. Add
current-behavior evidence when it affects scope, regression preservation,
migration, feasibility, or verification; do not require a baseline field on
every criterion. Label an unverified material baseline as unknown and investigate
it when a decision depends on it. Never invent failure evidence or confuse a
completed preparatory task with the requested feature outcome. Separate
preservation obligations from new behavior.

Prefer an existing verification boundary that exercises the relevant external
behavior. Propose a new boundary only with a concrete adequacy reason. Review
the feature-level outcome as well as individual task checks: task completion
alone never proves the whole feature works.

## Rendering

Templates are presentation guides, not text to publish verbatim. Omit empty
optional sections and authoring instructions. Keep required task metadata and
explicit `none` prerequisites so missing information is distinguishable from
no dependency. Lead with the problem and observable behavior; put compact identity
metadata at the end. Use concrete WHEN / THEN scenarios only where they clarify
a criterion, not as a second mandatory requirements list. Keep the task index
free of progress checkboxes and do not seed a Delivery progress section during
planning. Issue bodies embed task sections under `## Task details`.
Use `<a id="task-<task_id>"></a>`, H3 task titles, and H4 subsections, with a
`spec-<spec_id>` anchor for task back-links. The ordered index links to these
anchors. GitHub output owns transport and metadata.
