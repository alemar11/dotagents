# Execution Manifest Contract

Load this reference before preparing a source bundle or executing delivery
preflight, worker validation, or AutoReview through a command manifest.
`scripts/execution-manifest` is the shipped standard-library Python artifact;
its schema version is `2.0.0` and its CLI version is `2.0.0`.

## Boundary

This first version owns only:

- immutable source-bundle fingerprints;
- delivery-preflight command manifests;
- literal-argv validation command manifests;
- AutoReview command manifests;
- pinned tool and dependency observations;
- Git-visible write-set checks and output checks;
- command receipts, verification, and byte-identical evidence reuse.

Claims, ledger commands, GitStack, CI, and Codex hosted-review commands retain
their current owners and direct command contracts. Do not describe them as
manifest-exclusive until adapters and replay coverage land.

Delivery preflight requires GitHub access, push and PR capability, reads of PR
lifecycle, mergeability/conflicts, and policy visibility. It discovers the
default base and classifies CI only as `configured` or `not-configured`.

## Canonical JSON And Bundle Hash

Canonical JSON sorts object keys, uses compact separators, escapes non-ASCII,
rejects NaN, and has no trailing newline in its hashed bytes. Emitted files add
one newline after those bytes. Manifest fingerprints omit only their own
`manifest_sha256`; receipt fingerprints omit only `receipt_sha256`.

`bundle prepare` reads raw snapshot bytes without text normalization. Sort
entries by `entry_id`. For each entry, derive exactly `entry_id`, `kind`,
`source_ref`, `byte_length`, and `content_sha256`. Hash this byte sequence:

```text
implement-feature-bundle\0
sha256-frame-v1\0
8-byte big-endian entry count
for each canonical entry:
  8-byte big-endian canonical-entry byte length
  canonical-entry bytes
```

The aggregate excludes temporary snapshot paths, while the enclosing manifest
fingerprint covers them. A worker can therefore reconstruct the aggregate from
the entry records without receiving source bodies in its prompt.

## Templates And Preparation

Use absolute regular input/output paths:

```bash
scripts/execution-manifest --json bundle template --output '<absolute-json>'
scripts/execution-manifest --json bundle prepare --input '<absolute-json>' --output '<absolute-manifest>'
scripts/execution-manifest --json command template --operation 'delivery-preflight|validation|autoreview' --output '<absolute-json>'
scripts/execution-manifest --json command prepare --bundle '<absolute-bundle-manifest>' --input '<absolute-json>' --output '<absolute-command-manifest>'
```

Templates are intentionally non-executable. Change `template` to `false` only
after replacing every placeholder. Unknown fields and shapes are rejected.

The template request is authoritative only for `root_task_ref` plus each
source's `entry_id`, `kind`, `source_ref`, and `snapshot_path`; preparation
generates byte lengths, per-source digests, the aggregate bundle digest, and
the enclosing manifest digest. A command request is authoritative for
`command_id`, supported `operation`, `owner`, typed parameters, dependency-file
paths, write set, and expected exits. The adapter derives the exact cwd where
required, resolves literal argv and tool records, copies `bundle_sha256`, and
generates argv, gate, and manifest fingerprints. Receipts contain observations
only; callers author none of their fields.

These are hard-cut `2.0.0` exact-object schemas. There are no aliases, command
string inputs, migrations, or legacy packet readers.

`validation.parameters.argv` is a nonempty literal string array. A string
command line is invalid. Shell operators, substitutions, redirections,
environment assignments, and shell wrappers are invalid; invoke the executable
directly. Delivery preflight derives the helper cwd and root ownership.
AutoReview requires a worker-owned absolute managed-checkout cwd and typed mode,
base, phase, evidence, finding, and output fields.

## Tools, Writes, And Receipts

Preparation resolves each helper, executable, and relevant dependency and
records source kind/ref, exact path, real path, size, SHA-256, and observed
version. Execution rechecks those values before launch. Missing tools return
`tool-missing`; changed bytes or versions return `tool-digest-mismatch`.

If a pinned path moves, use `command refresh-tools`. It emits a new immutable
manifest only when source, digest, and version are unchanged. It rejects an
unpinned download, different source, or changed tool as
`unpinned-substitution-rejected`.

The write policy is `none` or `declared`. Declared paths are canonical
repository-relative paths; expected paths must be inside the allowed set.
Before and after execution, the helper hashes Git tracked and nonignored
untracked files in the managed checkout. It rejects observed changes outside
the set and missing expected paths. This is a strict managed-Git-root boundary,
not an operating-system syscall sandbox; ignored build products remain the
validation tool's responsibility.

Run and verify with:

```bash
scripts/execution-manifest --json command run --manifest '<absolute-command-manifest>' --receipt '<absolute-receipt>'
scripts/execution-manifest --json receipt verify --manifest '<absolute-command-manifest>' --receipt '<absolute-receipt>'
```

The receipt binds manifest, command/gate fingerprints, exact cwd/argv,
exit code, tool observations, stdout/stderr files, outputs, and observed writes.
It is valid evidence only when verification succeeds.

## Evidence Reuse

`receipt reuse` requires a verified passed/reused receipt with the same
`gate_fingerprint`, plus unchanged dependencies and tool identities. The gate
fingerprint binds operation, owner, cwd, argv, expected exits, dependency
digests, tool source/digest/version, write policy, outputs, and bundle digest.

This allows prior structure evidence only when its declared inputs are
byte-identical. For example, a Python/tests-only delta may reuse a structure
gate bound only to unchanged `SKILL.md` and `agents/openai.yaml`; changing
either file makes the evidence stale.

## Recovery Errors

| code | recovery |
| --- | --- |
| `manifest-schema-invalid` | prepare the command again |
| `manifest-hash-mismatch` | prepare the command again |
| `bundle-hash-mismatch` | prepare the bundle again |
| `command-cwd-invalid` | restore the managed checkout |
| `command-argv-invalid` | provide literal argv without shell syntax |
| `tool-missing` | restore the pinned tool or refresh an identical relocation |
| `tool-digest-mismatch` | restore the pinned artifact |
| `unpinned-substitution-rejected` | prepare a new reviewed run |
| `manifest-stale` | prepare the command against current dependencies |
| `gate-evidence-stale` | run the command again |

## CLI Maintenance

Normal runtime execution uses `scripts/execution-manifest`; there is no
maintenance project or generated runtime. Keep its standard-library Python
implementation and tests under this skill, use the script's `__version__` as
the semver source, and reverify `--help`, `--version`, `--json doctor`, fixtures,
and focused tests after changes. Use a major bump for incompatible command or
JSON changes, minor for additive operations, and patch for compatible fixes.
