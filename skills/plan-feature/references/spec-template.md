# Feature Spec Template

Use this shape unless the project already has a stronger local Feature Spec
format. Keep option selection out of the body; `references/options.md` owns the
two run choices.

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

- [ ] [Specific, testable product or system outcome.]

## Validation Expectations

- [Required automated or manual proof.]
- [Named integration gate when applicable.]

## Risks

- [Risk, tradeoff, or compatibility concern.]

## Open Questions

- [Question that must be resolved before publication or issue generation.]

## Issue-Splitting Notes

- [Suggested vertical slices or sequencing constraints.]

## Non-App Delivery

[Include this section only after loading `non-app-delivery.md` for an explicit
current request or a canonical durable source that already carries exactly one
target and one resolvable instruction ref. Use each canonical line exactly once
and state that this Feature Spec bundle is incompatible with
`$implement-feature`.]

non_app_delivery_target: [canonical value]
explicit_instruction_ref: [portable resolvable authorized-user instruction ref]
```

The `## Feature Dependencies` section is mandatory for every newly produced
Feature Spec. Keep the heading and table header with no data rows when there
are no authored edges. Every edge waits for upstream merge and integration
proof; no start-condition field exists.

Omit the optional Non-App Delivery section when its predicate is false. Do not
leave placeholder text in a published body.

When Plan Feature receives `source_idea_refs`, render their exact durable refs
only in `## Source` as defined by `idea-source.md`. Omit the placeholder when no
Idea is consumed, and never copy Idea refs into generated implementation issue
Execution Contracts.

No Feature Spec body persists `knowledge_delta` or a domain-knowledge handoff
section. The optional delta remains run/phase data
until the issue phase places its exact payload on the sole final
implementation/integration issue. For `spec-only` with a nonempty
`knowledge_delta`,
withhold every write and return only a blocked non-durable preview plus the
exact delta; no durable Feature Spec source exists. Only a later explicit
`full-flow` run carrying that exact delta may publish it and create its final
issue. A later `issues-from-existing-spec` run must never consume the preview.

Every multi-repository bundle has exactly one repo-owned integration partial
with its distinct backend-owned title or
path, retain `Partial role: integration` in its body, and include one merge-wait
Feature Dependency edge to every implementation partial. This integration
partial exists independently of a knowledge delta and never carries the delta
in its Feature Spec body.
