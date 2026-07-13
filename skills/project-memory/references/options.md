# Project Memory Option Contract

Load this reference before selecting a Project Memory branch or composing a
domain-memory handoff. It is the canonical registry shared by Project Memory,
Grill Me With Context, and planning callers.

## Syntax

- Option field names use snake_case.
- Enum values use lower-kebab-case. A one-word lowercase value already
  satisfies this rule.
- Natural-language requests, positional invocation words, and legacy labels
  are selection evidence only. Normalize them once and emit only canonical
  field/value assignments in current handoffs and reports.
- Paths, decisions, evidence, refs, reasons, and unresolved questions are data,
  not option values.

## Registry

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `memory_slice` | `tracker-routing`, `domain-memory`, `translation-memory`, `agents-pointers`, `full-setup` | Smallest slice implied by the request | Selects the owned memory surface. |
| `domain_operation` | `not-applicable`, `setup-bootstrap`, `inline-update`, `implementation-closeout`, `periodic-review` | `not-applicable` | A domain operation is required only for `memory_slice=domain-memory`. |
| `execution_context` | `current-project`, `fresh-setup`, `existing-project-bootstrap`, `orchestrator-workspace` | `current-project` | Describes the evidence and layout context; it does not grant writes. |
| `write_mode` | `apply`, `propose` | Derived from scoped authority | Inspect-only, review-only, dry-run, and proposal requests select `propose`. |
| `capture_mode` | `inline`, `defer-to-caller` | `inline` for direct Grill Me With Context invocation | Selects whether the composed grilling workflow may capture now or must return a delta. |
| `knowledge_delta` | `required`, `none` | Derived from accepted durable knowledge | Replaces the legacy nested `status` field. |
| `capture_outcome` | `captured`, `deferred`, `no-durable-change` | Derived at closeout | Explanations, destinations, and deferral reasons remain separate data. |

`capture_mode`, `knowledge_delta`, and `capture_outcome` apply only to
`memory_slice=domain-memory` and composed domain-memory handoffs. Other slices
omit these fields rather than inventing a `not-applicable` value.

## Cross-Field Validation

- `memory_slice=domain-memory` requires a `domain_operation` other than
  `not-applicable`; every other `memory_slice` requires
  `domain_operation=not-applicable`.
- A `memory_slice` other than `domain-memory` must not emit `capture_mode`,
  `knowledge_delta`, or `capture_outcome`.
- `write_mode=propose` cannot produce `capture_outcome=captured`.
- `knowledge_delta=none` requires
  `capture_outcome=no-durable-change` and empty decision, target, and evidence
  lists.
- `capture_outcome=captured` requires `knowledge_delta=required` and
  `write_mode=apply`.
- `capture_outcome=deferred` requires `knowledge_delta=required` and a separate
  target or reason explaining the deferral.
- `capture_mode=defer-to-caller` permits only `capture_outcome=deferred` or
  `capture_outcome=no-durable-change`.

## Legacy Input Normalization

Accept legacy `slice` and `operation` fields as input evidence and normalize
them to `memory_slice` and `domain_operation`. Accept
`domain_knowledge_delta.status=required|none` as legacy input and normalize it
to `domain_knowledge_delta.knowledge_delta`. Do not emit those legacy field
names in current structured results.
