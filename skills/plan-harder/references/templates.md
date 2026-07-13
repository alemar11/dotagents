# Plan Harder Templates

Use these templates only after `$plan-harder` has selected the matching
`planning_mode` and `output_surface` from `references/options.md`. With
`output_surface=standalone`, keep the returned plan or issue-hardening brief in
chat. `output_surface=caller` applies only to
`planning_mode=issue-hardening` and returns its structured result to the
calling workflow. Never create `plans/` or write files from this skill.

## Full-Plan Template

Use this for `planning_mode=full-plan`.

```markdown
# Plan: [Task Name]

**Generated**: [Date]
`estimated_complexity: <low|medium|high>`

## Overview
[Summary of the work and the recommended approach]

## Prerequisites
- [Dependencies or requirements]
- [Tools, libraries, access, or docs needed]

## Sprint 1: [Name]
**Goal**: [What this phase accomplishes]
**Demo/Validation**:
- [How to demo or verify the phase]

### Task 1.1: [Name]
- **Location**: [File paths or areas]
- **Description**: [What to do]
- **Complexity**: [1-10]
- **Dependencies**: [Earlier tasks or `None`]
- **Acceptance Criteria**:
  - [Specific outcome]
- **Validation**:
  - [Tests or verification steps]

### Task 1.2: [Name]
[...]

## Sprint 2: [Name]
[...]

## Testing Strategy
- [How to validate the work]
- [What to verify per phase]

## Potential Risks & Gotchas
- [What could go wrong]
- [Mitigation]

## Rollback Plan
- [How to safely undo or disable the change]
```

## Issue-Hardening Template

Use this for `planning_mode=issue-hardening`.

```markdown
## Implementation Plan

### Goal
[The exact vertical slice this issue should deliver.]

### Non-Goals
- [What this issue should not attempt.]

### Resolved Interpretation
- [Assumptions or decisions this plan relies on.]

### Approach
- [Concrete implementation approach.]

### Likely Touch Points
- [Files, modules, routes, tests, or docs to inspect or modify.]

### Dependencies
- [Blocking issues, prerequisites, or `None`.]

### Acceptance Criteria
- [ ] [Specific, verifiable outcome.]

### Validation
- [Command, test, manual check, or log/metric to verify.]

### Risks & Rollback
- [Risk and mitigation.]

### Handoff
[One short instruction to the implementation agent about where to start and what not to broaden.]
```

## Caller-Surface Issue-Hardening Result

Use this exact field structure when another skill invokes
`planning_mode=issue-hardening` with `output_surface=caller`.
Return only this result; do not append standalone closeout text. Use `[]` for an
empty list and set `result_status: blocked` whenever `blockers` is non-empty.

```yaml
result_status: ready | blocked
goal: >-
  Exact vertical outcome.
non_goals:
  - Explicit scope exclusion.
resolved_interpretation:
  - Assumption or accepted decision.
implementation_plan:
  - Concrete implementation step.
likely_touch_points:
  - Repo-relative file, module, route, test, or documentation area.
dependencies:
  - Direct prerequisite or None.
acceptance_criteria:
  - Specific verifiable outcome.
validation:
  - Command, test, manual check, or runtime proof.
risks_and_rollback:
  - Risk, mitigation, or rollback action.
handoff: >-
  One bounded instruction to the implementation agent.
blockers: []
```
