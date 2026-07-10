# ci-inspect Script Contract

## Commands

```bash
<skill-root>/scripts/ci-inspect --help
<skill-root>/scripts/ci-inspect --version
<skill-root>/scripts/ci-inspect doctor
<skill-root>/scripts/ci-inspect --json doctor
<skill-root>/scripts/ci-inspect --repo <owner/repo> --pr <number>
```

Resolve `<skill-root>` as the absolute directory containing the owning
`SKILL.md`; never assume the caller is in the dotagents checkout.

## JSON Mode

Success payloads include:

- `ok`
- `version`
- check or inspection data

Errors include a message and non-zero exit code. The script does not write
configuration files.

## Maintenance Source

The executable script is also the maintained source at `scripts/ci-inspect`.
Tests live under `tests/`.
