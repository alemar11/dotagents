# Dependencies and PR integration

Read when contributions need combining, units have prerequisites, a stack or
external inputs, or parent/base changes affect existing work.
The orchestrator owns topology and acceptance; workers perform integration and
validation in their assigned branches.

## Grouping and prerequisites

Group coupled steps into useful PRs; independent contributions can run in parallel.
Choose separate PRs for independent outcomes, stacks for actual branch dependencies,
or contribution branches feeding one integration PR for a coupled outcome.
Sequential landing alone does not imply stacked PRs. Name the integration target
and assigned writer before dispatching contributions that need combining.

For broad mechanical changes that cannot be split into independently passing
outcomes, consider expand–migrate–contract: introduce the compatible new form,
migrate consumers in bounded groups, then remove the old form after verifying
no consumers remain. If intermediate contributions cannot pass independently,
use one integration branch and establish correctness on the assembled result
before publication as ready. Define each contribution's applicable checks and
which checks require assembly in its assignment. A validated contribution passes
those applicable checks and reports the deferred checks and any observed failures
that depend on missing contributions; it does not establish combined correctness.
Unrelated failures still require correction. Repository-required gates remain
binding, and all required assembled checks must pass before the PR is ready.

Verify prerequisite behavior in the intended base or an exact validated candidate
before dependent work consumes it. A closed issue, completed task or planning
order is not prerequisite proof. Unselected missing prerequisites block affected
work without authorizing implementation. Explicit merge/deployment requirements
gate only their declared activity; they do not delay PR readiness unless that
evidence is explicitly part of its acceptance boundary.

## External prerequisites

Select one repository and return other scope to the caller; resolve an unclear
target before dispatch. External repositories are read-only context, never
additional implementation or worker targets.

Use the supplied contract and acceptance criteria to decide what can proceed.
An agreed interface may permit local implementation and fixture tests without a
provider candidate. Require real interaction only when readiness explicitly
calls for it; fixtures do not prove live compatibility. Keep later merge or
rollout conditions separate from PR readiness.

For required integration, consume an identifiable revision and usable artifact,
package or environment; a PR link alone is insufficient, and another repository's
branch is not a local Git base. If inputs are missing, finish independent work
and report the missing capability, preserved result and evidence needed to resume.
Do not invent provider behavior or poll indefinitely; ongoing monitoring requires
a caller request. On resume, recheck changed inputs and invalidate affected
evidence while preserving unrelated results.

## Integration assignment

Assign integration to a regular worker; it is an assignment, not a separate
permanent role. Reuse a finished worker/worktree when safe under
[workers.md](workers.md#serial-reuse-and-concurrent-work). Supply the target
repository, delivery branch/base, pinned contribution commits with their
validation evidence and deferred assembly checks, source contracts, combined
acceptance checks and intended PR. Make those exact commits
available in the integration checkout before combining them.

The assigned worker integrates the pinned commits into its owned delivery branch,
resolves conflicts without dropping either contribution's requirements, and runs
the affected tests and assembled-outcome checks on the combined result. A clean
Git merge or separate green worker tests do not establish combined correctness.
Material requirement conflicts return to the orchestrator for resolution.

The integration worker runs Deliver's single review pass on the assembled
candidate and verifies scoped fixes before readiness.
The worker publishes or updates the intended integration PR and completes required
CI and readiness under Deliver. Return source-to-result commit evidence with the
normal worker result; the orchestrator verifies contribution coverage and accepts
the combined outcome. Changed inputs invalidate affected integration evidence.

Do not mutate contribution branches owned by other workers, land PRs, or write
the repository's default/release branches as part of integration. If the target
is an existing PR branch, reconcile its writer before reassignment. Preserve
contribution branches and worktrees; integration does not authorize their cleanup.

## Source references through integration and stacks

Apply the entrypoint's [source references](../SKILL.md#source-references) rule.
An integration PR may carry closing references for selected issues whose full
outcomes it assembles, including commit-only contributions. Contribution PRs
that only implement part of an issue use ordinary links.

For stacks, assess completion against the actual PR base and contributed scope;
ancestor work alone does not justify another closing reference. Do not mark a
parent spec for closure when its completion is spread across PRs and no one PR
completes the whole scope. Use ordinary links in that case and report the
remaining closure handoff. Closing keywords on a non-default-base PR do not
establish automatic closure; report that limitation without retargeting or
merging the PR. Integration and stacks do not extend delivery beyond verified
ready PRs or authorize direct issue closure.

## Stacks and parent changes

The orchestrator may choose standalone or stacked PRs. For a stack, identify each
actual parent branch and full commit, PR base and landing order. Use G's stack
workflow only after establishing that it supports the intended topology; do not
invent dependencies or create branches to probe capability. Each child has its
own branch and PR and consumes the known parent candidate. Serial children may
reuse their worker's worktree under [workers.md](workers.md#serial-reuse-and-concurrent-work);
concurrently active parent/child assignments require separate workers and worktrees.

Parent changes invalidate affected child validation. Stop affected writers before
operations that rewrite their branches; assign one actor the bounded operation,
then update descendants in dependency order and rerun invalidated checks. Verify
actual ancestry, PR bases and current HEADs after publication. Do not allow a
compound stack operation to push another worker's unvalidated changes.

When changes interact, verify the selected assembled outcome at the current
commit combination before reporting delivery. Apply Deliver's candidate review
to each final PR delta; stacking adds no extra review round. Partial/draft/pending contributions remain incomplete;
ready stacked PRs do not mean their parents have merged.
