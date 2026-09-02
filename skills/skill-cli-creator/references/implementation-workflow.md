# Embedded CLI Implementation Workflow

Use this reference after the owner, artifact path, and CLI/tool name are clear.

## Choose the Runtime

Before choosing, inspect the user's machine and source material:

```bash
command -v cargo rustc node pnpm npm python3 uv || true
```

Choose the least surprising toolchain:

- Default to Rust when the embedded CLI needs a larger maintained
  implementation and benefits from a complete CLI project under
  `projects/<tool>/`.
- Use TypeScript/Node when the official SDK, auth helper, browser automation
  library, or existing repo tooling is the reason the embedded CLI can be
  better.
- Use Python when the source is data science, local file transforms, notebooks,
  SQLite/CSV/JSON analysis, or Python-heavy admin tooling.
- Use shell for thin orchestration surfaces whose shipped runnable script can
  live entirely in `scripts/`.

Choose direct `scripts/<tool>` for a simple single-file Python or shell CLI.
Choose `projects/<tool>/` only when the implementation needs multiple source
files, build metadata, dependency lockfiles, generated artifacts, compiled
binaries, or dedicated build/install helpers.

Do not pick a language that adds setup friction unless it materially improves
the CLI. If the best language is not installed, either install the missing
toolchain with the user's approval or choose the next-best installed option.

State the choice in one sentence before scaffolding, including the reason and
the installed toolchain you found.

## Command Contract

Sketch the command surface in chat before coding. Include:

- shipped artifact path
- discovery commands
- resolve or ID-lookup commands
- read commands
- write commands
- raw escape hatch
- auth/config choice
- JSON policy
- rebuild behavior needed to restore the shipped artifact in `scripts/`

Before finalizing, confirm that the CLI/tool name is the best runtime noun for
the planned jobs rather than defaulting to the host name out of symmetry.

Build toward a surface where:

- `<artifact-path> --help` exposes the major capabilities.
- `<artifact-path> --version` reports current CLI semver from the single source
  of truth.
- `<artifact-path> --json doctor` verifies config, auth, version, and missing
  setup. API-backed CLIs should also report endpoint reachability; local/offline
  CLIs should report fixture or tool readiness instead.
- `<artifact-path> init ...` stores local config when env-only auth is painful.
- Discovery commands find accounts, projects, workspaces, teams, queues,
  channels, repos, dashboards, or other top-level containers.
- Resolve commands turn names, URLs, slugs, permalinks, customer input, or build
  links into stable IDs.
- Read commands fetch exact objects and list or search collections.
- Write commands do one named action each and accept the narrowest stable
  resource ID.
- `--json` returns stable machine-readable output.
- Repeated jobs get high-level verbs rather than only a generic `request`
  command.
- The raw escape hatch exists but stays secondary to high-level commands.

Document the JSON policy in owning docs or reference files: raw API-shaped
responses versus a CLI-specific envelope, success shape, error shape, and one
example for each command family. Under `--json`, errors must be machine-readable
and must not contain credentials.

Use [agent-cli-patterns.md](agent-cli-patterns.md) for command-shape examples,
pagination, file outputs, write flows, raw escape hatches, and `doctor` output.

## Auth and Config

Support the boring paths first, in this precedence order:

1. Environment variable using the service's standard name, such as
   `GITHUB_TOKEN`.
2. Workspace-local config under the owner-specific `config.toml` for repeated
   local use when env-only auth is painful.
3. `--api-key` or a tool-specific token flag only for explicit one-off tests.

Never print full tokens. `doctor --json` should say whether a token is
available, the auth source category (`flag`, `env`, `config`, provider default,
or missing), and what setup step is missing.

If the CLI can run without network or auth, make that explicit in
`doctor --json`: report fixture/offline mode, whether fixture data was found,
and whether auth is not required for that mode.

For internal web apps sourced from DevTools curls, create sanitized endpoint
notes before implementing:

- resource name
- method/path
- required headers
- auth mechanism
- CSRF behavior
- request body
- response ID fields
- pagination
- errors
- one redacted sample response

Never commit copied cookies, bearer tokens, customer secrets, or full production
payloads. Use screenshots to infer workflow, UI vocabulary, fields, and
confirmation points. Do not treat screenshots as API evidence unless they are
paired with a network request, export, docs page, or fixture.

## Build Workflow

1. Read the source just enough to inventory resources, auth, pagination, IDs,
   media/file flows, rate limits, and dangerous write actions. If docs expose
   OpenAPI, download or inspect it before naming commands. For local/offline
   CLIs, inventory file formats, local tools, path handling, destructive
   operations, and no-network behavior instead of forcing an API-shaped model.
2. Sketch the command list in chat. Keep names short and shell-friendly.
3. Scaffold the CLI inside the resolved owner. Use direct `scripts/<tool>` for
   simple script-native tools; use the two-surface layout only when a
   CLI project is justified: `scripts/` for runtime and `projects/<tool>/` for
   the maintenance-only CLI project.
4. Add or wire the single semver source of truth before the CLI contract is
   considered complete.
5. Expose the shipped runnable artifact under `scripts/` and treat outputs in
   `target/`, `dist/`, virtualenvs, or similar locations as build intermediates.
6. Put tests with the maintained source: owner-root `tests/` for direct
   `scripts/<tool>` implementations, or `projects/<tool>/tests/` when a
   CLI project exists.
7. If the runtime produces a compiled executable, copy, install, or generate
   that executable into `scripts/`. For multi-OS support, install platform
   binaries into `scripts/bin/` and keep `scripts/<tool>` as the launcher.
8. Inspect which generated directories the chosen runtime creates inside the
   CLI project and add or update `projects/<tool>/.gitignore` only for paths
   that should remain uncommitted.
9. Create config only through explicit init/login/configure flows. Do not write
   config during reads or health checks.
10. Smoke test against `<artifact-path>`.
11. Run the shared validation core and the matching validation lane below.

When the source is an existing script or shell history, split the working
invocation into real phases: setup, discovery, download/export,
transform/index, draft, upload, poll, live write. Preserve flags, paths, and
environment variables the user already relies on, then wrap repeatable phases
with stable IDs, bounded JSON, and file outputs.

For raw escape hatches, support read-only calls first. Do not run raw
non-GET/HEAD requests against a live service unless the user asked for that
specific write.

For media, artifact, or presigned upload flows, test each phase separately:
create upload, transfer bytes, poll/read processing status, then attach or
reference the resulting ID.

For fixture-backed prototypes, keep fixtures in a predictable owner-owned path
and make the `scripts/...` surface locate them without requiring direct use of
`projects/<tool>/`.

For log-oriented CLIs, keep deterministic snippet extraction separate from model
interpretation. Prefer a command that emits filenames, line numbers or byte
ranges, matched rules, and short excerpts.

## Validation Lanes

Always run the shared validation core from the shipped artifact path:

- format, typecheck, or build as appropriate for the chosen runtime
- `<artifact-path> --help`
- `<artifact-path> --version`
- `<artifact-path> --json doctor`
- exit-code checks
- no-auth or no-config `doctor`
- at least one safe fixture, dry-run, or read-only end-to-end check

Then add the lane that matches the CLI:

- API-backed CLIs:
  - request builders
  - pagination or cursor handling when applicable
  - error mapping
  - at least one live or fixture-backed read-only API call
  - `doctor --json` endpoint reachability when network access is expected
- Local/offline or shell CLIs:
  - shell syntax or interpreter startup checks
  - quoted-path handling
  - deterministic fixture runs
  - missing-tool diagnostics
  - destructive-path guard checks
  - no-network execution
  - `doctor --json` local tool readiness, fixture availability, or offline mode
- Hybrid CLIs:
  - combine relevant API-backed and local/offline checks without forcing
    irrelevant test placeholders

If a live write is needed for confidence, ask first and make it reversible or
draft-only.

## Runtime Defaults

### Rust

Use established crates instead of custom parsers:

- `clap` for commands and help
- `reqwest` for HTTP
- `serde` / `serde_json` for payloads
- `toml` for small config files
- `anyhow` for CLI-shaped error context

Use `Cargo.toml` as the default semver source of truth and wire `--version` to
that version. Keep `Cargo.toml`, `Cargo.lock`, local caches, and build outputs
inside `projects/<tool>/`. If Rust build outputs or local caches live inside
`projects/<tool>/`, create or update `projects/<tool>/.gitignore` for entries
such as `target/` while keeping the shipped artifact in `scripts/` tracked when
appropriate.

For multi-OS Rust CLIs, add `projects/<tool>/scripts/install-runtime-binary` or
equivalent to build the current/requested target and copy the binary to
`scripts/bin/<tool>-<os>-<arch>`.

### TypeScript/Node

Prefer:

- `commander` or `cac` for commands and help
- native `fetch`, the official SDK, or the user's existing HTTP helper for API
  calls
- `zod` only where external payload validation prevents real breakage
- `tsup`, `tsx`, or `tsc` using the owner's convention

Keep the shipped runnable artifact in `scripts/` and use `projects/<tool>/` for
the full Node CLI project when the tool becomes multi-file. If the Node tool is
bundled or compiled, do not run it from `dist/` during normal execution.

Use `package.json` as the default semver source of truth and wire `--version` to
that version. Keep `package.json`, lockfiles, dependency installs, local caches,
and build outputs inside `projects/<tool>/`.

If Node tooling creates generated state, create or update
`projects/<tool>/.gitignore` for entries such as `node_modules/`, `dist/`,
`.tsbuildinfo`, and runtime-specific cache directories.

### Python

Prefer boring standard-library pieces unless the workflow needs more:

- `argparse` for commands and help, or `typer` when subcommands would otherwise
  get messy
- `urllib.request` / `urllib.parse`, `requests`, or `httpx` for HTTP, matching
  what is installed or used nearby
- `json`, `csv`, `sqlite3`, `pathlib`, and `subprocess` for local files,
  exports, databases, and existing scripts
- `uv` or a virtualenv only when dependencies are actually needed

Keep small Python runnable artifacts directly in `scripts/`. Introduce
`projects/<tool>/` when the implementation grows beyond a simple script or small
module. Do not treat virtualenv paths or external build directories as supported
runtime entrypoints.

When the Python CLI project has packaging metadata, use that manifest as the
semver source of truth; otherwise keep one explicit version constant or file
and wire `--version` to it.

If `projects/<tool>/` exists, keep Python test modules under
`projects/<tool>/tests/` by default. Ignore `.venv/`, `.uv-cache/`,
`__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, and similar local tooling
directories when generated inside the project.

## Host Integration

After the embedded CLI works, update owning skill docs or plugin docs so future
agents:

- execute from `<artifact-path>` during normal runtime usage
- trust `<artifact-path> --version` as the runtime version check
- treat `<artifact-path>` as the shipped runnable artifact rather than a pointer
  to `target/`, `dist/`, or other build directories
- treat `projects/<tool>/` as maintenance-only when it exists
- know the safe read path, intended draft/write path, and raw escape hatch
- have copy-pasteable executable examples that stay on the `<artifact-path>`
  surface
- use bare `<tool> ...` only as optional shorthand after docs define how that
  command becomes executable

Add a `CLI Maintenance` section to owning runtime docs. Require that section to:

- keep normal execution on `<artifact-path>`
- introduce plugin-shared CLI execution context explicitly, such as
  `From the plugin root, run ...`
- tell future agents to open `projects/<tool>/` only when fixing bugs,
  improving performance, rebuilding, or extending the CLI
- direct maintenance changes into `projects/<tool>/` when it exists, then
  rebuild the shipped artifact at `<artifact-path>` and re-verify through that
  artifact
- mention the version source of truth and that shipped CLI changes follow semver
- state that compiled outputs in `target/`, `dist/`, virtualenvs, or similar
  build locations are intermediates, not supported runtime entrypoints
- keep generated-path ignore rules in `projects/<tool>/.gitignore`
- define the bump policy explicitly:
  - major for breaking CLI contract changes
  - minor for backward-compatible new features or meaningful additions
  - patch for backward-compatible bug fixes and corrections
