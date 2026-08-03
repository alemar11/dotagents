# Implement Execution-Ready Feature Spec Contract

Read the complete durable GitHub Feature Spec and implementation-issue graph
before startup. Reject proposals, standalone or incomplete Specs, planning
requests, and any source or delivery transport other than a GitHub Issue and a
reviewed GitHub PR.

Each selected Spec must establish stable fields for:

- intended outcome and GitHub PR delivery;
- authorized repository, source, target branch, and allowed paths;
- ordered issues and dependency edges;
- acceptance text, criterion count, and criterion order;
- safety constraints;
- literal validation commands plus material retry or attempt budget and required
  terminal result.

## Stable Source Mutation Ownership

This table is the canonical execution-time write contract for the stable fields
above:

| actor | stable_field_write |
| --- | --- |
| `external-planning-owner` | `allowed` |
| `implement-feature-root` | `forbidden` |
| `implement-feature-worker` | `forbidden` |

`external-planning-owner` means a human tracker owner or a separately invoked
planning workflow operating outside the active `$se:implement` run. A
direct user message to the active root or worker does not change that actor's
role and does not grant planning authority.

The only active-run mutation route is the externally owned semantic repair in
`contract-repair-orchestration.md`. Root may invoke a separate SE Feature task
with the portable request, but root and worker still cannot author the change.
A successful result resumes the same assignment only when execution identity
remains compatible; otherwise that assignment is superseded and replaced.

When a stable field conflict is proven, root and worker stop as
`blocked-contract-repair` and report the exact conflicting source and field.
They must not edit the GitHub Feature Spec, implementation issue, or stable section,
including through G. The same root retains the run and claim while the
assignment is blocked. After an external planning owner publishes a correction,
the root rereads the complete authoritative Spec and issue graph and records the
exact durable-source readback. It may resume the existing assignment through the
normal recovery transition only when that readback restores the exact stable
contract already accepted by the run. A repaired contract that changes
repository, source identity, target branch, or claim compatibility cannot be
rebound to the retained assignment; it uses formal supersession and normal
replacement claim/bootstrap after the worker preserves useful HEAD evidence.
The recovery follow-up carries source identity and readback evidence only; it
does not draft, reinterpret, or prescribe the planning change.

An external dependency must satisfy its stable dependency contract before the
dependent proof can become final. Ordinary peer tasks may start earlier and
collaborate while the prerequisite implementation is still converging. Final
combined proof binds every prerequisite assignment's exact repository, branch,
HEAD, and ChatGPT-created worktree evidence. GitHub input must be merged only
when the durable dependency explicitly requires it. Never use claim release alone
as dependency or combined proof.

One selected implementation Spec owns one repository, head branch, visible task,
worktree, worker, GitHub PR delivery result, and claim. The PR targets the
observed default branch. Its claim identity is the canonical repository plus
canonical durable `source_spec_ref`; an active head branch is also unique within
that repository.
Different roots may therefore execute different Specs in the same repository
through distinct head branches and worktrees. Each root serializes its own
work: overlapping paths or issue dependencies serialize. Cross-root integration
conflict is ordinary worker-owned Git and PR evidence, not a controller path
claim.

Repository identity is always `github:owner/repository`, and every
`source_spec_ref` is the matching GitHub Issue ref or canonical URL.

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
before startup; the CLI stores no body hash. The Feature Spec Set is the execution
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
- compatible clarifications in explicitly mutable execution sections that do
  not reinterpret a stable field;
- progress, evidence, and status text;
- checkbox markers whose underlying acceptance text, count, and order did not
  change.

For any stable semantic conflict, stop editing at the conflict boundary and
report the structured request from `contract-repair-orchestration.md`. This
includes path, outcome, delivery, repository/source/branch authority,
dependency, acceptance, safety, and material validation contradictions.
Compare authoritative stable sections directly. Do not create body, contract,
result, assignment-packet, or message hashes.
