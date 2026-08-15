---
name: skill-cli-creator
description: Create or refactor embedded CLIs that ship from a skill or plugin scripts directory.
---

# Skill CLI Creator

## Goal

Create or refactor an embedded CLI that future agents run from a shipped
artifact inside an existing skill or plugin bundle.

Use this skill only for embedded host CLIs. Standalone global or PATH-first CLI
packages need a different workflow.

## Resolve The Contract

The owning skill or plugin must exist first. Use `$skill-creator` or
`$plugin-creator` when available to scaffold a missing host; outside Codex,
create the equivalent host before continuing.

Resolve these values before editing:

- Host mode: load [references/states.md](references/states.md) and record its
  canonical `host_mode` value
- Owner root: the skill directory, one bundled skill, or a plugin-shared root
- CLI/tool name: the runtime noun that owns `scripts/<tool>` and, when needed,
  `projects/<tool>/`
- Artifact path: the owner-root-relative shipped executable under `scripts/`
- Jobs and source evidence: the concrete reads, writes, APIs, fixtures, or
  existing scripts the command must support

Choose owner and command name independently. Reuse the host name only when it
is intentionally the clearest runtime noun.

## Progressive Reference Routing

Load only what the current change needs:

| Change shape | Reference |
| --- | --- |
| New/moved paths, plugin ownership, config namespace, cache, or multi-OS packaging | `references/embedded-cli-layout.md` |
| Runtime selection, implementation/build changes, auth, or validation lane | `references/implementation-workflow.md` |
| New/changed commands, JSON, pagination, files, writes, or raw escape hatch | `references/agent-cli-patterns.md` |

A small fix to an existing skill-owned script does not require loading the
plugin ownership, config, or multi-OS sections. A docs-only correction does not require
the implementation workflow.

## Core Workflow

1. Inspect the existing host and resolve the contract above. Check for path
   collisions from the owner root:
   ```bash
   test -e <artifact-path> && echo "artifact exists"
   test -e projects/<tool-name> && echo "project exists"
   ```
   Evolve an existing command rather than creating a duplicate.
2. Load the applicable reference branches and choose the smallest viable
   layout. Keep a simple script directly under `scripts/`; add
   `projects/<tool>/` only for a real multi-file or build-backed implementation.
3. Sketch new or changed command behavior before coding: discovery and resolve
   paths, reads, writes, auth/config, JSON, file transport, raw fallback, and
   rebuild behavior that actually apply.
4. Implement toward the shipped `<artifact-path>`. Normal execution never runs
   from `projects/<tool>/`, `target/`, `dist/`, virtualenvs, or other build
   outputs.
5. Verify through the shipped artifact:
   Run `<artifact-path> --help`, `<artifact-path> --version`,
   `<artifact-path> --json doctor`, runtime-appropriate build/test checks, and at
   least one safe fixture, dry-run, or read-only end-to-end check. For a runtime
   change, add the API-backed, local/offline, or hybrid lane from
   `references/implementation-workflow.md`; a docs-only correction may validate
   only the documented artifact path and examples it changes.
6. Update the owning docs with the artifact path, optional maintenance project,
   version source, rebuild path, config path, and safe read/write boundaries.

## Invariants

- `scripts/` contains the shipped runnable artifact used during normal
  execution.
- `projects/<tool>/` is optional and maintenance-only; introduce it only when
  the implementation benefits from a real project layout.
- The shipped artifact, optional maintenance project, persistent config
  namespace, runtime docs, and examples must share the same owner boundary.
- Runtime examples use the owner-root-relative artifact or a resolved absolute
  installed path. Bare commands require a documented wrapper or `PATH` setup.
- `<artifact-path> --version` is required and must report one semver source of
  truth.
- Create config only through an explicit mutating command. Reads and health
  checks, including `doctor`, must not write config.
- Runtime caches under `~/.cache/dotagents/...` are only for rebuildable
  downloaded or generated runtime artifacts, never for user config or normal repo
  content.
- If `projects/<tool>/` exists, add `projects/<tool>/AGENTS.md` with build,
  test, rebuild, runtime prerequisites, safe-maintenance instructions, version
  source of truth, and semver bump policy.

## References

- [references/states.md](references/states.md): canonical host mode and its
  persistence boundary.

- [references/embedded-cli-layout.md](references/embedded-cli-layout.md):
  owner roots, artifact placement, naming, config namespaces, runtime cache,
  multi-OS compiled layouts, config changes, and versioning rules.
- [references/implementation-workflow.md](references/implementation-workflow.md):
  runtime choice, command-contract sketching, auth/config handling, build
  workflow, validation lanes, language defaults, and host integration.
- [references/agent-cli-patterns.md](references/agent-cli-patterns.md):
  command-shape examples, composable CLI patterns, JSON conventions, pagination,
  file outputs, writes, raw escape hatches, and `doctor` output.
