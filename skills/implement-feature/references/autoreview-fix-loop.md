# AutoReview Fix Loop

Load only after AutoReview or Codex PR review returns an accepted finding.

Follow AutoReview's `references/evidence-chain.md` on the committed branch.
Batch accepted fixes, commit/push a substantive revision, run focused proof,
then use `fix-verification`; delta rounds have no numeric cap but each must
advance the head. After first-full fixes reach `verification-clean`, run the
only `terminal-full`. Later accepted findings, including terminal-full or PR
review findings, close through delta evidence as `terminal-composite-clean`.
Never run a third full in one lineage; no revision progress becomes
`needs-owner`. Record every helper result through `autoreview-observed` using
the strict packet registry.
If every open finding is rejected, use AutoReview's no-Codex `disposition`
phase on the unchanged head instead of inventing a fix revision.
