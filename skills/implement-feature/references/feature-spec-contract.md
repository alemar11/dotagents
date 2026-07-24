# Execution-Ready Feature Spec Contract

Read the complete durable Feature Spec and implementation-issue graph before
startup. Accept GitHub issues or local Markdown. Reject proposals, standalone
or incomplete Specs, missing issue graphs, planning requests, missing
`delivery_type`, and every tracker/delivery combination except GitHub plus
`github-pr`, local Markdown plus `github-pr`, or local Markdown plus
`local-branch`.

Each selected Spec must establish stable fields for:

- intended outcome and delivery type;
- authorized repository, source, target branch, and allowed paths;
- ordered issues and dependency edges;
- acceptance text, criterion count, and criterion order;
- safety constraints;
- literal validation commands plus material retry or attempt budget and required
  terminal result.

An external dependency must satisfy its stable dependency contract before the
dependent proof can become final. Ordinary peer tasks may start earlier and
collaborate while the prerequisite implementation is still converging. Final
combined proof binds every prerequisite assignment's exact repository, branch,
HEAD, and ChatGPT-created worktree evidence. GitHub input must be merged only
when the durable dependency explicitly requires it. Never use claim release alone
as dependency or combined proof.

One selected implementation Spec owns one repository, head branch, visible task,
worktree, worker, delivery result, and claim. `github-pr` additionally owns one
PR against the observed default branch; `local-branch` owns no push or provider
artifact. Its claim identity is the canonical repository plus canonical durable
`source_spec_ref`; an active head branch is also unique within that repository.
Different roots may therefore execute different Specs in the same repository
through distinct head branches and worktrees. Each root serializes its own
work: overlapping paths or issue dependencies serialize. Cross-root integration
conflict is ordinary worker-owned Git and PR evidence, not a controller path
claim.

Repository identity never selects tracker or delivery transport. A repository
identified as `github:owner/repository` may validly use a local Markdown
`source_spec_ref` and `local-branch`; source-ref validation keys from the stable
`tracker_backend` fact while terminal validation keys from `delivery_type`.

In a monorepo, one coherent Spec worker normally owns FE, BE, app, and their
integration in one worktree. In a multi-repository feature, every repo-owned
Spec carries the same canonical lowercase UUID `Feature ID` and exact normalized
`Feature Spec Set` table with columns
`feature_spec_ref | affected_repository | responsibility`. Require one globally
qualified row per member including self, deterministic repository ordering,
non-empty responsibility, exact equality across every member, and no proposed
refs. Normalize by parsing the table, trimming surrounding cell whitespace
without case folding or alias rewriting, rejecting duplicate refs or
repositories, sorting rows bytewise by `affected_repository`, and comparing
the canonical header and rows byte-for-byte. Each self row must match its
Spec's durable ref and repository. Planning Identity renders the parser-sensitive
fields exactly as `- Feature ID: \`<uuid>\`.` and
`- Repository key: \`<repository-key>\`.`. Every linked acceptance criterion
uses the exact checklist prefix
`- [ ] \`<repository-key>:ac-<NN>\` `, while every combined proof contract
contains the exact bullet
`- Proof ID: \`<repository-key>:proof-<slug>\`.`. Each ID must occur in exactly
one member body and exactly once in that member's responsibility cell as an
exact inline-code token; unbackticked IDs, prefix/suffix matches, malformed
tokens, and checklist items without a canonical ID are invalid. An
`Integration Execution Contract` requires at least one canonical Proof ID;
duplicate, missing, foreign-row, or contradictory ownership is invalid. The
root must prove this contract with read-only
`scripts/run-state --json feature-spec-set validate --input <absolute-file>`
over ephemeral complete member-body snapshots before permission, state, or
claims. The successful command's exact `manifest_feature_set` is the only
linked-set projection admitted to the run manifest, and `run start` must
revalidate those same current inputs and require exact equality before it opens
SQLite; proposed refs, validator-invalid bodies, missing or nonmatching
evidence, and hand-composed fragments are invalid. Root must re-read the
authoritative sources and replace/revalidate the snapshots if they change
before startup; the CLI stores no body hash. For a linked local member, the
validator also verifies
the exact `<feature-id>--<repository-key>/` qualifier and emits the physical
`repository_relative_spec_path` obtained by stripping it. The worker resolves
that remainder only inside its separately verified owning checkout; the
qualifier is never a directory or repository selector. The Feature Spec Set is the execution
authority; the saved-project list only proves that each named repository can
receive a worker. Existing repository workers own the combined boundaries
named by the plan and communicate directly.
Planning must assign component startup, HEAD readback, endpoint wiring, health,
validation, and cleanup to those ordinary workers without assuming a shared
filesystem. Before state, verify only that every repository can receive its
ordinary task/worktree and that the topology is complete. After those worktrees
exist, every worker stays inside its own checkout and proves distributed
peer-owned component execution. If the tasks cannot communicate or expose the
required components, the affected bundle is `blocked-app-capability`;
cross-worktree access, a dedicated integration task, controller execution, raw
worktrees, copied sources, and future manual testing are forbidden fallbacks.

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
