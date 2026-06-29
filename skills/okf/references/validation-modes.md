# OKF Validation Modes

The official OKF v0.1 conformance rules are intentionally permissive, while the
official reference agent is stricter. Keep these modes separate.

## `spec`

Use this mode to validate OKF v0.1 conformance.

Hard errors:
- non-reserved `.md` file has no parseable YAML frontmatter
- concept frontmatter is not a mapping
- concept frontmatter has no non-empty `type`
- `index.md` or `log.md` violates the reserved-file rules implemented by the
  checker

Warnings:
- missing recommended frontmatter fields
- unknown `type` values
- unknown producer-defined fields
- broken cross-links, unless `--strict-links` is used

## `reference-agent`

Use this mode when a bundle needs to work with the official OKF reference agent.

Hard errors include all `spec` errors plus missing:
- `title`
- `description`
- `timestamp`

This stricter mode reflects the reference implementation, not the minimum OKF
v0.1 spec.

## Parser Note

The shipped CLI uses `PyYAML` when it is installed. Without `PyYAML`, it falls
back to a limited parser for common scalar and flow-list frontmatter. Treat
parser-limit warnings as a sign to install `PyYAML` or verify the file with
another YAML-aware tool before publishing.
