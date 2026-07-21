# Multi-Repository Bundles

Load this reference when the connected Feature Spec bundle spans repositories.

## App-Compatible Topology

An App worktree task targets one project. Therefore every implementation-
eligible Feature Spec selected for a run must name exactly one affected Git
repository and one target branch. Create one task for that Spec in the matching
App project.

A durable Spec naming several repositories is not executable by this skill.
Return `planning-required`; do not invent several assignments for one source,
pretend one task owns several worktrees, use owner checkouts, or create raw
worktrees. Canonical multi-repository planning uses repo-scoped partial Specs
plus a later repo-owned integration Spec.

## Frontier Selection

Traverse the complete connected bundle so dependency and integration ownership
are known, but claim only the current dependency-ready frontier:

- a Spec with no cross-Spec dependency may be selected;
- a Spec with cross-Spec dependencies is selected only after every upstream
  implementation is authoritatively merged and its named integration proof is
  satisfied;
- blocked downstream and integration Specs are reported as the next frontier
  and receive no task, claim, branch, or PR in this run.

This makes the no-merge boundary explicit. A later `$implement-feature`
invocation starts the integration frontier after a separate owner/GitHub
workflow merges upstream PRs.

## Scheduling

Sort selected assignments by canonical source ref and assignment ID. Fill at
most three live slots. Two assignments may run together only when their
repository-qualified allowed paths do not overlap and no shared operational
resource makes concurrency unsafe. Missing or wildcard scope conflicts.

The same branch name in different repositories is valid. Two selected Specs
may not own the same `(repository_claim,target_branch_name)` pair. Distinct
branches in one repository are allowed, but overlapping paths serialize them.

## Delivery

Each selected assignment produces one real, non-draft, current-head reviewed,
CI-classified, ready-to-merge PR against that repository's discovered default
branch. Record and verify PR identity per assignment. A parent/coordination Spec
owns no task or PR.

The terminal handoff lists this run's ready PRs and the exact blocked next-
frontier source refs. It does not claim that downstream merge-gated Specs were
implemented.
