# Feature Flow Options

The `idea` and `plan` bundled skills expose the same run-scoped option
registry. The `implement` skill has its own startup-authorization contract.

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `run_mode` | `preview`, `publish` | `publish` for an explicit request to create durable artifacts | `preview` calculates and reports; `publish` performs authorized writes and verification. |

Resolve `run_mode` once before workflow work:

- Requests that forbid writes, ask for a dry run, or ask to inspect the result
  before publication resolve to `preview`.
- Explicit requests to save an Idea or create durable planning artifacts
  default to `publish`.
- `preview` never requests dry-run mutations, returns executable commands, or
  performs a write.
- `publish` never silently downgrades after a blocker; report the blocker and
  preserve the resolved mode.

Reject unregistered fields, noncanonical values, retired fields, and aliases.
