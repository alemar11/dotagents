# Codex CLI Patterns

Use this reference only when designing or changing an embedded CLI's command
surface. It owns command naming, JSON and file transport, pagination, writes,
and raw escape hatches. Ownership, artifact placement, config, cache, and
multi-OS packaging belong to [embedded-cli-layout.md](embedded-cli-layout.md);
runtime choice, implementation, and validation lanes belong to
[implementation-workflow.md](implementation-workflow.md).

Prefer composable discover, resolve, read, context, download, draft, and write
commands over one command that performs an entire investigation.

## Help is interface

Write `--help` for a future Codex thread that only has the shipped artifact in `scripts/...` and a vague task. Each command should have a short description and flags with literal names from the product or API.

Good top-level help should answer:

- What containers can I discover?
- What exact objects can I read?
- What stable IDs can I resolve?
- What files can I download or upload?
- Which write actions exist?
- What is the raw escape hatch?

Treat `--version` as part of that top-level interface, not an afterthought.

## Prefer this command shape

Use product nouns, then verbs:

```bash
<artifact-path> --version
<artifact-path> --json doctor
<artifact-path> --json accounts list
<artifact-path> --json projects list
<artifact-path> --json channels resolve --name codex
<artifact-path> --json messages search "exact phrase"
<artifact-path> --json messages context <message-id> --before 3 --after 3
<artifact-path> --json logs download <build-url> --failed --out ./logs
<artifact-path> --json media upload --file ./image.png
<artifact-path> --json drafts create --body-file draft.json
```

For APIs whose native noun is already strong, direct verbs can be fine:

```bash
<artifact-path> --json social-sets
<artifact-path> --json drafts list --social-set <id>
<artifact-path> --json request get /v2/me
```

The important rule is consistency. Do not mix many styles unless the product vocabulary demands it.

## Runtime surface

Run examples through `<artifact-path>` and keep the command contract stable
across implementation changes. Artifact placement, maintenance-project,
compiled-launcher, and semver rules live in
[embedded-cli-layout.md](embedded-cli-layout.md).

## Working-project config

Use the owner-aligned `config.toml` contract in
[embedded-cli-layout.md](embedded-cli-layout.md). Command design must keep reads
and health checks non-mutating and reserve config writes for explicit
`init`, `login`, `configure`, or migration commands.

## Runtime cache paths

Cache ownership and platform path forms live in
[embedded-cli-layout.md](embedded-cli-layout.md). Command contracts may use a
cache only for disposable, rebuildable runtime artifacts, never user config or
the sole copy of user state.

## Useful shapes from mature CLIs

Prefer these patterns over clever agent-only abstractions:

```bash
# Field-selected structured output: make common reads scriptable.
<artifact-path> issues list --json number,title,url,state
<artifact-path> issues list --json number,title --jq '.[] | select(.state == "open")'

# Human text by default, full API object when requested.
<artifact-path> pods get <name>
<artifact-path> pods get <name> -o json

# Product workflow commands, not just REST nouns.
<artifact-path> logs tail
<artifact-path> webhooks listen --forward-to localhost:4242/webhooks
<artifact-path> webhooks trigger checkout.completed
```

Only implement filtering or templating if the user will actually need it. Stable JSON plus narrow read commands are the baseline.

## Discovery, resolve, read, context

Design first-pass commands in this order:

1. **Discover** broad containers: workspaces, accounts, social sets, repos, projects, channels, queues.
2. **Resolve** human input into IDs: user names, channel names, permalinks, PR URLs, build URLs, customer slugs.
3. **Read** an exact object: issue, event, thread, draft, customer, job, run, media item.
4. **Context** around an anchor when useful: nearby messages, parent thread, surrounding logs, audit history.

Do not force Codex to repeatedly search when it already has a stable ID.

## Text, JSON, files, exit codes

Support human text by default if it helps. Support `--json` everywhere Codex will parse or pipe results.

Version reporting stays separate from `--json`: running `<artifact-path> --version` should print the current CLI semver cleanly, and `doctor --json` should include that same version in its structured diagnostics.

For `--json`:

- emit JSON to stdout only
- send progress and diagnostics to stderr
- keep success and error shapes documented
- redact tokens, cookies, customer secrets, private headers, and unrelated payloads

For downloads and exports:

- write files under a user-provided `--out` path when possible
- in JSON output, return the file path, byte count if cheap, source URL or ID, and follow-up command

For exit codes:

- exit zero when the command succeeded, including an empty result
- exit nonzero for auth failure, invalid input, network failure, parse failure, API error, or incomplete upload/download
- make `doctor --json` usable even when auth is missing; it should report missing auth rather than crashing

## Validation profiles

Always validate the shared core from `<artifact-path>`:

- `--help`
- `--version`
- `--json doctor`
- executable invocation from the resolved `owner root`
- exit codes and at least one safe fixture, dry-run, or read-only end-to-end check
- for launcher-based compiled CLIs, shell syntax checks for the launcher and `file` checks for shipped binaries

Then add the lane that matches the CLI:

- API-backed: auth handling, request builders, pagination or cursor handling when applicable, and at least one live or fixture-backed read-only API call
- local/offline or shell: syntax or interpreter startup checks, quoted-path handling, deterministic fixture runs, missing-tool diagnostics, destructive-path guards, and no-network execution
- hybrid: combine the relevant API-backed and local/offline checks without inventing irrelevant placeholders

## Pagination and breadth

Start shallow by default. Add explicit knobs for breadth:

```bash
<artifact-path> --json messages search "topic" --limit 10
<artifact-path> --json messages search "topic" --limit 50 --all-pages --max-pages 3
<artifact-path> --json drafts list --limit 20 --offset 40
```

Return the provider's real pagination field names, such as `next_cursor`, `next_url`, `offset`, or `page_count`, and document that shape clearly.

## Raw escape hatch

The raw command is a repair hatch, not the main interface.

Good raw commands still use configured auth, base URL, JSON parsing, redaction, status/error handling, and `--json`.

Make reads easy:

```bash
<artifact-path> --json request get /v2/me
```

Treat raw writes as live writes. Do not hide POST/PUT/PATCH/DELETE behind a "debug" command.

## Host pattern

The owning skill docs or plugin docs should teach the path through the embedded tool:

```md
Start with:

<artifact-path> --version
<artifact-path> --json doctor
<artifact-path> --json accounts list

For [common job]:

<artifact-path> --json ...
<artifact-path> --json ...

Rules:

- Prefer the shipped artifact at `<artifact-path>`.
- Check `<artifact-path> --version` when confirming the shipped CLI matches the latest built implementation.
- Use --json when analyzing output.
- Create drafts by default.
- Do not publish/delete/retry/submit unless the user asked.
- Do not inspect `projects/<tool>/` during normal execution.
- Use `request get ...` only when high-level commands are missing.
- Use bare `<tool> ...` only if the docs also define the wrapper, alias, or PATH setup that makes that shorthand executable.
```

Include JSON shape notes only when Codex needs them to choose the next command.

Add a `CLI Maintenance` section in the owning runtime docs for every embedded CLI. That section should say:

- normal runtime work stays on `<artifact-path>`
- `projects/<tool>/` is for bug fixes, performance work, rebuilds, and feature additions
- shipped CLI changes must update the implementation, rebuild the shipped artifact at `<artifact-path>` or platform binaries under `scripts/bin/`, and re-run `--help`, `--version`, and `--json doctor`
- multi-OS compiled CLIs keep `<artifact-path>` as the stable launcher and document rebuild commands such as `projects/<tool>/scripts/install-runtime-binary`
- compiled outputs in `target/`, `dist/`, virtualenvs, or similar paths are build intermediates rather than supported runtime entrypoints
- project-local generated state should be ignored through `projects/<tool>/.gitignore`
- the CLI follows semver from one declared version source of truth
- when a bundled skill points to a plugin-shared CLI, introduce the execution context explicitly before the command, such as `From the plugin root, run ...`
