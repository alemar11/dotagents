# Execution-Ready Feature Spec Bundle

## Applicability

Load during read-only intake. Accept only a durable Feature Spec with its
complete generated implementation-issue graph. Traverse the complete connected
bundle, then select the dependency-ready frontier for this run. The source may
be GitHub or local Markdown, but selected implementation ends in GitHub pull
requests ready to merge and not merged.

Reject rough intent, standalone Specs, proposed refs, incomplete issue graphs,
ad-hoc implementation requests, and retired planning vocabulary. Never repair,
regenerate, or publish planning artifacts from this workflow.

## Execution Contract

Every generated issue contains exactly one `## Execution Contract` table:

| Field | Required data |
| --- | --- |
| `source_spec_ref` | Stable durable parent Feature Spec ref. |
| `feature_slug` | Canonical bundle feature slug. |
| `affected_repositories` | Complete repository IDs or paths for the issue. |
| `allowed_paths` | Repository-qualified writable path scopes. |
| `target_branch_name` | Branch shared by affected repositories inside the Spec. |
| `dependency_ids` | Strictly earlier issue IDs in the same Spec, or `none`. |

Goals, requirements, acceptance criteria, implementation steps, literal
validation commands, working directories, and integration gates remain
authoritative in their existing sections. Inputs must be bounded enough to
execute without inventing paths, commands, branches, or acceptance behavior.

The parent Spec has a `## Feature Dependencies` table containing only
`upstream_feature_spec_ref` and `dependency_reason`. Missing tables are not
interpreted as empty. Intra- and cross-Spec dependency graphs must be acyclic;
every upstream Spec must be verified merged with integration proof before its
dependent Spec can enter a run. Blocked downstream Specs remain next-frontier
evidence and receive no assignment or claim.

## Validation

Require:

- stable source and issue refs plus one shared feature slug;
- every affected repository, target branch, and exact allowed path;
- exactly one affected repository per implementation-eligible Feature Spec;
- one executable Spec owner for each `(repository, target_branch_name)` pair;
- a complete generated-issue graph whose dependencies point strictly backward;
- bounded acceptance criteria and literal validation commands with working
  directories and expected results;
- no publish, deploy, destructive, interactive-secret, or merge command hidden
  inside validation;
- named integration gates for multi-repository work;
- no contradiction with current repository topology or instructions.

Do not project, rewrite, or classify validation commands. The App executes the
literal accepted command under its normal sandbox and approval path. If safe
execution cannot be established, return `planning-required` or
`unsupported-runtime` before implementation.

Normalize verified `owner/repository#N` GitHub refs to their canonical issue
URLs for claims and task identity while preserving the authored ref as source
evidence.

## Domain Knowledge Closeout

An accepted knowledge delta belongs only to the unique final integration issue
under `## Domain Knowledge Closeout`. Every target names exactly one repository
and portable repo-relative path contained by that issue's repositories and
allowed paths. Require `$project-memory` with `memory_slice=domain-memory` and
`domain_operation=implementation-closeout` only after integrated behavior is
proven. Missing, duplicate, early, escaping, contradicted, or graph-incomplete
closeout data is `planning-required`.

## Local Tracker Sources

For local Markdown, include the tracker repository, exact active path, and exact
derived `done/` path in scope. Both must resolve inside an affected repository
and App-managed checkout. Move only after substantive, integration, and domain
closeout proof; then commit, push, and regenerate all head-bound evidence. The
move is prepared closeout until later merge.

## Multi-Repository Bundles

Require one distinct repository-owned integration Feature Spec downstream of
all implementation partials. It owns a bounded path-changing issue plus named
cross-repository proof and produces a real PR in a later invocation after its
upstreams merge. Its branch is
`<ordinary_target_branch_name>-integration` in its repository. A validation-only
or no-op integration artifact is incompatible.

## Derived Delivery

One App task owns one selected Feature Spec in exactly one repository and
produces one real, open, non-draft, reviewed PR against its discovered default
branch, with configured CI passing or provider-backed proof that CI is not
configured. A multi-repository Spec is `planning-required`; never split one
source into several runtime assignments. Derive tracker closing refs from
source ownership, but leave hosted issues open until merge. A separate GitHub
workflow owns merge and post-merge closure.
