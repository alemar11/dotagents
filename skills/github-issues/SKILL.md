---
name: github-issues
description: "Manage GitHub issues and relationships, classify labels and types, or propose issue taxonomy."
---

# GitHub Issues

Own issue lifecycle operations, evidence-based label/type selection, and explicit
read-only taxonomy proposals. Product planning and orchestration remain with
the caller.

## Select the work

- For exact issue reads or lifecycle operations, including caller-selected
  metadata, comments, attachments, and relationships, read
  [lifecycle.md](references/lifecycle.md).
- For content-based label/type selection on an existing issue, read
  [metadata-classification.md](references/metadata-classification.md). The
  request selects preview or application; classification does not authorize
  label removal or taxonomy changes.
- Only for an explicit request to audit, design, recommend, or propose issue
  taxonomy, read [taxonomy-proposals.md](references/taxonomy-proposals.md).
  This branch is read-only and requires a repository, not a target issue.

These are request-derived branches, not persisted modes. Exact metadata
operations do not require classification. Read [states.md](references/states.md)
when interpreting native dependency, classification, or taxonomy results.

## Shared boundaries

Before contacting GitHub, use the runtime's narrowest network-enabled context
for `gh` and helper commands. Verify `gh` is runnable (`command -v gh`,
`gh --version`) and authentication with:

```sh
gh auth status --active --hostname github.com --json hosts \
  --jq '.hosts["github.com"] | map(select(.active == true) | {state, scopes})'
```

Require exactly one active account with `state=success`. Treat
restricted-environment network failures as inconclusive. Do not install or
refresh `gh` without explicit authorization. Network permission is not
mutation authority.

Use authenticated `gh`; binary uploads use only
`<skill-root>/scripts/attachment-upload` documented in the lifecycle branch.
Resolve `<skill-root>` as the absolute path of the directory containing this
`SKILL.md`.

Resolve the exact repository and target before mutation. Preserve existing
user authority: explicit write instructions authorize their scope; a preview
or recommendation alone does not. Normalize operations with the invocation
fields below. Classification may derive separate label and type operations from
one authorized classification request.

Keep free-form provider fields file-backed. Independently read mutations back
and reconcile uncertain effects before retrying. Report exact issue URLs,
verified changes or proposals, and unresolved evidence; do not infer success
from a write receipt.

Use `$github-status` for issue/PR queues. Ordinary code or history
investigation needs no skill.

## Invocation fields

| Field | Allowed values | Default | Meaning |
| --- | --- | --- | --- |
| `mutation_mode` | `apply`, `dry-run` | `dry-run` | For write-shaped operations, whether to execute or preview. Omit for pure reads. |
| `issue_operation` | `create`, `edit`, `set-type`, `remove-type`, `create-label`, `add-label`, `remove-label`, `comment`, `attach-parent`, `remove-parent`, `add-sub-issue`, `remove-sub-issue`, `add-blocked-by`, `remove-blocked-by`, `close`, `reopen` | none | The one issue lifecycle operation being requested. |

Keep the operation separate from its issue or relationship reference. A
classification request supplies the exact repository, issue, optional requested
dimensions, and `mutation_mode`; it need not preselect an `issue_operation`.
Taxonomy proposals are read-only and omit both operation and mutation fields.
Callers must normalize planning policy before invocation; reject caller-owned
planning, tracker, orchestration, delivery, permission, or phase fields.
`mutation_mode=apply` authorizes only the named operation and target.
