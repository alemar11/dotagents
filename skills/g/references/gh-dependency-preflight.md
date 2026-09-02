# G to gh Runtime Preflight

This reference owns the scoped, fail-closed readiness gate for G operations
that use the GitHub CLI. It must not install, update, or replace `gh` or an
extension without explicit authorization.

## Load condition

Load this reference:

- before the first provider-facing operation through direct `gh` or
  `<skill-root>/scripts/g` in any focused G workflow;
- before any stack command, in addition to the host and authentication checks;

The gate must finish before the dependent command, GitHub mutation, push,
stack operation, or extension installation.

## Host CLI checks

From the same host that will run the G operation, verify that the GitHub CLI is
available and runnable:

```sh
command -v gh
gh --version
```

Require an executable path and a successful, usable version result. Record the
resolved path and version as diagnostic evidence only. Do not infer CLI
availability from a skill link or an installed extension.

If the executable is missing, cannot run, or returns unusable version output,
stop with a CLI-missing or CLI-runtime blocker. No alternative GitHub provider
transport is defined by this skill; do not install or update the CLI
automatically.

## Authentication checks

For a network-bearing `gh` operation, run the shared diagnostic with scoped
network permission:

```sh
<skill-root>/scripts/g --json doctor
```

Require `checks.gh.authentication_status` to be `verified` before using
`gh` for authenticated provider work. An `unverified` result is inconclusive;
do not diagnose or change credentials from a restricted-network failure.

`doctor` is read-only. Authentication proof does not authorize a GitHub
mutation; retain the mutation authority owned by the focused G workflow.

## gh-stack checks

Before any stack command, run:

```sh
<skill-root>/scripts/g --json stack ensure
```

Require a successful result whose data reports:

- `status` is `ready`;
- `repository` is exactly `github/gh-stack`;
- `version` is present;
- `publisher_verification` is reported as `not-verified`.

The wrapper owns the read-only `gh extension list` check. A missing extension,
conflicting repository, missing version, malformed output, or failed listing is
a blocker. Run `stack ensure --install` only after the user explicitly
authorizes installing `github/gh-stack`; never fall back silently to an
ordinary PR workflow.

## Failure reporting

Report the exact failed layer and observed evidence. Preserve G's typed error
codes when the shared artifact returns them, including `gh_missing`,
`process_spawn_failed`, `extension_missing`, `extension_conflict`, and
`extension_unverified`. Do not classify provider failures from ad hoc stderr
text or claim that credentials are invalid from an inconclusive network result.
