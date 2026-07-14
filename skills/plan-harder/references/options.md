# Plan Harder Option Contract

Load this reference before selecting a Plan Harder route or returning a
structured caller result. It is the canonical registry for selectable planning
behavior and result classification.

## Syntax

- Option field names use snake_case.
- Enum values use lower-kebab-case. A one-word lowercase value already
  satisfies this rule.
- Natural-language requests are selection evidence only. Resolve them directly
  to the canonical field and value.
- Paths, issue refs, plan content, blocker text, and numeric task complexity are
  data, not option values.

## Registry

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `planning_mode` | `full-plan`, `issue-hardening` | Derived from the bounded input | `issue-hardening` applies to one issue or vertical slice; `full-plan` applies when phased or cross-cutting sequencing is necessary. |
| `output_surface` | `standalone`, `caller` | `standalone` | `caller` is valid only with `planning_mode=issue-hardening`. |
| `result_status` | `ready`, `blocked` | Derived from `blockers` | Caller results use `blocked` whenever `blockers` is non-empty; otherwise they use `ready`. |
| `estimated_complexity` | `low`, `medium`, `high` | Derived from the full plan | Applies only to `planning_mode=full-plan`; task-level numeric complexity remains data. |

## Cross-Field Validation

- `output_surface=caller` requires `planning_mode=issue-hardening`.
- `planning_mode=full-plan` requires `output_surface=standalone` and an
  `estimated_complexity` value.
- `result_status` is emitted only for `output_surface=caller`.
- `result_status=ready` requires `blockers=[]`.
- Any non-empty `blockers` list requires `result_status=blocked`.

## Input Validation

Structured callers must use the fields and values in this registry. Reject
unknown fields or values instead of translating them.
