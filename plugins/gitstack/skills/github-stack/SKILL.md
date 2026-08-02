---
name: github-stack
description: Manage stacked branches and dependent pull requests through the GitStack stack CLI. Use when the user asks to create, inspect, link, rebase, synchronize, navigate, restructure, or merge a stack of PRs.
---

# GitHub Stack

Before any shell command that may contact GitHub or a package registry, read
and follow [Network execution](../../references/network-execution.md).
Connector calls and local-only commands do not use shell escalation.

## Role

Use this skill for stack-level work through `<plugin-root>/scripts/gitstack
stack ...`. The wrapper delegates stack state, branch ordering, PR linking,
rebasing, synchronization, and merge behavior to the official
`github/gh-stack` extension while enforcing non-interactive invocation.

Resolve `<plugin-root>` as two directories above this `SKILL.md`. Read
[`../../references/stack-cli.md`](../../references/stack-cli.md) before using
the command surface and load [`references/workflows.md`](references/workflows.md)
for the requested lifecycle operation.

## Boundaries

- Use `$gitstack:send` for publishing or updating one PR, including its title,
  body, closing issue references, draft state, push ownership, and Codex review
  receipt.
- `send` may invoke `stack link` for one target/current PR pair. Do not replace
  that flow with `stack submit`.
- Use this skill when the user explicitly asks for stack-wide publication,
  navigation, rebase, sync, restructuring, merge, or recovery.
- Do not silently turn a single-PR request into a stack-wide operation.
- `stack submit` is an explicit multi-branch publication mode. It does not
  inherit `send`'s issue-linkage, body, draft-preservation, or review-receipt
  contract; route those responsibilities separately when required.

## Readiness and authorization

1. Resolve the repository and plugin root.
2. Run `gitstack --json doctor` and
   `gitstack --json stack ensure` before stack operations.
3. If the extension is missing, stop and report the prerequisite. Run
   `gitstack --json stack ensure --install` only after the user explicitly
   authorizes installing `github/gh-stack`.
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
- Use `view --json` before and after consequential operations and preserve the
  exact branch/PR state in the handoff.
- For conflicts, resolve and stage files, then use `rebase --continue`; use
  `rebase --abort` to restore the pre-rebase state.
- After a lower PR merges, use `sync` to fetch, reconcile, rebase, push, and
  update stack state. Use `--prune` only when local merged branches should be
  removed.
- Merge stacks only with `stack merge ... --yes`; do not substitute
  `gh pr merge`.

## Routing

| Request | Owner |
| --- | --- |
| One branch/PR publication or update | `$gitstack:send` |
| Link one new child PR to one existing target PR | `$gitstack:send` |
| Inspect or navigate an existing stack | `$gitstack:github-stack` |
| Publish all active stack branches | `$gitstack:github-stack` with explicit `stack submit --auto` |
| Rebase, sync, push, restructure, unstack, or merge a stack | `$gitstack:github-stack` |

For detailed procedures and failure recovery, read
[`references/workflows.md`](references/workflows.md). For the typed wrapper
contract, read [`../../references/stack-cli.md`](../../references/stack-cli.md).
