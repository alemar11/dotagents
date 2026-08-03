<!-- SE2-owned reference derived from the durable repository-context contract. -->

# Evidence Mining

Read this reference when discovering Code Review Rule candidates from a new or
existing repository, especially when previous Codex sessions are in scope.

## Source Priority

Use evidence in this order:

1. Current code, tests, schemas, public contracts, architecture documentation,
   and existing `AGENTS.md` guidance.
2. Accepted review findings, verified fixes, incident notes, and current pull
   request or commit history when those surfaces are available.
3. Explicit durable user corrections and repository-scoped Codex session,
   memory, or task evidence.

Historical evidence proposes candidates. Current repository evidence confirms
whether a candidate remains true. When current behavior contradicts an older
session, prefer current behavior and report the historical rule as stale.

## Bounded History Pass

Scope history to the canonical current repository and affected paths. Start
with the current session plus at most the 20 most recently updated
repository-scoped sessions discoverable from available Codex memory or session
indexes. Follow only the one or two strongest referenced rollouts when the
index summary is insufficient. An explicit user-supplied session or task ref
may replace or extend that default slice.

Report the examined scope. Do not imply that all historical work was searched
when evidence access or the bounded window was smaller.

If session or memory evidence is unavailable, continue from repository sources.
When the user explicitly requested historical mining, name that coverage
limitation in the proposal or no-op result.

## Candidate Admission

Admit a candidate only when it is consequential, repository-specific, and
supported by at least one of:

- an explicit durable correction whose intended scope is clear and whose rule
  still matches current code;
- an accepted review finding followed by a verified fix;
- the same accepted concern recurring across independent changes;
- a compatibility, privacy, authorization, data-boundary, or unsafe-side-effect
  invariant directly supported by current contracts and tests;
- an existing repository rule that guides implementation but needs a focused
  Code Review Rule projection.

A single source may be sufficient when it is authoritative and current, such
as a public wire contract plus a test that preserves it. Multiple weak session
mentions do not become strong evidence merely through repetition.

## Rejection Filter

Reject:

- tentative brainstorming, unresolved questions, or alternatives that were not
  selected;
- user instructions limited to one task, patch, branch, or temporary incident;
- findings later rejected, superseded, or shown to be false positives;
- behavior observed only in a failed or scope-violating run;
- implementation details already removed from current code;
- formatting, lint, generated-file drift, or other mechanical checks with a
  deterministic enforcement path;
- generic engineering advice that is not specific to the repository;
- rules whose only support is agent-authored prose with no accepted outcome or
  repository evidence.

## Privacy And Provenance

Keep enough provenance in the proposal for the user to judge the candidate:
repo-relative files, issue or pull-request refs, commit IDs, or a short session
summary. Do not include secret values, credentials, private conversation text,
absolute session paths, raw transcripts, or unrelated personal information.

The final `AGENTS.md` rule contains only the durable invariant, consequence,
and safe path. Historical provenance stays outside the persisted rule.

## New Repository Behavior

Do not manufacture "basic" rules for a repository without evidence. If no
candidate survives, return a no-op and recommend revisiting the operation after
the team has repeated review findings or documented a meaningful invariant.

Create a new `AGENTS.md` only after at least one supported rule is authorized.
An explicitly requested empty scaffold is allowed only after explaining that
it changes no review behavior.
