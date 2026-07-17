# Execution-Ready Feature Spec Bundle

## Applicability

Load this reference during read-only intake. Accept a durable Feature Spec only
with its complete generated implementation-issue graph. The bundle may be
hosted on GitHub or stored as local Markdown, but implementation always ends in
GitHub pull requests ready to merge and not merged.

Reject rough intent, standalone Specs, ad-hoc implementation requests,
`proposed-spec:<...>` refs, incomplete graphs, and retired planning or handoff
vocabulary. This contract never creates, repairs, regenerates, or publishes
planning artifacts.

## Canonical Execution Contract

Every generated issue contains exactly one `## Execution Contract` table with
these fields:

| Field | Required data |
| --- | --- |
| `source_spec_ref` | Stable durable parent Feature Spec id or path. |
| `feature_slug` | Canonical feature slug shared by the bundle. |
| `affected_repositories` | Complete repository ids or paths for this issue. |
| `allowed_paths` | Repository-qualified writable path scopes. |
| `target_branch_name` | Branch shared by every affected repository inside this Feature Spec. |
| `dependency_ids` | Earlier generated issue ids within this Feature Spec; use `none` when empty. |

Goal, requirements, acceptance criteria, implementation plan, validation
commands, and named integration gates remain authoritative in their existing
sections and must be complete. Persist a knowledge payload only in the final
integration issue's `## Domain Knowledge Closeout` when accepted durable
decisions actually need Project Memory closeout. A Feature Spec containing
`knowledge_delta` or `## Domain Knowledge Handoff` is incompatible.

When a final issue carries `knowledge_delta`, require all three lists and
normalize every `target_surfaces` entry to exactly one repository plus one
portable repo-relative path, rejecting absolute paths, `..` traversal, and
ambiguous ownership. That repository must appear in the same issue's
`affected_repositories`, and the target path must equal or descend from an
explicit scope in the same issue's `allowed_paths`. Reject the bundle as
`planning-required` when any target escapes that scope; intake must not widen
the Execution Contract or rely on Project Memory to cross its boundary.

Require exactly one `## Domain Knowledge Closeout` owner when the payload is
present and none when it is absent. For a single Spec, temporarily remove the
owner and its outgoing `dependency_ids`, derive the nodes with no dependents in
the remaining intra-Spec graph, and require the owner's final `dependency_ids`
to include every such node. No issue may depend on the owner. For a
multi-repository bundle, apply the same algorithm only inside the dedicated
integration partial and require its owner to be the unique final issue there;
the partial's Feature Dependencies provide the upstream merge waits. The
section must explicitly require `$project-memory` with
`memory_slice=domain-memory` and
`domain_operation=implementation-closeout` only after integrated behavior is
proven. Missing, duplicated, early, or graph-incomplete closeout data is
`planning-required`; intake must not infer or add it from worker instructions.
The closeout section must also require `capture_outcome=captured`, reconciliation
of every accepted delta item and required named target, named verified
destinations, and complete documentation-diff verification. For a nonempty
accepted delta, `deferred` or `no-durable-change` blocks the issue and must be
reported; neither satisfies terminal closeout. A supplied accepted item rejected
or contradicted by landed behavior also blocks and requires an owner decision
or separately authorized planning/implementation correction; it cannot count
as captured.

For a local Markdown issue, `affected_repositories` includes the tracker-owning
Git repository and `allowed_paths` includes both its exact active
path and exact derived `done/` destination. Both paths must resolve inside that
affected Git repository and an App-managed checkout. A tracker artifact outside
all affected Git repositories is non-App-executable; abort as
`planning-required` rather than inventing an owner or widening scope.
Snapshot both refs before CLAIM. The active ref is authoritative until the task
performs the one planned tracked move; then the ledger atomically adopts the
done ref while requiring an unchanged body fingerprint.

The root snapshots the complete source and each issue body and computes its own
fingerprints. Source-provided option rows, resolution fingerprints, duplicated
delivery sections, and `## Orchestrator Handoff` sections are incompatible.

## Intake Validation

Require:

- stable source and issue refs plus one shared feature slug;
- every affected repository and exact allowed path scope;
- one target branch name shared inside each Feature Spec, with the integration
  partial's branch equal to `<ordinary_target_branch_name>-integration` for the
  ordinary partial in its owner repo;
- exactly one implementation-eligible Feature Spec owner for every
  portfolio-wide `(repository, target_branch_name)` pair. Exclude a
  coordination-only parent/global artifact because it creates no task or
  App-managed worktree. The same branch name may appear in different
  repositories, but a same-repository executable-Spec collision is
  `planning-required` before CLAIM even when paths are disjoint or dependencies
  serialize execution;
- a complete acyclic generated-issue graph in which every `dependency_ids`
  entry resolves to a strictly earlier generated issue inside the same Spec;
  reject self, same-ID, and later-ID dependencies even when the graph would be
  acyclic;
- the parent Spec's mandatory `## Feature Dependencies` table, including an
  empty body when there are no edges, and containing
  only `upstream_feature_spec_ref` and `dependency_reason` rows that form an
  acyclic cross-Spec graph;
- bounded goals, requirements, acceptance criteria, and validation commands;
- named integration gates for multi-repository work;
- exactly one distinct repo-owned integration Feature Spec in every
  multi-repository bundle, downstream of every implementation partial, with at
  least one issue that owns a bounded path change plus cross-repository proof so
  it can produce a real PR, and with the exact derived integration branch rather
  than the ordinary partial's branch;
- no contradiction between the Spec, issues, and current repository topology.
- every domain-closeout target surface is contained by its final issue's
  affected repositories and allowed paths.

A Feature Spec without the canonical `## Feature Dependencies` heading and
two-column table is incompatible input and aborts as `planning-required`.
Never interpret absence as an empty edge set or infer edges from issue
`dependency_ids`, prose, branch names, or similar titles. Every authored
upstream Feature Spec must be verified merged with integration proof before
dispatch.

`non_app_delivery_target` or any other explicit non-App marker aborts as
`unsupported-app-delivery-target`. Retired delivery targets, delivery
permissions, review requirements or skips, worker actions, parallelization,
repository-layout copies, PR-count strategies, completion methods, closeout
enums, and issue-mutation permissions are invalid structured input. Merge
authorization is also invalid because merge is outside this skill.

Missing or contradictory execution data aborts as `planning-required` before
CLAIM. Report the exact source refs and fields; do not infer, rewrite, or widen
the bundle.

After verifying a GitHub source ref in the globally qualified shorthand
`owner/repository#N`, deterministically derive
`https://github.com/owner/repository/issues/N`. Preserve the shorthand as the
authoritative artifact ref in the source snapshot, but use the URL as the
canonical claim/task source id, scheduling key, and takeover identity. A source
already expressed as that canonical URL is unchanged. This normalization is
derived runtime evidence, not a bundle field or user option.

## Derived Delivery And Closeout

One App task owns all repositories named by its Feature Spec. The number of pull
requests equals the number of affected Git repositories. Every repository uses
the shared target branch as its head and must produce a real, `OPEN`, non-draft,
reviewed, CI-clean PR ready to merge into its discovered default branch. The PR
base is derived per repository and verified during preflight and current-head
review; it is not an input field.

Derive tracker closeout from the source backend. Put each generated
implementation issue's GitHub closing keyword in its owning repository PR. Put
each implementation-eligible Feature Spec keyword in its designated
default-branch whole-Spec closeout PR only after that Spec's gates pass. In a
multi-repository bundle, put any accepted hosted parent/global Feature Spec
keyword in the final integration partial's default-branch PR only after every
partial gate passes. Use a fully qualified
`owner/repository#number` ref when the issue and PR are in different
repositories, and record every link as armed; hosted issues stay open until
merge. Closing keywords are valid only in PRs whose base is the repository
default branch; a different base is a blocker, not a closeout vehicle.

For local Markdown, after substantive acceptance, integration proof, and any
knowledge closeout, move each issue to its derived `done/` path on the delivery
branch, commit and push that move, rerun final validation and `$autoreview`,
convert draft PRs to ready-for-review, then obtain current-revision review and
CI at the resulting head before terminal merge-ready state. The move is only
prepared closeout until the later default-branch
merge lands it. A separate GitHub workflow owns merge and post-merge closure
verification.
