# Stack CLI Contract

The plugin-shared artifact at `<plugin-root>/scripts/gitstack` exposes a thin
boundary around the official `github/gh-stack` GitHub CLI extension. It does
not reimplement stack state, branch ordering, PR linking, rebasing, or merge
logic; those remain owned by `gh-stack`.

## Readiness and installation

```bash
<plugin-root>/scripts/gitstack --json doctor
<plugin-root>/scripts/gitstack --json stack ensure
<plugin-root>/scripts/gitstack --json stack ensure --install
```

`stack ensure` is read-only. Only `stack ensure --install` may run:

```bash
gh extension install github/gh-stack
```

The wrapper checks `gh extension list` first and accepts only an extension entry
whose repository is exactly `github/gh-stack`. An installed entry reports
`publisher_verification: "not-verified"`: GitHub CLI extensions are executable
code from the publisher and are not a GitHub endorsement. The wrapper does not
upgrade an existing installation, replace a conflicting extension, create
GitStack configuration, or install an agent skill. Installation uses the latest
upstream version and is subject to the network and authorization rules in
[`network-execution.md`](network-execution.md).

## Stack commands

The typed command surface is:

```text
init add checkout link push submit sync rebase view merge unstack
up down top bottom trunk
```

Arguments and flags after the typed command are forwarded to `gh stack`. The
wrapper sets `GH_PAGER=cat`, `GIT_PAGER=cat`, `PAGER=cat`, and
`GIT_TERMINAL_PROMPT=0`, closes stdin, and rejects interactive paths:

- `modify`, `switch`, `alias`, and `feedback`;
- branch, stack, PR, or URL prompts with missing positional input;
- `submit` without `--auto`;
- `merge` without an explicit target and `--yes`;
- remote `unstack` without an explicit target. Use `unstack --local` to remove
  the active local tracking entry without a remote operation.

The raw escape hatch is available for non-interactive upstream commands:

```bash
<plugin-root>/scripts/gitstack --json stack raw -- view
```

Put the wrapper's `--json` before the raw `--` separator. Arguments after the
separator are forwarded verbatim to the upstream command. Raw is a repair path,
not a second primary API. Raw writes remain live writes and still require
caller authorization.

## JSON and errors

Use `--json` before or after the command. Successful output uses the normal
GitStack envelope:

```json
{
  "ok": true,
  "version": "8.2.1",
  "command": ["stack", "view"],
  "data": {}
}
```

`stack view` asks the upstream command for JSON and returns the parsed object.
Other successful commands return `{ "stdout": "...", "stderr": "..." }`.
`stack ensure` reports the detected repository, version, and publisher
verification state. Wrapper failures use stable GitStack error codes; upstream
command failures preserve the upstream exit code and expose only safe command,
exit-code, and reason details in the JSON error envelope.

## Maintenance

Normal execution uses `<plugin-root>/scripts/gitstack`. The implementation and
tests live under `projects/gitstack/`; rebuild the shipped artifact with
`projects/gitstack/scripts/build-artifact`, then re-run `--help`, `--version`,
`--json doctor`, and `--json stack ensure`. Do not run maintenance modules as
the normal runtime and do not install `github/gh-stack` during builds or tests.
