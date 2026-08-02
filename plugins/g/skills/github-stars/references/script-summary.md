# stars Script Contract

## Commands

```bash
<plugin-root>/scripts/g stars --help
<plugin-root>/scripts/g --version
<plugin-root>/scripts/g doctor
<plugin-root>/scripts/g --json doctor
<plugin-root>/scripts/g stars list
<plugin-root>/scripts/g stars add <owner/repo>
<plugin-root>/scripts/g stars remove <owner/repo>
<plugin-root>/scripts/g stars lists list
```

## JSON Mode

Global `--json` must appear before the command:

```bash
<plugin-root>/scripts/g --json stars list
```

Success envelopes include `ok`, `version`, `command`, and `data`.
Errors include `ok`, `version`, `command`, and `error`.

The script does not write configuration files.

## CLI Maintenance

The shipped command is built from the plugin maintenance project and invoked
only through `<plugin-root>/scripts/g`. Preserve the plugin-aligned
version and public command/JSON contract when maintaining the project.
