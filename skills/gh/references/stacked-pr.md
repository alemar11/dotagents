# Stacked PR extension

Use the official [github/gh-stack](https://github.com/github/gh-stack) extension
directly for stacked branches and dependent PRs. Stack tracking, ordering,
rebasing, and merge behavior belong to the extension. Consult
`gh stack <command> --help` for the installed version's arguments and behavior.

Use `$yeet` for publishing or updating one PR. An explicit parent/child link
or stack-wide publication is a separate operation; never infer a stack or
substitute `gh stack submit` for single-PR publication.

## Install and verify

Check `gh` availability and existing authentication as described in the main
skill. Inspect `gh extension list`; the `stack` command must be provided by
`github/gh-stack`. Do not silently replace a same-name extension from another
repository. If identity cannot be verified, resolve that prerequisite before use.

When installation is requested and the extension is missing:

```sh
gh extension install github/gh-stack
```

This installs an executable extension for the current user, not a repository
skill. It requires GitHub CLI and Git; report missing host prerequisites instead
of installing them incidentally. Do not install the extension for unrelated
GitHub work. Update only when requested, preserving deliberate version pins:

```sh
gh extension upgrade stack
```

After installation or update, verify the repository in `gh extension list`
and run `gh stack --version` and `gh stack --help`. Do not create branches or
publish PRs as an installation test.

## Select the operation

Resolve the repository, current branch, worktree changes, and intended stack
before a mutation. For locally tracked stacks, inspect `gh stack view --json`.
Missing local tracking is not proof that no stack exists on GitHub.

Use explicit targets and non-interactive flags. For unattended execution,
disable pagers and Git credential prompts with `GH_PAGER=cat`, `GIT_PAGER=cat`,
`PAGER=cat`, and `GIT_TERMINAL_PROMPT=0`, and close stdin. Do not depend on prompts
to confirm mutation scope; existing user authorization determines that scope.
Do not invoke interactive pickers such as `switch` or `modify` unattended.

These are alternatives selected by the request, not a sequence to run in full:

| Request | Command |
| --- | --- |
| Create or adopt local branches, bottom to top | `gh stack init --base main api-layer ui-layer` |
| Add a named layer | `gh stack add next-layer` |
| Inspect the current local stack | `gh stack view --json` |
| Adopt or check out a specific stack | `gh stack checkout <stack-number-or-pr-url>` |
| Link existing PRs, bottom to top | `gh stack link <bottom-pr-url> <top-pr-url>` |
| Publish the full stack | `gh stack submit --auto` |
| Rebase layers above the current branch | `gh stack rebase --upstack` |
| Push stack branches | `gh stack push` |
| Reconcile after trunk changes or a lower PR merge | `gh stack sync` |
| Merge a verified target | `gh stack merge <stack-or-pr-number> --yes` |
| Remove only current local tracking | `gh stack unstack --local` |
| Remove a specified remote grouping | `gh stack unstack <stack-number>` |

Substitute the intended trunk, branches, and verified identities. Keep staging
and committing explicit; `add -A` or `-u` can include work beyond the intended
change. After editing and committing a lower layer, rebase its dependents before
returning to the higher layer when that rebase is within the requested scope.

## Mutation boundaries

For linking existing PRs, prefer exact PR URLs. Branch arguments can push
branches and create PRs. Before linking, verify repositories, full heads, bases,
and bottom-to-top order. Linking does not require local stack tracking; do not
adopt a remote stack locally unless that is needed for the requested work.

`submit --auto` pushes branches and creates or updates multiple PRs. New PRs
default to drafts; add `--open` only when marking PRs ready is requested.
Stack publication does not inherit Yeet's issue-linkage, body, or draft-state
verification. Preserve those requirements separately when applicable.

`sync` can fetch, rebase, push, and update the remote stack. It is not read-only
inspection. Use `--prune` only when deleting merged local branches is intended.
If local and remote definitions diverge, report the conflict rather than
discarding tracking or recreating the remote stack automatically.

Before merging, resolve whether the numeric target identifies a stack or a PR;
the extension tries a stack number first. Confirm the included PRs and the
requested or established merge method, passing `--squash`, `--rebase`, or
`--merge` accordingly. A PR target includes its lower dependencies. Repository
rules and merge queues still govern completion; use `gh stack merge` for stack
merges rather than substituting `gh pr merge`.

Remote `unstack` changes GitHub grouping; `--local` changes only local tracking.
Neither deletes the underlying PRs or branches. Read back which PRs remain
stacked, since GitHub may retain those queued for merge or with auto-merge enabled.

## Recovery and readback

For rebase conflicts, inspect the reported state, resolve and stage the intended
files, then use `gh stack rebase --continue`. Use `gh stack rebase --abort` when
restoring the pre-rebase state is appropriate. Preserve unrelated work and do
not edit extension-owned tracking or recovery files manually.

After consequential operations, verify the resulting local branches and remote
PR heads, bases, ordering, and merge state as applicable. Use `view --json` for
local tracking and authenticated `gh` reads for remote state. A remote-only link
may not appear in the current branch's local view; do not repeat it on that basis.
If the installed CLI cannot expose the required relationship, report that
verification limit rather than claiming success from the mutation receipt alone.

Commands can fail after partial effects. Inspect exit status and diagnostics,
reconcile local and remote state, and only then decide whether to retry. Do not
repeat a mutation just to obtain more diagnostic output.
