---
name: setup-project-memory
description: Configure or refresh a repository's project-memory structure for agent workflows. Use when setting up a fresh repo, bootstrapping an already-used repo from repo evidence and recent Codex session history, or updating AGENTS.md pointers, issue-tracker instructions, triage type and label mappings, CONTEXT.md, and ADR layout before repo-backed planning, PRD, issue-splitting, triage, grill-with-docs, or architecture-improvement skills.
---

# Setup Project Memory

## Goal

Configure the repo-level project memory that other skills can rely on:

- `AGENTS.md` as the only agent-instruction file this skill writes.
- `project-memory/agents/issue-tracker.md` for where PRDs and issues live.
- `project-memory/agents/triage-labels.md` for canonical issue-type and
  triage-state mappings.
- `project-memory/agents/domain.md` for where `CONTEXT.md`, `CONTEXT-MAP.md`,
  and ADRs live.
- `CONTEXT.md` and `project-memory/adr/` as optional seeded domain memory when
  an existing project has strong repo or session evidence.

This is a setup skill. Run it once per repo before using workflows that publish
PRDs, split issues, triage incoming work, or update repo-backed domain memory.
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
- Ask for confirmation before writing files.

## Workflow

### 1. Choose setup mode

Use one of two modes:

- **Fresh setup**: the repo has little or no prior project-memory structure and
  the goal is to configure `AGENTS.md` plus `project-memory/agents/*`.
- **Existing-project bootstrap**: the repo already has code, docs, issues,
  prior agent sessions, or partial project-memory files, and the goal is to
  infer the setup plus seed `CONTEXT.md` and ADRs from strong evidence.

Default to existing-project bootstrap when the repo has meaningful existing
code/docs or prior project-memory files. Default to fresh setup for empty or
new repos.

### 2. Inspect the repo

Read the current state without assuming a layout:

- `git remote -v` and `.git/config` to infer GitHub or no GitHub remote.
- `AGENTS.md` to see whether an `## Agent skills` block already exists.
- `project-memory/agents/` to see whether prior setup exists.
- `CONTEXT.md`, `CONTEXT-MAP.md`, and `project-memory/adr/`.
- `.scratch/` as a signal that local markdown issue tracking may already be in
  use.
- Existing issue templates or tracker docs when present.
- README, project docs, package manifests, source directories, tests, and
  local architecture notes that define repo vocabulary or accepted behavior.

For existing-project bootstrap, also read recent session history with
`references/session-history.md`:

- Search local Codex sessions under `~/.codex/sessions` for the same git root
  over the last 14 days.
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

- **GitHub**: use GitHub Issues through `gh`.
- **Local markdown**: use `.scratch/<feature-slug>/PRD.md` and
  `.scratch/<feature-slug>/issues/*.md`.
- **Other**: ask for one paragraph describing the tracker workflow.

Default to GitHub when the remote is GitHub, and local markdown when no clear
GitHub issue tracker exists.

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
- `ready-for-agent`: fully specified and agent-ready.
- `ready-for-human`: requires human implementation or judgment.
- `wontfix`: will not be actioned.

Ask whether the actual tracker labels or status values differ. If not, use
identity mapping.

**Domain memory layout**

Choose:

- **Single-context**: one root `CONTEXT.md` and root `project-memory/adr/`.
- **Multi-context**: root `CONTEXT-MAP.md` points to context-specific
  `CONTEXT.md` files, with optional context-specific `project-memory/adr/`.

Default to single-context unless `CONTEXT-MAP.md` already exists or the repo is
clearly a multi-domain monorepo.

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
- `references/triage-labels.md`
- `references/domain.md`
- `references/session-history.md`

For an "other" issue tracker, write `issue-tracker.md` from the user's
description instead of forcing a hosted-tracker template.

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

### 6. Report completion

Summarize:

- setup mode,
- files written,
- selected issue tracker,
- issue-type and triage-state mapping,
- domain-memory layout,
- session-history window and whether it was used,
- `CONTEXT.md` terms/rules/open questions seeded, if any,
- ADRs created or updated, if any,
- what workflows can now consume this setup.

If session history could not be read or produced no strong evidence, say so
plainly and note that future `$domain-modeling`, `$grill-with-docs`, and
planning workflows can keep filling project memory incrementally.
