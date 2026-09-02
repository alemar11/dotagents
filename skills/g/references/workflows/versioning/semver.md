# SemVer and tag format

The [SemVer 2.0.0 specification](https://semver.org/spec/v2.0.0.html) defines
the semantic version; G maps that version into a narrower Git tag and branch
convention. `v2.4.0` is a Git tag name whose semantic version is `2.4.0`.
The `v` prefix is not part of SemVer and does not affect precedence.

## Universal SemVer 2.0.0 rules

- SemVer communicates changes to a declared public API. That API may be
  expressed in code or documentation, but it must be clear enough to classify
  compatibility.
- A normal version is `X.Y.Z`, with non-negative decimal integers and no
  leading zeroes.
- Increment `Z` for backward-compatible fixes. Increment `Y` for
  backward-compatible public functionality or deprecation, and reset `Z` to
  zero. Increment `X` for backward-incompatible public API changes, and reset
  `Y` and `Z` to zero.
- `0.y.z` denotes initial development and does not promise a stable public
  API. `1.0.0` defines the public API used for subsequent compatibility
  decisions.
- Once a version has been released, its contents are immutable. Any change
  requires a new version.
- Prereleases are optional. A stable `X.Y.Z` does not require a preceding
  prerelease, and every prerelease of that same core has lower precedence than
  the stable version.
- Precedence compares `X`, `Y`, and `Z` numerically before prerelease
  identifiers. Numeric prerelease identifiers compare numerically, so
  `rc.2 < rc.10`. Build metadata is ignored for precedence.

For example:

```text
2.4.0-rc.1 < 2.4.0-rc.2 < 2.4.0
2.4.9 < 2.5.0-rc.1
```

SemVer does not define Git tag prefixes, branch naming, active release-line
limits, pull requests, approvals, or automation. Those are repository or
workflow policies and must not be presented as universal SemVer requirements.

## G canonical Git convention

The canonical G identifiers are:

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

`N` is a positive decimal integer without leading zeroes. The candidate
identifier is separated as `rc.N`, preserving SemVer's numeric comparison of
candidate counters.

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
