---
name: idea
description: "Capture concrete proposals from the current session as tentative GitHub Ideas for later planning. Use only after an explicit request to save or preview an Idea; do not trigger for ordinary brainstorming."
---

# Idea Capture

## Purpose and boundary

Use `se2:idea` only after an explicit request to capture, select, save, or
preview an Idea from the current session or supplied input. It first builds a
transient in-memory capture bundle from the relevant session context, then
uses that same bundle for preview or verified hosted output. It preserves a
tentative proposal for later Feature planning and then stops.

The workflow is:

`Idea -> Feature -> Implement`

Idea capture does not write Feature Specs, acceptance criteria, implementation
plans, task graphs, project memory, architecture decisions, or code. It does
not create an application task, select a model profile, or delegate to another
task. Ordinary brainstorming must never create or prepare a durable Idea
implicitly.

The in-memory bundle is run state, not durable project memory. It may contain
the selected source excerpts, normalized candidates, decisions, target
repositories, rendered bodies, preflight observations, publication order, and
verified results. Discard it after the terminal capture report unless the
hosted issue itself is the explicitly authorized durable output.

## Workflow overview

The first three stages are local. Only the `publish` terminal branch may load
G or inspect and mutate GitHub state.

~~~mermaid
flowchart LR
    capture["Capture session"] --> normalize["Normalize candidates"]
    normalize --> freeze["Freeze local bundle"]
    freeze --> terminal{"Terminal operation"}
    terminal -->|"preview"| report["Local report<br/>proposed-idea:"]
    terminal -->|"publish"| preflight["G preflight"]
    preflight --> hosted["Hosted duplicate and collision checks"]
    hosted --> mutate["Create or reuse Idea"]
    mutate --> verify["Readback and recovery"]
~~~

## Run contract

Resolve `run_mode` once at the start. The only accepted values are:

- `preview`: calculate and report proposed Ideas without hosted mutations;
- `publish`: publish authorized Ideas and verify each hosted result.

Resolve an explicit request to inspect, draft, or avoid writes as `preview`.
Resolve an explicit request to save or create durable Ideas as `publish`.
Never silently upgrade, downgrade, or invent aliases for these values. If the
request does not establish publication authority, use `preview` and state that
the refs are non-durable.

The workflow contract in
[`../../references/workflow-contract.md`](../../references/workflow-contract.md)
owns the exact Idea marker and metadata. Load it before resolving hosted
metadata; do not repair or redefine it during a run.

## Dependency boundary

All hosted issue and label reads and writes belong to the repository's
G-owned GitHub issue workflow. Do not call a provider API directly, construct
an alternative transport, or return executable provider commands to the user.
Capture and preview are fully local: they must not load G, inspect hosted
issues or labels, or claim current hosted duplicate/collision state.

Only after `run_mode=publish` is resolved, before its first hosted read or
write, load
[`../../references/codex-dependency-preflight.md`](../../references/codex-dependency-preflight.md)
and complete its read-only availability gate. If the required G workflow is
missing, disabled, malformed, or unresolvable, fail closed before hosted
access; remediation is advisory and must never install, enable, refresh, or
substitute the dependency.

The dependency gate authorizes the next workflow handoff only. It does not
authorize publication. `publish` still requires explicit user authority for
the resolved Idea operations.

## Workflow

### 1. Resolve the source and repository

Use the current session or supplied input as source evidence. Resolve one exact
tracker-owning repository for every candidate from explicit user scope and
repository evidence. A task identity, saved project, filesystem location, or
display title is not repository ownership evidence.

For each candidate, keep a portable source description. Do not publish local
absolute paths, private prompt machinery, or irrelevant transcript fragments.

### 2. Extract and normalize candidates

Identify only concrete proposals actually present in the session or supplied
input. For each candidate, derive:

- a concise human name and deterministic lower-kebab `idea_slug`;
- exactly one tracker-owning repository;
- the summary, problem or opportunity, proposed direction, expected value,
  known context and constraints, open questions, and portable source evidence.

Deduplicate by substantive intended outcome, not by title wording. Do not merge
proposals whose outcomes, owners, or planning boundaries materially differ.
Preserve tentative language and unknowns. Do not add goals, non-goals,
acceptance criteria, implementation scope, dependencies, readiness, or
planning conclusions.

Keep these facts in one transient capture bundle for the rest of the run:

- the portable source snapshot and its provenance;
- the normalized candidate set and selection decisions;
- the resolved tracker owner for each candidate;
- rendered bodies and intended publication order;
- duplicate, equivalence, collision, and metadata observations;
- preview refs or verified hosted results.

Do not persist this bundle as project memory or split it across unrelated
artifacts. Reconcile it after every user decision or hosted operation before
continuing.

If no concrete proposal exists, report that nothing was captured and stop. If
one candidate exists and the request explicitly authorizes capture, do not ask
for a redundant confirmation. If several candidates remain, ask one focused
selection question and capture only the selected set. If one selected proposal
has a material gap in its problem, value, or direction, ask at most one
lightweight intake question; preserve any remaining non-blocking uncertainty
under `Open Questions`.

Read [`references/idea-template.md`](references/idea-template.md) when
rendering the canonical body. Keep its seven sections in order and do not add
planning sections.

### 3. Freeze the local accepted set

Complete the local capture bundle before choosing the terminal operation:

1. finalize every candidate's name, slug, body, owner, target, and intended
   metadata;
2. confirm that every candidate has exactly one tracker owner and portable
   source evidence;
3. derive its deterministic `proposed-idea:` ref for preview or retain the
   publication identity as unresolved until publish;
4. recheck all candidates after any user-directed rename, merge, or split.

Do not inspect hosted issues, labels, native Issue Types, or current duplicate
and collision state in this phase. Those checks belong to the publish terminal
operation. Preview must report that hosted equivalence and collision evidence
was not consulted rather than claiming that no conflict exists.

### 4. Preview or publish

For `run_mode=preview`, return the relevant in-memory bundle contents: each
candidate's intended target, title, canonical body, metadata, publication
order, and deterministic `proposed-idea:` ref. Mark every proposed ref
non-durable. Do not load the G dependency preflight, read GitHub, request a
dry-run mutation, or perform any hosted operation.

For `run_mode=publish`, load
[`references/publishing.md`](references/publishing.md). Hand off only the
normalized issue operation owned by the G workflow. The publication reference
performs the dependency preflight, current hosted duplicate/collision checks,
metadata checks, mutations, and readback only after the local bundle is
complete. Use the already reconciled in-memory bundle as the publication
source, and verify each result before moving to the next candidate. The hosted
issue is the durable output; the bundle remains transient.

### 5. Recover and report

If a hosted operation is ambiguous or partially succeeds, stop the batch and
reconcile the current hosted state. Distinguish verified created, reused,
missing, and failed operations. Retry only an operation proven absent; never
replay the entire batch from stale assumptions.

Report every selected candidate as `created`, `reused`, `proposed`, `skipped`,
or `failed`, with its owner, name, and qualified durable or explicitly
non-durable ref. Report blockers and safe resume work precisely. Stop after
capture reporting.

## Safety and independence

- Keep this skill self-contained and independent from other Idea skill
  implementations; do not import, alias, copy, or modify them.
- Keep GitHub transport in the existing G-owned issue workflow.
- Keep GitHub completely outside capture and preview; hosted state is a
  terminal publish concern.
- Keep caller publication authority separate from dependency availability.
- Never treat a preview ref as a hosted identity.
- Never infer ownership from task metadata or filesystem proximity.
- Never replay an uncertain mutation blindly.
- Do not add a model-index row: this skill runs in the invoking task and does
  not create or delegate an application task.
