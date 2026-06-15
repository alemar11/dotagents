# portfolio-scan Script Contract

## Commands

```bash
skills/github-portfolio-triage/scripts/portfolio-scan --help
skills/github-portfolio-triage/scripts/portfolio-scan --version
skills/github-portfolio-triage/scripts/portfolio-scan doctor
skills/github-portfolio-triage/scripts/portfolio-scan --json doctor
skills/github-portfolio-triage/scripts/portfolio-scan --repo <owner/repo>
```

## JSON Mode

Success envelopes include `ok`, `version`, `command`, and `data`.
Per-repository failures are captured inside the `data.repos[]` list so one bad
repository does not hide the rest of the scan.

The script does not write configuration files.

## Maintenance Source

The executable script is also the maintained source at
`scripts/portfolio-scan`. Tests live under `tests/`.
