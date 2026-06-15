# stars Script Contract

## Commands

```bash
skills/github-stars/scripts/stars --help
skills/github-stars/scripts/stars --version
skills/github-stars/scripts/stars doctor
skills/github-stars/scripts/stars --json doctor
skills/github-stars/scripts/stars list
skills/github-stars/scripts/stars add <owner/repo>
skills/github-stars/scripts/stars remove <owner/repo>
skills/github-stars/scripts/stars lists list
```

## JSON Mode

Global `--json` must appear before the command:

```bash
skills/github-stars/scripts/stars --json list
```

Success envelopes include `ok`, `version`, `command`, and `data`.
Errors include `ok`, `version`, `command`, and `error`.

The script does not write configuration files.

## Maintenance Source

The source and tests live under `projects/stars/`. The shipped runtime artifact
is `scripts/stars`.
