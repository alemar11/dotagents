# TanStack skills through Intent

Use TanStack's consumer CLI, `@tanstack/intent`, to enable official skills shipped
inside the project's installed npm packages. Skills stay with those packages;
setup writes source permissions and loading guidance rather than copying a
separate catalog into `.agents/skills/`. The shared
[Claude directory link](claude-code.md) exposes repository-installed
skill files; it does not replace Intent's dependency discovery or loading guidance.

## Install and configure

Inspect the package manager, lockfile, workspace boundaries, installed TanStack
packages, existing `intent` configuration, and project agent instructions.
Use the owning workspace package for scoped setup; do not overwrite inherited
policy with a new package-local declaration accidentally. Node.js 20.12.0+ and
the project's package manager are host prerequisites.

Add `@tanstack/intent` as a development dependency using that package manager,
or reuse its installed version. Keep the manifest and lockfile changes together.
Default mode installs missing consumer setup and refreshes existing setup.
For `setup`, reuse existing configuration and CLI content, adding only what is
missing. For `update`, require an existing Intent consumer setup; report missing
setup rather than installing it. Select the relevant installed TanStack packages
from project evidence, not the entire npm or workspace catalog.
For npm, from the intended package directory:

```sh
npm install -D @tanstack/intent
npx intent list --json
npx intent install
```

Run `npx intent` only after confirming that the local `intent` binary belongs to
`@tanstack/intent`; use the equivalent local binary runner for other package
managers. Prefer this installed CLI over `npx @tanstack/intent@latest`, which
can differ from the lockfile version. Check generated loading commands too:
Intent may emit `@latest` runners; adjust them to the project's installed CLI.

First-run `install` requires an interactive terminal. Select the discovered
official TanStack packages or individual skill IDs needed for the requested
scope, and inspect the destination and saved rules before confirming. A request
for all TanStack skills does not authorize the all-sources `"*"` option. Package
rules include future skills in those packages; `"@tanstack/*"` also admits future
TanStack packages and should be used only when that scope is intended. Do not
broaden permissions to bypass a missing terminal; report the remaining
interactive step if it cannot be completed.

Existing effective `intent.skills` permissions are preserved by plain `install`;
use `install --review` for requested permission changes. Preserve
`intent.exclude` and workspace inheritance. `install --dry-run` previews policy
and guidance without saving them, but first-run selection still needs a terminal.
If installed packages expose no skills, report the coverage gap rather than
adding or upgrading application libraries solely to obtain skills.

## Agent guidance

Intent updates an existing `intent-skills` managed block or defaults to a
repository `AGENTS.md`. Preserve instructions outside the block and ensure the
requested client actually reads it:

- Codex, Cursor, and Pi: use project `AGENTS.md` guidance.
- Claude Code: use project `CLAUDE.md`, either through an existing import of
  `AGENTS.md` or by placing the managed block there. Keep one maintained block
  and verify the resulting discovery path.

Use lightweight discovery/loading guidance by default; `--map` is optional for
explicit task mappings. Consumer setup does not require a TanStack MCP server,
agent hooks, or `intent maintainer` commands. Keep those outside this workflow
and never enable global scanning or user-scoped configuration.

## Updates and verification

Library releases own the packaged skills. Re-running `install` refreshes loading
guidance; it does not update library code or skills. Updating `@tanstack/intent`
updates the CLI only. In default or update mode, check/update the existing local
CLI through the project's package manager within its declared version constraints,
preserving explicit pins, then refresh loading guidance. In setup-only mode,
do not update that CLI or regenerate already-valid guidance. If newer skills
require a library upgrade, report the
required dependency change for the project's normal update workflow rather than
performing an application migration as skill setup.

After setup, verify the owning manifest, lockfile, effective source permissions,
and client-readable managed block. List skills with the installed CLI and load
one permitted, relevant ID returned by discovery:

```sh
npx intent list --json
npx intent load '<package>#<skill>'
```

Replace the placeholder with a discovered ID. Confirm the load resolves to an
installed project or workspace dependency. Report successful loading separately
from whether a live agent has consumed the guidance. If guidance generation
fails after permissions were saved, inspect both files before retrying; the
permission change is not automatically rolled back.

## Official sources

- [Consumer setup](https://tanstack.com/intent/latest/docs/getting-started/quick-start-consumers)
- [Install behavior](https://tanstack.com/intent/latest/docs/cli/intent-install)
- [Configuration and inheritance](https://tanstack.com/intent/latest/docs/concepts/configuration)
