# Installed GitStack Parity

Run `scripts/gitstack-installation-parity --json verify --loaded-skill-path
<absolute-system-catalog-path>` immediately after the App surface gate and before
any intake, preflight, authorization, claim, cache, ledger, task, Goal, or
provider action. The path is an App/system-catalog fact for the loaded
`$gitstack:github-review-threads` skill; it is never a user option, repository
path, environment override, or guessed cache path.

The verifier accepts only the canonical installed 6.0.0 GitStack root, its
expected bundled `SKILL.md`, exact manifest/package/CLI version, and pinned
shipped CLI hash. It reads only those installed files and runs CLI `--version`.
It emits `gitstack-installation-parity:v1` evidence with a canonical fingerprint.
No external or provider operation occurs.

Missing trustworthy App provenance is `unsupported-runtime`. Any missing,
symlinked, escaped, substituted, malformed, wrong-version, or hash-mismatched
artifact is `gitstack-installation-mismatch`. Both stop with zero side effects.
Carry the complete evidence plus fingerprint into registration; it is immutable
recovery evidence, not caller authority. Never accept GitStack 8 or a version
range.
