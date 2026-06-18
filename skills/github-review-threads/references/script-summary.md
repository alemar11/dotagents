# reviews Script Contract

## Commands

```bash
skills/github-review-threads/scripts/reviews --help
skills/github-review-threads/scripts/reviews --version
skills/github-review-threads/scripts/reviews doctor
skills/github-review-threads/scripts/reviews --json doctor
skills/github-review-threads/scripts/reviews address --repo <owner/repo> --pr <number>
```

## JSON Mode

Success envelopes:

```json
{
  "ok": true,
  "version": "1.0.0",
  "command": ["address"],
  "data": {}
}
```

Error envelopes:

```json
{
  "ok": false,
  "version": "1.0.0",
  "command": ["address"],
  "error": {"code": "invalid_arguments", "message": "..."}
}
```

The script does not write configuration files.

## Maintenance Source

The executable script is also the maintained source at `scripts/reviews`. Tests
live under `tests/`.
