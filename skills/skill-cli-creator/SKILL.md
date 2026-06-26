---
name: skill-cli-creator
description: Create or refactor embedded CLIs that ship from `scripts/<tool>` inside an existing skill or plugin.
---

# Skill CLI Creator

## Goal

Create or refactor an embedded CLI that future agents run from a shipped
artifact inside an existing skill or plugin bundle.

Build for embedded host use only. Do not use this skill for standalone global
CLIs, separate personal CLI repos, or PATH-first packaging.

## Start

This skill assumes the owning skill or plugin already exists. If the host does
not exist yet, scaffold it first with `$skill-creator` or `$plugin-creator` when
those Codex helpers are available. Outside Codex, create the equivalent host
directory, `SKILL.md` or plugin manifest, and metadata by hand, then return here
once the host boundary is real.

Before creating files, capture:

- Host mode: `skill` or `plugin`
- Host owner:
  - `host=skill`: the skill directory that owns the CLI surface
  - `host=plugin`: the plugin directory, plus whether one bundled skill or
    multiple bundled skills own the runtime surface
- CLI/tool name: the runtime noun that owns `scripts/<tool>` and, when needed,
  `projects/<tool>/`
- Source: API docs, OpenAPI JSON, SDK docs, curl examples, browser app, existing
  internal script, article, or working shell history
- Jobs: literal reads and writes such as `list drafts`, `download failed job
  logs`, `search messages`, `upload media`, or `read queue schedule`
- Artifact path: the shipped runnable artifact path such as
  `scripts/ci-logs`, `scripts/slack-cli`, or `scripts/buildkite-logs`

Choose the host owner and the CLI/tool name independently by default. Reuse the
skill or plugin name only when it is intentionally the clearest runtime command
name.

## Core Workflow

1. Resolve ownership before layout.
   Read [references/embedded-cli-layout.md](references/embedded-cli-layout.md)
   before creating `scripts/`, `projects/<tool>/`, config paths, or cache paths.
2. Check for collisions from the resolved owner root.
   ```bash
   test -e <artifact-path> && echo "artifact exists"
   test -e projects/<tool-name> && echo "project exists"
   ```
   If either exists, evolve the existing command or choose a clearer name.
3. Choose the runtime and layout deliberately.
   Use [references/implementation-workflow.md](references/implementation-workflow.md)
   to inspect installed toolchains, pick Rust/TypeScript/Python/shell, choose
   direct `scripts/` versus `projects/<tool>/`, and state the reason before
   scaffolding.
4. Sketch the command contract before coding.
   Include discovery commands, resolve or ID-lookup commands, read commands,
   write commands, raw escape hatch, auth/config choice, JSON behavior, and
   rebuild behavior.
5. Build toward the shipped artifact.
   Normal execution must run through `<artifact-path>` under `scripts/`, not from
   `projects/<tool>/`, `target/`, `dist/`, virtualenvs, or other build outputs.
6. Verify through the artifact.
   Run `<artifact-path> --help`, `<artifact-path> --version`,
   `<artifact-path> --json doctor`, runtime-appropriate build/test checks, and at
   least one safe fixture, dry-run, or read-only end-to-end check.
7. Update the owning docs.
   Add or update a `CLI Maintenance` section in the owning skill or plugin docs
   so future agents know the artifact path, maintenance project, version source
   of truth, rebuild path, config path, and safe read/write boundaries.

## Non-Negotiable Invariants

- `scripts/` contains the shipped runnable artifact used during normal
  execution.
- `projects/<tool>/` is optional and maintenance-only; introduce it only when
  the implementation benefits from a real project layout.
- A direct executable under `scripts/<tool>` is enough for a single-file script,
  a small dependency-free Python or shell tool, or a shim that does not need
  build metadata, generated outputs, or multiple source modules.
- Do not create `projects/<tool>/` just to hold one script plus tests. Keep
  script-owned tests beside the skill or plugin owner, such as
  `<skill-root>/tests/`, unless a real maintenance project exists.
- The shipped artifact, optional maintenance project, persistent config
  namespace, runtime docs, and examples must share the same owner boundary.
- Runtime examples use `<artifact-path> ...`, `<resolved-tool> ...`, or an
  absolute installed artifact path unless the host docs explicitly define a
  wrapper, alias, or `PATH` contract for bare `<tool> ...`.
- `<artifact-path> --version` is required and must report one semver source of
  truth.
- Owner-aligned config lives in `config.toml` under `.skills/...` or
  `.plugins/...`; create it only through explicit `init`, `login`, or
  `configure` flows.
- Runtime caches under `~/.cache/dotagents/...` are only for rebuildable
  downloaded or generated runtime artifacts, never for user config or normal repo
  content.
- If `projects/<tool>/` exists, keep project-local generated state ignored there
  with a scoped `.gitignore` only when generated state actually exists.
- If `projects/<tool>/` exists, add `projects/<tool>/AGENTS.md` with build,
  test, rebuild, runtime prerequisites, safe-maintenance instructions, version
  source of truth, and semver bump policy.

## References

- [references/embedded-cli-layout.md](references/embedded-cli-layout.md):
  owner roots, artifact placement, naming, config namespaces, runtime cache,
  multi-OS compiled layouts, config migration, and versioning rules.
- [references/implementation-workflow.md](references/implementation-workflow.md):
  runtime choice, command-contract sketching, auth/config handling, build
  workflow, validation lanes, language defaults, and host integration.
- [references/agent-cli-patterns.md](references/agent-cli-patterns.md):
  command-shape examples, composable CLI patterns, JSON conventions, pagination,
  file outputs, writes, raw escape hatches, and `doctor` output.

## Validation Summary

Always validate from the shipped artifact path. The minimum closeout is:

```bash
<artifact-path> --help
<artifact-path> --version
<artifact-path> --json doctor
```

Then add the matching lane from
[references/implementation-workflow.md](references/implementation-workflow.md):
API-backed, local/offline, or hybrid.
