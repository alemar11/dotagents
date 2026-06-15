# Embedded CLI Layout

Use this reference before creating or moving embedded CLI files inside a skill
or plugin host.

## Path Vocabulary

- `owner root`: the directory from which canonical executable examples run
  - `host=skill`: `<skill-root>`
  - `host=plugin` and exactly one bundled skill owns the CLI:
    `<plugin-root>/skills/<skill>`
  - `host=plugin` and the CLI is shared by multiple bundled skills:
    `<plugin-root>`
- `project root`: the consuming workspace or repository where local operator
  config is stored; this is distinct from the owner root.
- `artifact path`: the owner-root-relative shipped runnable artifact, usually
  `scripts/<tool>` or `scripts/<tool>.<ext>`.
- `public runtime noun`: optional shorthand such as `<tool>` only when the host
  docs explicitly define a wrapper, alias, or `PATH` setup.

Use `/` separators for repository-relative template paths such as
`scripts/<tool>` and `projects/<tool>/`. Use OS-specific home-directory notation
only for real per-user filesystem paths:

- macOS / Linux shell examples: `$HOME/...`
- Windows CMD examples: `%USERPROFILE%\...` or
  `%HOMEDRIVE%%HOMEPATH%\...`
- Windows PowerShell examples: `$env:USERPROFILE\...`

Do not use `%HOMEPATH%` alone because it does not include the drive.

## Ownership Model

Keep one embedded-CLI doctrine for all hosts:

- `scripts/` contains shipped runnable artifacts used during normal execution.
- `projects/<tool>/` is the optional maintenance-only build project behind one
  shipped CLI when a real project layout is needed.
- Persisted working-project config follows the same owner boundary and keeps
  plugin identity explicit when the host is a plugin.
- Normal runtime usage never runs from `dist/`, `target/`, virtualenv paths, or
  similar build outputs.

The owner of the shipped artifact also owns:

- the maintenance project
- the persistent working-project config namespace
- the runtime docs and examples

Do not split ownership:

- Do not allow plugin-root `projects/<tool>/` with skill-local
  `scripts/<tool>`.
- Do not drop plugin identity or skill scope from the persistent config
  namespace when the host is a plugin.
- Do not silently derive ownership from the CLI/tool name later.

## When `scripts/` Is Enough

Prefer a direct `scripts/<tool>` artifact when the CLI is:

- one small Python or shell script
- dependency-free or standard-library-only
- not compiled or bundled from multiple files
- not generated from source assets
- easy to test through the shipped script itself

In this layout, keep the executable implementation in `scripts/<tool>` and keep
tests at the owner root, such as `<skill-root>/tests/` or
`<plugin-root>/tests/<tool>/`. Do not add `projects/<tool>/` just to create a
place for one source file, one version constant, or a small test module.

Introduce `projects/<tool>/` only when the CLI needs a real maintenance
project: multiple source modules, package metadata, lockfiles, generated build
outputs, compiled binaries, vendored fixtures, or dedicated build/install
helpers.

## Placement Matrix

For `host=skill`:

- shipped artifact: `<skill-root>/scripts/<tool>`
- maintenance project: `<skill-root>/projects/<tool>/`
- working-project config: `<project-root>/.skills/<skill>/config.toml`

For `host=plugin` when exactly one bundled skill owns the CLI:

- shipped artifact: `<plugin-root>/skills/<skill>/scripts/<tool>`
- maintenance project: `<plugin-root>/skills/<skill>/projects/<tool>/`
- working-project config:
  `<project-root>/.plugins/<plugin>/skills/<skill>/config.toml`

For `host=plugin` when the CLI is intentionally shared by multiple bundled
skills:

- shipped artifact: `<plugin-root>/scripts/<tool>`
- maintenance project: `<plugin-root>/projects/<tool>/`
- working-project config: `<project-root>/.plugins/<plugin>/config.toml`

Default to the narrowest owner. Promote from skill-local ownership to
plugin-root ownership only when the CLI is intentionally shared by multiple
bundled skills.

Treat plugin-root `scripts/` as a repository convention supported by this skill,
not as an officially documented Codex plugin manifest component.

## Naming

Treat the host container and CLI/tool name as different design decisions:

- host name: the skill or plugin package container
- CLI/tool name: the runtime command noun used in `scripts/<tool>` and, when
  needed, `projects/<tool>/`

Use this naming rule:

- By default, choose the CLI/tool name independently when the runtime command is
  narrower than the host.
- Reuse the host name only when matching is intentionally justified because it is
  already the clearest ecosystem-standard runtime noun.
- Use the chosen CLI/tool name consistently in `scripts/<tool>`,
  `projects/<tool>/`, runtime examples, and maintenance docs.

Naming rubric:

- Prefer short, task- or domain-oriented names.
- Avoid names that imply broader scope than the CLI actually covers.
- Avoid generic suffix-only names such as `-cli` or `-tool` unless they improve
  clarity.
- If the CLI/tool name matches the host name, state the justification before
  scaffolding.

## Runtime Surface

Keep these invariants explicit in host docs and CLI docs:

- Run the tool from `<artifact-path>` during normal execution.
- Do not inspect or run from `projects/<tool>/` during normal execution.
- Treat `<artifact-path>` as the shipped runnable artifact or launcher
  regardless of language.
- Require `<artifact-path> --version` as part of the stable runtime surface.
- Let the chosen CLI/tool name govern both `<artifact-path>` and
  `projects/<tool>/` when a maintenance project exists.
- Open `projects/<tool>/` only when it exists and you are fixing, improving,
  rebuilding, or extending the implementation behind `<artifact-path>`.
- Keep script-native runnable artifacts entirely in `scripts/`; introduce
  `projects/<tool>/` only when the implementation grows enough to justify a real
  maintenance project.
- Keep manifests, lockfiles, dependency installs, caches, intermediate build
  outputs, project-local test/build config, and source inside
  `projects/<tool>/` when a real maintenance project exists.
- If `projects/<tool>/` exists, keep CLI-specific tests inside that project.
- Do not introduce host-root wrappers unless the user explicitly asks for that
  non-standard layout.
- Do not execute compiled CLIs from `target/`, `dist/`, virtualenv paths, or
  other build directories during normal usage.
- Do not tell bundled skills to run `scripts/<tool>` unless that path is
  actually the artifact path from that skill's owner root.
- When a bundled skill documents a plugin-shared CLI that runs from
  `<plugin-root>`, introduce that execution context before the command, such as
  `From the plugin root, run <artifact-path> ...`.

## Multi-OS Compiled Runtime

Use this pattern only when a compiled CLI must support more than one operating
system or CPU architecture:

- Keep `scripts/<tool>` as the stable executable surface normal users run.
- Make `scripts/<tool>` a portable launcher that detects OS and architecture.
- Store shipped platform binaries under `scripts/bin/` as
  `<tool>-<os>-<arch>`.
- Use `darwin-arm64`, `darwin-x86_64`, `linux-arm64`, and `linux-x86_64` as the
  standard platform suffixes.
- Make the launcher fail clearly when the current platform binary is missing,
  naming the expected `scripts/bin/<tool>-<os>-<arch>` path.
- Keep script-native or intentionally single-platform CLIs as a direct
  `scripts/<tool>` artifact; do not add `scripts/bin/` without a concrete
  multi-OS packaging need.

For multi-OS compiled runtimes, add a maintainer install helper under
`projects/<tool>/scripts/`, usually `install-runtime-binary`. It should build
the current platform or requested target and copy the result to
`scripts/bin/<tool>-<os>-<arch>`.

## Config Rules

Persist config only when the user explicitly chooses a write path such as:

- `<artifact-path> init ...`
- `<artifact-path> login ...`
- `<artifact-path> configure ...`

Never create config implicitly on install or on first read.

Use one owner-aligned `config.toml` namespace, not one file per tool:

- skill-owned: `<project-root>/.skills/<skill>/config.toml`
- plugin-owned shared: `<project-root>/.plugins/<plugin>/config.toml`
- plugin-owned but local to one skill:
  `<project-root>/.plugins/<plugin>/skills/<skill>/config.toml`

Keep config-only directories explicit:

- `<project-root>/.skills/<skill>/`
- `<project-root>/.plugins/<plugin>/`
- `<project-root>/.plugins/<plugin>/skills/<skill>/`

Do not place helper scripts or implementation code there.

Consuming repos should gitignore the local `config.toml` path that the CLI uses.
When a skill or plugin migrates from a legacy config filename to `config.toml`,
update consuming repo ignore rules in the same rollout.

Normative config format:

```toml
schema_version = "1.0.0"

[defaults]
profile = "staging"

[auth]
source = "env"

[tools.logs]
workspace = "mobile"

[tools.deploys]
confirm = "interactive"

[meta]
written_by = "logs"
written_by_version = "0.9.0"
```

Rules:

- `schema_version` is the config format version and the only required version
  field.
- Owner-wide settings live only in explicitly documented shared sections such as
  `[defaults]`, `[auth]`, or `[profiles]`.
- `[tools.<tool>]` stores tool-specific persisted settings.
- When multiple CLIs share one `config.toml`, each CLI may write only its own
  `[tools.<tool>]` subtree plus any shared section it uniquely owns as the
  documented single writer.
- `[meta]` is optional provenance only and must not drive runtime behavior.
- Do not require top-level `version` or `tools.<tool>.version`.
- Create parent directories only when the user actually persists config.

## Config Migrations

Promotion from plugin single-skill ownership to plugin-shared ownership changes
both config storage and the canonical artifact path:

- Normal read commands must use only the new config path under
  `.plugins/<plugin>/config.toml`.
- Update owning docs and examples to the new artifact path under the plugin root
  in the same rollout.
- Handle old-to-new import only during an explicit mutating flow such as `init`,
  `login`, `configure`, or `migrate-config`.
- If `.plugins/<plugin>/config.toml` already exists, import or merge only keys
  that are still absent and never silently overwrite existing keys.
- Preserve the CLI-owned `[tools.<tool>]` subtree plus any shared section the CLI
  uniquely owns as the documented single writer.
- Keep ignore rules aligned with the new canonical path in the same rollout.

## Runtime Cache

Use a per-user runtime cache only when the embedded CLI needs reusable
downloaded or generated runtime artifacts that should survive across consuming
repos, such as fetched toolchains, unpacked helper binaries, model files, or
other rebuildable runtime assets.

Do not use the runtime cache for:

- owner-aligned operator config, which belongs in `config.toml`
- maintenance-only build outputs or dependency caches inside `projects/<tool>/`
- normal repo content or tracked fixtures

When a runtime cache is truly needed, scope it by owner:

- skill-owned: `~/.cache/dotagents/skills/<skill-name>/...`
- plugin-owned shared: `~/.cache/dotagents/plugins/<plugin-name>/...`
- plugin-owned but local to one skill:
  `~/.cache/dotagents/plugins/<plugin-name>/skills/<skill-name>/...`

Runtime-cache rules:

- Create the cache lazily from the explicit runtime flow that needs it, not on
  install and not during unrelated reads.
- Treat cache contents as disposable and rebuildable; they must never be the
  sole source of truth for user state.
- Version or namespace cache subdirectories when format or upstream-version
  changes matter.
- Document the cache purpose and location only when the CLI actually needs one.

## CLI Versioning

Versioning is required for every embedded CLI produced through this skill.

- Support `<artifact-path> --version` on the public runtime surface.
- Keep one semver source of truth for the CLI version.
- Use the artifact stored at `<artifact-path>` as the only supported normal
  execution surface.
- Use the runtime-native manifest version when one exists, such as `Cargo.toml`,
  `package.json`, or `pyproject.toml`.
- When no native manifest exists, keep the version in one explicit code constant
  or a dedicated version file.
- Treat doc-only updates as no-version-bump changes unless they accompany
  shipped CLI behavior changes.
