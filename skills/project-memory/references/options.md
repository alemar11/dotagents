# Project Memory Option Contract

Load this reference before selecting a Project Memory branch or composing a
domain-memory handoff. It owns the complete option registry shared by Project
Memory and its composed callers.

## Syntax

- Option field names use snake_case.
- Enum values use lower-kebab-case. A one-word lowercase value already
  satisfies this rule.
- Natural-language requests and positional invocation words are selection
  evidence only. Resolve them directly to canonical field/value assignments.
- Paths, evidence, decisions, refs, reasons, and unresolved questions are data,
  not option values.

## Registry

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `memory_slice` | `tracker-routing`, `project-layout`, `domain-memory`, `translation-memory`, `agents-pointers`, `full-setup` | Smallest slice implied by the request | Selects the owned memory surface. |
| `domain_operation` | `not-applicable`, `setup-bootstrap`, `inline-update`, `implementation-closeout`, `periodic-review` | `not-applicable` | A domain operation is required only for `memory_slice=domain-memory`. |
| `write_mode` | `apply`, `propose` | Derived from scoped authority | Inspect-only, review-only, dry-run, and proposal requests select `propose`. |
| `capture_mode` | `inline`, `defer-to-caller` | `inline` for direct Grill Me With Context invocation | Selects whether a composed domain workflow may capture now or must return its data to the caller. |

`capture_mode` applies only to `memory_slice=domain-memory` and composed
domain-memory handoffs. Other slices omit it.

## Derived Context

`execution_context` is a factual classification derived from the current
workspace and selected memory surfaces, not an input option. Evaluate these
mutually exclusive rules in order:

1. `orchestrator-workspace`: `repository_layout=multi-repository-workspace` and
   the current root coordinates child repositories that retain their own
   project memory and code ownership. This wins even when root memory files are
   missing.
2. `fresh-setup`: the first rule is false and no established Project Memory
   surface exists yet at this project root. Existing source code alone does not
   turn a first Project Memory setup into bootstrap.
3. `existing-project-bootstrap`: the first two rules are false, Project Memory
   identity/routing already exists, and the selected domain-memory surface
   needs its initial accepted population from repository or same-repo session
   evidence.
4. `current-project`: none of the earlier rules applies; established Project
   Memory is being read or updated without bootstrap semantics.

Report the derived classification and its evidence. A structured caller may
provide workspace facts, but it must not select or override this result.

## Domain Data And Results

- `knowledge_delta` is optional input data containing accepted durable terms,
  rules, boundaries, or decisions plus their evidence and intended targets. It
  is not an enum and is not part of the option registry.
- `capture_outcome` is a closeout result with value `captured`, `deferred`, or
  `no-durable-change`. Destinations and deferral reasons remain separate result
  data. It is never accepted as an input option.

## Cross-Field Validation

- `memory_slice=domain-memory` requires a `domain_operation` other than
  `not-applicable`; every other `memory_slice` requires
  `domain_operation=not-applicable`.
- A `memory_slice` other than `domain-memory` must not emit `capture_mode` or
  domain capture results.
- `write_mode=propose` cannot produce `capture_outcome=captured`.
- An empty or absent durable `knowledge_delta` produces
  `capture_outcome=no-durable-change` unless inspection discovers another
  accepted durable change.
- `capture_outcome=captured` requires accepted durable knowledge,
  `write_mode=apply`, every accepted delta item reconciled, every required named
  target updated or verified already current, and documentation-diff
  verification across all destinations. One successful destination never
  masks an unresolved item or target. Every supplied accepted item must remain
  supported by landed behavior and be durably represented; a rejected or
  contradicted item cannot count as reconciled.
- `capture_outcome=deferred` requires accepted durable knowledge and names every
  unresolved item or target with its intended destination and reason.
- For `domain_operation=implementation-closeout` with a nonempty accepted
  `knowledge_delta`, `capture_outcome=no-durable-change` is invalid. Return
  `captured` only after complete supported reconciliation. A rejected or
  landed-behavior-contradicted accepted item returns `deferred` and requires an
  owner decision or separately authorized planning/implementation correction.
- `capture_mode=defer-to-caller` permits only `capture_outcome=deferred` or
  `capture_outcome=no-durable-change`.

## Input Validation

Structured option objects must use only the four registry fields and their
canonical values. Reject unknown option fields or values instead of translating
them. Keep workspace facts and `knowledge_delta` in separate input data, and
emit `execution_context` and `capture_outcome` only as derived output.
