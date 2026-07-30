# Plan Feature Option Contract

Load this reference before the first Plan Feature phase. It is the sole owner
of selectable Plan Feature behavior.

## Syntax And Hard Cut

- Field names use snake_case and enum values use lower-kebab-case.
- User wording is selection evidence, never an alternative value.
- Reject every selectable field or value not listed below.
- Reject retired fields, values, aliases, and partial-flow requests instead of
  translating them. Plan Feature has one convergent planning pipeline.
- Keep tracker facts, paths, slugs, refs, branches, dependencies, source route,
  evidence, continuation data, `scope_repair_request`, and result state outside
  the option registry.

## Run Registry

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `write_mode` | `apply`, `propose` | `apply` for an explicit request to create durable planning artifacts | `apply` writes through the configured tracker; `propose` performs no writes. |

## Resolution

Resolve `write_mode` once before phase work:

- A request that forbids writes, asks for a dry run, or asks to inspect the
  result before publication resolves to `write_mode=propose`.
- An explicit Plan Feature request to create durable planning artifacts
  defaults to `write_mode=apply`. Project Memory resolves its own write
  authority independently.
- `write_mode=propose` returns the complete proposed Feature Spec bundle:
  bodies, target locations, mapped metadata, relationships, and publication
  order. It writes nothing and returns no executable publication commands.
- Both modes withhold incomplete Feature Specs and implementation issues.
  Temporary hosted publication-transaction staging issues are non-executable
  transport, not successful output.

All remaining inputs and observations are facts or execution data owned by
`SKILL.md` and the phase reference that consumes them. Do not add them to this
registry merely to make them easier to pass between phases.
