# Run-State Cache Lifecycle

## Ownership And Timing

The root owns cache maintenance. Never create a visible task, internal subagent,
Goal, or worktree for it. Load this reference after successful CLAIM and before
REGISTER, then again before terminal claim release and archival.

The authorization disclosure names automatic deletion of valid archives older
than 180 days. Unsupported, denied, and `planning-required` runs stop before
CLAIM and perform no cache maintenance.

Run once per controller entry after an acquired, already-owned, or recovered
takeover claim:

```text
scripts/ledger-cache --json doctor
scripts/ledger-cache --json archive prune --older-than-days 180 --apply
```

Do not repeat maintenance for each scheduling wave. A doctor or prune warning
is nonblocking and belongs in final status. Active claim or run-state failures
remain blocking.

## Active And Archived State

Keep resumable ledger-schema `12.0.0` state as absolute direct-child `.json` files under
`~/.cache/dotagents/skills/implement-feature/ledgers/`. `ledger-cache` v15 is the
sole active-state writer. Archived entries live below `ledgers/archive/` as cold
evidence; never restore, load, or migrate them into active state.

Quote placeholders. `<claim-fingerprint>` is the raw 64-hex acquire fingerprint,
never a `sha256:` value or receipt fingerprint.
Release receipt schema `2.0.0` permits only `terminal` and
`preimplementation-abort`; every receipt binds its exact reason, evidence,
stable ledger hash, size, owner, and claim fingerprint.

For an in-flight review wait, retain active JSON, the complete typed request
receipt, and the exact claim/fingerprint.
Keep the root Goal active and do not release ownership. If the exact
request remains pending at its 45-minute deadline, record the persistent PR
warning and continue under `timeout-accepted`; do not schedule another check or
create a nonterminal handoff. A root replaced by authorized takeover stops.
Dependency-only waits also retain claim and state, return the exact
external action, and require explicit same-root resume; do not fabricate a
schedule, handoff, or receipt. A pre-REGISTER claim may keep a null state ref
until that retained claim binds registration.

After the terminal projection passes each staged readiness check, every task is
sealed and its terminal handoff is
recorded, `portfolio-terminal-verified` passes, the root Goal completion is read
back and recorded, and current evidence remains unchanged, run exactly:

```text
scripts/active-root-claim --json claim release --root-id '<root-id>' --expected-fingerprint '<claim-fingerprint>' --release-reason terminal --evidence '<terminal-evidence-ref>'
scripts/ledger-cache --json ledger archive --ledger '<absolute-active-json>' --root-id '<same-root-id>' --evidence-ref '<same-terminal-evidence-ref>'
```

Under lock, release requires claim schema `6.0.0`, exact ownership, and an
archive-ready terminal projection before receipt or claim deletion. Rejection
leaves claim and ledger unchanged.

`ledger_sha256` and `ledger_size_bytes` bind validated JSON bytes, root,
fingerprint, path, and the ledger's exact terminal evidence, not Markdown.
Archive consumes the receipt; interruption remains recoverable.

If baseline preparation/acceptance cannot continue, first apply the verified
`portfolio-preimplementation-aborted` event from `baseline-validation.md`, then
run the same two commands with `--release-reason preimplementation-abort` and
`ledger archive --reason preimplementation-abort`, using the exact abort
evidence ref. This path never creates, completes, or synthesizes a Goal.

## Archive V2 Contract

New terminal archives use metadata schema `2.0.0`:

```text
ledgers/archive/YYYY/MM/<timestamp>--<portfolio>--<sha12>/
  ledger.json
  ledger.md
  metadata.json
```

`ledger.json` is byte-identical canonical terminal state. `ledger.md` is a
deterministic audit projection rendered from that state during archival; it is
never active input. Repeating archive with the same receipt and bytes is
idempotent and resolves to the same entry.

| field | contract |
| --- | --- |
| `archive_id` | Canonical entry-directory identity. |
| `archive_reason` | `terminal` or `preimplementation-abort`. |
| `archive_group` | `null` for v2 terminal archives. |
| `archived_at` | UTC retention timestamp. |
| `portfolio_key` | Original active-state stem. |
| `original_ledger_ref` | Absolute direct child of the active state root. |
| `state_sha256` | SHA-256 of byte-identical `ledger.json`. |
| `state_size_bytes` | Canonical JSON byte count. |
| `markdown_sha256` | SHA-256 of deterministic `ledger.md`. |
| `markdown_size_bytes` | Markdown byte count. |
| `evidence_ref` | Exact terminal release evidence. |
| `root_id` | Released terminal owner. |
| `tool_version` | `ledger-cache` command-contract version. |

The helper rejects any post-terminal drift and validates staged terminal
eligibility, strict state schema, receipt checksum,
and deterministic projection before publishing the archive. It serializes
mutations under the claim-store lock, refuses active claim or takeover
references, rejects unsafe paths and symlinks, stages both artifacts before
unlinking active state, and never changes claim JSON or takeover journals.

## Frozen Archive V1 Compatibility

Existing metadata-schema `1.0.0` archives remain readable, verifiable, and
prunable byte-for-byte. Their frozen layout is:

```text
ledgers/archive/YYYY/MM/<existing-entry>/
  ledger.md
  metadata.json
```

The nine retained legacy cutover entries remain under
`ledgers/archive/legacy-cutover-2026-07-17/<portfolio-and-hash>/`. Preserve their
existing `ledger_sha256`, `size_bytes`, identity, evidence, and tool-version
metadata exactly. The helper may list, verify, and prune these entries but cannot
rewrite them, make them active, or create more v1 or legacy-cutover entries.
This cold-read contract is historical evidence preservation, not active-state
compatibility or migration.

## Automatic Retention

Use a strict 180-day TTL for every valid archive version and category, including
legacy cutover entries. Eligibility begins at `archived_at + 180 days`; file
mtime is irrelevant and there is no last-N exception.

Direct operator pruning is dry-run by default. Only `--apply` deletes. Each
entry is revalidated under the shared lock, moved into internal trash, and
deleted only through the exact file set allowed by its metadata version.
Malformed metadata, checksum mismatches, symlinks, unexpected files,
interrupted entries, and claim-referenced entries are protected and reported;
they do not prevent unrelated valid entries from expiring.

`doctor`, `archive list`, and `archive verify` are read-only and create no cache
directories. Doctor reports unsupported active Markdown, active-state integrity,
archive integrity, size, count, oldest entry, next expiry, interrupted
operations, and informational warnings at 25 MiB or 100 archives.

## Helper Maintenance

`scripts/ledger-cache` is the shipped local/offline artifact with one
`__version__` semver source of truth. It has no config, auth, network, raw escape
hatch, or maintenance project. After changes, run `--help`, `--version`,
`--json doctor`, focused helper tests, a dry-run fixture, and the complete
Implement Feature contract suite. Breaking command, JSON, active-state, or
metadata changes require a major version.
