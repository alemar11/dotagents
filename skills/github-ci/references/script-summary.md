# ci-inspect Script Contract

## Commands

```bash
skills/github-ci/scripts/ci-inspect --help
skills/github-ci/scripts/ci-inspect --version
skills/github-ci/scripts/ci-inspect doctor
skills/github-ci/scripts/ci-inspect --json doctor
skills/github-ci/scripts/ci-inspect --repo <owner/repo> --pr <number>
```

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
