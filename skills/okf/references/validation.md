# OKF Validation

The shipped CLI validates the permissive OKF v0.2 conformance contract. It has
one validation model; there is no producer-specific compatibility mode.

Run:

```sh
<okf-skill-root>/scripts/okf validate <bundle>
<okf-skill-root>/scripts/okf --json validate <bundle>
```

## Conformance

Hard errors:

- non-reserved `.md` file has no parseable YAML frontmatter
- concept frontmatter is not a mapping
- concept frontmatter has no non-empty `type`
- `index.md` or `log.md` violates the reserved-file rules implemented by the
  checker
- the selected bundle root is a symlink, a markdown path contains a symlink, a
  directory symlink could hide concepts, or a file cannot be safely anchored
  inside the bundle while it is read

Warnings:

- missing recommended frontmatter fields
- broken cross-links, unless `--strict-links` is used

The CLI does not reject missing optional provenance, trust, lifecycle, or
computation families. It also preserves the spec rule that unknown types and
additional keys remain consumable.

## Parser Note

The shipped CLI uses `PyYAML` when it is installed. Without `PyYAML`, it accepts
flat scalars, scalar block lists, and JSON-compatible flow frontmatter. It
fails closed on unsupported nesting or ambiguous flow mappings rather than
certifying content it did not parse. Install `PyYAML` or use another YAML-aware
tool when block-form nested mappings are required.

## Machine-Readable Output

Put global `--json` before the command:

```sh
<okf-skill-root>/scripts/okf --json doctor
<okf-skill-root>/scripts/okf --json validate <bundle>
<okf-skill-root>/scripts/okf --json scaffold <bundle> <concept-id> --type Reference
```

With `--json`, success and error envelopes go to stdout. Human diagnostics use
stderr.

`doctor` reports the `anchored_io` platform capability. It returns exit code 69
and `ok: false` when the operating system cannot provide the directory-relative
file access required for safe validation and scaffolding.

Scaffolding creates and opens bundle-relative paths through anchored directory
descriptors. It refuses symlinked path components and does not follow a path
that changes to a symlink while the command runs.

The retired `--mode` and `--timestamp` options are not accepted.
