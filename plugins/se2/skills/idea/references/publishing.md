# SE2 Idea Publication

Read this reference only when `run_mode=publish` has been explicitly resolved.
The G-owned GitHub issue workflow remains the only transport and owns safe
body handling, issue creation, label administration, verification, and
partial-failure mechanics.

This reference is the only external terminal phase of the Idea workflow. The
capture and preview paths must not load the G dependency preflight, inspect
GitHub, or mutate hosted state.

## Hosted artifact

Each durable Idea is an open issue with:

- title `Idea: <Name>`;
- the exact `idea` marker from the SE2 workflow contract;
- native Issue Type unset;
- the seven sections from `idea-template.md`.

Return a globally qualified durable ref such as `owner/repository#<number>` or
the canonical hosted URL. A bare issue number is not a source identity.

## Publication preflight

Before the first hosted mutation:

1. resolve the exact `owner/repository` target for every accepted candidate;
2. verify the SE2 workflow contract and exact `idea` marker;
3. inspect open issues for exact and near title matches, then inspect candidate
   bodies, labels, state, and native Issue Type;
4. reuse only an exact equivalent with the same substantive proposal, owner,
   marker, compatible open state, and absent native Issue Type;
5. ask for a decision on a materially different collision; do not silently
   edit, relabel, reopen, or remove an Issue Type;
6. confirm the exact `idea` marker is available for every candidate.

If the marker is missing, its creation is allowed only as the single exact
metadata operation authorized by the explicit publish request. Verify it before
creating an Idea. Do not create additional taxonomy.

## Handoff and verification

Translate each operation into the G workflow's normalized issue lifecycle
boundary. Keep caller-owned fields such as `run_mode`, candidate selection,
and publication policy outside that handoff. The handoff must identify one
exact target and one issue operation at a time.

Use the reconciled transient capture bundle as the only publication input. It
contains the selected candidate, final body, target owner, preflight evidence,
and publication order. Do not reconstruct a candidate from stale transcript
context after publication starts. The bundle is discarded after the terminal
report; only the explicitly published issue is durable.

Publish in checkpoints:

1. create or reuse the exact marker and verify it;
2. create one missing Idea with its final title, body, and marker;
3. read the result back before processing the next candidate;
4. verify title, open state, body, marker, and absent native Issue Type;
5. record the durable qualified ref.

Do not set a native Issue Type or apply workflow-state labels. Open questions
in an Idea body do not imply a workflow state.

## Failure and recovery

If an operation returns an error, no result, or ambiguous acknowledgement, stop
the batch and inspect the current hosted marker and issue state. Reuse a
verified issue that the attempted operation actually created. Retry only a
missing marker, issue, or assignment proven absent. Never replay the complete
batch from the original candidate list.

On partial publication, report verified created and reused refs, the exact
missing work, and the safe resume point. Clean up transient composition
artifacts through the G workflow's own recovery boundary.
