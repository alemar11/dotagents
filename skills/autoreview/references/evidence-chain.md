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

Do not calculate `finding_id`. Start with `scripts/autoreview --json findings
template`, fill only the authoritative finding, disposition, and reason fields,
set `template=false`, then run `findings prepare`. AutoReview's existing finding
validator and fingerprint implementation are the sole owners of the generated
id. Preparation makes no Codex call and consumes no review budget.

Pass the prepared `--finding-file <path>` for every fix verification. The file is strict:

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

Repository, base, or review-scope drift invalidates the lineage. A merge-base
SHA change preserves it only when the canonical reviewed patch fingerprint and
scope remain equivalent; otherwise explicit lineage-reset authority is
required. A new lineage starts with `full`; never disguise semantic target
drift as a fix delta.

Composing workflows invoke the ordinary AutoReview surface with an exact
committed target and may journal that request and result in their own state
store. AutoReview never discovers authority from or writes into a caller's
state. Publication facts attach to the existing clean committed revision and
do not reset lineage.

## Bounded Invalid-Output Recovery

This is a `[Medium][Edge case]` learned from two monitored runs, not a general
review-loop redesign. After a successful engine launch returns output that
fails only schema parsing or a semantic result invariant, a managed invocation
may make exactly one internal repair launch. It keeps the reservation, target,
phase, evidence parent, finding set, bundle, model, and web-search policy fixed.
The helper-owned appendix is at most 2 KiB and states only the validator code,
violated rule, and instruction to reuse the supplied immutable context.

Transport, timeout, cancellation, cleanup, filesystem, protocol, reservation,
target, lineage, or finding-identity failures never repair. Valid clean results
and valid actionable findings never repair. Reviewer output is stream-hashed
before loading, capped at 128 KiB, and represented in the append-only attempt
journal by its exact hash, size, classification, validator code, bounded
preview/artifact reference, prompt fingerprints, and `model_launch_count`.
The evidence schema and logical `counts.model_calls` remain `2.0.0` semantics;
the external attempt journal is `2.1.0` and counts physical launches.

Before every append, the helper replays the exact journal schema, identity,
parent fingerprint chain, transitions, and monotonic launch count. A second
invalid response appends terminal failure, consumes the reservation as
`consumed-failed`, emits no candidate or clean gate, and returns
`recovery=needs-owner`. A consumed-failed exact operation cannot reserve again.
Process interruption after either launch also cannot relaunch.

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

These explicit phase commands are standalone-only. Managed Implement Feature
runs use the reserved packet and artifact paths emitted by its manifest.

```bash
scripts/autoreview --json findings template --finding-source codex-review \
  --output /tmp/autoreview-finding-draft.json

scripts/autoreview --json findings prepare \
  --input /tmp/autoreview-finding-draft.json \
  --output /tmp/autoreview-findings.json

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
