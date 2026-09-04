# Implement Candidate Review

Load this reference before entering `review-candidate`. It owns the independent
local reviewer topology, candidate identity, reviewer profile, finding
contract, convergence, and recovery. [states.md](states.md) solely owns the
candidate-review disposition values and meanings. Hosted pull-request review
remains owned by G and is a separate later gate.

## Candidate and reviewer

Enter only after the assigned worker has implemented the Feature, passed its
required validation, locally committed the stable candidate, become quiescent,
and proved its worktree clean. Bind the
review to the verified repository, intended base branch and full base SHA,
candidate branch and full HEAD, complete Feature delta, an immutable content
identity for the exact authoritative Feature contract, applicable repository
instructions, and validation evidence. Review the whole Feature delta rather
than only the last worker turn or most recent commit.

Materialize a fresh isolated review checkout whose tree is exactly the locally
committed candidate HEAD and whose intended base resolves to the bound full
base SHA. Prove it clean before review. Start one fresh local noninteractive
Codex reviewer execution for that immutable snapshot. It must be independent
of the implementation worker's conversation, read-only in the isolated review
checkout, and unable to edit the candidate or perform Git or hosted mutations.
Request `gpt-5.6-sol` with `xhigh` reasoning explicitly. If the runtime cannot
establish the local reviewer capability, isolation, read-only boundary,
requested profile, clean snapshot, or exact target, produce `indeterminate`
instead of substituting a same-context self-review or a different profile.

Several independent candidates may be reviewed concurrently only when the
orchestrator already authorized their worker lanes. Each reviewer is bound to
one repository, base, Feature, and full candidate HEAD.

## Adversarial review contract

Act as a skeptical shipment reviewer. Inspect the candidate and its relevant
code paths for material correctness risks, hidden assumptions, authorization
or permission errors, data loss or corruption, concurrency, retries and
idempotency, migration and compatibility hazards, rollback and partial failure,
degraded dependencies, and missing observability. Apply only lenses relevant
to the actual change; do not manufacture findings to satisfy the posture.

Return one transient `candidate_review_disposition` defined canonically in
[states.md](states.md). Do not redefine or extend its values here.

Order findings by severity. Each finding identifies the concrete failure mode,
affected file and tight line range when available, supporting evidence,
confidence, and a focused recommendation. Keep the review read-only; it never
fixes its own findings.

## Convergence and invalidation

Every result returns to `reconcile`. A `clean` result lets `schedule` return the
same trustworthy worker to `deliver-feature` for publication. `findings` return
that worker for focused repair, full invalidated validation, and a new local
commit; the changed full HEAD requires another fresh candidate review.
`indeterminate` blocks unless authoritative evidence can resolve the same
review attempt without inventing a verdict.

The worker may rebut a finding with concrete repository evidence, but a fresh
independent review of the unchanged or repaired candidate must accept that
evidence before publication. Permit at most two repair or rebuttal cycles after
the initial review for one selected Feature, counting both changed and
unchanged candidates. Reconstruct the count from task history on resume. If the
budget is exhausted without `clean`, preserve the review's actual disposition
and return separate exhaustion evidence for `reconcile` to route to `blocked`;
never reset the budget by changing the finding or HEAD.

After review, independently prove that the isolated checkout stayed clean and
still resolves the bound full base and candidate HEAD. Any Feature-contract
content, candidate content, ancestry, base-tip, or full-HEAD change invalidates
the result. Immediately before publication, ready transition, and completion,
verify that the current authoritative Feature contract, intended base tip, and
candidate HEAD still equal the reviewed contract identity and full SHAs. A
resume with an already-published candidate still requires a current clean
candidate review before Implement can complete; subsequent hosted findings and
repairs create a new HEAD that must pass candidate review again before push.

Candidate-review prompts, results, and profile evidence remain transient in
task history. Never add them to the repository-claims registry or treat them
as a persisted workflow checkpoint.
