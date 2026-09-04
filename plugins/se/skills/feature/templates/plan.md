# Feature Plan

## Plan identity

- feature_plan_set_id: <stable lower-kebab identity>
- feature_plan_set_revision: <monotonic revision>
- source_route: <new-source or existing-source>
- run_mode: <publish or preview>
- plan_status: <draft, awaiting-input, ready, preview, published, or blocked>
- source_refs: <attributable sources>
- feature_member_count: <count>
- closure_policy: each-feature-and-its-associated-macro-tasks

## Feature Plan Set registry

The set contains genuinely independent Features and no container issue.

| feature_id | repository_identity | parent_issue_ref | blocked_by | feature_status |
| --- | --- | --- | --- | --- |
| feature-a | <repository> | <hosted identity or proposed preview ref> | <Feature IDs or none> | <ready or blocked> |

Feature `blocked_by` references only another Feature in this registry and
expresses a hard outcome dependency. A same-repository edge is stack intent for
Implement; a cross-repository edge is scheduling-only.

## Source and boundary decisions

| source | provenance | interpretation | feature_id | source_disposition |
| --- | --- | --- | --- | --- |
| <source> | <directive, proposal, evidence, context, prior-contract, or reference> | <evidence-backed interpretation> | <member> | <consolidated, separated, revised, or out-of-scope> |

<Explain why each residual outcome is one Feature or a distinct sibling.>

## Feature member plans

Repeat this section for every registry member.

### Feature `<feature_id>`

- repository_identity: <repository>
- feature_acceptance_high_water: <monotonic high-water>
- parent_issue_ref: <hosted identity or proposed preview ref>

#### Problem and outcome

<State the affected user, actor, or system, evidence-backed problem, observable
outcome, usable landing state, and ownership boundary.>

#### Scope

- <in-scope outcome or surface>

#### Non-goals

- <explicitly excluded outcome>

#### Repository context

- source: <AGENTS.md, code, documentation, or hosted source>
  fact: <relevant planning evidence>

#### Feature acceptance criteria

- [F-AC-01] <unique observable success criterion>
  falsifier: <observation that would prove the criterion false>
- [F-AC-02] <unique observable success criterion>
  falsifier: <observation that would prove the criterion false>

F-AC identities are durable contract identifiers, not execution checkboxes.
Every new-behavior criterion must be falsifiable and false before the Feature's
work. Record preservation of an existing invariant separately as a preservation
obligation; it never substitutes for evidence of the new Feature delta.

#### Macro Task registry

- parent_feature_id: `<feature_id>`
- macro_task_registry_revision: <monotonic revision>

| parent_feature_id | macro_task_id | macro outcome | observable_verification | scope | F-AC refs | blocked_by | macro_status | child_issue_ref |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<feature_id>` | macro-01 | <coherent outcome or vertical slice> | <observable path or integrated-verification rationale> | <boundary> | <F-AC-01> | <same-parent Macro IDs or none> | <ready or blocked> | <hosted identity or proposed preview ref> |

The registry is closed, covers every F-AC, adds no scope, and contains only
same-parent Macro dependencies. Macro edges are planning context, not technical
execution or PR boundaries.

#### Constraints, assumptions, and risks

- constraint: <constraint and evidence>
- assumption: <safe assumption and impact>
- risk: <risk and validation or mitigation intent>

#### Validation intent

- evidence: <observable behavioral, integration, or operational evidence>
  validation_seam: <highest practical existing or proposed seam, or defer-to-implementation>
  seam_rationale: <why the seam is sufficient and why it is existing, new, or deferred>

## Questions and decisions

List only real questions. When none were needed, state why the brief, delegated
choice, or safe assumptions were sufficient.

- question: <material decision>
  status: <open, resolved, or assumption>
  provenance: <user-decision, delegated-choice, source-issue, codebase-evidence, idea-source, existing-plan, or assumption>
  recommendation: <recommended answer>
  answer: <answer or assumption>
  evidence: <source>

## Review

- review_result: <clean, revision-required, clarification-required, or blocked>
- review_method: <independent-helper or serial-lens>
- material_findings: <findings and dispositions or none>
- structural_checks: <identity, falsifiable F-AC coverage, Macro verification, registries, DAGs, boundaries, provenance, validation seams, projections, maintenance preservation>

## Implementation handoff

<Describe the outcomes and evidence Implement must preserve.
Include same-repo stack and cross-repo scheduling intent, but do not prescribe
code design, technical execution-unit IDs, allowed paths, waves, workers, or
branches.>

## Operation evidence

- semantic_authority: body-and-registries
- parent_feature_issue_refs: <hosted identities or preview refs>
- macro_task_issue_refs_by_feature: <mapping>
- final_parent_body_reconciliation: <verified, no-op, ambiguous, or preview>
- parent_child_readback: <verified, no-op, failed, unavailable, unknown, or not-applicable>
- feature_dependency_results: <one result per edge or none>
- macro_dependency_results: <one result per edge or none>
- removed_dependency_results: <one result per explicitly removed prior SE-owned edge or none>
- semantic_body_readback: <verified, no-op, ambiguous, or preview>
- optional_classification_results: <results or not-requested>
- downstream_handoff_status: <not-requested, verified, no-op, failed, unavailable, or ambiguous>
- publication_warnings: <warnings or none>
