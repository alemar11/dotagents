# Existing release-controller dispatch

Read this reference when a repository already has an approval-gated release
controller and the user asks to create or apply a candidate or final tag. This
file owns discovery, operation selection, dispatch, and post-dispatch readback.
The controller topology and authoring contract remain in `github-actions.md`.

## Discovery and authority

Inspect provider-owned workflow definitions, the current default branch,
remote tags, relevant branch SHAs, and the requested ref. Use a controller only
when exactly one manual workflow exposes the five semantic operation prefixes
`[patch]`, `[minor]`, `[major]`, `[candidate]`, and `[final]`, calculates an
exact proposal, and gates mutation through `release-tag-approval`. Workflow
filenames and human-readable option text may vary by project; select by the
semantic prefixes and verified behavior rather than guessing from a filename.

Starting the controller is a remote mutation. A request to create or apply a
tag does not authorize dispatch until the exact tag, source SHA, workflow, ref,
and semantic operation have been previewed and explicitly confirmed. Dispatch
authorizes only the controller run. It does not authorize approving the
environment, bypassing reviewers, publishing a GitHub Release, or manually
starting the repository publisher.

## Context and operation selection

Treat remote branch and tag state as authoritative. A version that is obvious
from the user's request, the current focused change, or a small repository
inspection may help classify the intended release line, but it is advisory.
Do not maintain an ecosystem or manifest registry, crawl the repository for
every possible version source, or let application metadata override provider
state. If the version evidence conflicts with tags or branch identity, stop
and explain the mismatch.

Select the operation as follows:

| Selected ref | Explicit intent | Operation | Expected proposal |
| --- | --- | --- | --- |
| Current default branch | next patch line | `[patch]` | `vX.Y.(Z+1)-rc.1` |
| Current default branch | next minor line | `[minor]` | `vX.(Y+1).0-rc.1` |
| Current default branch | next major line | `[major]` | `v(X+1).0.0-rc.1` |
| `release/vX.Y.Z` | next candidate | `[candidate]` | next unused `vX.Y.Z-rc.N` |
| `release/vX.Y.Z` | stable final | `[final]` | `vX.Y.Z` |

On the default branch, a new patch, minor, or major line starts at `rc.1`. If
that same line already has any RC tag, do not dispatch another default-branch
operation; continue from its exact `release/vX.Y.Z` branch. An unrelated RC
line does not block a different line.

On `release/vX.Y.Z`, the branch name owns the version core. A request for an
RC selects `[candidate]` and the controller calculates the next `rc.N`. Select
`[final]` only from explicit finalization intent; an application version such
as `X.Y.Z` does not by itself distinguish a candidate build from the final.
When candidate versus final remains ambiguous, show both proposals and ask the
user to choose.

If the selected ref is neither the current default branch nor an exact
`release/vX.Y.Z`, do not dispatch. If the requested exact tag does not match
the controller's current proposal, stop rather than changing the operation or
normalizing the tag.

## Dispatch and verification

Immediately before dispatch, refresh the workflow definition, selected ref
SHA, default branch, and remote tags. Re-run canonical tag validation and the
contextual proposal. Reject drift, an existing final, a same-line default-
branch RC, a missing release branch, or an ambiguous controller.

Dispatch exactly one run with the selected ref and the option whose semantic
prefix matches the confirmed operation. Preserve the provider receipt and
independently read the created run before any retry. Require its repository,
workflow, event, selected ref, head SHA, and resolved proposal to match the
preview. An ambiguous dispatch result must be reconciled before retrying so
that one authorization cannot create duplicate runs.

When the run reaches `release-tag-approval`, report the exact proposed tag and
source SHA and leave approval to the configured reviewers. Do not treat
dispatch as approval or attempt to bypass the gate. If the user asks to wait,
monitor the same run; after approval and completion, read back the candidate or
final tag and release branch from the provider and require the verified commit
to equal the confirmed source SHA.

The normal controller may call its reusable publisher after a verified final
tag. Never manually dispatch that publisher as a substitute for the
controller. Publisher dispatch remains recovery-only for an already existing
canonical final tag under the contract in `github-actions.md`.
