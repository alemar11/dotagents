# Review Policy

Read this reference when AutoReview is used as another workflow's closeout gate
or when the change may need a second native Codex review.

## Review Profile

AutoReview owns the derived `review_profile` result:

- `standard`: run the structured AutoReview path only.
- `high-risk`: run structured AutoReview plus one native `codex review` on the
  same committed candidate HEAD.

`review_profile` is not a user option. Derive it from the accepted change and
the actual diff. Use `high-risk` when either source touches at least one of
these boundaries:

- authentication, authorization, identity, secrets, cryptography, or another
  security boundary;
- persistent-data schema, migration, destructive mutation, backup, restore, or
  recovery;
- concurrency, transactions, retry, idempotency, locking, or lifecycle state;
- a public API, external protocol, compatibility contract, or parser for
  untrusted input;
- filesystem paths, symlinks, archives, shell execution, or generated code
  execution;
- money, billing, or an irreversible external side effect;
- a cross-repository contract with distributed behavior.

Use `standard` otherwise. Do not promote a change merely because it is large,
and do not demote it because its diff is small.

## One Candidate, At Most Two Lenses

Finish implementation, formatting, focused validation, and committed tracker
updates before opening the review lineage. Both review lenses must inspect the
same candidate HEAD and base.

For `standard`, run one structured AutoReview full pass.

For `high-risk`, start the structured full pass and the native review before
applying either review's fixes. They may run concurrently when the environment
supports it; otherwise run them back to back without changing HEAD between
them. Use one exact native selector and no positional custom prompt:

```bash
codex review --base <base-branch>
codex review --commit <head-sha>
codex review --uncommitted
```

Current Codex CLI rejects a positional prompt combined with `--base`,
`--commit`, or `--uncommitted`. Put accurate repository, Feature Spec, risk
boundary, base, HEAD, and phase context in AutoReview's `--prompt-file`.
Describe the native review accurately in caller evidence instead of claiming
that this context was injected into its prompt.

Run native `codex review` at most once per lineage. It is a complementary,
unstructured lens, not a second loop. Verify its findings against the code,
import accepted or rejected findings through `findings template` and `findings
prepare` with `finding_source=codex-review`, and close them through AutoReview
fix verification. Never rerun native review merely because fixes, tracker
closeout, commit, push, PR, or final response happened.

## Bounded Fix Loop

Aggregate verified findings from both lenses before the first fix batch.
Commit a coherent fix HEAD, rerun only the affected deterministic validation,
restore and read back any invalidated tracker proof, then run one AutoReview
`fix-verification`.

A clean `verification-clean` result is sufficient terminal evidence under this
policy. Further fix verifications are allowed only after a substantive new
committed HEAD that addresses remaining accepted findings. Repeated feedback on
an unchanged HEAD is `review-no-progress`.

`terminal-full` is not an automatic closeout phase. Reserve the one supported
terminal full for explicit review escalation backed by a newly identified
broad regression concern. A lifecycle boundary, tracker-only closeout,
publication, or a desire for nicer wording is not escalation evidence.

If implementation or tracker work changes paths after the first full review,
the candidate was opened too early. Finish the new candidate coherently and
start one replacement lineage; do not continue stacking reviews on stale
scope.
