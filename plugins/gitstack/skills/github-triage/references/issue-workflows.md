# Issue Workflows

## Commenting

Write comments that are specific about observed state, requested action, and
next owner. Prefer `--body-file` for non-trivial comments so the exact text can
be reviewed before posting.

Use `$gitstack:github-issues` for authorized issue comments.

## Labels And Milestones

Read current labels before adding or removing labels:

Use `$gitstack:github-issues` for authorized label changes.

If the requested label does not exist, ask before creating new taxonomy.

## Closing Issues

Only close an issue when the user explicitly asks or the repository workflow
clearly requires it after a merged fix. Include the closing rationale in the
comment or close reason.

Before recommending closure, compare the issue body and latest known acceptance criteria
against the implemented proof. If any setup, live proof, adapter, migration,
security follow-up, or other acceptance criterion is deferred, do one of:

- create a follow-up issue when GitHub mutation is authorized, then link it in
  the closing comment or final report;
- link an existing follow-up issue that covers the exact deferred scope;
- if mutation is not authorized, keep the source issue open and report the
  proposed follow-up title/body to the owner.

Use `$gitstack:github-issues` for authorized closing comments, follow-up issue creation,
or closure. The follow-up should name the deferred behavior, the blocker or
missing setup, the proof already collected, and the remaining acceptance
criteria. Do not close a partially satisfied issue with only a chronological
note or an implicit promise to revisit it.
