# Feature Plan

## Plan identity

- feature_plan_set_id: <stable lower-kebab set identity>
- feature_plan_set_revision: 1
- plan_status: plan-ready
- source_route: new-source
- source_issues:
- feature_member_count: <count>
- feature_set_closure_policy: each-feature-and-its-associated-macro-tasks

## Feature Plan Set Registry

The Plan Set contains only genuinely distinct sibling Features. It never
publishes a container or integration issue. Each Feature entry has its own
outcome, acceptance criteria, parent Feature issue, and closed Macro Task
registry.

| feature_id | repository_identity | parent_issue_ref | blocked_by Feature IDs | feature_status |
| --- | --- | --- | --- | --- |
| feature-a | <repository> | <assigned after publication> | <Feature ID or none> | <ready or blocked> |

`feature_id` is stable lower-kebab identity within the
`feature_plan_set_id`. Feature-level `blocked_by` may reference only another
Feature ID in this table and represents a hard outcome dependency, not
preferred order. se:implement projects a same-repository edge as mandatory
stack intent and a cross-repository edge as scheduling-only.

## Plan Set context

<Explain the shared source context and why the set contains separate Feature
outcomes rather than one Feature container.>

## Feature member plans

Repeat the following member sections for every `feature_id` in the registry.

### Feature `<feature_id>`

#### Problem and outcome

##### Problem statement

<Explain who or what experiences the user or product problem, the evidence
that establishes it, and any material uncertainty.>

##### Desired outcome

<Describe the observable outcome in user and system terms, including the usable
landing state and ownership boundary.>

##### Scope

- <in-scope outcome or surface>

##### Non-goals

- <explicitly excluded outcome>

#### Source analysis and convergence

##### Source issue map

| source issue | interpretation | feature_id | decision |
| --- | --- | --- | --- |
| <source> | <evidence-backed interpretation> | <member> | <consolidated, separated, or out-of-scope> |

##### Boundary decision

<Explain the residual-outcome test and why sources were consolidated or
separated.>

##### Repository context

###### Sources read

- <AGENTS.md, scoped context, code, documentation, or other required source>

###### Relevant facts

- <fact and source>

##### Acceptance criteria

- feature_acceptance_high_water: <monotonic high-water for this Feature>

- [F-AC-01] <observable success criterion>
- [F-AC-02] <observable success criterion>

These are contract identities, not execution checkboxes. Each F-AC belongs to
this Feature member and must be covered by its local Macro Task registry.

#### Macro Task Plan

This is the closed set for the current Feature member, not the entire Plan
Set. Macro Tasks are not optional scope, technical execution units, worker
assignments, or separate PR boundaries. Use vertical rows when the Feature
outcome admits clean slices; otherwise keep fewer coherent rows and explain
the boundary. Every entry is included in this Feature's final implementation
closing set, and sibling Feature issues are excluded.

- macro_task_registry_revision: 1
- parent_feature_id: `<feature_id>`
- macro_task_closure_policy: parent-feature-and-its-associated-macro-tasks

| parent_feature_id | macro_task_id | macro outcome | scope | F-AC refs | blocked_by | macro status | child issue ref |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<feature_id>` | macro-01 | <vertical slice when the outcome admits one; otherwise coherent macro outcome> | <macro boundary> | <F-AC-01> | <none or local macro ID> | <ready or blocked> | <assigned after publication> |

Each `(parent_feature_id, macro_task_id)` pair is stable. Macro `blocked_by`
may reference only another Macro Task with the same `parent_feature_id` and
expresses planning order, not a technical Implement gate. Cross-Feature
Task-to-Task edges are invalid. The local registry must cover every F-AC-NN
in this Feature and must not add scope outside it.

## Constraints and assumptions

### Confirmed constraints

- <constraint and evidence>

### Accepted assumptions

- <assumption, impact, and owner>

## Risks and validation intent

- risk: <risk>
  impact: <impact>
  mitigation_or_validation: <validation intent>

## Critic analysis

### Independent challenges

- <critic challenge>

### Reconciliation

- accepted: <challenge or alternative>
- rejected: <challenge and evidence>
- unresolved: <question reference>

## Questions and decisions

### Question batch

- Q-01
  question: <decision requested>
  why_it_matters: <impact>
  options:
    - <option>
  recommendation: <recommended option>
  question_status: resolved
  answer: <user answer or accepted assumption>

## Implementation handoff

<Explain what se:implement must achieve and what evidence it should preserve.
Project every same-repository Feature-level `blocked_by` edge as mandatory
stack intent and every cross-repository edge as scheduling-only. Derive the
technical execution units independently, and cover every local Macro Task in
this Feature's final evidence. Keep this implementation-neutral: do not
prescribe code design, technical execution-unit IDs, allowed paths, execution
waves, or worker scheduling.>

### Likely affected surfaces

- <surface or repository area, with evidence>

### Validation intent

- <behavioral, integration, or operational validation expectation>

## Plan operation

- run_mode: publish
- feature_plan_set_registry_readback:
- parent_feature_issue_refs:
- macro_task_issue_refs_by_feature:
- feature_dependency_readback:
- macro_task_registry_readback_by_feature:
- publication_evidence:
