---
name: github-workflow-contract
description: Define the GitHub metadata contract for feature-flow workflows. Use when Capture Idea, Plan Feature, or a future feature-flow skill must classify, inspect, provision, or mutate GitHub issue labels, types, or workflow states.
---

# GitHub Workflow Contract

## Purpose And Ownership

Use this skill as the semantic metadata contract for the feature workflow. It
owns the canonical artifact marker, issue-type, workflow-state, and exact
GitHub values consumed by feature-flow skills; it does not perform GitHub
operations.

- `$gitstack:github-issues` owns GitHub transport, reads, mutations, and
  read-after-write verification.
- Feature workflows resolve their repository target from the current Git remote;
  `$project-context` owns durable context and ADR memory but does not define or
  map feature-workflow labels or issue types.
- A consuming feature skill owns when its metadata is read or changed and must
  load [github-labels.md](references/github-labels.md) before doing so.

This is a transitional standalone skill. The contract is intentionally shaped
so it can later be bundled into the planned `feature-flow` plugin without
changing the consuming workflow vocabulary.

## Contract Rules

- Use only the exact canonical values and GitHub values in
  [github-labels.md](references/github-labels.md). Do not infer aliases,
  repository-local alternatives, or compatibility mappings.
- Keep semantic metadata separate from run options, issue bodies, and durable
  project context. A proposal may report intended metadata, but it must not
  mutate GitHub.
- Before any read-dependent decision, read the exact issue labels and type
  through `$gitstack:github-issues`.
- Before an authorized write, verify every required label or type value. Create
  only an exact missing label through GitStack's `create-label` operation, then
  verify it before using it. Do not provision unrelated labels.
- Apply metadata only after the owning body or issue identity has passed its
  workflow gates. Verify every mutation and resume from observed tracker state
  after an ambiguous result.
- Preserve existing label colors and descriptions when a required label
  already exists. This contract does not invent visual metadata during a
  workflow run.

## Consumers

The current consumers are deliberately narrow:

- `capture-idea` reads and, when authorized, writes `idea` and the optional
  `needs-triage` labels. It never assigns an issue type to an Idea.
- `plan-feature` reads and, when authorized, writes the Idea lifecycle labels,
  the `feature` and `task` type labels, and `ready-for-agent`.
- `implement-feature` currently does not read or write this metadata contract;
  its workers update execution checkboxes and other tracker state through their
  own GitStack boundary. Add this dependency only when the implementation
  workflow gains explicit metadata behavior.

Do not make a workflow depend on this skill merely because it reads ordinary
GitHub issues. Add the dependency when it uses the feature metadata listed in
the contract.
