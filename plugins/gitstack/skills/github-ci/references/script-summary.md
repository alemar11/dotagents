# GitStack CI Inspect Contract

## Commands

```bash
<plugin-root>/scripts/gitstack ci inspect --help
<plugin-root>/scripts/gitstack --version
<plugin-root>/scripts/gitstack doctor
<plugin-root>/scripts/gitstack --json doctor
<plugin-root>/scripts/gitstack ci inspect --repo <owner/repo> --pr <number>
```

Resolve `<plugin-root>` as two directories above the directory containing the owning
`SKILL.md`; never assume the caller is in the dotagents checkout.

## JSON Mode

Success payloads include:

- `ok`
- `version`
- check or inspection data

Errors include a message and non-zero exit code. The script does not write
configuration files.

## Maintenance Source

The shipped command is built from the plugin maintenance project and invoked
only through `<plugin-root>/scripts/gitstack`.
