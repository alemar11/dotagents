# Issue Tracker: GitHub

Feature Specs, implementation issues, and captured Ideas for this repository
live as GitHub issues. Use `$gitstack:github-issues` for GitHub issue lifecycle
operations.

GitHub is the authoritative artifact store. Project Memory stores only the
resolved tracker target and human-readable conventions; feature workflows own
artifact metadata, label/type semantics, delivery, branch/PR strategy, and
executor permissions.

Do not create repository-local planning mirrors merely to feed hosted
mutations. Temporary body files must live outside the repository and be removed
after use.

## Publication Boundary

- `write_mode=apply`: the consuming workflow may use
  `$gitstack:github-issues` to create or update issues, relationships, types,
  and labels after its own contract gates pass. Normalize each write to
  `mutation_mode=apply`, the exact repository/issue target, and one canonical
  `issue_operation`, then verify hosted state.
- `write_mode=propose`: return proposed titles, bodies, metadata,
  relationships, and publication order without mutating GitHub or returning
  executable commands.

Project Memory does not select the metadata values or authorize their mutation.
The consuming workflow must load its feature or domain-specific contract and
delegate every operation to GitStack.

## Routing Conventions

Infer the repository from `git remote -v` unless this file records a specific
target. Use `$gitstack:github-issues` for issue reads, comments, relationships,
types, labels, and lifecycle transitions. A read or proposal supplies no
mutation authority and must not be upgraded at this boundary.

Keep globally durable hosted refs in the form
`owner/repository#<number>` or a canonical hosted URL. Never use a bare issue
number as a cross-repository identity.

When proposed output precedes a hosted artifact, the consuming workflow owns
the proposal-ref format, publication order, and replacement of that ref with a
verified hosted identity. Project Memory does not define a second workflow
contract for those details.

## Completion Convention

Use a GitHub closing keyword or explicit lifecycle transition only when the
consuming workflow has proved that its artifact contract is satisfied. Do not
close a parent artifact from an individual child unless the owning workflow's
completion contract explicitly permits it.

## Fetch

Use `$gitstack:github-issues` to view an issue and its recent comments. Read the
complete relevant state before making a decision or retrying an ambiguous
mutation.
