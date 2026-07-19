# Review Evidence Chain

Read this reference when a review finding changes a committed branch or when a
caller must persist and resume review evidence across revisions.

## Phases

Use canonical `review_phase` values:

- `full`: broad review of the current branch. A clean unchanged result is
  terminal; findings start a lineage with one full review consumed.
- `fix-verification`: verify dispositioned findings and regressions on the
  committed delta from the prior head. It never performs another broad review.
- `disposition`: close an unchanged head after every open finding was
  consciously rejected. It makes no Codex call and accepts no fix.
- `terminal-full`: the second and final broad review in a lineage. It requires
  `verification-clean` evidence produced after fixes to the first full review.

The helper permits any number of progressing fix verifications. It does not
permit a third full review in one lineage. Findings from the terminal full, or
later Codex PR review findings, close through fix verification and produce
`terminal-composite-clean` evidence.

## Finding Intake

Pass `--finding-file <path>` for every fix verification. The file is strict:

```json
{
  "finding_source": "autoreview",
  "findings": [
    {
      "finding_id": "<sha256>",
      "finding": { "<validated AutoReview finding>": "..." },
      "disposition": "accepted",
      "reason": "Verified against the real code path."
    }
  ]
}
```

`finding_source` is `autoreview` or `codex-review`; `disposition` is
`accepted` or `rejected`. An AutoReview intake must disposition every open
finding from the prior evidence. A fix verification requires at least one
accepted finding and a changed committed head.
Use `disposition` only with a rejection-only AutoReview intake. `codex-review`
intake is rejected while AutoReview findings remain open.

## Lineage And Terminal Rules

The evidence envelope binds repository identity, base, merge base, head,
effective changed paths, target fingerprint, counters, finding state, result,
metrics, and its parent fingerprint. Do not edit it manually.
Deletion-only regressions point to the nearest surviving current line, or line
1 under the deleted path when the file has no surviving line.

Repository, base, merge-base, or changed-path expansion returns
`lineage-invalidated` with `recovery=start-new-full-lineage`. A new lineage
starts with `full`; never disguise an expanded scope as a fix delta.

Terminal states are:

- `terminal-clean`: a full review is clean on the exact current patch.
- `verification-clean`: fixes to the first full are delta-clean but still need
  `terminal-full`.
- `terminal-composite-clean`: accepted findings after the second full or a
  later PR review are resolved by a clean delta chain.
- `fix-required`: accepted or newly surfaced delta findings remain.

Use only `terminal-clean` or `terminal-composite-clean` as closeout evidence.
If the same finding recurs without a substantive head change, stop with
`review-no-progress`; do not retry indefinitely.

## Commands

```bash
scripts/autoreview --mode branch --base origin/main \
  --review-phase full --evidence-output /tmp/autoreview-full.json

scripts/autoreview --mode branch --base origin/main \
  --review-phase fix-verification \
  --prior-evidence /tmp/autoreview-full.json \
  --finding-file /tmp/autoreview-findings.json \
  --evidence-output /tmp/autoreview-delta.json

scripts/autoreview --mode branch --base origin/main \
  --review-phase terminal-full \
  --prior-evidence /tmp/autoreview-delta.json \
  --evidence-output /tmp/autoreview-terminal.json

scripts/autoreview --mode branch --base origin/main \
  --review-phase disposition \
  --prior-evidence /tmp/autoreview-full.json \
  --finding-file /tmp/autoreview-rejections.json \
  --evidence-output /tmp/autoreview-disposition.json
```

Evidence files contain reports and fingerprints, not source bundles. The Git
revisions named by the evidence must remain available so the helper can
reconstruct later deltas.
