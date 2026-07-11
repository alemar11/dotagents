# GitHub Portfolio Triage Workflows

## Scan Explicit Repositories

Resolve `<plugin-root>` as two directories above the directory containing the owning
`SKILL.md`; this may be an installed or linked package outside the current
checkout.

```bash
<plugin-root>/scripts/gitstack portfolio scan --repo <owner/repo> --repo <owner/repo>
<plugin-root>/scripts/gitstack portfolio scan --repo-file <repos.txt>
<plugin-root>/scripts/gitstack --json portfolio scan --repo <owner/repo>
```

Repo files should contain one `owner/repo` per line. Blank lines and `#`
comments are ignored.

## Report Shape

For each repo, include:

- repository URL
- open issue and PR counts
- recent CI state
- latest release state
- top queue signals
- recommended next action

Keep it read-only. Escalate to `$gitstack:github-triage`,
`$gitstack:github-ci`, or `$gitstack:github-releases` for focused follow-up on
a single repository.
