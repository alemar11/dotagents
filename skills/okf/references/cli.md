# OKF CLI Reference

Run from the skill root, or as `<okf-skill-root>/scripts/okf` from another
repository. Put the global `--json` before the command. With `--json`, stdout
carries one JSON object; human diagnostics go to stderr.

## Diagnostics

```sh
scripts/okf --version
scripts/okf --json doctor
```

`--version` prints `okf <version>`. `doctor` returns `ok`, `command`,
`version`, `spec_version`, and `checks` (`python`, `pyyaml`, `executable`,
`anchored_io`). It always exits 0; `ok` is false when the operating system
cannot provide the directory-relative file access that safe validation and
scaffolding need.

## Validate

```sh
scripts/okf validate <bundle>
scripts/okf --json validate <bundle> [--strict-links]
```

Returns `ok`, `command`, `pyyaml`, `files_checked`, `concepts_checked`,
`errors`, and `warnings`, each message with `severity`, `path`, and `message`.
A bundle with errors adds `error` with code `validation-failed` and exits 65.
What counts as an error or a warning is in [validation](validation.md).

## Scaffold

```sh
scripts/okf --json scaffold <bundle> <concept-id> --type Reference \
  [--title T] [--description D] [--resource URL] [--tag T]... \
  [--generated-by WHO] [--generated-at now|<ISO 8601>] [--body-file F] [--force]
```

Returns `ok`, `command`, `version`, `spec_version`, and `path`, the created
concept file. It refuses to overwrite an existing concept unless `--force`.

## Errors

Every failure prints `{"ok": false, "command", "error": {"code", "message"}}`;
command errors also carry `error.exit_code`.

| Code | Exit | Meaning |
| --- | --- | --- |
| `invalid-arguments` | 2 | The arguments did not parse. |
| `invalid-input`, `unsafe-path` | 64 | Bad input, or a path that is a symlink or escapes the bundle. |
| `invalid-generation`, `missing-required-field` | 64 | Invalid scaffold metadata. |
| `validation-failed`, `invalid-utf8` | 65 | The bundle, or a body file, is not valid. |
| `overwrite-refused` | 73 | `scaffold` would overwrite a concept without `--force`. |
| `io-error` | 74 | A file could not be read or written. |
