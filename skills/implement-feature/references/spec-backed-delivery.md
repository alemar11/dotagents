# Execution-Ready Feature Spec Contract

Read the complete durable Feature Spec and implementation-issue graph before
startup. Accept GitHub issues or local Markdown. Reject proposals, standalone or
incomplete Specs, missing issue graphs, planning requests, and delivery types
other than one PR per Spec against its repository's default branch.

Each selected Spec must establish stable fields for:

- intended outcome and delivery type;
- authorized repository, source, target branch, and allowed paths;
- ordered issues and dependency edges;
- acceptance text, criterion count, and criterion order;
- safety constraints;
- literal validation commands plus material retry or attempt budget and required
  terminal result.

Every cross-Spec dependency must already be merged and integration-proven.
An unmerged dependency remains outside the run even when the upstream worker has
reached PR-ready and released its Feature Spec claim. Never use claim release as
merge proof.

One selected Spec owns one repository, head branch, App worktree, worker, PR,
and claim. Its claim identity is the canonical repository plus canonical durable
`source_spec_ref`; an active head branch is also unique within that repository.
Different roots may therefore execute different Specs in the same repository
through distinct head branches and worktrees. Each root serializes its own
work: overlapping paths or issue dependencies serialize. Cross-root integration
conflict is ordinary worker-owned Git and PR evidence, not a controller path
claim.

## Drift Classification

Workers reread the current Spec and issues before each issue, after recovery,
and before final verification. They may autonomously accept these compatible
operational changes when the stable fields above remain intact:

- implementation approach or internal technical design;
- safer or simpler rewrites;
- additional or equivalent tests;
- compatible clarifications;
- progress, evidence, and status text;
- checkbox markers whose underlying acceptance text, count, and order did not
  change.

Stop as `blocked-durable-contract` without asking when outcome, delivery type,
repository/path/source/branch authority, dependency structure, acceptance text
or shape, safety, or a material validation budget/terminal result changes.
Compare authoritative stable sections directly. Do not create body, contract,
result, assignment-packet, or message hashes.
