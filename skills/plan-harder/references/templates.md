# Plan Harder Templates

Use these templates only after `$plan-harder` has selected the matching output
mode. Keep the returned plan or issue-hardening brief in chat; do not create
`plans/` or write Markdown files from this skill.

## Full-Plan Template

Use this for full-plan mode.

```markdown
# Plan: [Task Name]

**Generated**: [Date]
**Estimated Complexity**: [Low/Medium/High]

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

Use this for issue-hardening mode.

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
