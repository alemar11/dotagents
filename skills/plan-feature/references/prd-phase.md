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
- Use structured values for multi-choice fields. `references/options.md` is the
  sole owner of option values, defaults, evidence, and cross-field resolution;
  read tracker and type mappings from project memory, then project the verified
  values through `references/prd-template.md`.
- Resolve `effective_target` only through `references/options.md`. After
  resolution, use `$project-memory`'s `references/tracker-publishing.md` for
  publication transport, stable `source_prd_ref` behavior, mutation
  verification, cleanup, and partial recovery.

## Phase Handoff Inputs

Receive the verified run-level `option_resolution` rows and
`option_rows_fingerprint` defined by `references/options.md`, plus:

- the planning identity (`feature_slug` and any selected `product_slug`,
  `workspace_path`, `context_file`, and `project_slug`);
- pending or existing `source_prd_ref` state and the
  `hosted_body_file_policy=transient-outside-repo` transport rule;
- `capture_mode=defer-to-caller`, `capture_outcome`, and the structured
  `domain_knowledge_delta` (`knowledge_delta`, `decisions`, `target_surfaces`,
  `evidence`, and independent `unresolved` blockers).

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

Use identity values passed by `plan-feature` when present. Otherwise derive
only those identity fields from project memory and repo evidence, asking when
multiple contexts could plausibly own the feature.

Do not resolve delivery or mutation options in this phase. Consume the complete
verified delivery tuple and `branch_name` data from the run-level
`option_resolution` handoff, whose values, defaults, evidence, and cross-field
rules are owned by `references/options.md`. If required rows are absent,
contradictory, or fail their fingerprint, return to caller-owned option
resolution before drafting. Project the accepted rows without reinterpreting
their prose or applying another default.

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

Read `project-memory/agents/issue-tracker.md` for the repo target and
`project-memory/agents/triage-labels.md` for the mapped `feature` type.
`references/options.md` solely owns effective-target and local-mirror option
resolution. After that resolution, `$project-memory`'s
`references/tracker-publishing.md` owns transient body transport, mirror-path
application, draft-ref replacement, hosted mutation verification, cleanup, and
partial recovery. Branch only on the verified target:

| Target | PRD phase action |
| --- | --- |
| `tracker_backend=github`, `effective_target=configured-tracker` | Publish the sanitized `PRD: <Feature Name>` through `$gitstack:github-issues`; apply the mapped feature type when supported. |
| `tracker_backend=local`, `effective_target=configured-tracker` | Write the resolved path from the PRD Target Model. |
| `effective_target=local-dry-run` | Return the resolved target, body, deterministic `draft-prd:<...>` ref, and PRD body fingerprint without writing; label the source non-executable. |
| `effective_target=draft-publish-commands` | Ask `$gitstack:github-issues` for exact commands and return the title, body, identity, deterministic draft ref, and fingerprint; publish the PRD first and replace draft refs before issue mutation. |

For `effective_target=local-dry-run`, Orchestrator may inspect but must not
dispatch or mutate from the temporary source. Hosted local writes require both
`effective_target=configured-tracker` and `local_mirror=requested`, and must use
the validated `local_mirror_path`.

For a local orchestrator workspace, the resolved PRD path is
`projects/<project-slug>/features/<feature-slug>/PRD.md`. This phase may also
create or update `PROJECT.md`, `repos/<repo-slug>.md`, and
`integration-gates.md` only from accepted planning sources and must report that
source. For GitHub workspace planning, publish linked partial PRDs through
`$gitstack:github-issues`, preserve cross-repo links, and create no local feature
artifacts except an authorized mirror.

Derive `<Feature Name>` from the accepted product or short feature phrase; omit
issue numbers, statuses, and slice names. State concrete repo/workspace scope,
including affected repos, cross-repo contracts, integration gates, and order
when material. In every PRD, render the verified delivery tuple through
`references/prd-template.md`, including the resolved repo/branch/PR shape and
integration proof. Placeholders are expectations, not completion proof.

The PRD remains canonical for the feature delivery tuple; the issue phase
projects it, adds issue-level scheduling/closeout, and validates the graph. For
GitHub, `$gitstack:github-issues` owns safe body transport, mutation
verification, cleanup, and recovery; do not construct a mutating `gh issue
create` command with generated Markdown.

Immediately before hosted publication, reject any remaining machine-local
absolute path. Hosted mutation is limited to PRD planning-artifact publication
and metadata; implementation lifecycle and closeout mutations
belong to `$codex-orchestrator`. If tracker setup is absent, return the PRD in
chat and recommend `$project-memory` before publication.

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
