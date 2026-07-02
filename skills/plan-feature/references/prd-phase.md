# PRD Phase

Use this reference when `plan-feature` needs to turn clarified feature,
product, migration, cross-repo project, or workflow intent into a practical PRD.
This is an internal phase, not a public skill.

## Goal

Produce or publish a PRD that can feed the issue phase. If the source material
is still too vague to produce a useful PRD, return the smallest blocking
question set or route back through `$grill-me-with-context`.

## Boundaries

- Do not implement the feature.
- Do not split the PRD into implementation issues; the issue phase owns that.
- Do not invent requirements, users, constraints, or acceptance criteria that
  are not supported by user input, repo evidence, or project memory.
- Do not ask for separate PRD write/publish confirmation after `plan-feature`
  has resolved setup, planning identity, blockers, and effective target.
  `tracker_backend` is the planning-artifact write authority unless the current
  run explicitly requested no-mutation output.
- In GitHub tracker mode, do not persist repo-local PRD mirrors
  or `.scratch/` staging copies unless the tracker config, current-run override,
  or user explicitly asks for a local mirror.
- Use structured values for multi-choice fields. Read tracker and type mappings
  from project memory, and use the `delivery_mode` values documented in
  `references/prd-template.md`.
- For publication mechanics, effective targets, and stable `source_prd_ref`
  behavior in draft command runs, use `$project-memory`
  `references/tracker-publishing.md`.

## Workflow

### 1. Ground In Project Memory

Inspect the current project context before drafting:

- `project-memory/agents/issue-tracker.md`
- `project-memory/agents/triage-labels.md`
- `project-memory/agents/domain.md`
- `CONTEXT.md` or `CONTEXT-MAP.md`
- `TRANSLATION.md`, when present for the selected context
- `project-memory/adr/`
- orchestrator workspace docs such as `projects/<project>/PROJECT.md` and
  `projects/<project>/repos/*.md`, when planning from a local orchestrator
  workspace
- README, product docs, issue templates, and relevant source/tests

If setup files are missing, continue with repo evidence and say which project
memory files were unavailable.

If `CONTEXT-MAP.md` or `project-memory/agents/domain.md` indicates a
multi-context repo or monorepo, resolve the selected product/workspace context
before writing:

- `product_slug`
- `workspace_path`
- `context_file`
- `feature_slug`
- `delivery_mode`

Use values passed by `plan-feature` when present. Otherwise derive them from
project memory and repo evidence, asking only when multiple contexts could
plausibly own the feature.

Resolve the PRD `delivery_mode` before drafting:

- `pull-request`: default for single-repo, monorepo, orchestrator workspace, and
  true cross-repo work. In a single repo or monorepo, use one feature branch and
  PR. In multi-repo work, every involved repo uses the same branch name and opens
  its own PR.
- `direct-commit`: exception only when the maintainer explicitly authorizes a
  direct commit path for this feature.

If the repo shape makes the affected repo set ambiguous, ask before writing the
PRD.

## PRD Target Model

Use this model before writing or publishing a PRD:

| Project shape | Tracker backend | PRD target | Generated issue source |
| --- | --- | --- | --- |
| Single repo | `github` | One PRD GitHub issue in the repo. | `Source PRD: #<number>` |
| Single repo | `local` | `.scratch/<feature-slug>/PRD.md` | `Source PRD: .scratch/<feature-slug>/PRD.md` |
| Monorepo or multi-context repo | `github` or `local` | One PRD for the selected product/workspace context. | The selected PRD issue/path plus product or workspace scope in each issue. |
| Workspace with multiple independent repos | `github` | Linked repo-scoped partial PRD issues when there is no accepted global PRD. | Each repo issue points at its repo partial PRD and links sibling partial PRDs. |
| Workspace with multiple independent repos | `local` | `projects/<project-slug>/features/<feature-slug>/PRD.md` or linked repo-scoped partial PRDs when that is the accepted source. | Each local issue points at the relevant PRD path and links sibling partial PRDs/issues. |

Do not invent a global PRD for workspace features. Use one only when it is the
accepted planning source; otherwise preserve the linked partial-PRD graph.

### 2. Confirm The PRD Source

Identify the source material:

- user conversation or pasted notes,
- output from `$grill-me-with-context`,
- an existing issue, doc, or planning note,
- repo behavior that needs to become a defined product surface.

If key facts are missing, ask only for decisions that would materially change
the PRD. Prefer defaults when the repo or project memory already implies them.

### 3. Draft The PRD

Use `references/prd-template.md` unless the repo has a stronger local PRD
format.

Before returning, writing, or publishing the PRD, sanitize every source and
evidence reference that came from local filesystem inspection. Published PRDs
must not include developer-machine absolute paths such as `/Users/<name>/...`,
`/home/<name>/...`, drive-root paths, temp directories, or cache paths. Use
portable references instead:

- current repository evidence: repo-relative paths such as
  `agents/src/session_data.py` or `agents/src/session_data.py:42`;
- sibling repository evidence: `<repo-name>/<repo-relative-path>` or
  `<repo-name>/<repo-relative-path>:<line>`, using the sibling repo directory
  name or configured repo slug;
- hosted source evidence: the URL, issue, PR, or `owner/repo:path` reference;
- local-only exploratory evidence that cannot be safely identified: a short
  descriptive label such as `<local-reference>: runtime session collector`, not
  the raw absolute path.

If the same file is useful both locally and in the PRD, keep the raw absolute
path only in private working context and put only the sanitized reference in
the PRD body or GitHub issue body. If sanitization would make the evidence
ambiguous, add the repo name or source label rather than restoring an absolute
path.

Keep the PRD implementation-facing:

- clear problem and target user,
- goals and non-goals,
- functional requirements,
- user workflow or system behavior,
- selected planning identity: feature slug, product or project slug, workspace
  path, and context file when applicable,
- delivery mode: branch naming guidance, expected PR shape, and integration
  proof expectations,
- issue-splitting note: sequencing, dependencies, and startability are derived
  from generated implementation issues and validated by the issue phase,
- data, permissions, API, or integration constraints when relevant,
- acceptance criteria,
- risks and open questions,
- notes for later issue splitting.

Do not include workflow status fields such as `Status: Draft` in the PRD body.
PRD readiness and lifecycle state belong in the issue tracker, mapped labels,
or the generated implementation issues, not in the PRD content itself.

### 4. Choose Publication Target

Read `project-memory/agents/issue-tracker.md` to determine where PRDs live.
Also read `$project-memory` `references/tracker-publishing.md` for the
shared effective-target and `source_prd_ref` contract.

- `Tracker backend: github`: publish through
  `$github-issues`, using the title format `PRD: <Feature Name>` and the
  mapped `feature` issue type when available. Do not write
  `.scratch/<feature-slug>/PRD.md` or `project-memory/features/...` as part of
  GitHub publishing unless explicitly asked for a local mirror.
- `Tracker backend: local`: write to the configured repo-local PRD path,
  normally `.scratch/<feature-slug>/PRD.md`. Derive or ask for
  `<feature-slug>` before writing. In multi-context repos, require the accepted
  product/workspace context and use the tracker's product-scoped slug convention
  when one is recorded.
- Local workspace PRDs: when the planning target is an orchestrator workspace,
  write `projects/<project-slug>/features/<feature-slug>/PRD.md`. Derive or ask
  for both `<project-slug>` and `<feature-slug>` before writing. The PRD phase
  owns the PRD and may create or update
  `projects/<project-slug>/PROJECT.md`,
  `projects/<project-slug>/repos/<repo-slug>.md`, and
  `projects/<project-slug>/features/<feature-slug>/integration-gates.md` only
  from accepted project, repo, or PRD source material needed for planning.
  Record the accepted source in each support doc or in the completion report so
  the source boundary is auditable.
- GitHub workspace PRDs: publish the relevant PRD issue or linked partial PRD
  issues through `$github-issues`. Derive or ask for `<project-slug>`,
  `<feature-slug>`, and the affected repo list. Related PRDs and implementation
  issues must link to each other. Do not create local `projects/...` feature
  artifacts or `.scratch/` mirrors unless the effective target is local or the
  user explicitly asked for a local mirror.

For GitHub PRDs, derive `<Feature Name>` from the
accepted product name or short feature phrase in title case. Do not include
issue numbers, status labels, or implementation slice names in the PRD title.

For orchestrator workspace PRDs, include repository scope, cross-repo
contracts, integration gates, and release or validation order when those affect
issue splitting.

For single-repo and monorepo PRDs, include concrete product or workspace scope
instead of using `N/A` when scope helps later issue splitting. For a simple
single repo, say "current repository." For a monorepo, include the selected
workspace path, context file, and explicitly out-of-scope sibling workspaces
when relevant.

Include a `## Delivery Mode` section in every PRD. For `pull-request`, record
branch naming such as `feature/<feature-slug>`, the expected PR shape, and the
validation required before implementation issues close. In multi-repo work,
record the same branch name for each affected repo, expected repo PR slots or
pre-implementation placeholders, and the cross-repo proof needed before issues
close. Use `direct-commit` only when explicitly authorized and record the
authorization reason. Placeholders in the PRD are delivery expectations, not
completion proof; `$codex-orchestrator` records real PR links or equivalent
integration proof during closeout.

Treat the PRD as the canonical source for delivery mode and branch/PR details.
The issue phase owns issue splitting and validates the generated issue graph
before publication. Generated issues copy only the effective `Delivery mode`
label as feature-level metadata inherited from `Source PRD`, plus issue-level
dependencies, parallelization, closeout, and any explicit issue-level exception
or cross-repo closeout rule.

Read `project-memory/agents/triage-labels.md` for the mapped `feature` type.
When GitHub issue types are available, create or update the PRD issue with that
mapped type, usually `Feature`. If issue types are disabled or unsupported,
publish the PRD without a type and keep the PRD title/body convention intact.
Use `$github-issues` for GitHub create, type, label, and dry-run command
mechanics.

Use the effective target from the `plan-feature` handoff without re-asking
unless this phase finds a new blocker or unresolved question. In hosted tracker
modes, local file writes apply only to explicit local mirrors or dry-run
targets; hosted body-file inputs are transient files outside the repo. Hosted
tracker mutation in this phase is limited to PRD planning-artifact publication
and metadata; implementation lifecycle comments, labels, direct closure, and
closeout mutations after scheduling starts belong to `$codex-orchestrator`.

Immediately before handing content to `$github-issues`, re-scan the final PRD
body for machine-local absolute paths and replace them with sanitized evidence
references. Treat any remaining unsanitized developer path as a blocker for
hosted publication.

If the configured target is GitHub but the current run explicitly requested
no-mutation output, do not mutate GitHub. Ask `$github-issues` for the exact
draft publish command and return it with the PRD body and stable
`source_prd_ref`, or use the configured local dry-run target when one is
recorded. For `draft-publish-commands`, also return the PRD title,
`feature_slug`, `project_slug` when applicable, and a short PRD body fingerprint
so later issue commands can prove they target the same draft. Return
`source_prd_ref=draft-prd:<feature-slug>` or
`source_prd_ref=draft-prd:<project-slug>/<feature-slug>` and state that the PRD
must be published first so generated issues can replace the draft ref with the
hosted PRD number before mutation.

If no issue-tracker setup exists, return the PRD in chat and recommend running
`$project-memory` before publishing.

### 5. Report Completion

Return:

- PRD title,
- authoritative `feature_slug`,
- product/workspace/context or orchestrator project identity used, when
  applicable,
- delivery mode used,
- that issue ordering and dependency graph validation are delegated to the
  issue phase,
- target location or "chat only",
- `source_prd_ref` for the issue phase,
- PRD body fingerprint when `source_prd_ref` is a `draft-prd:<...>` value,
- issue type applied, when the tracker supports it,
- support docs created or updated and the accepted source used for each, when
  applicable,
- any open questions,
- whether it is ready for the issue phase to create generated implementation
  issues.

## Guardrails

- Do not hide uncertainty. Put unresolved decisions in `## Open Questions`.
- Do not make the PRD a broad architecture plan; keep implementation details at
  the level needed for issue splitting.
- Do not create implementation issues from the PRD in this phase.
- Preserve existing PRD content when updating a local PRD file; revise only the
  sections needed for the current source material.
- Do not leak developer-machine paths in PRD evidence, source, or publication
  output. Use repo-relative, sibling-repo-relative, hosted, or descriptive
  sanitized references.

## References

- `references/prd-template.md`: default PRD shape.
- `$project-memory` `references/tracker-publishing.md`: shared tracker
  publication and `source_prd_ref` contract.
