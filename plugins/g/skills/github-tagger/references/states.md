# GitHub Tagger States

GitHub Tagger stores no durable local state. Every invocation derives a fresh
issue classification or taxonomy proposal from current repository and provider
evidence.

## Modes

`tagger_mode` is transient request routing state.

| Value | Meaning |
| --- | --- |
| `issue-classification` | Classify one exact issue against existing assignable labels and native types. This is the default for an issue target. |
| `taxonomy-proposal` | Analyze one exact repository and its issue corpus to propose missing labels and organization issue types without mutation. This requires an explicit user request. |

## External Persisted State

The following state belongs to GitHub rather than this skill:

- labels currently assigned to the issue;
- the issue's current native type;
- repository label definitions and organization issue-type definitions;
- issue open or closed state, fields, milestone, assignees, project membership,
  relationships, and dependencies.

This skill may add labels and set the native type only through the authorized
GitHub Issues lifecycle boundary. All other external state is read-only
context. `mutation_mode` and `issue_operation` are shared G invocation fields
owned by `../../../references/options.md`, not states owned here.

## Classification Dispositions

`classification_disposition` is transient derived state.

| Value | Meaning |
| --- | --- |
| `complete-match` | Every requested classification dimension has one clear supported result. |
| `partial-match` | At least one label or type is clear, while another requested dimension is ambiguous, unavailable, or blocked. |
| `no-confident-match` | The relevant catalogs are readable, but no exact candidate is sufficiently supported. |
| `no-available-metadata` | The relevant catalogs were read successfully and contain no assignable classification values. |
| `metadata-unavailable` | A usable classification catalog could not be proven because capability, access, or provider reads are indeterminate. |

## Application Statuses

`application_status` is transient execution state.

| Value | Meaning |
| --- | --- |
| `not-applicable` | No safe metadata proposal exists, so no mutation can be previewed or applied. |
| `previewed` | At least one exact change was proposed and no mutation was attempted. |
| `unchanged` | The supported proposal already matches the issue, so no mutation was needed. |
| `applied` | Independent readback proves every attempted label and type change. |
| `partially-applied` | Independent readback proves at least one attempted change and at least one requested change remains unapplied. |
| `failed` | Independent readback proves that none of the attempted changes reached the issue. |

Do not persist or reuse either transient value across invocations. An uncertain
write has no terminal `application_status` until the exact issue is read back
and reconciled.

`application_status` applies only to `issue-classification`.

## Taxonomy Dispositions

`taxonomy_disposition` is transient derived state used only by
`taxonomy-proposal`.

| Value | Meaning |
| --- | --- |
| `proposal-ready` | At least one new label or issue-type definition is supported by recurring evidence and passes the gap and overlap checks. |
| `no-taxonomy-gap` | The examined evidence is adequately represented by the current taxonomy, so no addition is proposed. |
| `insufficient-evidence` | The visible corpus, repository evidence, or organization scope cannot justify a stable new taxonomy entry. |
| `metadata-unavailable` | No requested proposal dimension has a catalog complete enough for reliable collision and gap checks. A usable dimension may still yield `proposal-ready` while another is reported unavailable. |

Taxonomy proposals and dispositions are never persisted or treated as provider
state. This mode has no `application_status` because it performs no mutation.
