# GitHub Projects Workflows

Use these patterns only after loading [workflow.md](workflow.md), resolving
`<skill-root>`, and completing the Projects checks in
[the GitHub CLI preflight](../../gh-dependency-preflight.md). The invocation
registry in [options.md](../../options.md) is the sole owner of canonical
operation values.

## Discover and resolve

Keep list breadth explicit and request JSON from `gh`:

```sh
gh project list --owner <owner-login> --closed --limit <bounded-limit> --format json
gh project view <project-number> --owner <owner-login> --format json
gh project field-list <project-number> --owner <owner-login> --limit <bounded-limit> --format json
gh project item-list <project-number> --owner <owner-login> --limit <bounded-limit> --format json
gh project item-list <project-number> --owner <owner-login> --query '<provider-query>' --limit <bounded-limit> --format json
```

Omit `--closed` when closed Projects are outside the request. Treat
`<provider-query>` as provider-native query syntax, not a G option value.
Pass the complete query as one shell-quoted argument.
Resolve an owner-qualified Project URL to owner type, login, and number, then
confirm its node ID and canonical URL from the exact Project read.

Field discovery must retain field ID and data type. For single-select fields,
retain every option ID and name; for iteration fields, retain every visible
iteration ID and its provider attributes. Item discovery must retain Project
item ID separately from issue, pull-request, or draft content identity.

When a high-level read does not expose an owner node ID, field option ID,
iteration ID, linked repository or team, or draft content ID needed by the
requested operation, use a bounded GraphQL query through the file-backed path
below. Do not fall back to a display name as identity.

## File-backed GraphQL

For a missing exact-identity read or a mutation carrying free-form provider
text, create a reviewed UTF-8 JSON request file outside checkout-owned paths
with this shape:

```json
{
  "query": "<one GraphQL operation using variables>",
  "variables": {
    "projectId": "<project-node-id>",
    "value": "<provider text>"
  }
}
```

Run only:

```sh
gh api graphql --input <absolute-request-json>
```

Use the provider operation matching the authorized action:

- `createProjectV2` for a new Project;
- `copyProjectV2` for a copy whose title or draft-item choice was reviewed;
- `updateProjectV2` for title, description, README, or visibility changes;
- `createProjectV2Field` for text, number, date, or single-select fields;
- `addProjectV2DraftIssue` and `updateProjectV2DraftIssue` for draft items;
- `updateProjectV2ItemFieldValue` for text field values.

Keep the query static and place all caller or provider values in `variables`.
Do not include tokens or unrelated provider payloads. Inspect the file before
mutation and remove transient request files afterward unless the caller
explicitly owns a persistent artifact path.

## Identity-only and typed mutations

Use high-level commands when every value is an exact identity or a typed
fact. Include JSON output where the command supports it.

```sh
gh project close <project-number> --owner <owner-login> --format json
gh project close <project-number> --owner <owner-login> --undo --format json
gh project delete <project-number> --owner <owner-login> --format json

gh project mark-template <project-number> --owner <organization-login> --format json
gh project mark-template <project-number> --owner <organization-login> --undo --format json

gh project link <project-number> --owner <owner-login> --repo <repository-identity>
gh project unlink <project-number> --owner <owner-login> --repo <repository-identity>
gh project link <project-number> --owner <organization-login> --team <team-identity>
gh project unlink <project-number> --owner <organization-login> --team <team-identity>

gh project field-delete --id <field-id> --format json
gh project item-add <project-number> --owner <owner-login> --url <issue-or-pr-url> --format json
gh project item-archive <project-number> --owner <owner-login> --id <item-id> --format json
gh project item-archive <project-number> --owner <owner-login> --id <item-id> --undo --format json
gh project item-delete <project-number> --owner <owner-login> --id <item-id> --format json
```

For typed Project field changes, use node IDs rather than names:

```sh
gh project item-edit --project-id <project-id> --id <item-id> --field-id <field-id> --number <number> --format json
gh project item-edit --project-id <project-id> --id <item-id> --field-id <field-id> --date <yyyy-mm-dd> --format json
gh project item-edit --project-id <project-id> --id <item-id> --field-id <field-id> --single-select-option-id <option-id> --format json
gh project item-edit --project-id <project-id> --id <item-id> --field-id <field-id> --iteration-id <iteration-id> --format json
gh project item-edit --project-id <project-id> --id <item-id> --field-id <field-id> --clear --format json
```

Do not use field names or `--value` for a mutation: names are not stable
identity and the value may be free-form text. Do not use `gh project create`,
`copy`, `edit`, `field-create`, or `item-create` when their text would be placed
on argv; use the file-backed GraphQL path instead.

## Readback and recovery

Keep requested state, mutation receipt, and observed state separate.

- For create, copy, field creation, and draft-item creation, compare the
  pre-existing ID set with a bounded exact read. Verify only when one new ID is
  attributable to the requested input; otherwise return `unknown`.
- For adding an issue or pull request, return `no-op` when the pre-read already
  contains its content ID. After mutation, require the same content ID and its
  Project item ID in readback.
- For settings, values, links, template state, closure, and archival, compare
  exact provider fields before and after the mutation.
- For delete or unlink operations, verify absence from the exact owning
  collection. A missing target discovered before mutation is `no-op`.
- A structured provider rejection is `failed` only when the mutation is known
  not to have applied. A capability, scope, access, or target-resolution gap
  before an attempt is `unavailable`.
- After a timeout, transport interruption, or contradictory response, perform
  one exact readback. Return `verified` if it proves the requested state;
  otherwise return `unknown` and do not retry.

Adding an item and setting one or more fields is never treated as one atomic
write. Verify the add first, then perform and verify each separately authorized
field mutation in order. Stop dependent field mutations after a non-success
result and report all earlier results.
