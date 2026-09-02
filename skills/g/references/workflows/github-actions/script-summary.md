# G CI and Actions Permissions Contract

## Commands

```bash
<skill-root>/scripts/g ci inspect --help
<skill-root>/scripts/g --version
<skill-root>/scripts/g doctor
<skill-root>/scripts/g --json doctor
<skill-root>/scripts/g ci inspect --repo <owner/repo> --pr <number>
<skill-root>/scripts/g ci permissions --repo <owner/repo> --allow-non-project
```

Use the `<skill-root>` resolved by the active G entrypoint; never assume the caller is in the dotagents checkout.

## JSON Mode

Success payloads include:

- `ok`
- `version`
- check, inspection, or Actions-permissions data

PR inspection reports one of the canonical summaries defined in
[`../../states.md`](../../states.md).

Errors include a message and non-zero exit code. The script does not write
configuration files.

## Maintenance Source

The shipped command is built from the skill CLI project and invoked
only through `<skill-root>/scripts/g`.
