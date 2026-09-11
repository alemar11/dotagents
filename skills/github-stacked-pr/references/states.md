# GitHub Stacked PR States

Namespace: `github-stacked-pr.extension_status`. These values are derived from
`scripts/stack --json ensure` / `extension_status` observations. They are not
persisted workflow checkpoints.

| Status | Meaning | Persisted? |
| --- | --- | --- |
| `ready` | Official `github/gh-stack` is installed with a usable version and reported publisher verification fields. Stack commands may proceed. | Transient observation |
| `missing` | `gh` is present but the official extension is not installed. Install only with explicit `--install` authorization. | Transient observation |
| `gh-missing` | The `gh` CLI is not available; extension checks did not run. | Transient observation |
| `conflict` | A different repository provides `gh stack`. Do not replace or override it silently. | Transient observation |
| `unverified` | Listing or identity checks failed closed (unparseable output, missing/invalid repository or version, or command failure). Treat stack state as unavailable. | Transient observation |

## Transitions

Re-run `ensure` / `extension_status` to observe a new status. Do not carry a
previous `ready` result across installs, upgrades, or repository changes.
`ensure --install` is authorized only when status is `missing` and the user
explicitly approved installation; other non-`ready` statuses remain blockers.

Doctor and authentication readiness (`provider_ready`, `gh` authentication
status) are separate health observations owned by `scripts/stack` doctor
output; they do not redefine these extension statuses.
