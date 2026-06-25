---
name: setup-project-memory
description: Configure or review lean project-memory before planning, PRD, issue-splitting, triage, or domain-memory workflows, including an initial CONTEXT.md seed when repo evidence is strong.
---

# Setup Project Memory

## Goal

Configure the project memory that other skills can rely on:

- `AGENTS.md` as the only agent-instruction file this skill writes, kept
  pointer-first and focused on operating rules rather than project context.
- `project-memory/agents/issue-tracker.md` for where PRDs and issues live.
- `project-memory/agents/triage-labels.md` for canonical issue-type and
  triage-state mappings.
- `project-memory/agents/domain.md` for where `CONTEXT.md`, `CONTEXT-MAP.md`,
  and ADRs live.
- `CONTEXT.md` as the initial domain memory seed when repo evidence is strong,
  and `project-memory/adr/` as optional decision memory when accepted
  load-bearing decisions exist.

This is a setup and setup-review skill. Run it once per code repo, monorepo, or
orchestrator workspace before workflows publish PRDs, split issues, triage
incoming work, or update project-backed domain memory. Re-run it when tracker
routing, issue types, triage states, or domain-memory layout changes, when an
existing project needs accepted knowledge migrated into project memory, or when
the user asks to show or change current project-memory settings.

Use `lower_snake_case` keys and `lower-kebab-case` values for structured
multi-choice fields. Keep tracker-specific values, labels, and prose only in
mapping columns or explanatory text.

## Hard Boundaries

- Always use `AGENTS.md` for setup pointers and project-memory routing when an
  agent-instruction file is needed.
- Keep `AGENTS.md` lean. It may contain repo-specific agent rules, ownership
  boundaries, validation constraints, and short pointers to project memory, but
  not copied domain context, broad architecture inventories, planning history,
  glossary material, or tracker workflow detail that belongs in `CONTEXT.md`,
  `project-memory/agents/*`, or ADRs.
- When `AGENTS.md` already contains project context, classify it before writing:
  keep true agent operating rules in `AGENTS.md`, move or summarize domain
  vocabulary and project context into `CONTEXT.md`, move tracker and workflow
  routing into `project-memory/agents/*`, move accepted load-bearing decisions
  into ADRs, and preserve uncertain content until the user confirms a target.
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

## Structured Values

Use these setup-owned values when writing `project-memory/agents/*` files or
handoffs:

- `tracker_mode`: `github` for GitHub Issues, `local-markdown` for repo-local
  markdown files, `orchestrator-local` for local cross-repo workspace files,
  `orchestrator-github` for a GitHub coordination repo, or `other` for a
  documented project-specific tracker.
- `effective_target`: `configured-tracker` for the durable configured target,
  `local-dry-run` for a non-mutating local rehearsal, or
  `draft-publish-commands` when returning external publish commands without
  executing them.
- `setup_mode`: `fresh-setup` for new project-memory setup,
  `existing-project-bootstrap` for reconciling an existing project, or
  `orchestrator-workspace` for a parent workspace that coordinates independent
  repos.
- `local_artifact_writes` and `external_tracker_mutation`: `allowed` or
  `disallowed`.
- `domain_memory_layout`: `single-context` for one root context,
  `multi-context` for `CONTEXT-MAP.md` routing, or `orchestrator-context` for
  coordination vocabulary in an orchestrator workspace.
- `context_seed_mode`: `seed-context` to write evidence-backed initial domain
  memory, or `routing-only` to configure project memory without writing domain
  memory.
- `delivery_mode` defaults recorded by setup: `one-feature-branch` for one
  shared branch/PR, `one-pr-per-repo` for true multi-repo work,
  `one-pr-per-issue` for isolated exceptions, or `direct-commit` for explicitly
  authorized direct commits.
- `default_worker_authorization`: a comma-separated capability list from
  `$codex-orchestrator` worker authorization values. Default to
  `inspect, implement`. Higher defaults such as `inspect, implement, commit`
  are policy defaults only and still require current owner/session authority
  before dispatch.

Meanings live in the setup workflow sections that ask the user to choose each
value and in the generated tracker, triage, and domain-memory files. Generated
issue type and state meanings live in `references/triage-labels.md`.
Lower-kebab-case values are canonical. Treat older uppercase kebab-case values
as legacy aliases when reading existing artifacts. When updating an artifact
that contains legacy aliases, rewrite touched structured values to
lower-kebab-case.

## Workflow

### 1. Choose setup mode

Use one of three `setup_mode` values:

- `fresh-setup`: the repo has little or no prior project-memory structure and
  the goal is to configure `AGENTS.md` plus `project-memory/agents/*`. In
  non-empty repos, also perform an initial context-seed check and recommend
  creating `CONTEXT.md` when README/docs/source evidence supports useful
  project vocabulary or rules.
- `existing-project-bootstrap`: the repo already has code, docs, issues,
  prior agent sessions, or partial project-memory/domain files, and the goal
  is to reconcile the setup, seed or enrich `CONTEXT.md`, and create ADRs from
  strong evidence when accepted load-bearing decisions exist.
- `orchestrator-workspace`: the current folder is a parent coordination
  workspace used to plan and run Codex across multiple independent repos. It
  owns cross-repo PRDs, vertical feature issues, repo pointer sheets, and
  integration gates, but not product code.

Default to `fresh-setup` when the repo has no prior project-memory files. If the
repo is non-empty and has durable docs, source, tests, schemas, or package
manifests, recommend `fresh-setup` plus an initial `CONTEXT.md` seed. Use
routing-only `fresh-setup` only when the repo is empty, the evidence is too thin,
the user asks for routing only, or the current run is a dry run that should not
write domain memory. Use `existing-project-bootstrap` when the user wants
recent session history considered, accepted repo knowledge migrated into an
existing domain-memory surface, ADRs created, or partial project-memory/domain
files reconciled. Recommend `orchestrator-workspace` when the folder has no clear
single codebase but contains or is intended to contain `projects/`, repo
pointer docs, symlinks/worktrees to external repos, or cross-repo planning
artifacts.

### 2. Inspect the repo

Read the current state without assuming a layout:

- `git remote -v` and `.git/config` to infer GitHub or no GitHub remote.
- `AGENTS.md` to see whether an `## Agent skills` block already exists and
  whether existing content should stay as agent rules or move into project
  memory.
- `project-memory/agents/` to see whether prior setup exists.
- `CONTEXT.md`, `CONTEXT-MAP.md`, and `project-memory/adr/`.
- `.scratch/` as a signal that local markdown issue tracking may already be in
  use.
- `projects/` as a signal that orchestrator workspace planning may already be
  in use.
- Existing issue templates or tracker docs when present.
- README, project docs, package manifests, source directories, tests, and
  local architecture notes that define repo vocabulary or accepted behavior.

When `AGENTS.md` already exists, classify existing content into these buckets:

- **Keep in AGENTS.md**: repo-specific instructions agents must obey while
  operating in the checkout, including ownership boundaries, safety rules,
  validation commands, maintenance routing, and short project-memory pointers.
- **Move to CONTEXT.md**: project purpose, product areas, glossary terms,
  canonical names, domain boundaries, and open questions.
- **Move to project-memory/agents/**: issue tracker routing, triage mappings,
  delivery-mode defaults, domain-memory layout, and orchestrator coordination
  backend details.
- **Move to ADRs**: accepted load-bearing decisions future work would otherwise
  reopen.
- **Preserve or ask**: content whose ownership is unclear, stale, conflicting,
  or not backed by strong evidence.

For any non-empty repo, identify initial `CONTEXT.md` seed candidates from
strong evidence:

- project purpose and non-goals,
- product areas, subprojects, or ownership boundaries,
- stable domain vocabulary and canonical names,
- durable rules, workflows, and cross-project constraints,
- open questions only when the evidence clearly shows uncertainty or conflict.

For existing-project bootstrap, also read recent session history with
`references/session-history.md`:

- Search local session history for the same git root over the last 14 days.
- Include archived history only when discoverable in the same date window.
- Keep at most the 10 most recent matching sessions.
- Match sessions by `session_meta.cwd`, `turn_context.cwd`, tool-call
  `workdir`/`cwd`, or absolute paths under the repo root.
- If session history is unavailable or unreadable, continue with repo-only
  evidence and report that limitation.

### 3. Review existing setup

If any of `project-memory/agents/issue-tracker.md`,
`project-memory/agents/triage-labels.md`, or
`project-memory/agents/domain.md` already exists, or if the user asks to show,
review, inspect, change, or edit setup, run this review path before asking fresh
setup questions.

Build a current settings summary from existing files. Use `Unknown` only when
the value is genuinely absent or ambiguous:

- `setup_mode`: inferred from repo evidence and tracker/domain files.
- `tracker_mode`: current tracker backend and any configured repo/path.
- `effective_target`: durable configured target plus current-run or dry-run
  override, if recorded.
- `run_authorization`: `local_artifact_writes` and
  `external_tracker_mutation`, including whether each value is durable or only
  a current-run override.
- `delivery_mode`: default delivery mode and branch/PR convention.
- `default_worker_authorization`: conservative worker capability default,
  usually `inspect, implement`.
- `issue_type` mapping: canonical values to tracker values, such as
  `task -> Task`.
- `triage_state` mapping: canonical values to tracker labels/status values,
  such as `ready-for-agent -> ready-for-agent`.
- `domain_memory_layout`: single-context, multi-context, or orchestrator
  context, plus current context files.
- `context_seed_mode`: whether durable context exists, should be seeded, or is
  routing-only.
- `AGENTS.md` setup block: present, missing, stale, or containing extra copied
  tracker/domain detail that belongs in project memory.

Print the summary before recommending changes. If the user only asked to view
current settings, stop after the summary unless they ask to edit.

When editing, ask which section to change. Offer these sections:

- `issue-tracker`
- `run-authorization`
- `delivery-mode`
- `worker-authorization`
- `issue-type-mapping`
- `triage-state-mapping`
- `domain-memory`
- `context-seed`
- `agents-pointers`
- `done`

For each selected section:

- Show the current value or mapping first.
- Show `keep-current` first, then every available value with a short
  description.
- Include a custom tracker value option only where the actual tracker may use
  a different label, issue type, path, or repo name.
- Record the user's choices as proposed settings in memory only.
- Preserve custom prose, comments, path conventions, dry-run overrides, project
  labels, and tracker-specific values unless the user explicitly changes them.
- Continue until the user chooses `done` or says no more changes.

Available editor options by section:

- `issue-tracker`: `keep-current`, `github`, `local-markdown`,
  `orchestrator-local`, `orchestrator-github`, or `other`.
- `run-authorization`: `keep-current`, `local-artifacts-only`,
  `external-tracker-only`, `both-allowed`, or `both-disallowed`. Treat these
  as current-run authority unless the user explicitly says to make them durable
  defaults. Never let a durable tracker preference silently grant external
  mutation. Interpret them as:
  `local-artifacts-only` means `local_artifact_writes=allowed` and
  `external_tracker_mutation=disallowed`; `external-tracker-only` means
  `local_artifact_writes=disallowed` and
  `external_tracker_mutation=allowed`; `both-allowed` means both are
  `allowed`; `both-disallowed` means both are `disallowed`.
- `delivery-mode`: `keep-current`, `one-feature-branch`, `one-pr-per-repo`,
  `one-pr-per-issue`, or `direct-commit`.
- `worker-authorization`: `keep-current`, `inspect, implement`,
  `inspect, implement, commit`, `inspect, implement, commit, push`,
  `inspect, implement, commit, push, pr`, or custom capability subset. These
  are defaults only; current owner/session authority may always restrict them.
- `issue-type-mapping`: `keep-current`, default GitHub mapping
  (`bug -> Bug`, `feature -> Feature`, `task -> Task`), canonical local mapping
  (`bug -> bug`, `feature -> feature`, `task -> task`), or custom per canonical
  type.
- `triage-state-mapping`: `keep-current`, default GitHub lowercase labels
  (`needs-triage -> needs-triage`, `needs-info -> needs-info`,
  `ready-for-agent -> ready-for-agent`,
  `ready-for-human -> ready-for-human`, `wontfix -> wontfix`), canonical local
  mapping, or custom per canonical state.
- `domain-memory`: `keep-current`, `single-context`, `multi-context`, or
  `orchestrator-context`.
- `context-seed`: `keep-current`, `seed-context`, or `routing-only`.
- `agents-pointers`: `keep-current`, create missing pointer block, refresh
  stale pointer block, or minimize copied setup detail into project-memory
  pointers.

After all selected edits, show the intended changed files and a before/after
summary for each changed setting. Ask for confirmation before writing. If the
user declines, report the proposed settings and do not write files.

### 4. Confirm setup decisions

Walk the user through these sections one at a time. Give a recommendation and
accept a short answer such as `default`.

**Issue tracker**

Choose `tracker_mode`, where PRDs and implementation issues live:

- `github`: for code repos, use GitHub Issues through `gh`.
- `local-markdown`: for code repos, use `.scratch/<feature-slug>/PRD.md` and
  `.scratch/<feature-slug>/issues/*.md`.
- `orchestrator-local`: for orchestrator workspaces, use
  `projects/<project-slug>/features/<feature-slug>/PRD.md` and
  `projects/<project-slug>/features/<feature-slug>/issues/*.md`.
- `orchestrator-github`: for orchestrator workspaces, publish PRD
  parent issues and vertical feature issues in a configured coordination repo.
  Repo-local implementation PRs are linked from those issues. Apply a GitHub
  label named exactly `<project-slug>` to each PRD parent issue and vertical
  feature issue for that orchestrator project.
- `other`: ask for one paragraph describing the tracker workflow.

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
`customer-portal-weekly-digest`. Record that convention so `$plan-feature` can
reject ambiguous feature paths before writing.

Confirm delivery mode defaults:

- `one-feature-branch` for a single project or monorepo in one git repo: one
  shared feature branch and usually one draft PR for the feature.
- `one-pr-per-repo` for orchestrator or true multi-repo work: one feature
  branch and draft PR per affected repo.
- `one-pr-per-issue` only for isolated exceptions with no shared contracts,
  migrations, lockfiles, generated files, or overlapping validation.
- `direct-commit` only with explicit maintainer authorization.

Record these defaults in `project-memory/agents/issue-tracker.md` so PRDs can
select a delivery mode before `$plan-feature` generates implementation issues.

Confirm the default worker authorization:

- `inspect, implement`: recommended default. Workers may inspect, edit, test,
  and report, but root owns commit, push, and PR creation.
- `inspect, implement, commit`: workers may also create local commits in the
  assigned checkout, but root still owns push and PR creation.
- `inspect, implement, commit, push`: workers may also push an exact assigned
  branch/refspec, but root still owns PR creation.
- `inspect, implement, commit, push, pr`: workers may also create or update the
  assigned draft PR when current publication authority allows it.

Record this as `default_worker_authorization` in
`project-memory/agents/issue-tracker.md`. Make clear it is a policy default,
not final permission: `$codex-orchestrator` must still apply current owner
authorization, publication authority, dirty-worktree state, inspectability, and
gates before assigning worker authorization modes.

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

In local markdown mode, default these to `Type:` values using the same
canonical values unless the repo records a tracker-specific lowercase mapping.

Ask whether the repo uses different issue types, disabled GitHub issue types,
or type-like labels instead.

Use these canonical state roles:

- `needs-triage`: maintainer needs to evaluate.
- `needs-info`: waiting on reporter or requester.
- `ready-for-agent`: fully specified and agent-queue-ready; listed
  dependencies still gate when work can start.
- `ready-for-human`: requires human implementation or judgment.
- `wontfix`: will not be actioned.

Ask whether the actual tracker labels or status values differ. If not, use the
mode default mapping: GitHub and GitHub coordination use lowercase labels such
as `ready-for-agent`, while local markdown may use canonical values unless the
repo records a different convention.

**Domain memory layout**

Choose:

- `single-context`: one root `CONTEXT.md` and root `project-memory/adr/`.
- `multi-context`: root `CONTEXT-MAP.md` points to context-specific
  `CONTEXT.md` files, with optional context-specific `project-memory/adr/`.
- `orchestrator-context`: root `CONTEXT.md` defines coordination vocabulary
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

Confirm the initial context seed decision for every non-empty repo:

- `seed-context`: recommended when README/docs/source/tests provide enough
  evidence for a useful first glossary, boundary list, or rule set.
- `routing-only`: recommended when the repo is empty, temporary, a dry run,
  or evidence is too thin to write durable domain memory.

When recommending a seed, explain the evidence sources and say that
`$domain-modeling` owns the final shape before writing.

**AGENTS.md minimization**

For fresh setup, recommend creating only the `## Agent skills` pointer block
plus any repo-specific operating rules the evidence clearly requires.

For existing-project bootstrap or reruns, recommend reducing `AGENTS.md` when
it duplicates material now owned by `CONTEXT.md`, `project-memory/agents/*`, or
ADRs. Show what will stay, what will be moved or summarized, and what will be
preserved because ownership is uncertain. Do not remove content just because it
is long; remove or move only content with a clear better home and user
confirmation.

### 5. Draft project memory

Before writing, show:

- for review existing setup mode, the current settings summary and the
  before/after summary for each proposed setting change,
- the `AGENTS.md` `## Agent skills` block,
- the `AGENTS.md` minimization plan, including any existing content to keep,
  move, summarize, or preserve,
- the intended `project-memory/agents/issue-tracker.md`,
- the intended `project-memory/agents/triage-labels.md`,
- the intended `project-memory/agents/domain.md`.
- the intended initial `CONTEXT.md` seed, or the reason no seed should be
  written.
- for existing-project bootstrap, any ADR drafts under `project-memory/adr/`.

Use these reference templates as starting points:

- `references/issue-tracker-github.md`
- `references/issue-tracker-local.md`
- `references/issue-tracker-orchestrator-github.md`
- `references/issue-tracker-orchestrator-local.md`
- `references/tracker-publishing.md`
- `references/triage-labels.md`
- `references/domain.md`
- `references/context-seed.md`
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
  context remain allowed. `$plan-feature` creates project or feature folders
  only when writing an actual feature.
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

For fresh setup with an initial context seed:

- Load `$domain-modeling` before drafting or writing `CONTEXT.md`.
- Use `references/context-seed.md` for the seed shape.
- Keep the seed minimal and evidence-backed. Prefer a useful first glossary and
  boundary/rule list over exhaustive architecture documentation.
- Do not create ADRs during fresh setup unless the user explicitly asks for
  accepted decisions to be recorded and the decision evidence is strong.

### 6. Write the setup

After confirmation:

- Create `project-memory/agents/` if needed.
- Write or update the three files under `project-memory/agents/`.
- In review existing setup mode, update only the files needed for confirmed
  changed settings. Preserve unrelated setup text, custom mappings, current-run
  overrides, comments, and project-specific prose.
- Create `AGENTS.md` if it does not exist; otherwise update the existing
  `## Agent skills` block in place and apply the confirmed minimization plan.
- In fresh setup with an accepted initial context seed, create or update root
  `CONTEXT.md` using `$domain-modeling`.
- In existing-project bootstrap mode, create or update root `CONTEXT.md` and
  useful ADR files under `project-memory/adr/` using `$domain-modeling`.
- In orchestrator workspace mode, create or update root `CONTEXT.md` only when
  useful coordination vocabulary is accepted or strongly evidenced. Do not
  create `projects/<project>/` or feature folders during setup.
- Preserve unrelated or uncertain `AGENTS.md` content unless the user confirmed
  a specific move, summary, or deletion.
- Do not duplicate moved project context in both `AGENTS.md` and `CONTEXT.md`
  or `project-memory/agents/*`. Leave a short pointer in `AGENTS.md` instead.
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

Keep this block concise. Do not paste domain vocabulary, tracker procedure,
delivery details, or context seed material into `AGENTS.md`; place those in the
referenced project-memory files.

For orchestrator workspace mode, the `AGENTS.md` block should explicitly say
that the workspace coordinates external repos and that each child repo keeps
its own project memory and code ownership.

### 7. Report completion

Summarize:

- setup mode,
- files written,
- settings reviewed and settings changed,
- selected issue tracker,
- run authorization and whether it is durable or current-run only,
- default worker authorization,
- issue-type and triage-state mapping,
- domain-memory layout,
- `AGENTS.md` minimization outcome, including content moved or intentionally
  preserved,
- workspace mode and, for orchestrator workspaces, selected coordination
  backend,
- session-history window and whether it was used,
- context-seed decision and evidence sources,
- `CONTEXT.md` terms/rules/open questions seeded, if any,
- ADRs created or updated, if any,
- what workflows can now consume this setup.

If session history could not be read or produced no strong evidence, say so
plainly and note that future `$domain-modeling`, `$grill-me-with-context`, and
planning workflows can keep filling project memory incrementally.
