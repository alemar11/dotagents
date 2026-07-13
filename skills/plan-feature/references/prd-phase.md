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
- Do not edit `CONTEXT.md`, project domain docs, or ADRs. Carry accepted durable
  knowledge as the caller-provided `domain_knowledge_delta`.
- Do not invent requirements, users, constraints, or acceptance criteria that
  are not supported by user input, repo evidence, or project memory.
- Do not ask for separate PRD write/publish confirmation after `plan-feature`
  has resolved setup, planning identity, blockers, and effective target.
  `tracker_backend` is the planning-artifact write authority only when
  `effective_target=configured-tracker`; other target values are non-mutating.
- In GitHub tracker mode, do not persist repo-local PRD mirrors
  or `.scratch/` staging copies unless `local_mirror=requested` and
  `effective_target=configured-tracker`.
- Use structured values for multi-choice fields. Read tracker and type mappings
  from project memory, and use the `delivery_mode` and `pr_closeout` values
  documented in `references/prd-template.md`.
- For publication mechanics, effective targets, and stable `source_prd_ref`
  behavior in draft command runs, use `$project-memory`'s `references/tracker-publishing.md`.

## Phase Handoff Inputs

When called by `plan-feature`, receive these fields from the entrypoint:

```text
mode: <full-flow|prd-only|issues-from-existing-prd>
execution_profile: <lean-prd|standard>
tracker_backend: <github|local>
effective_target: <configured-tracker|local-dry-run|draft-publish-commands>
no_mutation_override: <none|dry-run|temp|rehearsal|validation|disabled-writes|draft-output>
no_mutation_output: <not-applicable|local-artifacts|publish-commands>
local_mirror: <not-requested|requested>
local_mirror_path: <repo-relative mirror root|not-applicable>
partial_output: <withhold|allow-non-agent-ready>
source_prd_ref: <pending until #number, local path, or draft-prd:slug>
hosted_body_file_policy: transient-outside-repo
feature_slug: <accepted feature slug>
product_slug: <accepted product slug or not-applicable>
workspace_path: <accepted workspace path or not-applicable>
context_file: <selected CONTEXT.md or not-applicable>
project_slug: <accepted orchestrator project slug or not-applicable>
delivery_mode: <pull-request|direct-commit>
issue_mutation_authority: <none|pr-body-closeout-only|explicit-direct-mutation>
issue_mutation_authority_evidence: <option row evidence or none>
branch_name: <feature branch or exact authorized direct-commit target branch>
pr_closeout: <merge-ready|draft-only|not-applicable>
pr_shape: <single-pr|per-repo-pr|none>
capture_mode: defer-to-caller
capture_outcome: <deferred|no-durable-change>
option_resolution: <keyed run rows from references/options.md>
option_rows_fingerprint: <sha256:lowercase-hex for run rows>
domain_knowledge_delta:
  knowledge_delta: <required|none>
  decisions: <accepted durable terms, rules, boundaries, or decisions>
  target_surfaces: <repo-relative or repo-qualified context/docs/ADR destinations>
  evidence: <portable repo, hosted, or owner-decision references>
  unresolved: <empty for agent-ready planning, otherwise blockers>
```

The handoff is mandatory even when no grilling occurred. Use
`knowledge_delta: none` with `capture_outcome: no-durable-change` and empty
`decisions`, `target_surfaces`, and `evidence` lists when planning introduced
no durable project knowledge. Preserve `unresolved` independently and route
non-empty blockers through clarification and readiness gates. Use
`capture_outcome: deferred` when `knowledge_delta: required`.
Recompute `option_rows_fingerprint` with `references/options.md` before any
drafting or write. Stop on a mismatch.

## Workflow

### 1. Ground In Project Memory

For `lean-prd`, begin with only:

- `project-memory/agents/issue-tracker.md`;
- `project-memory/agents/triage-labels.md`;
- the shape/ownership routing in `project-memory/agents/domain.md` and
  `CONTEXT-MAP.md` when either exists, without loading unrelated content;
- the selected `CONTEXT.md` only when needed to resolve terminology or scope;
- the supplied intent plus directly relevant source, tests, or product docs.

Do not scan every ADR, sibling workspace doc, translation memory, or broad
source tree on the lean path unless the minimum evidence is missing,
contradictory, or reveals multi-context/cross-repo ownership. Widen to
`standard` immediately when a lean prerequisite fails and record why.

For `standard`, inspect the current project context before drafting:

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
- `issue_mutation_authority`
- `pr_closeout`

Use values passed by `plan-feature` when present. Otherwise derive them from
project memory and repo evidence, asking only when multiple contexts could
plausibly own the feature.

Resolve the PRD `delivery_mode` before drafting:

- `pull-request`: default for single-repo, monorepo, orchestrator workspace, and
  true cross-repo work. In a single repo or monorepo, use one feature branch and
  PR. In multi-repo work, every involved repo uses the same branch name and opens
  its own PR.
- `direct-commit`: a new decision records `delivery_mode=direct-commit` with
  `source=owner-instruction`; the row evidence names the exact owner
  instruction, feature scope, and authorized target branch, and `branch_name`
  equals that target. An existing PRD may use `source=source-prd` only when it
  preserves the same evidence. Unproven PRD prose cannot grant this mode.

Resolve `issue_mutation_authority` independently from delivery authority:

- local trackers use `none`;
- GitHub pull-request delivery uses `pr-body-closeout-only`;
- GitHub direct-commit delivery requires
  `explicit-direct-mutation` with a separate owner-authority row whose evidence
  explicitly authorizes final-commit issue closure for the same feature scope,
  target, and branch. Direct-commit publication wording alone cannot select
  this value; stop on the missing canonical choice before drafting.

For `pull-request`, resolve `pr_closeout` separately:

- `merge-ready`: default. Open the PR as draft initially, then validate, mark
  it ready, request Codex review, address feedback, and stop merge-ready.
- `draft-only`: use only when the option-resolution row records
  `pr_closeout=draft-only` with `source=owner-instruction` or `source-prd`.
  Other option evidence cannot select this value.

If the repo shape makes the affected repo set ambiguous, ask before writing the
PRD.

## PRD Target Model

Use this model before writing or publishing a PRD:

| Project shape | Tracker backend | PRD target | Generated issue source |
| --- | --- | --- | --- |
| Single repo | `github` | One PRD GitHub issue in the repo. | `source_prd_ref: #<number>` |
| Single repo | `local` | `.scratch/<feature-slug>/PRD.md` | `source_prd_ref: .scratch/<feature-slug>/PRD.md` |
| Monorepo or multi-context repo | `github` or `local` | One PRD for the selected product/workspace context. | The selected PRD issue/path plus product or workspace scope in each issue. |
| Workspace with multiple independent repos | `github` | Linked repo-scoped partial PRD issues when there is no accepted global PRD. | Each repo issue points at its repo partial PRD and links sibling partial PRDs. |
| Workspace with multiple independent repos | `local` | `projects/<project-slug>/features/<feature-slug>/PRD.md` or linked repo-scoped partial PRDs when that is the accepted source. | Each local issue points at the relevant PRD path and links sibling partial PRDs/issues. |

Do not invent a global PRD for workspace features. Use one only when it is the
accepted planning source; otherwise preserve the linked partial-PRD graph.

### 2. Confirm The PRD Source

Identify the source material:

- user conversation or pasted notes,
- output from `$grill-me-with-context`,
- the structured `domain_knowledge_delta` returned by deferred clarification,
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
- delivery contract: `delivery_mode`, independently resolved
  `issue_mutation_authority`, `pr_closeout`, `pr_shape`, branch data, and
  integration-proof expectations,
- issue-splitting note: sequencing, dependencies, and startability are derived
  from generated implementation issues and validated by the issue phase,
- data, permissions, API, or integration constraints when relevant,
- acceptance criteria,
- risks and open questions,
- notes for later issue splitting.

When `domain_knowledge_delta.knowledge_delta` is `required`, include a
`## Domain Knowledge Handoff` section using `references/prd-template.md`. Keep
the decisions and target surfaces portable and specific enough for the final
implementation task to update the repository after the behavior lands. This
section is a deferred-work carrier, not proof that domain docs were captured.
For multi-repo work, use `<repo-slug>/<repo-relative-path>` for every target and
repo-local evidence item; never publish an ambiguous bare `CONTEXT.md` or ADR
path.

Before returning, writing, or publishing the PRD, run a small documentation
gate: verify that evidence references are portable, runtime worker settings are
absent, delivery expectations are not presented as completion proof, open
questions are explicit, and rationale is sufficient for issue splitting without
turning the PRD into an implementation plan. Repair the PRD before output when
this gate fails.

Do not include workflow status fields such as `Status: Draft` in the PRD body.
PRD readiness and lifecycle state belong in the issue tracker, mapped labels,
or the generated implementation issues, not in the PRD content itself.

### 4. Choose Publication Target

Read `project-memory/agents/issue-tracker.md` to determine where PRDs live.
Also read `$project-memory`'s `references/tracker-publishing.md` for the
shared effective-target and `source_prd_ref` contract.

- `tracker_backend=github`: when `effective_target=configured-tracker`, publish through
  `$gitstack:github-issues`, using the title format `PRD: <Feature Name>` and the
  mapped `feature` issue type when available. Do not write
  `.scratch/<feature-slug>/PRD.md` or `project-memory/features/...` as part of
  GitHub publishing unless `local_mirror=requested`; when requested, write the
  mirror under `local_mirror_path`.
- `tracker_backend=local`: when `effective_target=configured-tracker`, write to the configured repo-local PRD path,
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
  issues through `$gitstack:github-issues`. Derive or ask for `<project-slug>`,
  `<feature-slug>`, and the affected repo list. Related PRDs and implementation
  issues must link to each other. Do not create local `projects/...` feature
  artifacts or `.scratch/` mirrors unless
  `effective_target=configured-tracker` and `local_mirror=requested`; write any
  requested mirror under `local_mirror_path`.

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
branch naming such as `feature/<feature-slug>`, `pr_closeout`, canonical
`pr_shape`, and the validation required before implementation issues close. In
multi-repo work,
record the same branch name for each affected repo, expected repo PR slots or
pre-implementation placeholders, and the cross-repo proof needed before issues
close. For `delivery_mode=direct-commit`, record the exact authorized target
branch, scoped `delivery_mode_evidence`, and separately scoped
`issue_mutation_authority_evidence` from their option rows. Placeholders in
the PRD are delivery expectations, not completion proof;
`$codex-orchestrator` records real PR links or equivalent integration proof
during closeout.

Treat the PRD as the canonical source for `delivery_mode`,
`issue_mutation_authority`, `pr_closeout`, `pr_shape`, and branch/PR data.
The issue phase owns issue splitting and validates the generated issue graph
before publication. Generated issues copy the effective `delivery_mode`,
`issue_mutation_authority`, `pr_closeout`, and `pr_shape` values as
feature-level metadata inherited from `source_prd_ref`, plus
issue-level dependencies, parallelization, closeout, and any explicit
issue-level exception or cross-repo closeout rule.

Read `project-memory/agents/triage-labels.md` for the mapped `feature` type.
When GitHub issue types are available, create or update the PRD issue with that
mapped type, usually `Feature`. If issue types are disabled or unsupported,
publish the PRD without a type and keep the PRD title/body convention intact.
Use `$gitstack:github-issues` for GitHub create, type, label, and dry-run command
mechanics. In mutating GitHub runs, pass the sanitized PRD title, body, target
repo, type, and labels to `$gitstack:github-issues`; do not assemble a direct `gh issue
create` shell command with generated Markdown in this phase. `$gitstack:github-issues`
owns safe temporary body-file creation, non-interpolating body writes, cleanup,
state verification, and partial-failure recovery.

Use `effective_target` from the `plan-feature` handoff without re-resolving it.
`configured-tracker` performs the backend write. `local-dry-run` returns paths
and bodies without writing. `draft-publish-commands` returns exact hosted
commands without mutation. In hosted tracker modes, local file writes apply
only when `effective_target=configured-tracker` and `local_mirror=requested`;
hosted body-file inputs are transient files outside the repo. Hosted
tracker mutation in this phase is limited to PRD planning-artifact publication
and metadata; implementation lifecycle comments, labels, direct closure, and
closeout mutations after scheduling starts belong to `$codex-orchestrator`.

Immediately before handing content to `$gitstack:github-issues`, re-scan the final PRD
body for machine-local absolute paths and replace them with sanitized evidence
references. Treat any remaining unsanitized developer path as a blocker for
hosted publication.

For `tracker_backend=github`, branch only on `effective_target`:
`configured-tracker` publishes, `local-dry-run` returns the PRD body and target
without mutation, and `draft-publish-commands` asks `$gitstack:github-issues`
for the exact draft publish command. For `draft-publish-commands`, also return the PRD title,
`feature_slug`, `project_slug` when applicable, and a short PRD body fingerprint
so later issue commands can prove they target the same draft. Return
`source_prd_ref=draft-prd:<feature-slug>` or
`source_prd_ref=draft-prd:<project-slug>/<feature-slug>` and state that the PRD
must be published first so generated issues can replace the draft ref with the
hosted PRD number before mutation.

For `effective_target=local-dry-run`, return the same deterministic
`draft-prd:<...>` form plus the PRD body fingerprint and resolved local target.
This is a non-executable temporary source: the issue phase may use it to build
dry-run bodies, but Orchestrator may inspect only and must not dispatch or
mutate from it.

If no issue-tracker setup exists, return the PRD in chat and recommend running
`$project-memory` before publishing.

### 5. Report Completion

Return:

- PRD title,
- canonical keyed option rows and option-resolution evidence, including any
  execution-profile widening reason,
- `option_rows_fingerprint`,
- authoritative `feature_slug`,
- the structured delivery handoff tuple: `delivery_mode`,
  `issue_mutation_authority`, `issue_mutation_authority_evidence`,
  `branch_name`, `pr_closeout`, and `pr_shape`,
- product/workspace/context or orchestrator project identity used, when
  applicable,
- that issue ordering and dependency graph validation are delegated to the
  issue phase,
- target location or "chat only",
- `local_mirror` result and `local_mirror_path`,
- `source_prd_ref` for the issue phase,
- PRD body fingerprint when `source_prd_ref` is a `draft-prd:<...>` value,
- issue type applied, when the tracker supports it,
- support docs created or updated and the accepted source used for each, when
  applicable,
- any open questions,
- `knowledge_delta`, `capture_outcome`, and whether the PRD contains a
  `## Domain Knowledge Handoff`,
- whether it is ready for the issue phase to create generated implementation
  issues.

## Evidence And Phase Metrics

Read each unchanged source body once. Keep a compact working index containing
its portable path/ref, fingerprint, and relevant headings. After drafting or
repairing the PRD, carry only the target path/ref, body fingerprint, changed
headings, and failed-gate excerpts between passes. Re-open or emit the complete
body only when its fingerprint changed, a gate requires the relevant section,
the effective target is chat/draft output, or final publication needs it.

For configured local or hosted targets, completion output should identify the
PRD and its fingerprint instead of repeating the complete body. Draft/chat
output still returns the requested body.

When root-scoped runtime token counters cover an uncontaminated PRD interval,
capture start and end checkpoints and return:

```text
phase=prd
tokens=<exact delta|unavailable>
references_loaded=<paths actually opened>
artifact=<source_prd_ref>; fingerprint=<sha256 or hosted revision>
full_body_emitted=<no|chat-output|draft-output|publication|gate-failure>
```

If the interval contains other activity, label its delta `exact-interval` and
do not attribute it to the PRD phase. If exact counters are unavailable, record
`tokens=unavailable` once without probing session archives, estimating from
text size, or blocking the phase.

## Guardrails

- Do not hide uncertainty. Put unresolved decisions in `## Open Questions`.
- Do not make the PRD a broad architecture plan; keep implementation details at
  the level needed for issue splitting.
- Do not create implementation issues from the PRD in this phase.
- Do not treat the PRD's `## Domain Knowledge Handoff` as completed durable
  capture.
- Preserve existing PRD content when updating a local PRD file; revise only the
  sections needed for the current source material.
- Do not leak developer-machine paths in PRD evidence, source, or publication
  output. Use repo-relative, sibling-repo-relative, hosted, or descriptive
  sanitized references.

## References

- `references/prd-template.md`: default PRD shape.
- `$project-memory`'s `references/tracker-publishing.md`: shared tracker
  publication and `source_prd_ref` contract.
