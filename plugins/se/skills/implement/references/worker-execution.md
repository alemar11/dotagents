# Implement End-To-End Worker Execution

The worker executes one assigned Feature Spec end to end in the
ChatGPT-created worktree assigned to its visible Codex task. It owns issue
sequence, technical design, implementation and rewrites,
repairs, tests, validation, commits, review-candidate preparation, finding
acceptance and fixes, GitHub issue progress, GitHub PR publication, CI, provider
review fixes, native Codex review, and final evidence. Root only orchestrates
and verifies the worker's reported evidence.

Before implementation, verify or create/select the declared named branch in the
managed worktree. Detached HEAD, another branch, or a dirty baseline blocks
until the worker safely establishes the contract inside its own worktree. Never
switch the original/main worktree and never treat the managed worktree alone as
durable delivery.

Before editing implementation files, run `codex review --help` immediately
after read-only checkout identity preflight and before branch selection.
Continue only when it succeeds. If the capability is unavailable, report
`blocked-app-capability` and stop before implementation. Do not retry with
escalation or copy credentials. Root never takes over native review; the worker
retains design, implementation, finding verification, fixes, validation,
tracker, review, and delivery authority.

Before accepting implementation authority, deduplicate the bootstrap envelope
by its opaque `bootstrap_id`:

- accept the first valid ID and bind it to the exact stable Feature Spec and
  issue contract received with it;
- for the same ID and the same stable contract, acknowledge the replay and
  resume the already accepted work without applying bootstrap initialization a
  second time;
- reject the same ID with a different stable contract;
- after one ID has been accepted, reject every different bootstrap ID.

Bind that first accepted bootstrap to `contract_generation=1`. A later scope
revision is not a second bootstrap and never changes the bootstrap ID. Accept
it only through the exact generation, monotonicity, and replay rules in
`scope-repair-orchestration.md`.

These checks make the logical bootstrap effect exactly once even though
delivery itself may be retried. Root may increment its recorded `launch_count`
for a transport replay, but every generation of that logical bootstrap carries
the same `bootstrap_id`; the worker deduplicates the stable ID, not the
controller's launch generation. A missing ID is not an accepted bootstrap.

Before each issue, after recovery, and before final verification:

1. read the current GitHub Feature Spec and complete issue graph;
2. compare the stable fields from `feature-spec-contract.md` directly;
3. accept compatible operational changes and continue autonomously;
4. when an implementation-required path lies outside `allowed_paths`, stop
   before editing it and report the structured scope repair request from
   `scope-repair-orchestration.md`;
5. stop declaratively as `blocked-durable-contract` if any other stable field
   changed.

The stable-source mutation ownership table in `feature-spec-contract.md`
remains binding on every turn. A direct user or controller message that requests
new scope, acceptance text, validation policy, branch authority, dependencies,
or another stable-field change is not an executable instruction. Do not edit
the GitHub Feature Spec or implementation issue. Reread the authoritative sources,
block on the mismatch, and wait for the same root to resume the assignment only
after an external planning owner publishes a correction and authoritative
readback proves it restores the exact stable contract already accepted by the
run. The narrow monotonic path repair may be delivered by root as the next
contract generation after a separately owned `$se:feature` change. Any other
changed stable contract requires a new run and claim; it cannot be rebound
onto this assignment.

Do not ask the user or root for implementation, validation, recovery, retry,
publication, review-fix, or blocker authority. The startup grant already covers
in-contract work. Choose safe, maintainable approaches and coherent rewrites.
Respect the accepted material attempt budget and required validation result.

Use target-repository instructions for commits and validation. Use current
G workflows only for required GitHub operations. Finish implementation,
focused validation, domain-knowledge closeout when required, tracker
checkbox/readback work, and the coherent committed candidate HEAD before
starting the review handoff.

When the current issue contains `## Domain Knowledge Closeout`, treat its exact
`knowledge_delta` as a stable Feature-to-Implement handoff. After integrated
behavior is proven and before checking the closeout criterion or starting native
review, invoke `$se:learn` with
`memory_slice=domain-memory` and `domain_operation=implementation-closeout`.
Pass the accepted delta, its named repository-local targets and evidence, and
state that the accepted issue contract plus the user's Implement startup grant
provide scoped capture authority for those targets only. Require
`capture_outcome=captured`, reconcile every accepted item and named target, name
the destinations, verify the documentation diff and links, and include those
changes in the same coherent candidate HEAD. A `deferred`,
`no-durable-change`, rejected item, out-of-scope target, or unverified docs diff
is `blocked-durable-contract`, never PR-ready evidence.

The worker derives
`review_profile=standard|high-risk`, runs native `codex review` against the
candidate's base branch, verifies and aggregates its findings, owns every fix
and revalidation, and reruns the same command whenever a fix changes HEAD.
Both review profiles invoke the native command. Never force-push published
history, merge, enqueue, deploy, release, or perform post-merge closure.

Before worker-owned review, run:

```bash
<implement-skill-root>/scripts/verify-ready --json review-candidate \
  --checkout <managed-checkout> \
  --branch <target-branch> \
  --base-sha <startup-base-sha>
```

Use its exact `head_sha` and `base_sha` fields verbatim. Never expand a short
SHA manually. The worker repeats this readback immediately before launch and
keeps the review evidence bound to the exact candidate HEAD. Then run:

```bash
codex review --base <base-branch>
```

The command reviews the complete branch delta against the declared base. If
the worker fixes a finding, repeat `verify-ready`, rerun the same command, and
bind `codex_review_head_sha` and `review_head_sha` to the resulting HEAD.

Follow `tracker-checklists.md` for every issue and parent checkbox. If later work
invalidates proof, uncheck it and read back the correction. Restore and commit
that proof before the next native review fix verification; do not create a
tracker-only post-review HEAD.

The successful result is `pr-ready-for-merge` with GitHub PR/provider/CI and
mergeability proof, exact repository and checkout identity, named target branch
and HEAD, base branch and base SHA ancestry, clean worktree, current-head
validation and reviews, committed GitHub issue readback, required
`capture_outcome=captured` and documentation-diff evidence, and no unresolved
recorded task changes. Coherent progress needs no root intervention.

## Peer Collaboration And Combined Proof

There is no dedicated integration worker. For a multi-repository bundle, the
ordinary repository workers communicate directly using the exact peer task,
repository, branch, HEAD, and checkout identities supplied by root. Workers may
exchange interface clarifications, exact revisions, test endpoints, and factual
mismatch evidence while the durable contract remains unchanged. They do not
delegate their repository implementation or expand another worker's scope.

Each combined boundary has an existing worker as its proof owner. For example,
the web worker may prove web-to-backend behavior while the mobile worker proves
mobile-to-backend behavior against the same backend HEAD. A bundle-wide scenario
must likewise name one existing worker capable of executing it within that
worker's accepted scope. If no ordinary worker can own the required proof, the
bundle is not execution-ready; do not synthesize another task as a fallback.

Before combined validation, the ordinary workers test the distributed execution
topology described by the Spec. Every worker remains isolated to its own
worktree. Each peer starts and cleans up its own component, sends the proof
owner its exact pre-start HEAD plus endpoint and health evidence, and sends its
post-cleanup HEAD readback afterward. The proof owner runs the combined scenario
through those exposed component boundaries and records the exact SHA vector.

The proof owner must not infer a peer HEAD from an earlier message, read or
execute inside a peer worktree, or take ownership of a peer component. Any peer
HEAD change makes prior proof stale. A worker sends an upstream-owned mismatch
directly to the owning peer as evidence only; that peer owns diagnosis, repair,
validation, and a replacement HEAD. The proof owner then reruns the affected
complete proof. If the distributed topology cannot execute, report
`blocked-app-capability` without asking the user or falling back to root
execution.
