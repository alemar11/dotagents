# stars Script Contract

## Commands

```bash
<plugin-root>/scripts/gitstack stars --help
<plugin-root>/scripts/gitstack --version
<plugin-root>/scripts/gitstack doctor
<plugin-root>/scripts/gitstack --json doctor
<plugin-root>/scripts/gitstack stars list
<plugin-root>/scripts/gitstack stars add <owner/repo>
<plugin-root>/scripts/gitstack stars remove <owner/repo>
<plugin-root>/scripts/gitstack stars lists list
```

## JSON Mode

Global `--json` must appear before the command:

```bash
<plugin-root>/scripts/gitstack --json stars list
```

Success envelopes include `ok`, `version`, `command`, and `data`.
Errors include `ok`, `version`, `command`, and `error`.

The script does not write configuration files.

## CLI Maintenance

The shipped command is built from the plugin maintenance project and invoked
only through `<plugin-root>/scripts/gitstack`. Preserve the plugin-aligned
version and public command/JSON contract when maintaining the project.
