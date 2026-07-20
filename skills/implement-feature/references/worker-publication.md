# Worker Publication And Delivery Phases

Load only for publication, ready transition, CI, tracker closeout, or
mergeability selected by the controller.

## Provider Text Transport

Treat every provider-owned title, body, description, comment, reply, review,
release note, and warning as opaque UTF-8 bytes. Never place that text in argv,
an environment variable, a shell command string or command substitution, logs,
dry-run output, or errors.

For each provider-text mutation other than the typed review request:

1. Write each field without interpolation to its own absolute regular
   non-symlink file outside the managed checkout using a literal tool such as
   `apply_patch`.
2. From the exact checkout run GitStack `--json repo snapshot` and retain its
   SHA-256 fingerprint.
3. Invoke only the typed file operation with `--title-file`, `--body-file`, or
   its matching file field plus
   `--expected-worktree-fingerprint <fingerprint>`. Inline text flags, parser
   aliases, generic API writes, and shell-built commands are forbidden.
4. Require exact target, provider object id and URL, UTF-8 byte count and
   SHA-256, and unchanged worktree fingerprint.

`reviews address` is read-only. Open a PR with
`publish open --title-file --body-file`; GitStack has no `publish edit`
command. A failed or unreadable mutation permits only one exact-target
read-back and is never retried blindly. Preserve provider identity as
partial-success evidence if later worktree proof fails. A connector response
alone is not byte verification. Old snapshots and temporary files are not
recovery authority. Provider transport is a typed GitStack request operation,
does not extend `execution-manifest`, and does not define Codex review-request
content.

Create or update each delivery PR against its discovered default branch. Use
GitStack's typed file-backed provider-text operations with immediate repository
snapshot and exact target/text/worktree readback. Never place provider text in
argv, environment variables, shell strings, substitutions, logs, or errors.
Ambiguous mutation uses exact-target reconciliation and is never retried.

Commit through `$gitstack:git-commit`; use a regular commit unless repository
instructions require one exact targeted fixup. Never autosquash or rewrite a
published branch. Observe every changed head as a new revision and invalidate
prior revision-bound gates.

After substantive proof and terminal AutoReview, convert a draft through exact
PR identity. Outside the ready mutation's shell chain, resolve and persist its
exact number and URL; run `gh pr ready <number> --repo <owner/repo>` with no
selectorless or branch inference, then re-read the same number and require the
unchanged URL and `isDraft=false`. Then obtain current-revision Codex
review, configured CI or explicit `not-configured`, tracker-closeout evidence,
and current branch-rule, approval, base-freshness, conflict, mergeability, and
merge-queue eligibility proof.

The ready-for-review transition is nonterminal. After that nonterminal
transition, continue through review, CI, tracker closeout, and mergeability.

Arm hosted closing refs only in their designated default-branch delivery PRs;
leave issues open until merge. The PR must remain `OPEN`. Unknown, pending, closed, merged, stale,
conflicting, or ineligible state blocks. Never enqueue or merge.
