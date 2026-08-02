# G CI Inspect Contract

## Commands

```bash
<plugin-root>/scripts/g ci inspect --help
<plugin-root>/scripts/g --version
<plugin-root>/scripts/g doctor
<plugin-root>/scripts/g --json doctor
<plugin-root>/scripts/g ci inspect --repo <owner/repo> --pr <number>
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
only through `<plugin-root>/scripts/g`.
