# stars Script Contract

## Commands

```bash
<skill-root>/scripts/g stars --help
<skill-root>/scripts/g --version
<skill-root>/scripts/g doctor
<skill-root>/scripts/g --json doctor
<skill-root>/scripts/g stars list
<skill-root>/scripts/g stars add <owner/repo>
<skill-root>/scripts/g stars remove <owner/repo>
<skill-root>/scripts/g stars lists list
```

## JSON Mode

Global `--json` must appear before the command:

```bash
<skill-root>/scripts/g --json stars list
```

Success envelopes include `ok`, `version`, `command`, and `data`.
Errors include `ok`, `version`, `command`, and `error`.

The script does not write configuration files.

## CLI Maintenance

The shipped command is built from the skill CLI project and invoked
only through `<skill-root>/scripts/g`. Preserve the skill-owned
version and public command/JSON contract when maintaining the project.
