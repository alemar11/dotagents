# <Feature title>

<a id="spec-<spec_id>"></a>

## Why

<Who is affected, what problem they have, and what success looks like. Cite current behavior when it matters to the change.>

## What changes

<Describe observable behavior, interfaces, or invariants. Include important failure cases and compatibility obligations.>

**Out of scope:** <Explicit boundaries that could otherwise be mistaken for included work.>

## Acceptance criteria

- <Observable success condition.>

<!-- Add WHEN / THEN scenarios beneath a criterion when they clarify distinct triggers, edge cases, or failure behavior. Do not repeat the same requirement in several formats. -->

## Design decisions

<Only accepted choices that constrain implementation, with rationale and evidence. Label safe assumptions and optional suggestions separately. Omit this section when unnecessary.>

## Related specs

<Ordinary links to companion specs and their part in the shared outcome. Omit when none.>

## Shared contract

<For cross-repository work: define the interface in its owning spec, or link its canonical definition. State this repository's producer/consumer obligations, relevant data and failure semantics, and compatibility assumptions. Omit when no shared boundary exists.>

## PR readiness

<State which checks make this repository's PR ready. For shared contracts, distinguish local contract tests from required real-candidate integration; name the verification owner and required input. Keep later deployment conditions separate.>

## Dependencies

- <Exact prerequisite spec link> — **Required:** <Implementation outcome or evidence>. **Gates:** <Implementation, integration, publication, merge, or deployment of the affected work>.

<!-- Write "None" when no spec-level prerequisites exist. Task-specific prerequisites belong in task details. Use ordinary issue links; an open prerequisite issue does not imply all work must wait. A usable PR candidate may satisfy the stated condition. -->

## Implementation plan

1. [<task_id> — <Task title>](#task-<task_id>)

## Task details

<!-- Repeat the following task section for each indexed task. Keep all tasks in this document. -->

<a id="task-<task_id>"></a>

### <Task title>

- spec: [<qualified spec identity>](#spec-<spec_id>)
- task_id: <stable lower-kebab identity>
- acceptance_refs: <Exact acceptance-criterion text to which this task contributes>

#### Outcome and scope

<What this task delivers, its boundaries, and relevant exclusions. Include enough context to act on this task together with the main spec.>

#### Prerequisites

- blocked_by: <task ID and required outcome, or none>
- external_prerequisites: <exact reference and required evidence, or none>

#### Checks

- <Observable completion condition> — **Verify:** <Test or observation, including integration evidence when needed>.

## Risks and open questions

<Material risks, mitigations, and non-blocking unknowns. Resolve decisions that prevent implementation before marking the plan ready. Omit this section when empty.>

## Spec metadata

- spec_id: <stable lower-kebab identity>
- spec_revision: <positive integer>
- owner_repository: <verified repository identity>
