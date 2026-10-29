# Command Design

Read when designing or changing the commands of a skill CLI. The required
interface is in [standard](standard.md); this file is how to choose good
commands on top of it.

## Write help for an agent with only the artifact

A future agent sees `scripts/<skill> --help` and a vague task. Top-level help
should answer: what can I list, what exact object can I read, how do I turn a
name or URL into an ID, which commands write, and what is the raw fallback.

## Discover, resolve, read, context

Shape first-pass commands in this order, and offer only the ones the job needs:

1. **Discover** containers: accounts, projects, channels, playlists.
2. **Resolve** human input to a stable ID: a name, a permalink, a PR URL.
3. **Read** one exact object by ID.
4. **Context** around an anchor: nearby messages, the parent thread, log lines.

Once the agent holds an ID, it should not have to search again. Prefer several
narrow commands to one that runs a whole investigation.

## Breadth

Start shallow and make breadth explicit:

```bash
scripts/<skill> --json messages search "topic" --limit 10
scripts/<skill> --json messages search "topic" --limit 50 --all-pages --max-pages 3
```

Return the provider's own pagination fields (`next_cursor`, `offset`) and
document them in `references/cli.md`.

## Files

Downloads and exports write under a caller-given `--out`. The JSON names each
file's path, its size when cheap, its source ID, and the follow-up command.

## Writes

- Draft by default when the product has drafts.
- A command that publishes, deletes, retries, or submits says so in its name
  and help; the skill's `SKILL.md` says it runs only when the user asked.
- A multi-step upload reports creation, transfer, processing, and attachment
  apart, so a partial failure is visible.

## Raw fallback

A `request get <path>` style command is a repair hatch for a missing high-level
command, not the main interface. It still uses configured auth, redaction,
`--json`, and the error shape. A raw write is a live write: do not hide it
behind a debug name.

## Wrapping an existing script

Keep the flags and environment variables callers already rely on, move the
command onto `scripts/<skill>`, and add the standard surface (`--version`,
`--json`, `doctor`, the error shape) around it. Bump the major version if a
caller-visible contract changes.

## Deriving a CLI from an internal API

Keep sanitized evidence of each endpoint: method and path, auth mechanism,
request shape, response IDs, pagination, and errors. Screenshots explain a
workflow, not an API. Never keep copied credentials or private payloads as
fixtures.
