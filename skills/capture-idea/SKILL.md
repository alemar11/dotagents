---
name: capture-idea
description: Manually capture one or more discussed proposals as durable local or GitHub Ideas for later planning.
---

# Capture Idea

## Purpose And Invocation

Use this capture-only skill to save tentative proposals after a discussion so
they can be selected later as explicit input to a planning workflow. The public
pipeline is:

`Capture Idea -> Plan Feature -> Implement Feature`

Use this skill only when the user invokes `$capture-idea`, asks to run Capture
Idea, or a manually invoked parent workflow explicitly routes here. Do not
auto-select it for ordinary brainstorming, discussion, planning, issue
creation, or implementation requests. After reporting the captured Ideas,
stop.

Capture Idea does not create Feature Specs or implementation issues, plan the
proposal, modify domain memory, make architecture decisions, or implement
anything. It preserves an early proposal without claiming that the proposal is
approved, specified, or ready for work.

## Structured Option Contract

Load [options.md](references/options.md) before resolving capture behavior. It
owns the complete selectable registry:

| Field | Values |
| --- | --- |
| `write_mode` | `apply`, `propose` |

Reject every unregistered field or noncanonical value. Tracker backend,
explicit repository scope, tracker owner, marker and state mappings, candidate
decisions, names, slugs, paths, refs, and queue intent are execution facts or
data, not options.

## Fixed Capture Contract

- Every Idea has exactly one tracker-owning repository. Use globally
  unambiguous durable refs: `owner/repository#<number>` or a canonical hosted
  URL for GitHub, and
  `<repository-slug>/planning/ideas/<idea-slug>.md` for local storage. A bare
  local path is acceptable only as an additional same-repository display path.
- Project Memory owns tracker routing, the `idea` artifact marker mapping,
  workflow-state mappings, and their explicit transports. Explicit user scope
  owns the repository set; each Idea then names one tracker-owning repository.
  Require `label` for GitHub marker/state rows and `local-header` for local
  rows; reject missing or incompatible transports. Consume configured facts;
  do not define fallback taxonomy or silently write setup files.
- A GitHub Idea is an open issue titled `Idea: <Name>`, has the configured
  `idea` label, and has native Issue Type unset. A local Idea lives at
  `planning/ideas/<idea-slug>.md`, begins with `# Idea: <Name>`, and has exactly
  one `artifact_marker: idea` line in its header metadata region. It never has
  an `issue_type` line.
- Capture creates a dormant Idea by default. Add `needs-triage` only when the
  user explicitly queues that candidate for evaluation. At capture time,
  `needs-triage` is the only allowed workflow state. Open questions in the body
  do not imply `needs-info` or any other label or state.
- Resolve every candidate decision, tracker owner, duplicate, and collision
  before the first write. A later write failure may produce a verified partial
  result, but unresolved input must not.
- In `write_mode=propose`, return proposed bodies, intended targets and
  metadata, and deterministic `proposed-idea:` refs without writing files or
  mutating GitHub. Proposed refs are non-durable and must never be presented as
  valid Plan Feature input.
- Capture only the accepted proposal. Do not add a planning analysis, domain
  knowledge handoff, Feature Spec fields, acceptance criteria invented by the
  agent, implementation scope, or readiness claim.

## Runtime Portability

Capture Idea is Codex-aware but portable. When Codex provides
`request_user_input`, it is an optional accelerator for multi-candidate
selection; load
[multi-idea-selection.md](references/multi-idea-selection.md) and preserve its
semantics exactly. In runtimes without that tool, use the documented plain
one-question-at-a-time fallback. The core capture and tracker contracts do not
depend on Codex-only tools.

## Composed Skills

| Skill | Load when | Boundary |
| --- | --- | --- |
| `$project-memory` | Required tracker routing or Idea marker mapping is missing, stale, or contradictory. | Inspect or run the matching setup slice only when separately authorized in the same request. Otherwise stop with the exact prerequisite; Capture Idea never performs implicit setup writes. |
| `$gitstack:github-issues` | The resolved tracker backend is GitHub and Capture Idea needs exact issue or label reads, or `write_mode=apply` authorizes publication. | Pure preflight reads are allowed in either write mode and omit mutation fields. For writes, translate each operation to GitStack-owned `mutation_mode=apply`, the exact target, and one canonical `issue_operation`. GitStack owns safe transport, label administration, issue creation, verification, and partial recovery. |

Do not invoke GitStack for local storage. In `write_mode=propose`, allow only
read-only GitHub inspection; do not request a dry-run mutation, return
executable commands, or perform any write.

## Workflow

### 1. Resolve Write Mode And Setup

Resolve `write_mode` once from [options.md](references/options.md). Read the
selected memory-owning root's:

- `project-memory/config/issue-tracker.md`;
- `project-memory/config/triage-labels.md`.

Use explicit user scope and repository evidence to determine the only valid
tracker-owning Git repository for each possible Idea. A cross-repository Idea
must name one canonical owning repository; optional qualified backlinks may
appear elsewhere. Do not infer ownership from the current Codex task, the
ChatGPT App primary project or saved-project list, or filesystem proximity.

Require an explicit configured mapping for `artifact_marker: idea`. For the
GitHub backend, require transport `label`, its concrete `idea` label mapping,
and `label` for any consumed workflow-state row; confirm that Ideas use no
native Issue Type. For the local backend, require `local-header`, the canonical
marker, and local path convention. If a required fact is missing, stale,
contradictory, or ambiguous, stop before capture writes and report the exact
Project Memory setup prerequisite. Do not repair configuration unless the same
request separately authorizes Project Memory setup.

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
one candidate exists, an explicit Capture Idea request authorizes saving it
without another confirmation. If more than one remains, run the selection
contract from
[multi-idea-selection.md](references/multi-idea-selection.md) before continuing.

### 3. Preflight The Entire Accepted Set

Before any write:

1. Resolve every accepted candidate's final name, slug, body, queue intent, and
   one tracker owner.
2. Render its body with [idea-template.md](references/idea-template.md).
3. Derive its target and globally unambiguous applied or proposed ref.
4. Inspect the target tracker for equivalent open Ideas, title collisions,
   label availability, and local path collisions.
5. Treat an existing artifact as an exact equivalent only when its proposal,
   tracker owner, canonical marker, type absence, and queue state are
   compatible. Reuse that durable ref and do not create a duplicate.
6. When the same title, slug, or path has materially different content or
   incompatible metadata, ask whether to reuse, rename, or revise. Never
   overwrite an existing local Idea or silently reclassify a hosted issue.
7. Recheck names, slugs, targets, and equivalence after any rename, merge, or
   split. Resolve all resulting collisions before publication starts.

For GitHub, perform these preflight reads through
`$gitstack:github-issues` without mutation fields in both write modes. Proposal
mode still requires current duplicate and label evidence even though it cannot
change that evidence.

For `write_mode=propose`, stop after returning the complete proposed bodies,
targets, intended marker/state metadata, non-durable refs, and publication
order. Do not return executable tracker commands.

### 4. Publish Through The Resolved Backend

For GitHub `apply`, load
[github-publishing.md](references/github-publishing.md). Publish each accepted,
non-reused Idea through `$gitstack:github-issues`, checkpointing and verifying
each result before moving to the next candidate.

For local `apply`, load
[local-publishing.md](references/local-publishing.md). Create each accepted,
non-reused Idea only at its canonical new path, then read it back and validate
the title, header metadata, sections, and durable qualified ref.

### 5. Recover And Report

If publication fails after any mutation, stop the batch. Inspect current
tracker state, distinguish verified created or reused artifacts from missing
operations, and retry only operations proven absent. Never replay the complete
batch from stale assumptions.

Report each candidate as `created`, `reused`, `proposed`, `skipped`, or
`failed`, with its tracker owner, name, queue intent, and durable or proposed
ref. Clearly mark proposals as non-durable. On partial failure, list the exact
verified refs already created and the remaining safe resume work.

End after capture reporting. Planning and source-Idea lifecycle transitions
belong to Plan Feature, not Capture Idea.
