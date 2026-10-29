# Skill CLI Creator CLI Reference

Run from this skill's root. Put `--json` before the command.

## Diagnostics

```bash
scripts/skill-cli-creator --version
scripts/skill-cli-creator --json doctor
```

`doctor` returns `ok`, `command`, `version`, `python_version`, and
`template.path` and `template.exists`. It writes nothing.

## Create a skill

```bash
scripts/skill-cli-creator --json new release-notes --into ../ --description "Read release notes. Use when ..."
```

Copies `assets/template/` to `<into>/<name>/`, filling the name, module name
(`-` becomes `_`), title (`--title`, default the name in title case), and
description. Returns `path`, `files`, and `next`, the check command to run. It
refuses a name that is not lower-kebab and an existing target.

## Check a skill

```bash
scripts/skill-cli-creator --json check ../youtube
```

Runs the checks below and returns `skill`, `path`, and `checks`, a list of
`{id, ok, message}`. It runs the skill's artifact with `--help`, `--version`,
`--json doctor`, and an unknown command, each with a 30-second timeout.

| Check | Passes when |
| --- | --- |
| `skill-name` | the `SKILL.md` frontmatter `name` equals the directory name |
| `skill-description` | the description has 1 to 1024 characters |
| `file:<path>` | `AGENTS.md`, `agents/openai.yaml`, and `references/cli.md` exist |
| `tests` | `tests/test_*.py` exists, or `projects/<skill>/tests/` for a compiled CLI |
| `links` | every relative Markdown link outside code resolves |
| `artifact` | `scripts/<skill>` exists and is executable; `artifact-shebang` fails without a shebang |
| `help` | `--help` exits 0 |
| `version` | `--version` prints `<skill> x.y.z` and exits 0 |
| `doctor` | `--json doctor` exits 0 with a boolean `ok`, `command: "doctor"`, and the same `version` |
| `error-shape` | an unknown command exits nonzero with `ok: false` and `error.code` and `error.message` |

## Errors

Every failure prints `{"ok": false, "command", "error": {"code", "message"}}`.
A failed check also carries `skill`, `path`, and `checks`.

| Code | Exit | Meaning |
| --- | --- | --- |
| `standard-violations` | 1 | `check` found at least one failing check. |
| `not-a-skill` | 1 | The checked directory has no `SKILL.md`. |
| `target-exists` | 1 | `new` would overwrite an existing directory. |
| `invalid-name` | 2 | The `new` name is not lower-kebab-case. |
| `invalid-arguments` | 2 | The arguments did not parse. |
