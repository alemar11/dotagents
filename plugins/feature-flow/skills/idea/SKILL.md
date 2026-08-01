---
name: idea
description: Manually capture one or more discussed proposals as durable GitHub Ideas for later planning, clarifying only material intake gaps.
---

# Idea

## Purpose And Invocation

Use this capture-only skill to save tentative proposals after a discussion so
they can be selected later as explicit input to a planning workflow. The public
pipeline is:

`Idea -> Plan -> Implement Feature`

Use this skill only when the user invokes `$idea`, asks to run Idea, or a
manually invoked parent workflow explicitly routes here. Do not
auto-select it for ordinary brainstorming, discussion, planning, issue
creation, or implementation requests. After reporting the captured Ideas,
stop.

Idea does not create Feature Specs or implementation issues, plan the
proposal, modify domain memory, make architecture decisions, or implement
anything. It preserves an early proposal without claiming that the proposal is
approved, specified, or ready for work.

## Structured Option Contract

Load the shared [options.md](../../references/options.md) before resolving capture behavior. It
owns the complete selectable registry:

Reject every unregistered field or noncanonical value. Explicit repository
scope, tracker owner, feature metadata values, candidate decisions, names,
slugs, and refs are execution facts or data, not options.

## Fixed Capture Contract

- Every Idea has exactly one tracker-owning repository. Use globally
  unambiguous durable refs: `owner/repository#<number>` or a canonical hosted
  URL.
- The Feature Flow workflow contract owns the `idea` artifact marker and its
  GitHub label transport. Explicit user scope owns the repository set; each Idea
  then names one tracker-owning repository. Load the contract and reject
  missing or incompatible metadata; do not define fallback taxonomy or silently
  write setup files.
- A GitHub Idea is an open issue titled `Idea: <Name>`, has the contract's
  `idea` label, and has native Issue Type unset.
- Capture creates an Idea with only the `idea` label. Open questions in the body
  do not imply `needs-info` or any other workflow state.
- Resolve every candidate decision, tracker owner, duplicate, and collision
  before the first write. A later write failure may produce a verified partial
  result, but unresolved input must not.
- In `run_mode=preview`, return proposed bodies, intended targets and
  metadata, and deterministic `proposed-idea:` refs without mutating GitHub.
  Proposed refs are non-durable and must never be presented as valid Plan
  Feature input.
- Capture only the accepted proposal. Do not add a planning analysis, domain
  knowledge handoff, Feature Spec fields, acceptance criteria invented by the
  agent, implementation scope, or readiness claim.
- When an accepted proposal is not yet faithfully capturable, use only the
  lightweight Idea profile from the internal clarification protocol. It may
  refine intake facts but never turns Idea into planning or knowledge capture.

## Runtime Dependency

Idea is Codex-dependent because its authoritative GitHub reads and
writes use `$gitstack:github-issues`. When Codex provides `request_user_input`,
it is an optional accelerator for multi-candidate selection; load
[multi-idea-selection.md](references/multi-idea-selection.md) and preserve its
semantics exactly. In runtimes without that tool, use the documented plain
one-question-at-a-time fallback.

## Composed Skills

| Skill | Load when | Boundary |
| --- | --- | --- |
| Feature Flow workflow contract | Idea reads or writes Idea metadata. | Load the exact `idea` contract value; Idea owns when it is applied, and never edits the contract at runtime. |
| `$gitstack:github-issues` | Idea needs exact issue or label reads, or `run_mode=publish` authorizes publication. | Pure preflight reads are allowed in either write mode and omit mutation fields. For writes, translate each operation to GitStack-owned `mutation_mode=apply`, the exact target, and one canonical `issue_operation`. GitStack owns safe transport, label administration, issue creation, verification, and partial recovery. |

In `run_mode=preview`, allow only read-only GitHub inspection; do not request
a dry-run mutation, return executable commands, or perform any write.

## Workflow

### 1. Resolve Write Mode And Setup

Resolve `run_mode` once from [options.md](../../references/options.md). Read:

- the current repository's GitHub remote, resolved to one exact
  `owner/repository` target;
- the `workflow contract` and its
  [workflow-contract.md](../../references/workflow-contract.md).

Use explicit user scope and repository evidence to determine the only valid
tracker-owning Git repository for each possible Idea. A cross-repository Idea
must name one canonical owning repository; optional qualified backlinks may
appear elsewhere. Do not infer ownership from the current Codex task, the
ChatGPT App primary project or saved-project list, or filesystem proximity.

Require the contract's exact `idea` label and confirm that Ideas use no native
Issue Type. If the contract or GitHub remote is missing, stale, contradictory,
or ambiguous, stop before capture writes and report the exact prerequisite. Do
not repair either contract implicitly.

### 2. Extract And Normalize Candidates

Identify the distinct proposals actually discussed in the supplied session or
input. For each candidate, derive a concise name, lowercase kebab-case
`idea_slug`, tracker owner, summary, problem or opportunity, proposed
direction, expected value, known context and constraints, open questions, and
portable source evidence.

Deduplicate candidates by intended outcome and substantive proposal, not title
alone. Do not split wording variants into separate Ideas. Do not merge
proposals whose outcomes, owners, or later planning boundaries materially
differ.

If no concrete proposal exists, report that nothing was captured. If exactly
one candidate exists, an explicit Idea request authorizes saving it
without another confirmation. If more than one remains, run the selection
contract from
[multi-idea-selection.md](references/multi-idea-selection.md) before continuing.

After selection, if the accepted set still has one material capture gap in its
problem or opportunity, expected value, or proposal boundary,
load [clarification-protocol.md](../../references/clarification-protocol.md) and
run its Idea profile before preflight. Do not invoke it merely to improve
wording. Apply the answer only to transient capture facts, preserve remaining
nonblocking uncertainty in `Open Questions`, and stop when no concrete proposal
can be resolved without invention. Candidate selection, tracker ownership,
duplicate detection, and collision resolution remain owned by their existing
Idea branches.

### 3. Preflight The Entire Accepted Set

Before any write:

1. Resolve every accepted candidate's final name, slug, body, and one tracker
   owner.
2. Render its body with [idea-template.md](references/idea-template.md).
3. Derive its target and globally unambiguous applied or proposed ref.
4. Inspect the target tracker for equivalent open Ideas, title collisions, and
   label availability.
5. Treat an existing artifact as an exact equivalent only when its proposal,
   tracker owner, canonical marker, type absence, and workflow state are
   compatible. Reuse that durable ref and do not create a duplicate.
6. When the same title or slug has materially different content or
   incompatible metadata, ask whether to reuse, rename, or revise. Never
   overwrite or silently reclassify a colliding issue.
7. Recheck names, slugs, targets, and equivalence after any rename, merge, or
   split. Resolve all resulting collisions before publication starts.

Perform these preflight reads through `$gitstack:github-issues` without mutation
fields in both write modes. Proposal mode still requires current duplicate and
label evidence even though it cannot change that evidence.

For `run_mode=preview`, stop after returning the complete proposed bodies,
targets, intended marker/state metadata, non-durable refs, and publication
order. Do not return executable tracker commands.

### 4. Publish To GitHub

For `run_mode=publish`, load
[github-publishing.md](references/github-publishing.md). Publish each accepted,
non-reused Idea through `$gitstack:github-issues`, checkpointing and verifying
each result before moving to the next candidate.

### 5. Recover And Report

If publication fails after any mutation, stop the batch. Inspect current
tracker state, distinguish verified created or reused artifacts from missing
operations, and retry only operations proven absent. Never replay the complete
batch from stale assumptions.

Report each candidate as `created`, `reused`, `proposed`, `skipped`, or
`failed`, with its tracker owner, name, and durable or proposed ref. Clearly
mark proposals as non-durable. On partial failure, list the exact verified refs
already created and the remaining safe resume work.

End after capture reporting. Planning and source-Idea lifecycle transitions
belong to Plan, not Idea.
