# Managed Multi-Repository App Workspace

Load this reference when one Feature Spec affects more than one Git repository
or the bundle contains partial and integration Feature Specs, even when each
individual Spec is single-repository.

## Ownership

The root owns the shared claim, dependency graph, scheduling, typed run state,
and final handoff. Each repository retains its code, project memory, validation, branch,
commit, pull request, and tracker artifacts. Repository topology is bundle or
Project Memory data, never an App option.

## Managed Task Workspace

Create one visible App task per Feature Spec, not per repository. Registration
creates one `deliveries[]` entry per affected repository. Before work, prove
that its App-managed workspace exposes a distinct isolated checkout for every
required repository delivery, then atomically record the complete delivery-keyed map with repository
id, checkout path, shared target branch, Git top-level, baseline revision, and
isolation proof.

Every delivery in every repository participates in the same portfolio-level
baseline CAS before implementation. One missing or invalid validation row
rejects all repositories; partial repository acceptance cannot create a Goal or
grant mutation authority.

If the checkout map is incomplete, abort as blocked before edits. Do not use
owner checkouts, raw helper worktrees, branch rotation, or one task per child
repository as fallback.

## Scheduling

One multi-repository Spec consumes one of the three run-wide task slots. Its
affected scope is the union of repository-qualified allowed paths. Two Specs
may run together only when those unions are disjoint and no dependency edge
connects them. Missing or wildcard scopes conflict. Cross-Spec dependencies
must be verified merged before dispatch.

Independently of path scheduling, every portfolio-wide `(repository,
target_branch_name)` pair across implementation-eligible Specs has exactly one
Feature Spec owner. Exclude coordination-only parent/global artifacts because
they create no task or App-managed worktree. The same branch name in different
repositories is valid. Two executable Specs in the same repository may not
share it, even when their paths are disjoint or dependencies serialize them;
reject that bundle as `planning-required` before CLAIM and never rename,
force-bind, or schedule around the collision.

Every multi-repository bundle contains exactly one distinct repo-owned
integration Feature Spec whose dependencies cover all implementation partials.
After those upstream merges, dispatch its own visible App task. That task owns a
bounded path change in its repository plus the named cross-repository proof and
must produce a real PR; a validation-only or no-op integration task is
incompatible intake. Its target branch must equal
`<ordinary_target_branch_name>-integration`, derived from the resolved ordinary
partial branch in the same repository (the default example is
`feature/<feature_slug>-integration`), so the new App-managed worktree never
reuses the first task's bound branch. A knowledge delta, when present, belongs only to this
integration Spec's final issue and does not control whether the integration Spec
exists.

## Delivery And Closeout

Each task uses its Feature Spec's target branch name in every delivery. Each
delivery produces one real, non-draft, reviewed PR with CI passed when configured,
ready-to-merge PR based on that repository's
discovered default branch. Delivery observations and revision gates are keyed
independently; task-set validation and integration bind the complete canonical
delivery revision set.
It runs named cross-repository integration gates before preparing tracker
closeout. Each implementation-eligible partial is armed in its own designated
default-branch closeout PR. If the bundle has an accepted hosted parent/global
Feature Spec, the final integration partial's default-branch PR also arms that
parent's fully qualified ref after every partial gate passes. After task seal
the root records one terminal handoff containing
every delivery PR and hosted Spec closeout vehicle. After all task handoffs it
independently verifies the portfolio, completes the root Goal, releases, and
archives. A separate GitHub workflow owns merges and post-merge closure.
