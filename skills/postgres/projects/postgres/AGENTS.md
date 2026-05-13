# Postgres Rust CLI

This `projects/postgres/` directory is the maintenance/build project behind the
public runtime entrypoint at `skills/postgres/scripts/postgres`.

## Runtime surface

- Normal usage must go through the shipped launcher at `../../scripts/postgres`.
- Do not tell normal skill users to run `cargo`, `rustc`, or binaries from
  `target/` directly.
- `Cargo.toml` is the single source of truth for the CLI version.
- Canonical persisted config lives at `<project-root>/.skills/postgres/config.toml`.
- Platform-specific release binaries live under `../../scripts/bin/` and use
  `postgres-<os>-<arch>` names, such as `postgres-darwin-arm64` and
  `postgres-linux-x86_64`.

## Build and test

- Build: `cargo build --release --manifest-path skills/postgres/projects/postgres/Cargo.toml`
- Rebuild and install the runtime binary for the current platform:
  `skills/postgres/projects/postgres/scripts/install-runtime-binary`
- Rebuild and install a cross-targeted runtime binary when the Rust target and
  linker are available:
  `skills/postgres/projects/postgres/scripts/install-runtime-binary x86_64-unknown-linux-gnu`
- Run tests: `cargo test --manifest-path skills/postgres/projects/postgres/Cargo.toml`
- Verify help: `skills/postgres/scripts/postgres --help`
- Verify version: `skills/postgres/scripts/postgres --version`
- Verify JSON doctor: `DB_PROJECT_ROOT=/path/to/repo skills/postgres/scripts/postgres --json doctor`

## Semver policy

- Patch: backward-compatible fixes, doc-aligned runtime cleanups, and internal
  maintenance changes that do not change the CLI contract.
- Minor: backward-compatible command, flag, or JSON-output additions.
- Major: breaking command renames/removals, incompatible flag changes, or
  breaking JSON-contract changes.

## Safe maintenance

- Keep the CLI contract stable around the top-level nouns:
  `doctor`, `profile`, `query`, `activity`, `schema`, `migration`, and `docs`.
- Prefer adding behavior in Rust over reintroducing per-task shell wrappers.
- Keep config migration one-way from legacy `postgres.toml` to canonical
  `config.toml`; do not reintroduce writes to the legacy path.
- Keep the runtime surface focused on SQL, inspection, diagnostics, and
  migration release; do not reintroduce dump, restore, export, or schema-diff
  flows into this CLI.
- Rebuild the relevant `../../scripts/bin/postgres-<os>-<arch>` artifacts after
  any change that affects runtime behavior or operator-facing output, then
  verify through `../../scripts/postgres` rather than `target/` binaries.
- Keep project-local generated state scoped to `projects/postgres/.gitignore`.
- Delete stale pre-`skills/` layout artifacts if they
  reappear, including `skills/postgres/.build/`, `skills/postgres/target/`, `skills/postgres/src/`,
  and root-level Cargo files.
