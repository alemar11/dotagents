<!-- Learn-owned durable repository-context reference. -->

# Project Context Option Contract

Load this reference for structured handoffs or ambiguous branch selection;
ordinary requests use the entrypoint's routing table. It owns the complete
option registry. Request wording,
write authority, confirmation, repository facts, paths, evidence, decisions,
and result state are data, not selectable configuration.

## Syntax

- Option field names use `snake_case`.
- Enum values use lower-kebab assigned values.
- Resolve natural language to these canonical values at the skill boundary.
- Reject unknown fields or retired aliases in structured handoffs.

## Registry

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `memory_slice` | `domain-memory`, `durable-capture`, `translation-memory`, `agents-guidance`, `agents-pointers`, `agents-compaction`, `code-review-rules`, `full-setup` | Smallest slice implied by the request | Selects the owned context surface. |
| `domain_operation` | `not-applicable`, `setup-bootstrap`, `inline-update`, `implementation-closeout`, `periodic-review` | `not-applicable` | Required only for `memory_slice=domain-memory`. |
| `capture_mode` | `inline`, `defer-to-caller` | `inline` for an explicitly composed handoff | Applies only to composed durable context/capture workflows. |

There is no persisted Project Context configuration or generic run-mode field.
Write authority is derived from the current request or an explicit caller
handoff and is reported as result data.

The Project Context pointer/evolution check is a derived preflight fact when
the selected operation reads or changes that context. A standalone AGENTS.md
rule edit does not require it. The check creates no configuration or authority;
`agents-pointers` selects an explicit pointer-maintenance request.

`durable-capture` is proposal-first unless the user explicitly asks to
remember, save, or preserve a specific durable item and its repository scope
and destination are unambiguous. That direct request is write authority for the
scoped item and any required minimal Learn bootstrap; the selected slice remains
`durable-capture`.

## Derived Context

`execution_context` is factual output derived from the current Git repository
and selected surfaces:

1. `fresh-setup`: no established root context exists at the selected Git root,
   or a selected first-class subproject has no local context tree yet;
2. `existing-project-bootstrap`: a root or selected subproject context exists
   and the selected domain slice needs its first accepted population;
3. `current-project`: established context is being read or updated.

Do not let a caller select or override this classification.

## Durable Data And Results

- `knowledge_delta` is input data containing accepted durable terms, rules,
  boundaries, decisions, evidence, and named targets. It is not an option.
- `capture_outcome` is result data with `captured`, `deferred`, or
  `no-durable-change`. It is never an input option.
- `write_authority` is result data describing the explicit request, caller
  scope, or confirmation that authorized a write. It is not persisted.
- Destinations, before/after blocks, deferral reasons, evidence, and unresolved
  questions remain separate data fields.

## Cross-Field Validation

- `memory_slice=domain-memory` requires a `domain_operation` other than
  `not-applicable`; every other slice requires `domain_operation=not-applicable`.
- `capture_mode` may be emitted only for a composed `domain-memory` or
  `durable-capture` handoff.
- `code-review-rules` is selected only for an explicit Code Review Rules
  request; ordinary code review and general AGENTS maintenance do not select it.
- `agents-compaction` is selected only for an explicit chain-size review or
  compaction request. Crossing a threshold alone never selects it.
- `agents-guidance` covers general AGENTS.md creation, rule edits, review, and
  refactoring without requiring byte measurements or Project Context setup.
  A request to remember one specific rule remains `durable-capture` and uses
  the same AGENTS.md writing guidance for that destination.
- A direct `durable-capture` request cannot return `captured` without either an
  explicit save/remember/preserve instruction for an unambiguous scoped item or
  affirmative approval of the exact target and wording.
- `capture_outcome=captured` requires every accepted item and named target to be
  reconciled and verified. Any unresolved item or target returns `deferred`.
- `capture_mode=defer-to-caller` permits only `deferred` or
  `no-durable-change`.

## Repository Boundary

Ordinary targets remain inside the current Git root. A composed
cross-repository operation must supply candidate local roots and verify each
one against exactly one authorized repository identity. Never fabricate a path
from a hosted reference, use a common parent, or widen scope after a mismatch.
