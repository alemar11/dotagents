# Orchestration Cache Lifecycle

## Ownership And Timing

The root owns cache maintenance. Never create a visible task, internal subagent,
Goal, or worktree for it. Load this reference after a successful CLAIM and
before REGISTER, and again before terminal claim release and ledger archival.

The authorization disclosure names automatic deletion of valid archived
ledgers older than 180 days. Unsupported, denied, and `planning-required` runs
perform no cache maintenance because they stop before CLAIM.

Run once per controller entry after an acquired, already-owned, or recovered
takeover claim:

```text
scripts/orchestrator-cache --json doctor
scripts/orchestrator-cache --json archive prune --older-than-days 180 --apply
```

Do not rerun maintenance for every scheduling wave. A doctor or prune warning is
nonblocking: continue the claimed implementation and report the warning in the
final status. Active claim or ledger failures remain governed by their existing
blocking contracts.

## Active And Archived State

Keep resumable ledgers directly under
`~/.cache/dotagents/skills/implement-feature/ledgers/`. Archived ledgers are cold
cache evidence only and live below `ledgers/archive/`; never load, restore, or
migrate them as active recovery state.

Archive only after terminal reconciliation and exact claim release. Release the
claim with `claim release --release-reason terminal`; its durable receipt binds
the root, claim fingerprint, ledger path, checksum, byte count, and terminal
evidence. Pass that same evidence ref to the archive command. The helper
requires and then consumes the matching receipt.

Monitoring handoffs, dependency waits, blockers, active tasks, due checks, and
other resumable states use `claim release --release-reason durable-handoff` and
keep their active ledger. A durable-handoff receipt never authorizes archival.
If failure occurs after CLAIM but before REGISTER creates the ledger, this
release reason may persist a receipt with null checksum and byte count so claim
ownership is never stranded.
The receipt remains only for idempotent release proof; the next successful
same-root acquire removes obsolete durable-handoff receipts.
Run terminal archival with:

```text
scripts/orchestrator-cache --json ledger archive \
  --ledger <absolute-active-ledger> \
  --archive-reason terminal \
  --root-id <released-root-id> \
  --evidence-ref <terminal-evidence-ref>
```

If terminal archival fails, preserve the active ledger and report cache
maintenance as incomplete without changing the already-proven implementation
result.

## Archive Contract

The helper keeps `ledger.md` byte-identical and writes `metadata.json` beside it:

```text
ledgers/archive/YYYY/MM/<timestamp>--<portfolio>--<sha12>/
  ledger.md
  metadata.json
```

Legacy cutover entries use
`ledgers/archive/legacy-cutover-2026-07-17/<portfolio-and-hash>/`.
Metadata schema `1.0.0` owns these fields:

| field | contract |
| --- | --- |
| `archive_id` | Canonical entry-directory identity. |
| `archive_reason` | `terminal` or `legacy-cutover`. |
| `archive_group` | Cutover group or `null`. |
| `archived_at` | UTC retention timestamp. |
| `portfolio_key` | Original active-ledger stem. |
| `original_ledger_ref` | Absolute direct child of the active ledger root. |
| `ledger_sha256` | SHA-256 of byte-identical `ledger.md`. |
| `size_bytes` | Ledger byte count. |
| `evidence_ref` | Terminal or cutover authorization evidence. |
| `root_id` | Released terminal owner or `null` for cutover. |
| `tool_version` | `orchestrator-cache` command-contract version. |

The helper serializes mutations through the existing claim-store lock, requires
the exact terminal release receipt, refuses active claim or takeover references,
rejects unsafe paths and symlinks, stages the complete batch before unlinking
active ledgers, and never changes claim JSON or takeover journals.

## Automatic Retention

Use a strict 180-day TTL for every valid archive category, including legacy
cutover entries. Eligibility begins exactly at `archived_at + 180 days`; file
mtime is irrelevant and there is no last-N exception.

Direct operator pruning is dry-run by default. Only `--apply` deletes. Each
entry is revalidated under the shared lock, moved into internal trash, and
deleted through its two known files without recursive unresolved-path removal.
Malformed metadata, checksum mismatches, symlinks, unexpected files,
interrupted entries, and claim-referenced entries are protected and reported;
they do not prevent unrelated valid entries from expiring.

`doctor`, `archive list`, and `archive verify` are read-only and create no cache
directories. Doctor reports integrity, size, count, oldest archive, next expiry,
interrupted operations, and informational warnings at 25 MiB or 100 archives.

## Helper Maintenance

`scripts/orchestrator-cache` is the shipped local/offline artifact and keeps one
`__version__` semver source of truth. It has no config, auth, network, raw escape
hatch, or maintenance project. After changes, run `--help`, `--version`,
`--json doctor`, focused cache-helper tests, a dry-run fixture, and the complete
Implement Feature contract suite. Use major versions for breaking command,
JSON, or metadata contracts.
