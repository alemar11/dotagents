# Feature Specification Operations and Results

The `spec` namespace describes transient caller choices and operation results,
not a workflow graph. The saved identity and revision contract belongs to
[specification.md](specification.md). A request resolves to refinement or
explicit publication; review findings return to drafting or clarification. Each
spec has its own result within the invocation's single repository. Verify all
selected specs and their same-repository links; report partial publication by
exact artifact. Other repository work is out of scope. An unresolved required
effect remains blocked.

## Caller choices

| Field | Values | Meaning and default |
| --- | --- | --- |
| `operation` | `refine`, `publish` | Refine in conversation by default; publish to GitHub only after an explicit user request. |

These are operation choices, not project configuration. The exact issue or
repository target is caller/repository data, not another enum. Refinement may
read an explicitly supplied hosted source through `$github-issues`; a local-only
source constraint still forbids hosted reads. No operation grants
additional source access or implementation authority.

## Derived evidence and result values

| Field | Values | Meaning |
| --- | --- | --- |
| `source_route` | `new-source`, `existing-source` | Derived from whether the request creates a spec or revises an existing authoritative artifact. |
| `planning_readiness` | `ready`, `clarification-required`, `blocked` | Whether evidence supports drafting, a material choice remains, or essential evidence is unavailable. |
| `grilling_outcome` | `refined`, `user-stopped`, `blocked` | Composed interview result; a stopped handoff is usable only when remaining assumptions are safe. |
| `review_result` | `clean`, `revision-required`, `clarification-required`, `blocked` | Assessment of the complete spec and task contract. |
| `refinement_result` | `refined`, `clarification-required`, `blocked` | Complete in-conversation spec, unresolved material choice, or unavailable essential evidence. |
| `publication_result` | `not-requested`, `published`, `no-op`, `failed`, `unavailable`, `ambiguous` | Verified GitHub publication or its exact unresolved outcome. |
| `readback` | `not-applicable`, `verified`, `no-op`, `ambiguous` | Exact GitHub artifact observation when publication is requested. |

A saved spec may contain its semantic revision, explicit assumptions, acceptance
baselines, and a record of retired identities. It does not persist a current
workflow node, worker assignment, execution status, review receipt, or operation
journal. Task progress and GitHub issue state belong to their execution/provider
owners; Spec preserves them during revision.

Keep refinement and publication results separate. A refined spec remains in the
conversation until explicit publication is requested. No result proves that a
label, monitor or worker has started.
