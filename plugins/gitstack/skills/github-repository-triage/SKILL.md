---
name: github-repository-triage
description: Triage GitHub repositories read-only. Use for detailed issue and pull request queues in one repository or explicit multi-repository summaries of blockers, CI, releases, and next actions; route mutations to $gitstack:github-issues.
---

# GitHub Repository Triage

## Transport

Prefer the required GitHub connector for supported remote reads. Use the
read-only portfolio scanner for multiple explicit repositories, and use direct
`gh` reads only for connector gaps after authentication and access
verification. Report every fallback. This skill never performs GitHub writes
or automatically falls back between write transports; route every
write-shaped request to its owning skill.


## Role

Triage one or more GitHub repositories. For one repository, inspect its issue
and pull request queues in enough detail to identify blockers, stale items,
review needs, CI needs, and ownership gaps. For multiple explicit
repositories, produce a comparative summary of queue size, CI, release state,
blockers, and next actions. Keep both report shapes URL-first, concise,
read-only, and action-oriented.

Use `$gitstack:github-stars` for star and list operations. Use
`$gitstack:github-issues` for issue creation, issue type changes, comments,
labels, parent/sub-issue relationships, and closure.

## Multi-Repository Script

Resolve `<plugin-root>` as two directories above the directory containing this
`SKILL.md`, then invoke the helper from the installed plugin root. Do not
assume the current checkout contains the GitStack source tree.

```bash
<plugin-root>/scripts/gitstack portfolio scan --help
<plugin-root>/scripts/gitstack --version
<plugin-root>/scripts/gitstack --json doctor
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
2. For one repository, confirm context with the connector, or use
   `gh repo view --json nameWithOwner,url` when local context or fallback is
   needed. Gather open issues and PRs, inspect only the items needed for the
   queue question, and group them by blocker, stale item, ready-for-review,
   CI/review need, or follow-up owner.
3. For multiple repositories, run
   `<plugin-root>/scripts/gitstack portfolio scan` and summarize queue size,
   blocking CI, release gaps, and next actions per repository. Preserve
   per-repository failures instead of hiding the rest of the scan.
4. Do not edit labels, milestones, assignees, titles, comments, releases, or
   workflows from this
   skill; route authorized GitHub issue lifecycle mutations to
   `$gitstack:github-issues` only after normalizing the handoff to
   `mutation_mode=apply`, the exact repository and issue target, and one
   canonical `issue_operation`. Route an explicit mutation preview with
   `mutation_mode=dry-run` and the same exact target and operation. Pure queue
   reads omit both fields.
5. Route evidence-backed issue disposition questions, including whether an
   issue should close or partial work satisfies its acceptance criteria, to
   `$gitstack:github-investigation`. Route any authorized resulting lifecycle
   mutation to `$gitstack:github-issues`.

## References

- `references/workflows.md`: single- and multi-repository triage workflows.
- `references/script-summary.md`: `gitstack portfolio scan` command contract.
- `../../references/options.md`: canonical GitStack invocation fields for routed handoffs.
