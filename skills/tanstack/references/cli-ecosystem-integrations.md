# Ecosystem Integrations

Use this guide when the task is to discover or compare installable ecosystem integrations before installing anything.

Owns:
- CLI metadata queries for integrations and add-ons
- mapping ecosystem options to installable ids
- filtering choices by compatibility constraints

Workflow:
1. Use `tanstack ecosystem --json` to discover ecosystem projects, then
   `tanstack create --list-add-ons --framework <name> --json` and
   `--addon-details <id>` to verify which integrations the CLI can install.
   An ecosystem listing does not itself prove an installable add-on exists.
2. Compare option constraints before choosing an install path.
3. Keep the recommendation anchored to what the CLI can actually install.

Do not use this guide for executing a known add-on install, new app scaffolding
once choices are fixed, or framework-level design outside CLI metadata.

Verification: verify against current `@tanstack/cli` ecosystem metadata
commands when exact JSON surfaces or compatibility rules matter.

Source: [CLI discovery commands](https://tanstack.com/cli/latest/docs/cli-reference).
