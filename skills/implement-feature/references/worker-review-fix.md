# Worker Review Fix Phase

Load only when the controller selects repair of accepted AutoReview or Codex
review findings.

Bind every finding to the exact repository, PR, source revision, evidence, and
accepted disposition. Apply only supported in-scope fixes, create a new scoped
commit with no pending Git-visible changes, observe the new revision, and rerun
invalidated validation and review phases.

Use `$gitstack:git-commit` with `commit_kind=regular` unless target-repository
instructions require one exact targeted fixup and `target_commit`. Feedback
alone never selects a fixup. Never autosquash or rewrite a published branch;
the new head invalidates current-revision review and CI evidence.

AutoReview fix verification follows its evidence lineage. After first-full
fixes reach verification-clean, run the only terminal-full phase. Later hosted
findings close through delta evidence and terminal-composite-clean. Rejected
findings use the unchanged-head disposition path. Never run a third full phase.

Inline Codex findings retain exact thread identity. Provider reply and resolve
are separate controller-owned GitStack operations; this phase prepares repair
evidence but does not post, resolve, or infer a synthetic thread.
