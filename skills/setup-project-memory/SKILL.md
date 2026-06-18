---
name: setup-project-memory
description: Configure or refresh project-memory for code repos, monorepos, and orchestrator workspaces. Use when setting up a fresh repo, bootstrapping an already-used repo from repo evidence and recent local session history, or configuring AGENTS.md pointers, issue-tracker instructions, triage mappings, CONTEXT.md, and ADR layout before planning, PRD, issue-splitting, triage, grill-me-with-context, or architecture-improvement skills.
---

# Setup Project Memory

## Goal

Configure the project memory that other skills can rely on:

- `AGENTS.md` as the only agent-instruction file this skill writes.
- `project-memory/agents/issue-tracker.md` for where PRDs and issues live.
- `project-memory/agents/triage-labels.md` for canonical issue-type and
  triage-state mappings.
- `project-memory/agents/domain.md` for where `CONTEXT.md`, `CONTEXT-MAP.md`,
  and ADRs live.
- `CONTEXT.md` and `project-memory/adr/` as optional seeded domain memory when
  an existing project has strong repo or session evidence.

This is a setup skill. Run it once per code repo, monorepo, or orchestrator
workspace before using workflows that publish PRDs, split issues, triage
incoming work, or update project-backed domain memory.
Re-run it when the issue tracker, issue-type vocabulary, triage vocabulary, or
domain-memory layout
changes, or when an already-used project needs its existing knowledge migrated
into the project-memory structure.

## Hard Boundaries

- Always use `AGENTS.md` for setup pointers and project-memory routing when an
  agent-instruction file is needed.
- Load and follow `$domain-modeling` before creating or updating `CONTEXT.md`
  or ADRs.
- Seed `CONTEXT.md` or ADRs only from strong evidence: repo docs, code,
  tests, committed behavior, final session summaries, or explicit user
  acceptance.
- Never record tentative proposals, rejected ideas, secrets, raw logs, broad
  doctrine, or weak inferences from session text.
- Do not create empty `project-memory/adr/` directories just to show intent.
  Create only files with useful content.
- In orchestrator workspace mode, keep setup config-only: configure root setup
  files only. Root `AGENTS.md`, `project-memory/agents/*`, `CONTEXT.md`, and
  ADR layout are allowed when useful, but do not create `projects/<project>/`,
  feature PRDs, or issue files during setup.
- Do not treat an orchestrator workspace as a monorepo. It coordinates
  external repos; those repos keep their own project memory, validation,
  branches, commits, and PRs.
- Ask for confirmation before writing files.

## Workflow

### 1. Choose setup mode

Use one of three modes:

- **Fresh setup**: the repo has little or no prior project-memory structure and
  the goal is to configure `AGENTS.md` plus `project-memory/agents/*`, even if
  the repo already has starter code, README files, tests, or package manifests.
- **Existing-project bootstrap**: the repo already has code, docs, issues,
  prior agent sessions, or partial project-memory files, and the goal is to
  infer the setup plus seed `CONTEXT.md` and ADRs from strong evidence.
- **Orchestrator workspace**: the current folder is a parent coordination
  workspace used to plan and run Codex across multiple independent repos. It
  owns cross-repo PRDs, vertical feature issues, repo pointer sheets, and
  integration gates, but not product code.

Default to fresh setup when the user only needs tracker, triage, and domain
memory routing, even in a non-empty repo. Use existing-project bootstrap only
when the user wants accepted repo knowledge migrated or seeded into
`CONTEXT.md` or ADRs, or when partial project-memory/domain files already need
reconciliation. Recommend orchestrator workspace when the folder has no clear
single codebase but contains or is intended to contain `projects/`, repo
pointer docs, symlinks/worktrees to external repos, or cross-repo planning
artifacts.

### 2. Inspect the repo

Read the current state without assuming a layout:

- `git remote -v` and `.git/config` to infer GitHub or no GitHub remote.
- `AGENTS.md` to see whether an `## Agent skills` block already exists.
- `project-memory/agents/` to see whether prior setup exists.
- `CONTEXT.md`, `CONTEXT-MAP.md`, and `project-memory/adr/`.
- `.scratch/` as a signal that local markdown issue tracking may already be in
  use.
- `projects/` as a signal that orchestrator workspace planning may already be
  in use.
- Existing issue templates or tracker docs when present.
- README, project docs, package manifests, source directories, tests, and
  local architecture notes that define repo vocabulary or accepted behavior.

For existing-project bootstrap, also read recent session history with
`references/session-history.md`:

- Search local session history for the same git root over the last 14 days.
- Include archived history only when discoverable in the same date window.
- Keep at most the 10 most recent matching sessions.
- Match sessions by `session_meta.cwd`, `turn_context.cwd`, tool-call
  `workdir`/`cwd`, or absolute paths under the repo root.
- If session history is unavailable or unreadable, continue with repo-only
  evidence and report that limitation.

### 3. Confirm setup decisions

Walk the user through these sections one at a time. Give a recommendation and
accept a short answer such as `default`.

**Issue tracker**

Choose where PRDs and implementation issues live:

- **GitHub**: for code repos, use GitHub Issues through `gh`.
- **Local markdown**: for code repos, use `.scratch/<feature-slug>/PRD.md` and
  `.scratch/<feature-slug>/issues/*.md`.
- **Local orchestrator**: for orchestrator workspaces, use
  `projects/<project-slug>/features/<feature-slug>/PRD.md` and
  `projects/<project-slug>/features/<feature-slug>/issues/*.md`.
- **GitHub coordination repo**: for orchestrator workspaces, publish PRD
  parent issues and vertical feature issues in a configured coordination repo.
  Repo-local implementation PRs are linked from those issues. Apply a GitHub
  label named exactly `<project-slug>` to each PRD parent issue and vertical
  feature issue for that orchestrator project.
- **Other**: ask for one paragraph describing the tracker workflow.

Default to GitHub for code repos when the remote is GitHub, and local markdown
when no clear GitHub issue tracker exists. If the user is running a temp
exercise, validation pass, rehearsal, dry run, or otherwise says not to mutate
external systems, recommend local markdown for that run and record the reason
in `project-memory/agents/issue-tracker.md` as a current-run or dry-run
override, not as proof that the durable tracker preference changed. When a
durable tracker preference is known, record both the durable default and the
current-run effective target. For orchestrator workspaces, ask whether the
default should be local orchestrator files or a GitHub coordination repo;
record the chosen backend in `project-memory/agents/issue-tracker.md`.

For local markdown in a multi-context repo or monorepo, confirm whether feature
slugs must include a product or workspace prefix, such as
`customer-portal-weekly-digest`. Record that convention so `$plan-feature`,
`$to-prd`, and `$to-issues` can reject ambiguous feature paths before writing.

Confirm delivery topology defaults:

- **One Feature Branch** for a single project or monorepo in one git repo: one
  shared feature branch and usually one draft PR for the feature.
- **One PR Per Repo** for orchestrator or true multi-repo work: one feature
  branch and draft PR per affected repo.
- **One PR Per Issue** only for isolated exceptions with no shared contracts,
  migrations, lockfiles, generated files, or overlapping validation.
- **Direct Commit** only with explicit maintainer authorization.

Record these defaults in `project-memory/agents/issue-tracker.md` so PRDs can
select a topology before `$to-issues` generates implementation issues.

**Triage types and labels**

Use these canonical issue types:

- `bug`: something is broken or regressed.
- `feature`: a new capability or product enhancement.
- `task`: maintenance, docs, refactor, follow-up, cleanup, or implementation
  work item.

In GitHub mode, default these to native GitHub Issue Types:

- `bug` -> `Bug`
- `feature` -> `Feature`
- `task` -> `Task`

In local markdown mode, default these to `Type:` values using the canonical
lowercase strings.

Ask whether the repo uses different issue types, disabled GitHub issue types,
or type-like labels instead.

Use these canonical state roles:

- `needs-triage`: maintainer needs to evaluate.
- `needs-info`: waiting on reporter or requester.
- `ready-for-agent`: fully specified and agent-queue-ready; listed
  dependencies still gate when work can start.
- `ready-for-human`: requires human implementation or judgment.
- `wontfix`: will not be actioned.

Ask whether the actual tracker labels or status values differ. If not, use
identity mapping.

**Domain memory layout**

Choose:

- **Single-context**: one root `CONTEXT.md` and root `project-memory/adr/`.
- **Multi-context**: root `CONTEXT-MAP.md` points to context-specific
  `CONTEXT.md` files, with optional context-specific `project-memory/adr/`.
- **Orchestrator context**: root `CONTEXT.md` defines coordination vocabulary
  such as project, feature, repo pointer, vertical issue, integration gate, and
  done. Feature-specific context lives in `projects/<project>/PROJECT.md` and
  `projects/<project>/features/<feature>/PRD.md`, not in child repos.

Default to single-context unless `CONTEXT-MAP.md` already exists or the repo is
clearly a multi-domain monorepo. Use orchestrator context only for
orchestrator workspace mode. For multi-context repos, record how a planning
workflow selects and carries `product_slug`, `workspace_path`, and
`context_file` into PRDs and generated issues.

For existing-project bootstrap, also confirm whether to seed domain memory from
the evidence found. Recommend seeding only high-confidence items and presenting
uncertain items as open questions.

### 4. Draft project memory

Before writing, show:

- the `AGENTS.md` `## Agent skills` block,
- the intended `project-memory/agents/issue-tracker.md`,
- the intended `project-memory/agents/triage-labels.md`,
- the intended `project-memory/agents/domain.md`.
- for existing-project bootstrap, the intended `CONTEXT.md` additions and any
  ADR drafts under `project-memory/adr/`.

Use these reference templates as starting points:

- `references/issue-tracker-github.md`
- `references/issue-tracker-local.md`
- `references/issue-tracker-orchestrator-github.md`
- `references/issue-tracker-orchestrator-local.md`
- `references/triage-labels.md`
- `references/domain.md`
- `references/session-history.md`

For an "other" issue tracker, write `issue-tracker.md` from the user's
description instead of forcing a hosted-tracker template.

For orchestrator workspace mode:

- Record whether the workspace uses local orchestrator files or a GitHub
  coordination repo.
- Draft tracker instructions that say where project folders, feature PRDs,
  vertical issues, repo pointer sheets, and integration gates live.
- For GitHub coordination mode, state that each PRD parent issue and vertical
  feature issue gets a project label named exactly `<project-slug>`.
- State that setup does not create project or feature folders. In this context,
  config-only means no project or feature artifacts during setup; root setup
  files such as `AGENTS.md`, `project-memory/agents/*`, and accepted root
  context remain allowed. `$plan-feature`, `$to-prd`, and `$to-issues` create
  project or feature folders only when writing an actual feature.
- State that child repos retain their own `AGENTS.md`, `CONTEXT.md`,
  `project-memory`, validation commands, branches, commits, and PRs.
- State that `codex-orchestrator` owns runtime worker state and ledgers; the
  orchestrator workspace owns durable planning artifacts.
- Start from the matching orchestrator tracker template and preserve its
  config-only setup, artifact ownership, child-repo ownership, issue content,
  and completion sections. Do not collapse orchestrator tracker setup to path
  patterns alone.

For existing-project bootstrap:

- Use `$domain-modeling` to shape `CONTEXT.md` and ADR content.
- Prefer enriching existing `CONTEXT.md` and existing ADRs over replacing them.
- Put high-confidence terms, rules, workflows, and unresolved questions in
  `CONTEXT.md`.
- Create ADRs only for accepted, load-bearing decisions future work would
  otherwise reopen.
- Link to source files, docs, issues, commits, or session summaries when useful
  and available.

### 5. Write the setup

After confirmation:

- Create `project-memory/agents/` if needed.
- Write or update the three files under `project-memory/agents/`.
- Create `AGENTS.md` if it does not exist; otherwise update the existing
  `## Agent skills` block in place.
- In existing-project bootstrap mode, create or update root `CONTEXT.md` and
  useful ADR files under `project-memory/adr/` using `$domain-modeling`.
- In orchestrator workspace mode, create or update root `CONTEXT.md` only when
  useful coordination vocabulary is accepted or strongly evidenced. Do not
  create `projects/<project>/` or feature folders during setup.
- Preserve unrelated `AGENTS.md` content.
- Preserve unrelated `CONTEXT.md`, ADR, and project doc content.

Use this `AGENTS.md` block shape:

```markdown
## Agent skills

### Issue tracker

[one-line summary of where PRDs and issues live]. See `project-memory/agents/issue-tracker.md`.

### Triage types and labels

[one-line summary of the issue type and state vocabulary]. See `project-memory/agents/triage-labels.md`.

### Domain memory

[one-line summary of single-context or multi-context layout]. See `project-memory/agents/domain.md`.
```

For orchestrator workspace mode, the `AGENTS.md` block should explicitly say
that the workspace coordinates external repos and that each child repo keeps
its own project memory and code ownership.

### 6. Report completion

Summarize:

- setup mode,
- files written,
- selected issue tracker,
- issue-type and triage-state mapping,
- domain-memory layout,
- workspace mode and, for orchestrator workspaces, selected coordination
  backend,
- session-history window and whether it was used,
- `CONTEXT.md` terms/rules/open questions seeded, if any,
- ADRs created or updated, if any,
- what workflows can now consume this setup.

If session history could not be read or produced no strong evidence, say so
plainly and note that future `$domain-modeling`, `$grill-me-with-context`, and
planning workflows can keep filling project memory incrementally.
