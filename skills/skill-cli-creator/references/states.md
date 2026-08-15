# Skill CLI Creator State Contract

This reference owns the derived host mode used while designing an embedded
CLI. It is transient planning state and is not written into runtime config.
The owner tree, shipped artifact, and optional maintenance project remain
persistent filesystem state.

## Host mode

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `host_mode` | `skill`, `plugin` | Derived from the existing owner | `skill` places the artifact under one skill owner; `plugin` places it under a bundled-skill or plugin-shared owner. |

Reject any other value. Do not infer `host_mode` from the CLI display name;
derive it from the existing package boundary and keep owner-root selection as
a separate execution fact.
