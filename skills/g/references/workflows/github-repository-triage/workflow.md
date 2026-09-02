# GitHub Repository Triage

Before any shell command that may contact GitHub or a package registry, read
and follow [Network execution](../../network-execution.md).

## Transport

Use authenticated `gh` for provider reads. Use the read-only portfolio scanner
for multiple explicit repositories and direct `gh` for focused single-repository
reads. This workflow never performs GitHub writes; route every write-shaped
request to its owning workflow.

Before the first provider-facing direct `gh` or shared CLI operation, load
[`../../gh-dependency-preflight.md`](../../gh-dependency-preflight.md)
and require its host and authentication checks.


## Role

Triage one or more GitHub repositories. For one repository, inspect its issue
and pull request queues in enough detail to identify blockers, stale items,
review needs, CI needs, and ownership gaps. For multiple explicit
repositories, produce a comparative summary of queue size, CI, release state,
blockers, and next actions. Keep both report shapes URL-first, concise,
read-only, and action-oriented.

Use the `github-stars` workflow for star and list operations. Use the `github-tagger` workflow
when one exact issue must be read to select existing labels or a native issue
type, or when the user explicitly requests repository and issue-corpus analysis
to propose missing taxonomy. Use the `github-issues` workflow when the exact issue
creation, metadata change, comment, relationship, or closure operation is
already decided.

## Multi-Repository Script

Use the `<skill-root>` resolved by the active G entrypoint, then invoke the helper from the installed skill root. Do not
assume the current checkout contains the G source tree.

```bash
<skill-root>/scripts/g portfolio scan --help
<skill-root>/scripts/g --version
<skill-root>/scripts/g --json doctor
```

The script accepts repeated explicit `owner/repo` inputs or a user-supplied
repo file, emits stable JSON success/error envelopes in JSON mode, preserves
per-repository failures, and writes no implicit config.

## Workflow

1. Resolve the repository scope:
   - When the user identifies no repository, use the current repository.
   - When the user identifies one repository, use the detailed queue path.
   - When the user identifies multiple repositories or supplies a repo file,
     require explicit `owner/repo` identities and use the comparative scan.
2. For one repository, confirm context with
   `gh repo view --json nameWithOwner,url`. Gather open issues and PRs, inspect only the items needed for the
   queue question, and group them by blocker, stale item, ready-for-review,
   CI/review need, or follow-up owner.
3. For multiple repositories, run
   `<skill-root>/scripts/g portfolio scan` and summarize queue size,
   blocking CI, release gaps, and next actions per repository. Preserve
   per-repository failures instead of hiding the rest of the scan.
4. When queue work identifies one exact issue that needs content-based label or
   type selection, route it to the `github-tagger` workflow; do not choose metadata from a
   queue summary.
   When the user instead requests a taxonomy proposal, route the exact
   repository and corpus context to that workflow; do not invent new labels from
   the triage summary alone.
5. Do not edit labels, milestones, assignees, titles, comments, releases, or
   workflows from this workflow; route predetermined authorized GitHub issue
   lifecycle mutations to the `github-issues` workflow only after normalizing the handoff to
   `mutation_mode=apply`, the exact repository and issue target, and one
   canonical `issue_operation`. Route an explicit mutation preview with
   `mutation_mode=dry-run` and the same exact target and operation. Pure queue
   reads omit both fields.
6. Route evidence-backed issue disposition questions, including whether an
   issue should close or partial work satisfies its acceptance criteria, to
   the `github-investigation` workflow. Route any authorized resulting lifecycle
   mutation to the `github-issues` workflow.

## References

- `workflows.md`: single- and multi-repository triage workflows.
- `script-summary.md`: `g portfolio scan` command contract.
- `../../options.md`: canonical G invocation fields for routed handoffs.
