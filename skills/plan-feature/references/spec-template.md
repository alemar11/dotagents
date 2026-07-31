# Feature Spec Template

Use this shape for GitHub Feature Spec issues. Keep option selection out of the
body; `references/options.md` owns the single run choice.

```markdown
# Feature Spec: [Feature Name]

## Source

- Conversation, issue, document, or repository evidence used to create this
  Feature Spec.
- Source Idea: [durable Idea ref; include one line per selected Idea whose
  scope this Feature Spec represents, otherwise omit].
- Use only repo-relative, repo-qualified, hosted, or descriptive references.

## Planning Identity

[For a linked member, replace the placeholders and render the next two lines
exactly, including inline-code delimiters and trailing periods. Omit both lines
for a standalone Spec.]
- Feature ID: `<canonical-lowercase-uuid>`.
- Repository key: `<repository-key>`.
- Feature slug: [accepted lowercase kebab-case slug].
- Planning scope: [optional stable product, package, or path-derived scope when
  one Git repository contains independently planned areas].
- Context files: [include every applicable available repository root and
  matched scoped context used for planning; omit roots and routes with no
  context file].

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
- Allowed paths: [smallest complete safe repo-relative or repo-qualified
  envelope, preferring stable directory or subsystem prefixes].
- Spec target branch: [valid branch shared by this Spec's generated issues].
- [For monorepos, include the selected planning scope and optional scoped contexts.]
- [For multi-repository work, state each repository's role and cross-repo
  contract.]

## Feature Spec Set

[Include only for multi-repository work. Every linked Spec carries the same
`Feature ID` and this exact normalized table. Order rows by
`affected_repository`; use globally qualified durable refs after publication.]

| feature_spec_ref | affected_repository | responsibility |
| --- | --- | --- |
| [globally qualified hosted ref or URL] | [canonical repository identity] | [non-empty implementation responsibility plus every owned ID as an exact inline-code token such as `<repository-key>:ac-<NN>` or `<repository-key>:proof-<lower-kebab-boundary>`] |

## Feature Dependencies

| upstream_feature_spec_ref | dependency_reason |
| --- | --- |
| [durable upstream Feature Spec ref] | [concrete non-empty reason] |

## Cross-Repo Contracts

[Include only when multiple repositories or packages must preserve an API,
schema, version, migration, fixture, deployment, or compatibility contract.]

## Integration Execution Contract

[Include in an existing implementation member that owns combined proof for a
multi-repository boundary. Replace the placeholder in the next line and render
it exactly, including the bullet, inline-code delimiters, and trailing period.
The stable ID must also appear in the owning Feature Spec Set responsibility
cell. In concise executable prose, name every repository role and component
start command; endpoint and environment wiring; collision-safe port allocation;
health checks; the integration/E2E command or scenario; timeout, retry, and any
material validation budget; evidence to retain; cleanup behavior; and the
required terminal outcome. Bind proof to the exact repository/branch/HEAD
vector. Assign each component either to the proof owner or to its owning peer.
Require every worker to stay inside its own worktree, start and clean up its own
component, and read its own HEAD before startup and after cleanup. The proof
owner must validate through peer-exposed component boundaries, never through
cross-worktree access. Omit this section when the member owns no combined
proof.]

- Proof ID: `<repository-key>:proof-<lower-kebab-boundary>`.

## Acceptance Criteria

[For a linked member, replace the placeholders and render every criterion in
the exact checklist form below, including inline-code delimiters. Each stable
ID also appears in the owning Feature Spec Set responsibility cell. A standalone
Spec omits only the ID prefix.]

- [ ] `<repository-key>:ac-<NN>` [One unique, individually provable product or
  system outcome. Keep criterion text, count, and order stable; only
  executor-owned checkbox markers may change after publication.]

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
are no authored edges. Every edge waits for stable prerequisite delivery
evidence and its required integration proof. A GitHub dependency waits for
merge only when the durable contract explicitly requires merged input; no
start-condition field exists.

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
section. The optional delta remains run/phase data until the issue phase places
each exact repository-owned shard on that member's final closeout issue in the
same complete bundle. One explicitly named canonical target owns every
cross-repository decision using the exact
`<feature-id>--<repository-key>/<repo-relative-path>` identity of its declared
owning Feature Spec Set member; other shards may carry only backlinks that copy
that exact value. On the
existing-source route, explicit accepted delta data remains separate from the
immutable source and every target must already fit that source's repository and
path scope.

In a multi-repository feature, assign each combined boundary to an existing
implementation member that can execute the proof within its scope. Record its
peer inputs as Feature Dependencies and include an executable `## Integration
Execution Contract` in that member. Different consumers may own different
proofs against the same producer HEAD. Withhold the bundle when no existing
member can own a required proof; never create a dedicated integration Spec.
A monorepo normally keeps FE, BE, app, and integration inside one Feature Spec
worker and one ChatGPT-created worktree.
