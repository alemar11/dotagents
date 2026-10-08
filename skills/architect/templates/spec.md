# <Feature title>

<!-- Template for new or consolidated specs. For legacy revisions, preserve task locations under references/existing-specs.md. -->

<a id="spec"></a>

## Problem and expected behavior

<Who is affected, what problem they have, and how behavior changes. Show a realistic user journey or caller example and its expected result. Include relevant failure cases, compatibility obligations and scope boundaries; cite current behavior where it matters.>

## Design and decisions

<Include only when needed. Describe accepted responsibilities, state ownership, invariants and interfaces, with rationale and material tradeoffs. Separate binding decisions from assumptions and optional suggestions. For a simple change, fold the necessary detail into the behavior section and omit this section.>

<!-- Put relevant risks, exclusions, source links and prerequisites beside the design or task they affect. A prerequisite names its exact same-repository artifact, required evidence and gated activity. Resolve blocking decisions before calling the plan ready. -->

## Acceptance criteria

- <Observable success condition.>

<!-- Add concrete scenarios only when they clarify the criterion. -->

## Tasks and verification

<!-- Order tasks by the recommended implementation sequence. Add a linked index only when it improves navigation; omit it for a single task. Repeat the task section below for each task. -->

<When feature-wide verification needs coordination, state the shared checks, required inputs and verification owner here. Distinguish local tests from real integration evidence and later rollout conditions. Omit when task checks suffice.>

<a id="task-<task_id>"></a>

### <Task title>

- spec: [<spec title>](#spec)
- task_id: <stable lower-kebab identity>
- acceptance_refs: <Exact acceptance-criterion text to which this task contributes>

#### Outcome and scope

<What this task delivers, its boundaries, and relevant exclusions. Include enough context to act on this task together with the main spec.>

#### Prerequisites

- blocked_by: <task ID and required outcome, or none>
- external_prerequisites: <same-repository artifact outside this spec and required evidence, or none>

#### Checks

- <Observable completion condition> — **Verify:** <Test or observation, including integration evidence when needed>.

---

- spec_revision: <positive integer>
- owner_repository: <verified repository identity>
