---
name: review-pr
description: "Request or resume a hosted Codex PR review, wait for its result, and report it to the caller."
---

# Review PR

Obtain the hosted Codex review result for one exact GitHub PR and HEAD. Run in
the calling session/task, standalone or composed by another workflow, with the same
behavior in both cases. Do not create tasks or subagents. No spec, local checkout,
implementation context, candidate-review receipt, or repair budget is required.

Prefer this skill for a one-shot obtain-and-report hosted review. Use
`$github-review-threads` directly for inspect, reply, resolve, and other
provider review operations beyond that path.

## Scope and authority

Default invocation authorizes the needed explicit hosted review request and
bounded wait without another confirmation. Reuse a completed current-target
review, resume a matching pending request, or request and wait when no applicable
explicit lineage exists and prior effects are reconciled. Both clean and findings
are completed provider results; findings do not trigger a repair or another
unchanged-HEAD request.

An explicit audit-only, inspect-only, or read-only request reports existing
evidence without posting or starting a wait. The only hosted write this skill
owns is the requested review mention. It does not change draft state,
implement fixes, rebut findings, reply to or resolve threads, publish commits,
inspect CI or merge policy, update planning progress, or decide delivery acceptance.
The calling task owns those follow-up actions under its own authority.

Read [states.md](references/states.md) for result meanings and
[hosted-review.md](references/hosted-review.md) before inspection, requests,
waiting or resume. Before hosted access, verify that `$github-review-threads`
is installed and reachable by canonical name in the current session. A local
directory or unrelated connector alone does not establish availability. If
unavailable, report the dependency and stop the affected operation; do not
substitute direct provider calls.

Keep the review request limited to the verified PR, commit, and relevant review
scope. Exclude local absolute paths, internal prompts, and machine or task
details, including those copied from tool output. Inspect the exact request
before sending and its provider readback afterward. For a leaked local path,
attempt at most one authorized correction of the same request through
`$github-review-threads`; never post a second review request as a content repair.
Report unavailable or uncertain correction separately from the review result.

## Result and caller handoff

Return the PR URL, expected and observed full HEAD, exact explicit request
identity and unchanged review receipt/deadline, `review_pr_result`, provider verdict,
findings with provider links when present, and any pending state or blocker.
Report the provider result faithfully; do not adjudicate findings or turn
review completion into acceptance of the code. A clean response is review
evidence, not proof of CI, spec completion, or merge readiness.

The caller supplies its exact published ready candidate and any existing review receipt.
Return the result directly to that caller, which decides whether
to repair, rebut, defer, or accept, manages agents and budgets, and invokes this
skill again when the next published candidate needs hosted review. Standalone
invocation reports the same evidence directly to the user in the calling task.

## Skill Dependencies

`$github-review-threads` supplies exact review requests, inspection, bounded
waiting, and reconciliation. Compose only those operations; its reply/resolution
operations are outside this skill's scope. Never install,
refresh, or substitute the dependency during a run.
