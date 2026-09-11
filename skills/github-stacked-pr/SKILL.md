---
name: github-stacked-pr
description: "Manage stacked Git branches and dependent pull requests through the stack CLI wrapper."
---

# GitHub Stacked PR

Before remote `git`, `gh`, registry, or skill helper commands that contact the
network, use the runtime's narrowest network-enabled context for that command
family. Keep local-only git sandboxed. Verify `gh` is runnable (`command -v gh`,
`gh --version`) and authentication with:

```sh
gh auth status --active --hostname github.com --json hosts \
  --jq '.hosts["github.com"] | map(select(.active == true) | {state, scopes})'
```

Require exactly one active account with `state=success`. Treat
restricted-environment network failures as inconclusive. Do not install or
refresh `gh` without explicit authorization. Network permission is not
mutation authority.

## Role

Use this skill for stack-level work through `<skill-root>/scripts/stack --json ...`.
Resolve `<skill-root>` as the absolute path of the directory containing this
`SKILL.md`. The wrapper delegates stack state, branch ordering, PR linking,
rebasing, synchronization, and merge behavior to the official
`github/gh-stack` extension while enforcing non-interactive invocation.

Read [references/stack-cli.md](references/stack-cli.md) before using the
command surface and [references/workflows.md](references/workflows.md) for the
requested lifecycle operation. Read
[references/states.md](references/states.md) before interpreting `ensure`
extension-status values.

## Boundaries

- Use `$yeet` for publishing or updating one PR, including its title, body,
  closing issue references, draft state, and push ownership.
- Use this skill for an explicit parent/child link, even when the PRs were just
  published by `$yeet`. `yeet` does not infer or invoke `stack link`; do not
  replace this explicit relationship flow with `stack submit`.
- Use this skill when the user explicitly asks for stack-wide publication,
  navigation, rebase, sync, restructuring, merge, or recovery.
- Do not silently turn a single-PR request into a stack-wide operation.
- `stack submit` is an explicit multi-branch publication mode. It does not
  inherit `yeet`'s issue-linkage, body, or draft-preservation contract; route
  those responsibilities separately when required.

## Readiness and authorization

1. Resolve the repository and `<skill-root>`.
2. Complete the `gh` host and authentication checks above.
3. Run `<skill-root>/scripts/stack --json ensure` and require `status=ready`,
   repository `github/gh-stack`, a present version, and reported
   `publisher_verification`. If the extension is missing, stop and report the
   prerequisite. Run `<skill-root>/scripts/stack --json ensure --install` only after
   the user explicitly authorizes installing `github/gh-stack`.
4. Never fall back silently to an ordinary unstacked PR workflow when stack
   state is unavailable, ambiguous, or unsupported.
5. Treat `push`, `submit`, `sync`, `rebase`, `merge`, and remote `unstack` as
   separate mutations. Explain their scope before executing them.

## Non-interactive rules

Always supply the positional arguments and flags required by the wrapper:

- `init`, `add`, and `checkout` require an explicit branch, stack, PR, or URL;
- `view` requires `--json`;
- `submit` requires `--auto`;
- `merge` requires an explicit target and `--yes`;
- remote `unstack` requires an explicit target; use `unstack --local` for local
  tracking only.

Never invoke blocked interactive commands such as `modify`, `switch`, `alias`,
or `feedback`. Do not use the raw escape hatch unless the typed surface cannot
express an explicitly requested non-interactive operation.

## Core operating rules

- Model the stack from trunk upward: foundational changes belong in lower
  branches and dependent changes in higher branches.
- Keep each branch a cohesive, independently reviewable unit.
- When changing a lower or middle branch, work on that branch, commit there,
  then run `rebase --upstack` before returning to the higher branch.
- Use `view --json` for a locally tracked stack; remote-only links use the
  relationship readback in `references/workflows.md`. Verify before and after
  consequential operations and preserve exact branch/PR state in the handoff.
- For conflicts, resolve and stage files, then use `rebase --continue`; use
  `rebase --abort` to restore the pre-rebase state.
- After a lower PR merges, use `sync` to fetch, reconcile, rebase, push, and
  update stack state. Use `--prune` only when local merged branches should be
  removed.
- Merge stacks only with `stack merge ... --yes`; do not substitute
  `gh pr merge`.
