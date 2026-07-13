# reviews Script Contract

## Commands

```bash
<plugin-root>/scripts/gitstack reviews --help
<plugin-root>/scripts/gitstack --version
<plugin-root>/scripts/gitstack doctor
<plugin-root>/scripts/gitstack --json doctor
<plugin-root>/scripts/gitstack reviews address --repo <owner/repo> --pr <number>
<plugin-root>/scripts/gitstack reviews address --repo <owner/repo> --pr <number> --comment-ids <ids> --reply-body-file <message-file>
<plugin-root>/scripts/gitstack reviews comment --repo <owner/repo> --pr <number> --body-file <message-file>
<plugin-root>/scripts/gitstack --json reviews check --provider codex --repo <owner/repo> --pr <number> --head <sha>
<plugin-root>/scripts/gitstack --json reviews wait --provider codex --repo <owner/repo> --pr <number> --head <sha> --timeout 15m
```

Resolve `<plugin-root>` as two directories above the directory containing the owning
`SKILL.md`. Prefer `--reply-body-file` for replies so arbitrary text never needs
shell interpolation.

## JSON Mode

Success envelopes:

```json
{
  "ok": true,
  "version": "<plugin-version>",
  "command": ["address"],
  "data": {}
}
```

Error envelopes:

```json
{
  "ok": false,
  "version": "<plugin-version>",
  "command": ["address"],
  "error": {"code": "invalid_arguments", "message": "..."}
}
```

The script does not write configuration files.

## Automated Review State

Both `check` and `wait` return `data.provider`, `data.review_state`, `data.head`,
`data.current_head`, `data.head_is_current`, plus review and request evidence.
States are `not-requested`, `acknowledged`, `pending`, `clean`, `findings`, and
`stale`.

Exit codes are stable: `0` for clean, `1` for findings, `2` for
not-requested/acknowledged/pending, `3` for stale review evidence, `4` for an
API or configuration failure, `64` for invalid arguments, and `124` when
`wait` times out. JSON envelopes remain valid for nonzero review-state exits.

`wait` accepts `--timeout`, `--interval`, and `--max-interval` durations using
seconds, minutes, or hours, such as `30s`, `15m`, or `1h`.
`--head` accepts a full hexadecimal commit SHA or an unambiguous prefix of at
least seven characters. Review-request comments must include that SHA or prefix
for acknowledgement and reaction evidence to count toward the target head.

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

The shipped command is built from the plugin maintenance project and invoked only through `<plugin-root>/scripts/gitstack`.
