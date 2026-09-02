# GitHub Delivery Status

Before any shell command that may contact GitHub, read and follow
[Network execution](../../network-execution.md). Before the first
direct `gh` or shared CLI call, load
[G to gh Runtime Preflight](../../gh-dependency-preflight.md).

## Role

Own the provider-facing, read-only delivery-status boundary for one pull
request. Preserve GitHub's original fields and add one conservative normalized
classification. Do not decide caller-owned acceptance, implementation, review,
or release policy.

Use the `<skill-root>` resolved by the active G entrypoint. From the
skill root, run:

```sh
scripts/g --json pr delivery-status \
  --repo <owner/repository> \
  --pr <number> \
  --expected-head <full-sha>
```

Require `--expected-head` when a composing workflow binds evidence to one
candidate commit. It is optional for general inspection. Read
[workflows.md](workflows.md) for the complete read and recovery
sequence and [../../states.md](../../states.md) for fields and
classification semantics.

## Output contract

Require the stable JSON envelope and inspect:

- `identity`, including exact-head equality;
- `lifecycle` and draft state;
- `technical_mergeability` and provider `mergeStateStatus`;
- policy rules, checks, review decision, and unresolved threads;
- repository and PR automation state;
- closing issue references;
- `classification.disposition`, attribution, blockers, pending evidence, and
  warnings;
- `completeness` and every unavailable provider surface.

Use the canonical dispositions and completeness rules from `../../states.md`.
Treat `unknown` and incomplete evidence as non-terminal unless the composing
workflow explicitly owns a narrower evidence rule.

Auto-merge capability, an existing PR auto-merge request, or a merge-queue
entry are observations, not authorization and not blockers by themselves.
Report them under `automation` without enabling, disabling, enqueueing,
dequeueing, or merging anything.

## Safety boundary

This workflow has no mutation mode. Never merge, bypass protections, update a
branch, enable or disable auto-merge, enqueue or dequeue a PR, request a review,
resolve a thread, rerun CI, or edit hosted content. Route separately authorized
operations to their focused G owner.

Preserve unfamiliar provider enum values in the evidence and classify them as
`unknown` rather than guessing. A successful read with a non-ready disposition
still exits successfully; transport, authentication, invalid input, and
unreadable provider responses are command failures.

## CLI maintenance

Normal execution uses `<skill-root>/scripts/g`. Open
`<skill-root>/projects/g/` only to extend or repair the shared runtime, then
run its standard-library tests, rebuild the shipped artifact, and verify
`--help`, `--version`, `--json doctor`, and one read-only delivery-status call.
`projects/g/pyproject.toml` is the standalone CLI version source of truth;
runtime changes use semantic versioning and keep the package, source version,
tests, and shipped artifact aligned.
