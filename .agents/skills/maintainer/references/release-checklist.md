# Shared Validation and Closeout

This is the single closeout owner for standalone and mixed Maintainer routes.
Use branch evidence already collected; do not recursively run a full closeout
for each package or nested playbook. Load [states.md](states.md) for the canonical
result fields.

## Alignment and verification

1. Confirm requested scope, preserved unrelated changes, and creator-first
   handling for substantial reshapes. In a review, report findings without
   changing files, staging, or publishing.
2. For authorized changes to public descriptions, identities, or catalog entries,
   run [metadata-sync.md](metadata-sync.md) once across affected packages unless
   that alignment is already complete. Do not reopen a completed metadata route.
3. Select applicable lanes from [validation-matrix.md](validation-matrix.md).
   For audits, use only non-mutating proof. Verify affected metadata, reference
   paths, ownership, invocation, and authorization boundaries in proportion to
   the change. Include manifests, versioning, artifacts, and installation state
   only for applicable package changes. Use health criteria for unresolved
   structural questions, not a second whole-repository audit.
4. Run checks not already satisfied by evidence for the final state. A relevant
   edit invalidates its affected checks; unchanged results can be reused. Run
   native `codex review` for non-trivial implementations and resolve or
   explicitly disposition findings. A missing required lane is `result=fail`
   unless the user accepts a narrower result.
5. Read the scoped diff, scan for retired references where applicable, and run
   `git diff --check`. Distinguish failed required gates from non-blocking
   warnings; size alone is never a failing gate.

When a package was renamed, moved, merged, replaced, or removed, select the
migration/removal lane. Verify updated callers and discovery, absence of retired
names and owned links, and the intended replacement or removal of capability.
For affected plugins, verify version/artifact alignment and installed/cache
parity; any reinstall must preserve unrelated work and introduce no checkout
changes. Unresolved callers, duplicate discovery, or a mismatched replacement
remain failed verification, not completed maintenance.

## Delivery

Maintenance authority does not imply commit, push, PR, or publication authority.
Use `$git-commit` for authorized commits/pushes and `$yeet` for authorized
single-PR publication when available; scoped Git is the commit/push fallback.
A push-only request never authorizes staging or committing. Scope staging,
inspect the staged diff, and split distinct package or migration responsibilities.
After delivery, verify the exact commit range, branch divergence, and requested
remote result while preserving unrelated pre-existing changes.

## Report

Emit `result` and `change_state`. Briefly state coverage, findings or changes,
verification and its limits, remaining work, and delivery state when relevant.
Include runtime evidence, artifact/cache parity, or size estimates only when they
support a claim. Omit unused fields rather than producing a template of
`not applicable` entries. A valid no-op requires no persistent edit.
