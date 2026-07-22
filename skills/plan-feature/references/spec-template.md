# Feature Spec Template

Use this shape unless the project already has a stronger local Feature Spec
format. Keep option selection out of the body; `references/options.md` owns the
single run choice.

```markdown
# Feature Spec: [Feature Name]

## Source

- Conversation, issue, document, or repository evidence used to create this
  Feature Spec.
- Source Idea: [durable Idea ref; include one line per selected Idea whose
  scope this Feature Spec represents, otherwise omit].
- Use only repo-relative, repo-qualified, hosted, or descriptive references.

## Planning Identity

- Feature slug: [accepted lowercase kebab-case slug].
- Partial role: integration. [Include only for the dedicated multi-repository
  integration partial; omit it from the parent and implementation partials.]
- Product or project slug: [include only for monorepos or orchestrator workspaces].
- Workspace path: [include only for monorepos or multi-repository workspaces].
- Context files: [include every applicable available current/coordination root,
  affected child-repository root, and matched scoped context used for planning;
  omit roots and routes with no context file].
- Repository layout: [Project Memory fact].

## Problem

[The user or system problem this change solves.]

## Goals

- [Concrete outcome.]

## Non-Goals

- [Explicitly excluded work.]

## Users And Use Cases

- [Target user, actor, or system.]
- [Primary workflow.]

## Requirements

- [Functional behavior.]
- [Data, permission, API, or integration requirement when relevant.]

## Product / Repository Scope

- Affected repositories: [canonical repo slugs or current repository].
- Allowed paths: [repo-relative or repo-qualified scope].
- Spec target branch: [valid branch shared by this Spec's generated issues; use
  the distinct derived integration branch for an integration partial].
- [For monorepos, include the selected workspace and optional scoped contexts.]
- [For multi-repository work, state each repository's role and cross-repo
  contract.]

## Feature Dependencies

| upstream_feature_spec_ref | dependency_reason |
| --- | --- |
| [durable upstream Feature Spec ref] | [concrete non-empty reason] |

## Cross-Repo Contracts

[Include only when multiple repositories or packages must preserve an API,
schema, version, migration, fixture, deployment, or compatibility contract.]

## Acceptance Criteria

- [ ] [One unique, individually provable product or system outcome. Keep
  criterion text, count, and order stable; only executor-owned checkbox markers
  may change after publication.]

## Validation Expectations

- [Required automated or manual proof.]
- [Named integration gate when applicable.]
- [For paid, external, non-repeatable, or otherwise constrained proof, state in
  prose the attempt/retry budget, allowed fallback, evidence to retain, and
  required terminal outcome.]

## Risks

- [Risk, tradeoff, or compatibility concern.]

## Open Questions

- [Question that must be resolved before publication or issue generation.]

## Issue-Splitting Notes

- This is planning-time guidance. Generated implementation approaches are
  recommendations and may be replaced by a simpler or safer design without
  changing the accepted goal, scope, constraints, or acceptance criteria.
- [Suggested vertical slices or sequencing constraints.]

```

The `## Feature Dependencies` section is mandatory for every newly produced
Feature Spec. Keep the heading and table header with no data rows when there
are no authored edges. Every edge waits for upstream merge and integration
proof; no start-condition field exists.

For a GitHub `write_mode=apply` publication, resolve the configured `feature`
transport before rendering the final body. Apply `native-type` or `label`
outside the body after publication verifies. When Project Memory instead maps
`feature` to `body-field`, insert that exact configured field in the
header metadata region after the H1 and before `## Source`; include it in the
final body and do not invent a key or value. In `write_mode=propose`, omit
applied metadata from the body and report the intended mapping separately.

When Plan Feature receives `source_idea_refs`, render their exact durable refs
only in `## Source` as defined by `idea-source.md`. Omit the placeholder when no
Idea is consumed, and never copy Idea refs into generated implementation issue
Execution Contracts.

Use `idea-source.md`'s section mapping to transform the complete Idea body into
planning evidence. Do not copy the tentative Idea sections wholesale or treat
Proposed Direction and Expected Value as accepted requirements without
evidence. Keep the transient per-element coverage map out of the Feature Spec;
persist only the source refs here and the canonical cumulative outcome on the
Idea after the complete applied planning result is durable and verified.

No Feature Spec body persists `knowledge_delta` or a domain-knowledge handoff
section. The optional delta remains run/phase data
until the issue phase places its exact payload on the sole final
implementation/integration issue in the same complete bundle. On the
existing-source route, explicit accepted delta data remains separate from the
immutable source and every target must already fit that source's repository and
path scope.

Every multi-repository bundle has exactly one repo-owned integration partial
with its distinct backend-owned title or
path, retain `Partial role: integration` in its body, and include one merge-wait
Feature Dependency edge to every implementation partial. This integration
partial exists independently of a knowledge delta and never carries the delta
in its Feature Spec body.
