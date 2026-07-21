# Worker Review Fix Phase

Load for accepted AutoReview or Codex review findings.

Bind each finding to the exact repository, PR, source head, evidence, and
disposition. Apply only supported in-scope fixes, validate them, create a new
scoped commit, and observe the new head. Rerun every invalidated validation,
AutoReview, Codex review, and configured-CI gate.

Use `$gitstack:git-commit` with a regular commit unless repository instructions
require one exact targeted fixup. Never autosquash or rewrite a published
branch.

AutoReview owns its evidence lineage and bounded fix loop. Codex inline
findings retain exact thread identity. Journal GitStack reply and resolution as
separate one-use operations; never synthesize a thread for a summary-only
finding.
