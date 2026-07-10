# portfolio-scan Script Contract

## Commands

```bash
<skill-root>/scripts/portfolio-scan --help
<skill-root>/scripts/portfolio-scan --version
<skill-root>/scripts/portfolio-scan doctor
<skill-root>/scripts/portfolio-scan --json doctor
<skill-root>/scripts/portfolio-scan --repo <owner/repo>
```

Resolve `<skill-root>` as the absolute directory containing the owning
`SKILL.md`; never assume the caller is in the dotagents checkout.

## JSON Mode

Success envelopes include `ok`, `version`, `command`, and `data`.
Per-repository failures are captured inside the `data.repos[]` list so one bad
repository does not hide the rest of the scan.

The script does not write configuration files.

## Maintenance Source

The executable script is also the maintained source at
`scripts/portfolio-scan`. Tests live under `tests/`.
