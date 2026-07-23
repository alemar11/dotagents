# GitStack Multi-Repository Scan Contract

## Commands

```bash
<plugin-root>/scripts/gitstack portfolio scan --help
<plugin-root>/scripts/gitstack --version
<plugin-root>/scripts/gitstack doctor
<plugin-root>/scripts/gitstack --json doctor
<plugin-root>/scripts/gitstack portfolio scan --repo <owner/repo>
```

Resolve `<plugin-root>` as two directories above the directory containing the owning
`SKILL.md`; never assume the caller is in the dotagents checkout.

## JSON Mode

Success envelopes include `ok`, `version`, `command`, and `data`.
Per-repository failures are captured inside the `data.repos[]` list so one bad
repository does not hide the rest of the scan.

The script does not write configuration files.

## Maintenance Source

The shipped command is built from the plugin maintenance project and invoked
only through `<plugin-root>/scripts/gitstack`.
