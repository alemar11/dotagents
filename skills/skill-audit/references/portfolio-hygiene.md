# Portfolio Hygiene

Use this reference when an audit needs inventory-level evidence before
recommending skill merges, disables, description trims, or cleanup.

## Helper

Run the shipped helper from the `skill-audit` root:

```bash
scripts/portfolio-health --help
scripts/portfolio-health --version
scripts/portfolio-health --json doctor
scripts/portfolio-health scan --months 3
```

Useful variants:

```bash
scripts/portfolio-health scan --no-live --no-logs
scripts/portfolio-health scan --months 6 --deep-logs --max-log-mb 800
scripts/portfolio-health scan --context-tokens 272000 --budget-percent 2
scripts/portfolio-health --json scan --root ~/.codex/skills --root ~/.agents/skills
```

## How To Read The Report

- `budget`: prompt-inventory pressure. Treat this as a prioritization signal,
  not a deletion trigger by itself.
- `entrypoint_policy`: the estimator and diagnostic thresholds used for each
  activated `SKILL.md`. The estimator is `ceil(UTF-8 bytes / 4)` and is not a
  tokenizer-exact measurement.
- `entrypoint_candidates`: activated entrypoints outside the `normal` band.
  Interpret the bands as follows:

  | Band | Entrypoint signal |
  | --- | --- |
  | `normal` | At most 2,500 estimated tokens and fewer than 500 lines. |
  | `review` | 2,501-4,000 estimated tokens. |
  | `high-density` | 4,001-5,000 estimated tokens. |
  | `over-guideline` | More than 5,000 estimated tokens or at least 500 lines. |

  Size alone is diagnostic and never makes a skill fail health checks. Use
  `references/writing-style-review.md` to identify duplicated, stale,
  branch-specific, or misplaced content before recommending a change.
- `description_candidates`: long descriptions that may be worth tightening
  while preserving trigger nouns. Use `references/writing-style-review.md`
  when the audit needs to explain the description problem precisely.
- `duplicates`: same names, same bodies, or same descriptions across installed,
  repo-local, shared, or cached roots. Verify the editable owner before
  recommending changes; use `references/writing-style-review.md` to distinguish
  repeated trigger branches from useful shared vocabulary.
- `unused_candidates`: no recent heuristic evidence in scanned logs. Inspect at
  least one representative surface before claiming a skill is low-value.
- `root_summary`: where the inventory came from, useful for spotting cache
  copies, symlink farms, or unexpected roots.

## Audit Rules

- Keep audits read-only unless the user explicitly asks to apply changes.
- Prefer merging or improving an existing skill before adding a new surface.
- Treat plugin cache entries as verification evidence only.
- Do not delete, disable, or rewrite a skill solely because it has zero recent
  usage evidence.
- When usage evidence affects a recommendation, state whether it is
  session-confirmed, summary-only, or heuristic-only.
- Separate `catalog_cost` (always-visible inventory descriptions),
  `entrypoint_cost` (the activated `SKILL.md`), and `invoked_path_cost`
  (`SKILL.md` plus references required by one representative branch). Do not
  sum every file in a package or claim savings from moving text behind a
  pointer that every branch must still follow.

## CLI Maintenance

- Keep normal runtime execution on `scripts/portfolio-health`.
- The helper is local/offline and Python standard-library only.
- `scripts/portfolio-health --version` is the semver source of truth.
- Re-verify helper changes with:

```bash
scripts/portfolio-health --help
scripts/portfolio-health --version
scripts/portfolio-health --json doctor
scripts/portfolio-health scan --no-live --no-logs --root .
```
