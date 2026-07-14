# Feature Spec Phase

Use this reference when `plan-feature` needs to turn clarified feature,
product, migration, cross-repo project, or workflow intent into a practical Feature Spec.
This is an internal phase, not a public skill.

## Goal

Produce or publish a Feature Spec that can feed the issue phase. If the source material
is still too vague to produce a useful Feature Spec, return the smallest blocking
question set or route back through `$grill-me-with-context`.

## Boundaries

- Do not implement the feature.
- Do not split the Feature Spec into implementation issues; the issue phase owns that.
- Do not edit `CONTEXT.md`, project domain docs, or ADRs. Carry accepted durable
  knowledge as the caller-provided `domain_knowledge_delta`.
- Do not invent requirements, users, constraints, or acceptance criteria that
  are not supported by user input, repo evidence, or project memory.
- Do not ask for separate Feature Spec write/publish confirmation after `plan-feature`
  has resolved setup, planning identity, blockers, and effective target.
  `tracker_backend` is the planning-artifact write authority only when
  `effective_target=configured-tracker`; other target values are non-mutating.
- In GitHub tracker mode, do not persist repo-local Feature Spec mirrors
  or `planning/tmp/` staging copies unless `local_mirror=requested` and
  `effective_target=configured-tracker`.
- Use structured values for multi-choice fields. `references/options.md` is the
  sole owner of option values, defaults, evidence, and cross-field resolution;
  read tracker and type mappings from project memory, then project the verified
  values through `references/spec-template.md`.
- Resolve `effective_target` only through `references/options.md`. After
  resolution, use `$project-memory`'s `references/tracker-publishing.md` for
  publication transport, stable `source_spec_ref` behavior, mutation
  verification, cleanup, and partial recovery.

## Phase Handoff Inputs

Receive the verified run-level `option_resolution` rows and
`option_rows_fingerprint` defined by `references/options.md`, plus:

- the planning identity (`feature_slug` and any selected `product_slug`,
  `workspace_path`, `context_file`, `project_slug`, `repository_layout`,
  `child_repository_layout`, `workspace_context`, `workspace_parent_source_ref`,
  and `workspace_feature_repos`);
- pending or existing `source_spec_ref` state and the
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

For `lean-spec`, begin with only:

- `project-memory/config/issue-tracker.md`;
- `project-memory/config/project-layout.md`;
- `project-memory/config/triage-labels.md`;
- the shape/ownership routing in `project-memory/config/domain.md` and
  `CONTEXT-MAP.md` when either exists, without loading unrelated content;
- the selected `CONTEXT.md` only when needed to resolve terminology or scope;
- the supplied intent plus directly relevant source, tests, or product docs.

Do not scan every ADR, sibling workspace doc, translation memory, or broad
source tree on the lean path unless the minimum evidence is missing,
contradictory, or reveals multi-context/cross-repo ownership. Widen to
`standard` immediately when a lean prerequisite fails and record why.

For `standard`, inspect the current project context before drafting:

- `project-memory/config/issue-tracker.md`
- `project-memory/config/project-layout.md`
- `project-memory/config/triage-labels.md`
- `project-memory/config/domain.md`
- `CONTEXT.md` or `CONTEXT-MAP.md`
- `TRANSLATION.md`, when present for the selected context
- `project-memory/adr/`
- orchestrator workspace docs such as `orchestration/<project>/PROJECT.md` and
  `orchestration/<project>/repos/*.md`, when planning from a local orchestrator
  workspace
- README, product docs, issue templates, and relevant source/tests

If setup files are missing, continue with repo evidence and say which project
memory files were unavailable.

If `CONTEXT-MAP.md` or `project-memory/config/domain.md` indicates a
multi-context repo or monorepo, resolve the selected product/workspace context
before writing:

- `product_slug`
- `workspace_path`
- `context_file`
- `feature_slug`
- `repository_layout`

Use identity values passed by `plan-feature` when present. Otherwise derive
only those identity fields from project memory and repo evidence, asking when
multiple contexts could plausibly own the feature.

Do not resolve delivery or mutation options in this phase. Consume the complete
verified delivery tuple and `target_branch_name` data from the run-level
`option_resolution` handoff, whose values, defaults, evidence, and cross-field
rules are owned by `references/options.md`. If required rows are absent,
contradictory, or fail their fingerprint, return to caller-owned option
resolution before drafting. Project the accepted rows without reinterpreting
their prose or applying another default.

If the repo shape makes the affected repo set ambiguous, ask before writing the
Feature Spec.

## Feature Spec Target Model

Use this model before writing or publishing a Feature Spec:

When `workspace_context=multi-repository-workspace`, `repository_layout` is the
workspace graph topology and must use `multi-repository-workspace`. Repo-scoped child
partials preserve the child repo's durable topology in `child_repository_layout`.

| Project topology | Tracker backend | Feature Spec target | Generated issue source |
| --- | --- | --- | --- |
| `single-repository` | `github` | One Feature Spec GitHub issue in the repo. | `source_spec_ref: #<number>` |
| `single-repository` | `local` | `planning/features/<feature-slug>/SPEC.md` | `source_spec_ref: planning/features/<feature-slug>/SPEC.md` |
| `monorepo` | `github` or `local` | One Feature Spec for the selected product/workspace context. | The selected Feature Spec issue/path plus product or workspace scope in each issue. |
| `multi-repository-workspace` | Parent `github` or `local`; child tracker per affected repo | Parent/global Feature Spec only when it is the accepted source. Repo-scoped partial Feature Specs route through each affected child repo's tracker. | Each repo issue points at its repo partial Feature Spec and links sibling partial Feature Specs. |

Do not invent a global Feature Spec for workspace features. Use one only when it is the
accepted planning source; otherwise preserve the linked partial Feature Spec graph.
For `multi-repository-workspace`, resolve `workspace_feature_repos` first, then read
each affected child repo's `project-memory/config/issue-tracker.md` and
`project-memory/config/project-layout.md`, or accepted repo metadata that
explicitly covers both tracker routing and durable topology, before publishing
partial Feature Specs. Use the child layout config or accepted metadata as the
source for `child_repository_layout`; if child topology is unavailable or
contradictory, stop before child partial publication. A child repo with
`tracker_backend=github` gets a repo-scoped GitHub Feature Spec issue in that
child repository. A child repo with `tracker_backend=local` gets its configured
repo-local Feature Spec path. If child tracker routing is unavailable, stop
instead of writing a parent-local artifact as a substitute. Because the current
run-level contract has one `tracker_backend` and one `effective_target`, one
option-resolution run may publish only one artifact set. Publish an accepted
parent/global Feature Spec in a parent run, then publish child repo partials in
child run(s) that cite the parent `source_spec_ref`. All affected child repos
in one generated issue graph must share the same effective child backend
because issue publication, closeout, and option fingerprints are currently
single-backend per graph; stop before agent-ready issue generation when child
backends are mixed. Use a two-pass child publication flow: publish or draft all
child partials to obtain stable refs, then update every child partial with the
complete `workspace_child_source_refs` mapping and cross-links before issue
generation. Parent `tracker_backend` controls only the parent/global
coordination artifact, while child runs keep each child repo's durable
topology as `child_repository_layout` and carry parent workspace context as
`workspace_context=multi-repository-workspace`, `workspace_parent_source_ref`, and
source/ref data.

### 2. Confirm The Feature Spec Source

Identify the source material:

- user conversation or pasted notes,
- output from `$grill-me-with-context`,
- the structured `domain_knowledge_delta` returned by deferred clarification,
- an existing issue, doc, or planning note,
- repo behavior that needs to become a defined product surface.

If key facts are missing, ask only for decisions that would materially change
the Feature Spec. Prefer defaults when the repo or project memory already implies them.

### 3. Draft The Feature Spec

Use `references/spec-template.md` unless the repo has a stronger local Feature Spec
format.

Before returning, writing, or publishing the Feature Spec, sanitize every source and
evidence reference that came from local filesystem inspection. Published Feature Specs
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

If the same file is useful both locally and in the Feature Spec, keep the raw absolute
path only in private working context and put only the sanitized reference in
the Feature Spec body or GitHub issue body. If sanitization would make the evidence
ambiguous, add the repo name or source label rather than restoring an absolute
path.

Keep the Feature Spec implementation-facing:

- clear problem and target user,
- goals and non-goals,
- functional requirements,
- user workflow or system behavior,
- selected planning identity: feature slug, product or project slug, workspace
  path, context file, and project topology when applicable,
- delivery contract: `change_delivery_target`, independently resolved
  `change_delivery_permission`, `issue_update_permission`,
  `codex_review_requirement`, `repository_layout`, `child_repository_layout`,
  `pull_request_count_strategy`, branch data, and integration-proof expectations,
- issue-splitting note: sequencing, dependencies, and startability are derived
  from generated implementation issues and validated by the issue phase,
- data, permissions, API, or integration constraints when relevant,
- acceptance criteria,
- risks and open questions,
- notes for later issue splitting.

When `domain_knowledge_delta.knowledge_delta` is `required`, include a
`## Domain Knowledge Handoff` section using `references/spec-template.md`. Keep
the decisions and target surfaces portable and specific enough for the final
implementation task to update the repository after the behavior lands. This
section is a deferred-work carrier, not proof that domain docs were captured.
For multi-repo work, use `<repo-slug>/<repo-relative-path>` for every target and
repo-local evidence item; never publish an ambiguous bare `CONTEXT.md` or ADR
path.

Before returning, writing, or publishing the Feature Spec, run a small documentation
gate: verify that evidence references are portable, runtime worker settings are
absent, delivery expectations are not presented as completion proof, open
questions are explicit, and rationale is sufficient for issue splitting without
turning the Feature Spec into an implementation plan. Repair the Feature Spec before output when
this gate fails.

Do not include workflow status fields such as `Status: Draft` in the Feature Spec body.
Feature Spec readiness and lifecycle state belong in the issue tracker, mapped labels,
or the generated implementation issues, not in the Feature Spec content itself.

### 4. Choose Publication Target

Read `project-memory/config/issue-tracker.md` for the repo target,
`project-memory/config/project-layout.md` for topology, and
`project-memory/config/triage-labels.md` for the mapped `feature` type.
`references/options.md` solely owns effective-target and local-mirror option
resolution. After that resolution, `$project-memory`'s
`references/tracker-publishing.md` owns transient body transport, mirror-path
application, draft-ref replacement, hosted mutation verification, cleanup, and
partial recovery. Branch only on the verified target:

| Target | Feature Spec phase action |
| --- | --- |
| `tracker_backend=github`, `effective_target=configured-tracker` | Publish the sanitized `Feature Spec: <Feature Name>` through `$gitstack:github-issues`; apply the mapped feature type when supported. |
| `tracker_backend=local`, `effective_target=configured-tracker` | Write the resolved path from the Feature Spec Target Model. |
| `effective_target=local-dry-run` | Return the resolved target, body, deterministic `draft-spec:<...>` ref, and Feature Spec body fingerprint without writing; label the source non-executable. |
| `effective_target=draft-publish-commands` | Ask `$gitstack:github-issues` for exact commands and return the title, body, identity, deterministic draft ref, and fingerprint; publish the Feature Spec first and replace draft refs before issue mutation. |

For `effective_target=local-dry-run`, Orchestrator may inspect but must not
dispatch or mutate from the temporary source. Hosted local writes require both
`effective_target=configured-tracker` and `local_mirror=requested`, and must use
the validated `local_mirror_path`.

For a local orchestrator workspace with an accepted parent/global Feature Spec,
the resolved parent path is
`orchestration/<project-slug>/features/<feature-slug>/SPEC.md`. This phase may also
create or update `PROJECT.md`, `repos/<repo-slug>.md`, and
`integration-gates.md` only from accepted planning sources and must report that
source. Do not publish repo-scoped child partials in that same parent run.
Repo-scoped partial Feature Specs use each affected child repo's tracker
backend in child run(s) that cite the parent source. For child GitHub planning,
publish linked partial Feature Specs through `$gitstack:github-issues`,
preserve cross-repo links, and create no local feature artifacts except an
authorized mirror.

Derive `<Feature Name>` from the accepted product or short feature phrase; omit
issue numbers, statuses, and slice names. State concrete repo/workspace scope and topology,
including affected repos, cross-repo contracts, integration gates, and order
when material. In every Feature Spec, render the verified delivery tuple through
`references/spec-template.md`, including the resolved topology, repo/branch/PR shape, and
integration proof. For child partials in a multi-repo workspace, include
`workspace_context=multi-repository-workspace` and `workspace_parent_source_ref` in
the Feature Spec body and phase handoff. Placeholders are expectations, not
completion proof.

The Feature Spec remains canonical for the feature delivery tuple; the issue phase
projects it, adds issue-level scheduling/closeout, and validates the graph. For
GitHub, `$gitstack:github-issues` owns safe body transport, mutation
verification, cleanup, and recovery; do not construct a mutating `gh issue
create` command with generated Markdown.

Immediately before hosted publication, reject any remaining machine-local
absolute path. Hosted mutation is limited to Feature Spec planning-artifact publication
and metadata; implementation lifecycle and closeout mutations
belong to `$codex-orchestrator`. If tracker setup is absent, return the Feature Spec in
chat and recommend `$project-memory` before publication.

### 5. Report Completion

Return:

- Feature Spec title,
- canonical keyed option rows and option-resolution evidence, including any
  execution-profile widening reason,
- `option_rows_fingerprint`,
- authoritative `feature_slug`,
- the structured delivery handoff tuple: `change_delivery_target`, `repository_layout`,
  `child_repository_layout`, `workspace_context`, `workspace_parent_source_ref`,
  `workspace_feature_repos`, `change_delivery_permission`,
  `change_delivery_permission_evidence`,
  `issue_update_permission`, `issue_update_permission_evidence`,
  `codex_review_requirement`, `target_branch_name`, and
  `pull_request_count_strategy`,
- `workspace_child_source_refs` mapping each `workspace_feature_repos` repo to
  its child partial Feature Spec ref only after the child partial artifact set
  exists. Keys are canonical repo slugs and must match
  `workspace_feature_repos`. A parent/global run or first-pass child run
  returns `workspace_child_source_refs=unresolved-first-pass` or omits it, and
  is not issue-ready by itself,
- product/workspace/context or orchestrator project identity used, when
  applicable,
- that issue ordering and dependency graph validation are delegated to the
  issue phase,
- target location or "chat only",
- `local_mirror` result and `local_mirror_path`,
- `source_spec_ref` for the issue phase,
- Feature Spec body fingerprint when `source_spec_ref` is a `draft-spec:<...>` value,
- issue type applied, when the tracker supports it,
- support docs created or updated and the accepted source used for each, when
  applicable,
- any open questions,
- `knowledge_delta`, `capture_outcome`, and whether the Feature Spec contains a
  `## Domain Knowledge Handoff`,
- whether it is ready for the issue phase to create generated implementation
  issues.

## Evidence And Phase Metrics

Read each unchanged source body once. Keep a compact working index containing
its portable path/ref, fingerprint, and relevant headings. After drafting or
repairing the Feature Spec, carry only the target path/ref, body fingerprint, changed
headings, and failed-gate excerpts between passes. Re-open or emit the complete
body only when its fingerprint changed, a gate requires the relevant section,
the effective target is chat/draft output, or final publication needs it.

For configured local or hosted targets, completion output should identify the
Feature Spec and its fingerprint instead of repeating the complete body. Draft/chat
output still returns the requested body.

When root-scoped runtime token counters cover an uncontaminated Feature Spec interval,
capture start and end checkpoints and return:

```text
phase=spec
tokens=<exact delta|unavailable>
references_loaded=<paths actually opened>
artifact=<source_spec_ref>; fingerprint=<sha256 or hosted revision>
full_body_emitted=<no|chat-output|draft-output|publication|gate-failure>
```

If the interval contains other activity, label its delta `exact-interval` and
do not attribute it to the Feature Spec phase. If exact counters are unavailable, record
`tokens=unavailable` once without probing session archives, estimating from
text size, or blocking the phase.

## Guardrails

- Do not hide uncertainty. Put unresolved decisions in `## Open Questions`.
- Do not make the Feature Spec a broad architecture plan; keep implementation details at
  the level needed for issue splitting.
- Do not create implementation issues from the Feature Spec in this phase.
- Do not treat the Feature Spec's `## Domain Knowledge Handoff` as completed durable
  capture.
- Preserve existing Feature Spec content when updating a local Feature Spec file; revise only the
  sections needed for the current source material.
- Do not leak developer-machine paths in Feature Spec evidence, source, or publication
  output. Use repo-relative, sibling-repo-relative, hosted, or descriptive
  sanitized references.

## References

- `references/spec-template.md`: default Feature Spec shape.
- `$project-memory`'s `references/tracker-publishing.md`: shared tracker
  publication and `source_spec_ref` contract.
