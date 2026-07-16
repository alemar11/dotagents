# Later-Wave Evidence Transport

Load this reference before a second controller wave. On resume, load and apply
`recovery-validation.md` first. This reference changes evidence transport only;
source artifacts, claims, tasks, gates, and the ledger remain authoritative.

Take one full snapshot per stable fingerprint. Later passes carry only:

- artifact path or ref and root-computed fingerprint;
- changed source, repository, task, or ledger rows;
- focused hunks required for the current decision;
- validation command and compact result;
- failed-gate evidence and next action.

Prefer `git status --short`, `git diff --stat`, `git diff --name-only`,
`git diff --check`, and path-scoped hunks. Read the complete relevant diff
before `$autoreview`, commit/publication, or when compact evidence cannot explain
a gate failure.

Require a complete source and ledger read for initial claim, incompatible or
stale recovery, ownership ambiguity, changed source fingerprints, or final
reconciliation when compact proof is insufficient. Do not record token metrics,
fallback reasons, or unchanged poll observations as progress.
