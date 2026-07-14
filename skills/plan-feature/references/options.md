# Plan Feature Option Contract

Load this reference before resolving a Plan Feature run. It is the canonical
registry for selectable planning behavior.

## Syntax

- Option field names use snake_case and match
  `^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$`.
- Enum values use lower-kebab-case and match
  `^[a-z0-9]+(?:-[a-z0-9]+)*$`. A one-word lowercase value already satisfies
  this rule.
- Counts, paths, slugs, issue refs, fingerprints, and evidence are data, not
  option values.
- User wording, tracker prose, and legacy labels are selection evidence only.
  Normalize them once, record the canonical field/value plus evidence, and do
  not carry the prose as an alternative option value.
- Emit only canonical option field names and values in phase handoffs,
  generated structured metadata, draft commands, and completion reports.

## Registry

These run-level options resolve before the first phase handoff.

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `mode` | `full-flow`, `spec-only`, `issues-from-existing-spec` | `full-flow` for new intent | A direct existing Feature Spec issue split resolves to `issues-from-existing-spec`; an explicit Feature Spec stop resolves to `spec-only`. |
| `execution_profile` | `lean-spec`, `lean-issues`, `standard` | `standard` | Internal optimization only; it cannot weaken a selected mode's gates. |
| `tracker_backend` | `github`, `local` | From project memory | Planning-artifact write authority for the current artifact set. In `multi-repo-workspace`, parent/global artifacts and child repo partial artifacts are separate artifact sets. |
| `effective_target` | `configured-tracker`, `local-dry-run`, `draft-publish-commands` | `configured-tracker` | Derived from tracker routing plus the current-run mutation option. |
| `no_mutation_override` | `none`, `dry-run`, `temp`, `rehearsal`, `validation`, `disabled-writes`, `draft-output` | `none` | Changes the effective target, not delivery or PR lifecycle. |
| `no_mutation_output` | `not-applicable`, `local-artifacts`, `publish-commands` | `not-applicable` when mutation is allowed; otherwise `publish-commands` for GitHub and `local-artifacts` for local trackers | Selects the non-mutating output shape. |
| `local_mirror` | `not-requested`, `requested` | `not-requested` | Applies only when a hosted artifact would otherwise have no local mirror. |
| `project_topology` | `single-repo`, `monorepo`, `multi-repo-workspace` | From project memory, workspace context, or safe repo evidence | Planning graph topology. In workspace issue generation it is `multi-repo-workspace`; child repo durability is carried separately as `repo_project_topology`. It is not a worker or execution-order setting. |
| `workspace_context` | `multi-repo-workspace`, `not-applicable` | `multi-repo-workspace` when the source or topology proves a workspace graph; otherwise `not-applicable` | Gates workspace-only partial Feature Spec, child-source mapping, and orchestrator loading behavior. |
| `delivery_mode` | `pull-request`, `direct-commit` | `pull-request` | `direct-commit` requires explicit owner authority evidence. |
| `issue_mutation_authority` | `none`, `pr-body-closeout-only`, `explicit-direct-mutation` | Derived from tracker and delivery | Final-commit issue closure is separate from direct-commit publication authority. |
| `pr_closeout` | `merge-ready`, `draft-only`, `not-applicable` | `merge-ready` for `pull-request`; `not-applicable` for `direct-commit` | `draft-only` requires explicit owner or structured source evidence. |
| `pr_shape` | `single-pr`, `per-repo-pr`, `none` | Derived from repo scope and `delivery_mode` | `none` is valid only for `direct-commit`. |
| `partial_output` | `withhold`, `allow-non-agent-ready` | `withhold` | The non-default value permits `needs-info` or `ready-for-human` artifacts but never `ready-for-agent`. |

`local_mirror_path` is a data field, not an enum. Use a validated repo-relative
mirror root when `local_mirror=requested`; use `not-applicable` otherwise.

`branch_name` is also data. For `pull-request`, default it to
`feature/<feature_slug>` unless an accepted source Feature Spec or repository policy
provides another valid branch; multi-repo work uses the same exact branch in
every involved repository. For `direct-commit`, it must equal the exact target
branch in the scoped owner evidence.

`repo_project_topology` is data for repo-scoped workspace partial Feature
Specs. It uses the same topology values as `project_topology`, records the
child repo's durable project layout, and is `not-applicable` outside
repo-scoped workspace partials.

Resolve `workspace_context` before phase handoff. Precedence is: explicit
current Feature Spec or handoff value; `project_topology=multi-repo-workspace`;
linked parent/global source or sibling partial Feature Spec evidence; safe
workspace evidence from project memory; otherwise `not-applicable`. If an
explicit value contradicts the linked source graph or project topology, stop as
`needs-owner` instead of guessing.

## Per-Issue Registry

Resolve these fields once per generated issue after the issue graph exists and
before emitting that issue or its `## Orchestrator Handoff`.

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `delivery_source` | `feature-level-inherited`, `issue-level-override` | `feature-level-inherited` | Authorization evidence for an override is stored separately. |
| `delivery_mode` | `pull-request`, `direct-commit` | Inherited from the feature | Records the issue-effective value after any authorized override. |
| `issue_project_topology` | `single-repo`, `monorepo`, `multi-repo-workspace` | Inherited from the issue's repo-scoped Feature Spec or target repo | Preserves per-issue child topology when a workspace graph spans heterogeneous repos. |
| `issue_mutation_authority` | `none`, `pr-body-closeout-only`, `explicit-direct-mutation` | Inherited from the feature | Re-resolve atomically with tracker, delivery, and closeout. |
| `pr_shape` | `single-pr`, `per-repo-pr`, `none` | Inherited from the feature | Re-resolve atomically when `delivery_source=issue-level-override`. |
| `pr_closeout` | `merge-ready`, `draft-only`, `not-applicable` | Inherited from the feature | Re-resolve atomically when `delivery_source=issue-level-override`. |
| `parallelization` | `independent`, `depends-on`, `blocks`, `root-integrated` | Derived per issue | Dependency ids are carried separately as data. |
| `closeout_mode` | `feature-pr-closes-issue`, `repo-pr-closes-issue`, `direct-commit-closes-issue`, `local-done-move-after-proof` | Derived from tracker and delivery | Names the issue completion path. |
| `integration_mode` | `single-repo-pr`, `repo-pr`, `direct-commit`, `not-applicable` | `not-applicable` when no exceptional integration path exists | Repo refs and ordering remain data. |
| `domain_closeout` | `not-applicable`, `implementation-closeout` | `not-applicable` | The final integration owner selects `implementation-closeout`; decisions and targets remain data. |

The feature-scoped and issue-scoped delivery fields deliberately share names.
Scope is carried by the resolution row: every issue records its effective
`delivery_mode`, `pr_shape`, and `pr_closeout`, whether inherited or overridden.

## Effective Target Resolution

Resolve this pair once before either phase starts:

| `tracker_backend` | `no_mutation_override` | `no_mutation_output` | `effective_target` |
| --- | --- | --- | --- |
| `github` | `none` | `not-applicable` | `configured-tracker` |
| `local` | `none` | `not-applicable` | `configured-tracker` |
| `github` | Any non-`none` registry value | `publish-commands` | `draft-publish-commands` |
| `github` | Any non-`none` registry value | `local-artifacts` | `local-dry-run` |
| `local` | Any non-`none` registry value | `local-artifacts` | `local-dry-run` |

Reject any other combination as an invalid option snapshot. Downstream phases
branch only on `effective_target`; they do not reinterpret the mutation reason.

## Cross-Field Validation

- `local_mirror=requested` requires `tracker_backend=github` and
  `effective_target=configured-tracker` plus a non-empty, safe
  `local_mirror_path`. `local_mirror=not-requested` requires
  `local_mirror_path=not-applicable`.
- `delivery_mode=pull-request` requires
  `pr_closeout=merge-ready` or `pr_closeout=draft-only` and requires
  `pr_shape=single-pr` or `pr_shape=per-repo-pr`.
- `pr_shape` is derived from affected repository scope, not topology alone.
  Pull-request delivery for one affected repo uses `pr_shape=single-pr` with
  one feature branch and PR. Pull-request delivery for multiple affected repos
  uses `pr_shape=per-repo-pr`, the same `branch_name` in every involved repo,
  and one PR per involved repo. For `project_topology=multi-repo-workspace`,
  resolve affected repos before deriving `pr_shape`.
- `pr_closeout=merge-ready` opens each PR as draft, then proceeds through
  validation, ready-for-review, Codex review, and merge-ready closeout without
  authorizing merge. `pr_closeout=draft-only` stops after validated draft
  publication.
- `delivery_mode=direct-commit` requires `pr_closeout=not-applicable` and
  `pr_shape=none`. Its separate `branch_name` data must equal the exact target
  branch named in the scoped owner evidence.
- `project_topology=multi-repo-workspace` must not publish parent/global
  artifacts and child repo partial artifacts from the same option-resolution
  run. Publish the accepted parent/global source first when needed, then run
  child repo partial planning against that source. Repo-scoped partial Feature
  Specs require all affected child repos in one generated issue graph to share
  the same effective child `tracker_backend` because issue publication,
  closeout, and option fingerprints are single-backend per graph. Child repos
  may have different durable topology values; preserve those as
  `repo_project_topology` in repo-scoped handoffs and as
  `issue_project_topology` in generated issues. If affected child repos mix
  `github` and `local`, stop
  before agent-ready issue generation and return the mixed-backend limitation
  as a planning blocker.
- `tracker_backend=local` requires `issue_mutation_authority=none`.
- `tracker_backend=github` with `delivery_mode=pull-request` requires
  `issue_mutation_authority=pr-body-closeout-only`.
- `tracker_backend=github` with `delivery_mode=direct-commit` requires the
  independently resolved `issue_mutation_authority=explicit-direct-mutation`.
  Its owner evidence must explicitly authorize final-commit closure for the
  same scope, target, and branch; direct-commit publication authority alone is
  insufficient. Stop as a planning blocker when this row is missing.
- Every `branch_name` must pass `git check-ref-format --branch <branch_name>`.
- `delivery_mode=pull-request` permits `integration_mode=single-repo-pr`,
  `integration_mode=repo-pr`, or `integration_mode=not-applicable`.
- `delivery_mode=direct-commit` permits `integration_mode=direct-commit` or
  `integration_mode=not-applicable`.
- An authorized per-issue `delivery_mode` override atomically resolves
  `issue_mutation_authority`, `pr_shape`, `pr_closeout`, `closeout_mode`, and
  `integration_mode` from the
  effective issue delivery mode and tracker backend. Reject any tuple that
  retains incompatible feature-level values. A direct-commit override also
  requires separate `branch_name` data equal to the exact target branch in the
  scoped owner evidence.
- `tracker_backend=local` requires
  `closeout_mode=local-done-move-after-proof` for every issue.
- `tracker_backend=github` with `delivery_mode=pull-request` requires
  `closeout_mode=feature-pr-closes-issue` when `pr_shape=single-pr` and
  `closeout_mode=repo-pr-closes-issue` when `pr_shape=per-repo-pr`.
- `tracker_backend=github` with `delivery_mode=direct-commit` requires
  `closeout_mode=direct-commit-closes-issue`.
- `parallelization=independent` requires `dependency_ids=none` and
  `blocked_issue_ids=none`.
- `parallelization=depends-on` requires one or more `dependency_ids` and
  `blocked_issue_ids=none`.
- `parallelization=blocks` requires `dependency_ids=none` and one or more
  `blocked_issue_ids`.
- `parallelization=root-integrated` may carry either ID list when root-owned
  integration requires it. Every non-empty ID list requires a separate
  `dependency_reason`; all IDs must resolve inside the generated feature graph,
  and the normalized graph must remain acyclic.

## Resolution Record

Record exactly one row per Run Registry field plus `local_mirror_path` and
`branch_name` before the first phase handoff. This includes
`project_topology` and `workspace_context`.
Record exactly one row per
Per-Issue Registry field plus issue-effective `branch_name`, including the
complete effective delivery tuple, after the issue graph exists and before
that issue is emitted; use canonical defaults instead of omission:

| row_id | scope_id | field | value | source | evidence |
| --- | --- | --- | --- | --- | --- |
| `run:<field>` | `run` | `<run registry field>` | `<canonical value>` | <allowed source for this field/value below> | `<instruction ref, config path, issue ref, or none>` |
| `run:local_mirror_path` | `run` | `local_mirror_path` | `<repo-relative root or not-applicable>` | `owner-instruction` or `default` | `<instruction ref or none>` |
| `run:branch_name` | `run` | `branch_name` | `<exact branch>` | `runtime-derived`, `owner-instruction`, or `source-spec` | `<delivery/source evidence>` |
| `issue:<NN>:<field>` | `issue:<NN>` | `<per-issue registry field>` | `<canonical value>` | <allowed source for this field/value below> | `<instruction ref, Feature Spec ref, issue ref, or none>` |
| `issue:<NN>:branch_name` | `issue:<NN>` | `branch_name` | `<exact branch>` | `source-spec`, `owner-instruction`, or `runtime-derived` | `<delivery/source evidence>` |

## Resolution Source Constraints

| Field/value | Allowed sources |
| --- | --- |
| `mode=full-flow` | `default` or `owner-instruction` |
| `mode=spec-only` | `owner-instruction` |
| `mode=issues-from-existing-spec` | `owner-instruction` or `source-spec` |
| `execution_profile` | `default` or `runtime-derived` |
| `tracker_backend` | `tracker-config`, `child-tracker-config`, or `legacy-migration` |
| `effective_target` | `runtime-derived` from the target-resolution matrix |
| `no_mutation_override=none` | `default` |
| Any non-`none` `no_mutation_override` | `owner-instruction` or `legacy-migration` preserving owner evidence |
| `no_mutation_output=not-applicable` | `default` |
| `no_mutation_output=local-artifacts` or `publish-commands` | `default`, `owner-instruction`, or `legacy-migration` after a non-`none` mutation override is proven |
| `local_mirror=not-requested` and `local_mirror_path=not-applicable` | `default` |
| `local_mirror=requested` and its path | `owner-instruction` |
| `partial_output=withhold` | `default` |
| `partial_output=allow-non-agent-ready` | `owner-instruction` |
| `project_topology` | `project-layout-config`, `runtime-derived`, or `owner-instruction` |
| `workspace_context` | `source-spec`, `project-layout-config`, `runtime-derived`, or `owner-instruction` |
| Feature `delivery_mode=pull-request` | `default` or `source-spec` |
| Feature `delivery_mode=direct-commit` | `owner-instruction` naming the exact instruction, feature scope, and authorized target branch; or `source-spec` preserving that same owner evidence |
| Feature `issue_mutation_authority=none` or `pr-body-closeout-only` | `runtime-derived` from tracker and delivery |
| Feature `issue_mutation_authority=explicit-direct-mutation` | `owner-instruction` separately authorizing final-commit issue closure for the exact feature scope, target, and branch; or `source-spec` preserving that evidence |
| Feature `branch_name` for `pull-request` | `runtime-derived` or `source-spec` |
| Feature `branch_name` for `direct-commit` | `owner-instruction`, or `source-spec` preserving exact scoped owner and target-branch evidence |
| Feature `pr_closeout=merge-ready` | `default` or `source-spec` |
| Feature `pr_closeout=draft-only` | `owner-instruction`, or `source-spec` preserving explicit owner evidence |
| Feature `pr_closeout=not-applicable` and feature `pr_shape` | `runtime-derived` from `delivery_mode` and affected repo scope, or `source-spec` |
| Issue `issue_project_topology` | `source-spec`, `project-layout-config`, or `runtime-derived` from target repo evidence |
| Issue `delivery_source=feature-level-inherited` and its effective delivery tuple | `source-spec` |
| Issue `delivery_source=issue-level-override` and its effective delivery tuple | `owner-instruction`; for `direct-commit`, name the exact instruction, issue scope, and authorized target branch; or use `source-spec` only when it preserves that same owner evidence and branch data |
| Issue `issue_mutation_authority=none` or `pr-body-closeout-only` | `runtime-derived` or `source-spec` from the validated tracker/delivery tuple |
| Issue `issue_mutation_authority=explicit-direct-mutation` | `owner-instruction`, or `source-spec` preserving the separately authorized final-commit closure evidence projected to the exact issue scope |
| Issue `branch_name` with feature inheritance | `source-spec` |
| Issue `branch_name` with an authorized override | `owner-instruction`, or `source-spec` preserving the same scoped evidence; `runtime-derived` only for a non-authority pull-request branch |
| `parallelization`, `closeout_mode`, and `integration_mode` | `runtime-derived` from the validated issue graph, tracker, and effective delivery tuple, or `source-spec` |
| `domain_closeout` | `runtime-derived` from the accepted knowledge delta and final-owner graph, or `source-spec` |

`tracker-config`, `source-spec`, and `runtime-derived` may select only the
field/value pairs allowed above. They never grant `direct-commit`, local-mirror
writes, partial backlog publication, or an issue-level delivery override
without the required preserved owner evidence. `legacy-migration` cannot
upgrade ambiguous legacy input into authority; it may preserve an exact
non-authority mapping, while every authority-sensitive mapping must retain the
same owner evidence required by this table.

For a direct-commit feature or issue override, the delivery, `branch_name`, and
`issue_mutation_authority=explicit-direct-mutation` rows use evidence containing
`owner-ref=<ref>;scope-ref=<run-or-issue-scope>;target-ref=<feature-or-source-ref>;target-branch=<branch_name>`.
A `source-spec` row preserves those tokens and never synthesizes them from
prose. The mutation row is separate and its `owner-ref` must resolve to an
instruction that explicitly authorizes final-commit issue closure; delivery
authority alone cannot select it. For an effective direct-commit issue, the
delivery, branch, and mutation rows use identical scope, target, branch, and
transfer tokens so the orchestrator can verify one scoped target. Preserve the
delivery and closure `owner-ref` values independently; they may name different
owner instructions and must never be rewritten to match.
For feature-level inherited direct commit, each issue rewrites only the scope
projection to `scope-ref=issue:<NN>` and adds `scope-transfer-ref=run`; it
preserves the Feature Spec owner, `target-ref`, and target branch verbatim.

Every row whose `source` is not `default` requires normalized `evidence` that
is neither empty nor `none`. Validate this after the source-constraint table
and before hashing. Authority-bearing values still require the stronger scoped
evidence described above; a non-empty generic phrase does not satisfy those
requirements.

## Row Serialization And Fingerprint

Keep every `row_id` unique. Canonicalize the complete current row set using
these exact rules:

1. Use the six columns `row_id`, `scope_id`, `field`, `value`, `source`, and
   `evidence` in that order.
2. Encode a literal `|` in evidence as `%7C`.
3. Trim outer whitespace and one pair of wrapping backticks from every cell.
4. Validate every field/value/source combination and reject empty or `none`
   evidence for every non-`default` source.
5. Sort rows bytewise by normalized `row_id` using the C locale.
6. Serialize each row as its six normalized cells joined by one tab, with one
   trailing newline per row and no header row.
7. SHA-256 hash the serialized UTF-8 bytes and emit the Markdown field
   `option_rows_fingerprint: sha256:<lowercase-hex>`.

The entrypoint computes the run-row fingerprint before the Feature Spec phase. Each
phase recomputes and verifies the incoming rows before acting. The issue phase
then adds all `issue:<NN>` rows, recomputes the fingerprint over the complete
run-plus-issue set, and returns that value in its handoff and completion
report. A missing or mismatched row, duplicate `row_id`, or fingerprint
mismatch is a blocking invalid snapshot; never reinterpret prose to repair it.

For each durable issue body, apply the same serialization rules to that issue's
Per-Issue Registry rows plus its `branch_name` row and record
`issue_option_rows_fingerprint: sha256:<lowercase-hex>`. This artifact-local
fingerprint is independently verifiable from the issue body; it does not
replace the graph-wide `option_rows_fingerprint` in the phase handoff and
completion report.

The `source` column is itself canonical lower-kebab. The `evidence` cell may be
free-form because it is data. If wording is ambiguous between two values, ask
for the choice and then store only the resolved canonical value.

## Legacy Input Normalization

Read older human labels only for compatibility and rewrite them when touched:

| Legacy label | Canonical field |
| --- | --- |
| `Plan-feature mode` | `mode` |
| `Execution profile` | `execution_profile` |
| `Effective target for this run` | `effective_target` |
| `No-mutation override` | `no_mutation_override` |
| `No-mutation output` | `no_mutation_output` |
| `Local mirror` | `local_mirror` |
| `Delivery mode` | `delivery_mode` |
| `Issue mutation authority` | `issue_mutation_authority` |
| `PR shape` | `pr_shape` |
| `PR closeout` | `pr_closeout` |

Legacy labels are read aliases, not valid current output fields. For a legacy
Feature Spec without canonical `pr_shape`, resolve `delivery_mode` first, then normalize
to `single-pr` for one-repo `pull-request`, `per-repo-pr` for multi-repo
`pull-request`, or `none` for `direct-commit`. Treat older PR-shape prose only
as evidence for the repo-scope check, record `source=legacy-migration`, and
rewrite the touched projection. If repo scope is ambiguous, stop for owner
resolution instead of retaining or branching on the prose.
