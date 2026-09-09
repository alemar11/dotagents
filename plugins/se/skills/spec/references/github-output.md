# GitHub Output

Read only for GitHub preview or save. The content contract is
[specification.md](specification.md). G owns issue transport, safe file handling,
provider operations, and readback; Spec owns the semantic projections.

## Projection

Save exactly one issue in the spec's `owner_repository`, titled
`Spec: <spec title>`. Apply the prefix exactly once; it is display metadata,
not identity, and a prefix-only change does not increment `spec_revision`.
Keep body headings unprefixed. Never create task issues or sub-issue relationships.

The issue body contains the complete spec, ordered task index, and every detailed
task contract for that repository. Use the single [spec template](../templates/spec.md)
with the shared [embedded task rendering](specification.md#rendering). Task links
point to sections in this issue. Issue types and classification labels are optional;
the [delivery marker](delivery-authorization.md) alone controls pickup authorization.

For `operation=preview`, render the complete issue, target repository, and proposed
spec links and prerequisite conditions without writes or collision claims. Local-source previews
need no G access; hosted source reads retain their preflight and caller constraints.

## Spec dependencies

Link related specs only with exact issue URLs in the selected repository.
Verify repository identity for every authored issue reference before saving;
reject cross-repository links rather than publishing companion specs. When one supplies a prerequisite, state the required outcome or
evidence and the activity it gates: implementation, integration, publication,
merge, or deployment. Task-specific prerequisites stay in their task contracts;
internal `blocked_by` references stay in the body. Shared scope or recommended
order alone does not establish a dependency.

Spec never creates, updates, or removes native GitHub blocked-by relationships. Delivery
ends at ready PRs, so a usable candidate can satisfy a prerequisite while its
issue remains open. An agreed interface can permit parallel implementation;
integration may require a consumable candidate, and release may require deployed
behavior. Specify the actual condition without choosing Delivery's PR topology.

Preserve existing native relationships. If the user explicitly asks to add or
remove blockers, that action belongs to `g:github-issues` outside the Spec workflow;
keep its result separate from the spec save. Spec must not infer such a request
from semantic prerequisites. Verify exact linked spec identities and reject
self-dependencies or cycles in hard prerequisites without creating placeholder
issues. Issue closure remains distinct from implementation or availability evidence.

## Save and verify

Before hosted reads or writes, apply the shared
[G dependency preflight](../../../references/codex-dependency-preflight.md).
Before each write, apply [hosted-content safety](../../../references/hosted-content-safety.md)
to the exact final content, including worker- or provider-originated content.

Resolve the owning repository and inspect for the intended spec identity. Reuse
a verified match; reconcile a materially different collision before creation.
Create or update the single complete issue and read it back under
[existing-specs.md](existing-specs.md). Verify identity, title, revision, every
task and anchor, acceptance coverage, prerequisites, and preserved foreign or
executor-owned content before reporting semantic save complete.

Verify ordinary spec links and body-backed prerequisites as part of the save.
Preserve provider relationships and foreign metadata. Optional issue classification
must preserve delivery markers and does not gate semantic save.

Reconcile an ambiguous operation against the same issue before retrying.
Retry only after proved non-application and stop on unresolved ambiguity. Report
completed and remaining effects; never recreate the issue or substitute a local
save after partial publication. Saving does not close this spec or any source or
prerequisite issue. Separately authorized closure or notification follows verified
save through its owner and requires its own reconciliation.

## Delivery marker

After the complete authoritative issue is verified, apply the decision from
[delivery-authorization.md](delivery-authorization.md) through `g:github-issues`.
Apply the shared [readiness states](../../../references/states.md) contract for
label creation, canonical colors, mutually exclusive state replacement and
readback. Pickup approval covers the scoped label operations. Apply readiness
only to the authoritative main spec; preserve other labels and the issue state.

Marker operations follow the same G preflight, hosted-content safety and
uncertain-effect reconciliation as other writes. A failed or ambiguous marker
operation leaves the verified spec saved but the requested authorization change
incomplete. Retry only the unresolved effect against the same repository/issue;
do not recreate the spec or report pickup enabled from label creation alone.
