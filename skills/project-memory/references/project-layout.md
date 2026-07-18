# Project Layout

Use this reference when Project Memory sets, reviews, or updates the durable
project topology. This file owns only the project-level topology classification;
runtime worker choices, source-root inventories, worktree paths, and Codex App
UI state remain orchestrator-owned runtime evidence.

## Configuration

Write `project-memory/config/project-layout.md` with one human-first
configuration table:

| Key | Type | Value | Allowed values | Meaning |
| --- | --- | --- | --- | --- |
| `repository_layout` | enum | `<value>` | `single-repository`, `monorepo`, `multi-repository-workspace` | Durable project layout used by planning and orchestration workflows. |

Canonical values:

- `single-repository`: one `.git` repository and one primary project/context.
- `monorepo`: one `.git` repository with multiple independently planned
  internal projects, packages, products, or contexts.
- `multi-repository-workspace`: a parent coordination workspace with multiple child
  `.git` repositories.

## Detection

Use repo evidence first, then explicit owner instruction. Prefer `Unknown` and
ask when evidence is contradictory.

- Select `single-repository` when the current project has one Git repository and no
  strong evidence of multiple independently planned internal contexts.
- Select `monorepo` when one Git repository contains multiple internal
  projects or packages that can be planned separately, such as workspace
  manifests, multiple app/package roots, independently released packages, or
  established scoped planning boundaries.
- Select `multi-repository-workspace` when the current root coordinates multiple
  child Git repositories, especially when the parent root is not itself the
  implementation repository or when child repos keep their own project memory,
  branches, validation, commits, and PRs.

## Boundaries

- Do not store child source-root lists, Git remotes, worktree paths, thread
  IDs, worker limits, worker surfaces, dispatch state, scheduled checks, or
  publication authority here.
- Do not treat `multi-repository-workspace` as a Codex-owned workspace schema. Local
  descriptors such as `sources.json` remain probe or project documentation
  unless a current Codex product contract proves otherwise.
- Keep tracker routing in `project-memory/config/issue-tracker.md`; topology
  does not decide whether Feature Specs are local Markdown or GitHub issues.
- Keep context discovery and scope routing in root `CONTEXT.md`; topology may
  prove that a minimal routing surface is needed, but it is not domain
  vocabulary.

## Consumers

- `$plan-feature` reads `repository_layout` when planning identity, Feature Spec
  scope, affected repositories, or workspace routing depends on repo layout.
- `$implement-feature` reads `repository_layout` as factual topology while it
  derives affected repositories and managed checkouts from the Feature Spec.
- `$project-memory full-setup` creates this file when setup authority covers
  project layout. Direct layout-only updates use `memory_slice=project-layout`.
