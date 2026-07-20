# Worker And Portfolio Closeout

This file is the canonical owner of terminal sequencing, the no-merge boundary,
and post-terminal behavior.

The only successful App result is
`pull-request-ready-for-merge-but-not-merged`.

After root-title revalidation, execute the closeout sequence below.

For local tracker sources, move only the predeclared active ref to its done ref
after current substantive, integration, and domain-closeout proof. Require an
unchanged body, record the move, commit and push it, observe the newer revision,
rerun validation and terminal AutoReview, then obtain current-revision review,
CI status, and all terminal gates. The move remains prepared until later merge.

Closeout order is irreversible:

1. Seal each task against its complete current revision set and gates.
2. Record its `pull-request-ready` handoff with
   `external-merge-required` authority.
3. Independently reverify every task and record portfolio verification.
4. Complete the sole root Goal, read it back, and record completion.
5. Reverify eligibility, release the claim, and archive through
   `cache-lifecycle.md`.

Failure or changed truth retains active state and blocks the next stage. After
seal or Goal completion, record drift only as post-terminal drift; never reopen
the Goal or resume implementation. Correction requires owner action and a new
separately authorized run.

Neither root nor any worker enqueues or merges a pull request, deploys,
releases, closes hosted tracker items, or performs post-merge verification. A
later GitHub workflow owns those actions and must recheck any late review
findings.
