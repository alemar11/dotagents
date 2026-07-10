# reviews Script Contract

## Commands

```bash
<skill-root>/scripts/reviews --help
<skill-root>/scripts/reviews --version
<skill-root>/scripts/reviews doctor
<skill-root>/scripts/reviews --json doctor
<skill-root>/scripts/reviews address --repo <owner/repo> --pr <number>
<skill-root>/scripts/reviews address --repo <owner/repo> --pr <number> --comment-ids <ids> --reply-body-file <message-file>
<skill-root>/scripts/reviews comment --repo <owner/repo> --pr <number> --body-file <message-file>
```

Resolve `<skill-root>` as the absolute directory containing the owning
`SKILL.md`. Prefer `--reply-body-file` for replies so arbitrary text never needs
shell interpolation.

## JSON Mode

Success envelopes:

```json
{
  "ok": true,
  "version": "1.1.1",
  "command": ["address"],
  "data": {}
}
```

Error envelopes:

```json
{
  "ok": false,
  "version": "1.1.1",
  "command": ["address"],
  "error": {"code": "invalid_arguments", "message": "..."}
}
```

The script does not write configuration files.

## Discussion Comments

Use `comment` for top-level PR discussion comments. It supports `--body`,
`--body-file`, `--dry-run`, `--json`, `--repo`, `--pr`, and
`--allow-non-project`.

Use `address --reply-body-file` with `--selection` or `--comment-ids` for safe
file-backed replies. `--reply-body` remains available for callers that already
pass an argument vector without a shell, but shell examples must use the file
surface.

In JSON mode, `comment` returns the same success/error envelope as other
commands, with `data.action.status` set to `dry-run` or `posted`.

## Maintenance Source

The executable script is also the maintained source at `scripts/reviews`. Tests
live under `tests/`.
