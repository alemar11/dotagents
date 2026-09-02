# G Multi-Repository Scan Contract

## Commands

```bash
<skill-root>/scripts/g portfolio scan --help
<skill-root>/scripts/g --version
<skill-root>/scripts/g doctor
<skill-root>/scripts/g --json doctor
<skill-root>/scripts/g portfolio scan --repo <owner/repo>
```

Use the `<skill-root>` resolved by the active G entrypoint; never assume the caller is in the dotagents checkout.

## JSON Mode

Success envelopes include `ok`, `version`, `command`, and `data`.
Per-repository failures are captured inside the `data.repos[]` list so one bad
repository does not hide the rest of the scan.

The script does not write configuration files.

## Maintenance Source

The shipped command is built from the skill CLI project and invoked
only through `<skill-root>/scripts/g`.
