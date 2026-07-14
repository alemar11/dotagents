---
name: plan-feature
description: Manually plan features into PRDs and agent-ready issues through full-flow, prd-only, or issues-from-existing-prd modes.
---

# Plan Feature

## Purpose And Invocation

Use this planning-only skill to turn feature intent into a durable Product
Requirements Document (PRD) and, when requested by the selected mode, hardened
vertical implementation issues. The public pipeline is:

`project-memory routing if needed -> repo-backed clarification if needed -> PRD phase -> issue phase -> deferred domain-memory closeout`

Use it only when the user invokes `$plan-feature`, asks to run Plan Feature, or
a manually invoked parent workflow routes here. Do not auto-select it for
ordinary planning, PRD, implementation, issue-splitting, or triage requests.
Do not implement the planned feature.

## Structured Option Contract

Load `references/options.md` before resolving mode, target, delivery, or output
behavior. Every selectable choice uses a snake_case field and a lower-kebab
value from that registry. Natural-language instructions and legacy labels are
evidence for resolving a field, never alternative option values. Record the
canonical option-resolution rows once and pass only those values to phases,
handoffs, templates, draft commands, and reports.

## Modes

Resolve `mode` once from the registry and branch only on that canonical value:

| Mode | Use when | Stop point |
| --- | --- | --- |
| `full-flow` | `mode=full-flow`; default for new feature intent after input normalization. | PRD plus hardened issues. |
| `prd-only` | `mode=prd-only`. | PRD phase report. |
| `issues-from-existing-prd` | `mode=issues-from-existing-prd`; a durable PRD already exists and supplies the verified handoff. | Hardened issues. |

In `issues-from-existing-prd`, skip clarification unless unresolved PRD
questions affect scope, acceptance criteria, dependencies, validation,
publication, permissions, or cross-repo contracts.

## Execution Profiles

Select an internal profile after resolving mode and identity:

- `lean-prd`: use only for `prd-only` when tracker routing exists, one
  repo/context is unambiguous, the supplied intent is PRD-ready, and no
  clarification or cross-repo contract is needed.
- `lean-issues`: use only for `issues-from-existing-prd` when the durable PRD is
  unambiguous, one repo/context is involved, at most two candidate vertical
  issues are expected, and no cross-repo gate, enabling slice, or separate
  domain-closeout owner is needed.
- `standard`: use for every other run and whenever lean-path evidence becomes
  incomplete or contradictory.

Lean profiles reduce discovery and repeated output only. They never skip
templates, `$plan-harder`, verticality, graph, documentation, publication, or
domain-closeout gates required by the selected mode.

## Non-Negotiable Invariants

- Keep PRD writing and issue splitting as internal phases. Load
  `references/prd-phase.md` before PRD work and `references/issue-phase.md`
  before issue work; load their templates and `vertical-slices.md` only for the
  phase that needs them.
- Treat `tracker_backend` as planning-artifact write authority. `github`
  publishes through `$gitstack:github-issues`; `local` writes the configured
  Markdown paths when `effective_target=configured-tracker`.
  `effective_target=local-dry-run` or `draft-publish-commands` is non-mutating.
- In hosted tracker mode, keep body files transient and outside the repo. Do
  not create `.scratch/`, `project-memory/features/`, or other local mirrors
  unless `effective_target=configured-tracker` and
  `local_mirror=requested`.
- Resolve and carry one planning identity: `feature_slug`, selected
  product/workspace/context when applicable, and `project_slug` for
  orchestrator workspaces.
- Default `delivery_mode` to `pull-request`; use `direct-commit` only with
  accepted option-resolution evidence. For pull requests, default
  `pr_closeout` to `merge-ready`; use `draft-only` only when the canonical
  option-resolution row selects it. Do not select it by comparing source prose
  or from the separate `no_mutation_override` value.
- Initialize every run with a structured `domain_knowledge_delta`:
  `knowledge_delta` (`none` or `required`) plus `decisions`,
  `target_surfaces`, `evidence`, and `unresolved` lists. Empty `decisions`,
  `target_surfaces`, and `evidence` when `knowledge_delta=none`; preserve
  independent `unresolved` blockers and route them through planning gates.
- Call `$grill-me-with-context` only with `capture_mode=defer-to-caller`.
  Planning may read durable context but must not update `CONTEXT.md`, domain
  docs, ADRs, or other domain-memory surfaces.
- When a required domain delta exists, preserve it in the PRD handoff and make
  exactly one final implementation/integration issue own feature-level proof
  plus `$project-memory domain-memory` with
  `memory_slice=domain-memory` and
  `domain_operation=implementation-closeout`. That issue depends on every
  other terminal issue and is never docs-only.
- Run `$plan-harder` once per generated issue with
  `planning_mode=issue-hardening` and `output_surface=caller`. Then run the
  final verticality and graph gates; repair and re-harden changed issues before
  output.
- Never label unresolved planning work `ready-for-agent`. Resolve
  `partial_output=withhold` by default. Only
  `partial_output=allow-non-agent-ready` permits `needs-info` or
  `ready-for-human` artifacts.
- Carry a durable `source_prd_ref` into every generated issue. A
  `draft-prd:<...>` ref is inspection-only until replaced by a hosted PRD
  number or durable local path.
- Keep worker surfaces, worker counts, publication authority, runtime issue
  mutation overrides, and other `$codex-orchestrator` session choices out of
  PRDs, generated issues, handoffs, local tracker files, and draft commands.
  The independently resolved source-contract `issue_mutation_authority` and its
  scoped evidence are delivery metadata, not a worker/session grant, and must
  remain in PRDs and generated issue handoffs.
- Snapshot each source or artifact in full at most once per unchanged
  fingerprint. On later passes use paths, fingerprints, changed sections, and
  failed-gate excerpts; emit a full body only when chat/draft output requires
  it or at the final publication/review boundary.
- When the runtime exposes counters scoped to this run, checkpoint only
  uncontaminated phase intervals and report deltas for routing, clarification,
  PRD work, each issue-hardening call, and final validation/publication. Label
  interleaved cumulative deltas `exact-interval`, not phase usage; otherwise
  record `unavailable`. Never estimate or make metrics a completion gate.

## Composed Skills

| Skill | Load when | Boundary |
| --- | --- | --- |
| `$project-memory` | Tracker routing is missing, incomplete, or stale. | Use only `tracker-routing`; Plan Feature never invokes `domain-memory`. |
| `$grill-me-with-context` | Repo-backed clarification is materially needed. | Always `capture_mode=defer-to-caller`; consume its structured delta. |
| `$plan-harder` | For every generated implementation issue. | One issue per `planning_mode=issue-hardening` call; the issue phase owns writes. |
| `$gitstack:github-issues` | Publishing GitHub PRDs/issues or producing hosted dry-run commands. | It owns safe body transport, metadata, parent/sub-issues, verification, cleanup, and partial recovery. |

After implementation scheduling begins, issue lifecycle mutations belong to
`$codex-orchestrator`, not Plan Feature.

## Workflow

### 1. Resolve Setup, Target, And Identity

Read `project-memory/config/issue-tracker.md` and
`project-memory/config/triage-labels.md`. Read `project-memory/config/domain.md`,
`CONTEXT.md`, or `CONTEXT-MAP.md` only when context selection is material.

If tracker routing or mappings are missing or inconsistent with the requested
target, run only `$project-memory tracker-routing`. Do not bootstrap unrelated
domain, localization, ADR, or `AGENTS.md` content. Orchestrator-workspace setup
is config-only and does not create project or feature artifacts.

Resolve and record the canonical option snapshot from `references/options.md`:

- `execution_profile`: `lean-prd`, `lean-issues`, or `standard`;
- `effective_target`: `configured-tracker`, `local-dry-run`, or
  `draft-publish-commands`;
- `no_mutation_override`: `none`, `dry-run`, `temp`, `rehearsal`, `validation`,
  `disabled-writes`, or `draft-output`;
- `no_mutation_output`: `not-applicable`, `local-artifacts`, or
  `publish-commands`;
- `partial_output`: `withhold` or `allow-non-agent-ready`;
- `local_mirror` and its repo-relative `local_mirror_path` data when requested;
- `feature_slug` and, when applicable, `product_slug`, `workspace_path`,
  `context_file`, and `project_slug`;
- `delivery_mode`, `issue_mutation_authority`, `branch_name`, `pr_closeout`, and `pr_shape` using the
  registry defaults and scoped evidence.

Phase handoffs use the snake_case fields `mode`, `execution_profile`, `tracker_backend`,
`effective_target`, `no_mutation_override`, `no_mutation_output`,
`local_mirror`, `local_mirror_path`, `partial_output`, `delivery_mode`,
`issue_mutation_authority`, `branch_name`, `pr_closeout`, and `pr_shape`, plus keyed `option_resolution` rows and the
`option_rows_fingerprint` data field.

Use `$project-memory`'s `references/tracker-publishing.md` for effective-target,
temporary-body-file, and draft `source_prd_ref` mechanics. Stop before writing
when repo/context identity or cross-repo delivery is materially ambiguous.

### 2. Clarify Only Material Unknowns

In `full-flow` and `prd-only`, run `$grill-me-with-context` only when the
provided intent and repository evidence are not sufficient for the PRD and
issue graph. Resolve one blocking question at a time.

Build or consume the canonical `domain_knowledge_delta`. Durable accepted
terms, rules, boundaries, and decisions use repo-relative or repo-qualified
targets and evidence. Planning blockers must be resolved or explicitly proven
non-blocking before agent-ready output.

For `issues-from-existing-prd`, inspect open questions first and clarify only
those that block a safe split.

### 3. Run The PRD Phase

Skip only when `issues-from-existing-prd` uses an unchanged durable PRD.
Otherwise load `references/prd-phase.md` and its required template, then pass
the resolved mode, execution profile, target, no-mutation override, planning
identity, delivery values, partial-output value, option-resolution evidence,
source-ref state, and domain delta. A `lean-prd` run reads only the phase's
minimum evidence set unless a gate forces widening.

Require a durable local/hosted `source_prd_ref`, or a deterministic
`draft-prd:<feature-slug>` / `draft-prd:<project-slug>/<feature-slug>` plus
body fingerprint and publish-order note for draft commands. Route any new
material blocker back through clarification. Stop here for `prd-only`.

### 4. Run The Issue Phase

Load `references/issue-phase.md`, `references/issue-body-template.md`, and
`references/vertical-slices.md`. Pass the same identity, delivery, source-ref,
target, `capture_outcome`, domain-delta, partial-output, option-resolution, and
execution-profile fields. A `lean-issues` run still hardens and validates every
issue separately; it only narrows discovery and uses delta evidence between
issue passes.

The issue phase owns vertical splitting, one `$plan-harder` pass per issue,
mapped metadata, dependency/acyclicity validation, PRD parent/sub-issue links,
the canonical `## Orchestrator Handoff`, publication or local writes, and final
reporting. In draft-command runs, output remains non-executable until the draft
PRD ref is replaced by a durable source.

If `knowledge_delta=required`, make its exact decisions, targets, evidence,
`memory_slice=domain-memory`, and
`domain_operation=implementation-closeout` part of the final integration issue
and its Orchestrator Handoff. Reuse a suitable terminal integration issue or
append one that depends directly on every terminal issue, then harden and
validate it like every other issue.

### 5. Report Completion

Return the phase locations/counts and the effective target, planning identity,
canonical keyed option rows with resolution evidence, verticality
repairs/exceptions, graph validation, blockers, applied tracker metadata,
`option_rows_fingerprint`, local-mirror result and path, artifact fingerprints,
and phase-token evidence (`exact-phase`,
`exact-interval`, or `unavailable`).
Include exactly one canonical domain outcome plus separate target/reason data
when deferred:

- `capture_outcome=deferred`, `capture_target_ref=<final task ref>`, and
  `capture_reason=implementation-closeout`;
- for a `mode=prd-only` run with `knowledge_delta=required`,
  `capture_outcome=deferred`,
  `capture_target_ref=final-implementation-task-from:<source_prd_ref>`, and
  `capture_reason=prd-only-stop`; or
- `capture_outcome=no-durable-change`.

Plan Feature never emits `capture_outcome=captured`.

## References

- `references/options.md`: canonical option fields, values, defaults,
  normalization, and legacy input migration.
- `references/prd-phase.md`: PRD handoff, drafting, publication, sanitization,
  and `source_prd_ref` rules.
- `references/issue-phase.md`: issue splitting, hardening, graph validation,
  publication, and completion.
- `references/prd-template.md`: default PRD shape.
- `references/issue-body-template.md`: generated issue and Orchestrator
  Handoff shape.
- `references/vertical-slices.md`: slicing, verticality, and readiness gates.
- `references/full-flow-dry-run.md`: no-mutation forward fixture.
