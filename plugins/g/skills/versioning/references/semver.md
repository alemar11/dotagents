# SemVer and tag format

The canonical public release identifiers are:

| Kind | Format | Example |
| --- | --- | --- |
| Stable release | `vX.Y.Z` | `v2.4.0` |
| Release candidate | `vX.Y.Z-rc.N` | `v2.4.0-rc.2` |
| Stabilization branch | `release/vX.Y.Z` | `release/v2.4.0` |

For tag application, the accepted language is deliberately narrower than full
SemVer and matches exactly:

```text
^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-rc\.([1-9][0-9]*))?$
```

Anything outside that language is a hard mutation block. Explain the problem,
but never create or push the requested tag. User confirmation cannot override
the format gate, and a suggested canonical replacement requires its own new
preview and confirmation.

When a repository has no SemVer tags, use `v0.1.0-rc.1` only as the safe
bootstrap proposal. If the user supplies an initial version, use that
`X.Y.Z` as the base instead. The proposal must still be shown and explicitly
confirmed before any tag is created or pushed.

`X`, `Y`, and `Z` are non-negative decimal integers without leading zeroes.
`N` is a positive decimal integer without leading zeroes. The candidate
identifier is separated as `rc.N`, so SemVer compares `rc.2` before `rc.10`
numerically.

Avoid these forms:

- `1.0.0`: new tags require the `v` prefix; this form is legacy input only;
- `v1.0.0-beta` or `v1.0.0-alpha.1`: full SemVer permits other prerelease
  identifiers, but this shared convention permits only `rc.N`;
- `v2.4.0-rc01`: the counter is embedded in an alphanumeric identifier and
  does not provide a numeric SemVer field;
- `v2.4.0-rc.01`: the numeric identifier has a forbidden leading zero;
- `v2.4.0-RC.1`: the convention is case-sensitive and uses lowercase `rc`;
- `v2.4.0+build.248`: build metadata is not part of the canonical tag format.

Build metadata such as `+build.248` may be recorded in CI or an artifact
manifest, but it does not participate in SemVer precedence. Keep it out of the
canonical Git tag unless a consuming external system explicitly requires it.

Legacy tags without `v` are accepted only as read-only input for version
calculation. A requested migration adds the missing canonical `vX.Y.Z` alias
at the same commit and leaves the legacy tag untouched; it must stop on any
target conflict and requires explicit confirmation immediately before the
mutation.
