# Compiled CLIs, Configuration, and Cache

Read only when a skill CLI needs a build, persisted configuration, a cache, or
lives inside a plugin. Everything else is in [standard](standard.md).

## Maintenance project

A standard-library Python script needs no project. Add `projects/<skill>/` only
for a real build: several source modules, package metadata, lockfiles,
dependencies, or compiled binaries.

- `projects/<skill>/` holds the source, manifest, lockfile, its tests, and its
  own `.gitignore` for build output. Agents never run anything from it during
  normal use, and never from `target/`, `dist/`, or a virtualenv.
- The build copies its output to the shipped artifact. The manifest
  (`Cargo.toml`, `package.json`, `pyproject.toml`) is the version source.
- `AGENTS.md` gives the build command and says to rerun the
  [validation](standard.md#validation) on the rebuilt artifact.

### Several platforms

When a compiled CLI must run on more than one OS or architecture:

- `scripts/<skill>` is a portable launcher that picks the binary for the
  current platform.
- Binaries live in `scripts/bin/<skill>-<os>-<arch>`, with `darwin-arm64`,
  `darwin-x86_64`, `linux-arm64`, `linux-x86_64`.
- A missing binary fails with a message naming the expected path.
- `projects/<skill>/scripts/install-runtime-binary` builds one platform and
  copies it into `scripts/bin/`.

## Configuration

Persist configuration only through an explicit `init`, `login`, or
`configure` command, never on install or first read. It lives in the project
that uses the skill, in one `config.toml` per owner:

| Owner | Path |
| --- | --- |
| a skill | `<project>/.skills/<skill>/config.toml` |
| a skill inside a plugin | `<project>/.plugins/<plugin>/skills/<skill>/config.toml` |
| a CLI shared by a plugin's skills | `<project>/.plugins/<plugin>/config.toml` |

```toml
schema_version = "1.0.0"

[defaults]
profile = "staging"

[tools.<skill>]
workspace = "mobile"
```

`schema_version` is the only required field. Each CLI writes only its own
`[tools.<skill>]` table and any shared table it alone owns. Consuming
repositories should ignore the file in git. Prefer the provider's own auth or
environment variables to stored secrets, and never take a secret as a flag,
where it lands in shell history.

## Cache

Use a cache only for rebuildable downloads or generated files, never for
configuration or the only copy of user state:

- a skill: `~/.cache/dotagents/skills/<skill>/`
- a plugin: `~/.cache/dotagents/plugins/<plugin>/`, with a skill's part under
  `skills/<skill>/`

Create it lazily from the command that needs it; `doctor` reports it without
creating it. Version its subfolders when the format changes.

## Inside a plugin

A CLI owned by one bundled skill lives at `<plugin>/skills/<skill>/scripts/<skill>`.
One shared by several bundled skills lives at `<plugin>/scripts/<tool>`, with
`<plugin>/projects/<tool>/` when it needs a build; skills that use it say
"from the plugin root, run ...". Keep the narrowest owner, and move to the
plugin root only when a second skill needs the CLI.
