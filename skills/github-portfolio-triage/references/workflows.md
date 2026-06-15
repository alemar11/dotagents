# GitHub Portfolio Triage Workflows

## Scan Explicit Repositories

```bash
skills/github-portfolio-triage/scripts/portfolio-scan --repo <owner/repo> --repo <owner/repo>
skills/github-portfolio-triage/scripts/portfolio-scan --repo-file <repos.txt>
skills/github-portfolio-triage/scripts/portfolio-scan --json --repo <owner/repo>
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

Keep it read-only. Escalate to `github-triage`, `github-ci`, or
`github-releases` for focused follow-up on a single repository.
