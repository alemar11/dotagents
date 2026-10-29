# __TITLE__ CLI Reference

Run from the skill root. Put `--json` before the command.

## Diagnostics

```bash
scripts/__SKILL__ --version
scripts/__SKILL__ --json doctor
```

`doctor` returns `ok`, `command`, `version`, and `python_version`. It writes
nothing and exits 0.

## Errors

Every failure prints `{"ok": false, "command", "error": {"code", "message"}}`.

| Code | Exit | Meaning |
| --- | --- | --- |
| `invalid-arguments` | 2 | The arguments did not parse. |
