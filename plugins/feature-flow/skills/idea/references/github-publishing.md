# GitHub Idea Publishing

Load this reference only when `run_mode=publish`.

## Canonical Hosted Artifact

Each GitHub Idea is an open issue with:

- title `Idea: <Name>`;
- the exact `idea` label from `workflow contract`;
- the exact `needs-triage` label from `workflow contract` only when the
  user explicitly queued this candidate;
- native GitHub Issue Type unset;
- the seven canonical body sections from `idea-template.md`.

The durable ref is `owner/repository#<number>` or the canonical issue URL. A
bare `#<number>` is not globally unambiguous and must not be the returned source
identity.

## Preflight

Before the first hosted mutation:

1. Resolve the exact `owner/repository` target for every accepted candidate.
2. Load `workflow contract` and use its exact Idea-marker and optional
   workflow-state label values. Reject a missing or incompatible contract; do
   not invent or hard-code a parallel taxonomy.
3. Search open issues for exact and near title matches, then inspect candidate
   bodies, labels, state, and `issueType`.
4. Reuse only a canonical exact equivalent with the same substantive proposal,
   marker, compatible queue state, open state, and `issueType=null`.
5. Resolve materially different matches with the user. Do not silently edit,
   relabel, reopen, or remove an Issue Type from a colliding issue.
6. Confirm every contract label required by the accepted set: the `idea` label
   for every candidate and the `needs-triage` label when at least one candidate
   was explicitly queued. If a required exact label does not exist, the
   `publish` capture request authorizes creation of that exact label only. Create
   and verify every required missing label before the first issue; do not create
   any other taxonomy.

## GitStack Composition

Delegate every mutation to `$gitstack:github-issues`. Translate Idea's
contract at the boundary; do not pass `run_mode` or other caller-owned policy.
For each missing contract Idea-marker or required workflow-state label pass:

```text
mutation_mode=apply
issue_operation=create-label
target=owner/repository
```

For each new Idea pass:

```text
mutation_mode=apply
issue_operation=create
target=owner/repository
```

Create every missing contract label, when necessary, as its own verified
`create-label` operation. A fresh repository with queued Ideas may therefore
need both the `idea` label and the `needs-triage` label before issue creation.
Then create the issue with the final title, safely
transported body, and final labels in the smallest supported `create`
operation. Omit `--type` or any Issue Type field entirely; do not set a
fallback `feature` or `task` type.

After each issue creation, read it back and verify title, open state, body,
labels, and `issueType=null`. Record its durable qualified ref before moving to
the next candidate.

## Failure And Retry

If a mutation response is missing or ambiguous, inspect the current repository
issue and label state before retrying. Reuse a verified issue that the failed
attempt actually created. Retry only a missing label, issue, label assignment,
or other operation proven absent; never replay the whole batch.

On partial multi-Idea publication, stop, clean up transient body files, and
report verified created and reused refs plus the exact missing work. Resume
from verified hosted state, not from the original candidate list.
