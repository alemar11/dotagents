# Implement Review And Delivery

This reference owns exact-HEAD Feature Worker-session review, PR publication,
the `candidate-published` handoff, orchestrator-owned CI and review monitoring,
and final exact-HEAD evidence.
Use [states.md](states.md) for the canonical distinction between workflow
nodes, assignment statuses, checkpoints, provider dispositions, runtime-only
modes, and output labels.

## Candidate boundary

The Feature Worker operates only in its application-managed worktree. After it
implements every derived execution unit for one Feature member, validates
the complete outcome, and commits, freeze one candidate with exact repository,
base branch, base SHA, head branch, and full head SHA. The worktree must be
clean and pinned to that candidate before review. Do not create a reviewer task
or a second review worktree.

The authoritative requirements remain the current published Feature Plan Set,
the selected parent Feature semantic contract, and its stable F-AC-NN
criteria. The hosted local Macro Task registry and child Task issues are
durable macro-planning projections of that same Feature outcome. Implement
records their observed availability as `complete`, `partial`, or `absent`;
they are not technical execution units, T-AC-NN records, worker assignments,
PR boundaries, or an acceptance gate when the parent contract is sufficient.

For a dependency-bearing assignment, also freeze the exact prerequisite HEAD
vector and prove every member is an ancestor of the candidate. The candidate's
integration base and intended PR base must preserve that ancestry; a
prerequisite PR being ready is not sufficient proof.

A Feature-level `blocked_by` relation has a deterministic repository-sensitive
delivery projection. Every same-repository edge is mandatory stack intent;
every cross-repository edge remains scheduling-only and standalone. The
delivery record still proves the exact parent branch, full HEAD, and ancestry;
the relation never substitutes for Git evidence or creates technical
execution-unit edges.

Freeze one transient delivery record before review. A standalone or stack-root
candidate uses the verified caller-selected starting branch, or the
authoritative provider default branch when the caller omitted the selection,
plus the exact refreshed base SHA used for worktree bootstrap. A stacked child
names exactly one immediate parent assignment and PR, the parent head branch,
the exact parent candidate SHA used as base_sha, and its bottom-to-top
position. Do not infer a parent from branch naming, plan order, display
metadata, or operational serialization.

## Delivery lifecycle boundary

The canonical persisted assignment lifecycle is:

```text
active @ worker-bootstrap
  -> active @ native-review
  -> delivery-pending @ candidate-published
  -> delivery-ready @ final-verify
```

The workflow nodes `candidate`, `publish-pr`, `stack-reconcile`,
`candidate-published`, `delivery-monitor`, and `final-verify` perform the work
between those durable pairs. After every assignment reaches
`delivery-ready @ final-verify`, the run enters `active @ release-claims` and
then `complete @ complete`. Optional provider-policy dispositions such as
`ready` and `ready-with-manual-action` may be recorded as diagnostics, but they
are not required by final verification and are not assignment statuses.

Implement terminates with a PR published and verified on its exact HEAD. The PR
may remain open; merge, the effective closure of the Feature and its Macro
Tasks, and every post-merge activity are outside this workflow. The
`closing_issue_refs` values are closure intent derived from authoritative
hosted identities: the parent Feature plus every verified existing associated
local Macro Task. A missing or quarantined projection is reported and never
invented. They become effective only when GitHub merges the PR.

Preserve exact readback of the current PR HEAD, the PR body carrying source-derived closure intent, the stack link, CI, and review evidence. If the
provider exposes `closingIssuesReferences`, record it as optional diagnostic
evidence only; it never affects a workflow transition, does not authorize
merge, and does not imply that the Feature or Macro Tasks are already closed.

## Git and GitHub operation ownership

The Feature Worker owns application semantics: code, tests, conflict
resolution, validation, and the decision that a candidate is ready for review.
It does not select an alternate Git or GitHub transport. Every Git transport
operation is routed through a G-owned workflow, and every hosted GitHub read or
write is routed through the G-owned workflow for that domain. The shared SE
dependency preflight gates hosted access; local worktree edits and validation
do not require that hosted gate, but they are never a local-only Implement
result. Every run must continue through the authoritative hosted source and
verified PR-delivery path.

Before every hosted write in this reference, load and apply the shared
hosted-content-safety.md contract to the exact final title/body, comment,
reply, review text, or review request. This includes Feature Worker- and
tool-originated content. A typed review request with only its required
portable marker and full SHA still passes the same final gate.

| Operation | Semantic owner | Required authority and readback |
| --- | --- | --- |
| Starting-branch refresh and exact base snapshot | G-owned branch transport; the orchestrator owns selection and bootstrap gating | Exact repository, caller-selected or provider-default branch, authoritative upstream tip, fast-forward-only or isolated-ref refresh evidence, and full base SHA readback before worktree creation. |
| Worktree inspection, scoped staging, and candidate commit | G-owned local Git workflow; Feature Worker owns the content and validation evidence | Authorized repository and paths; read back branch, clean worktree, full candidate HEAD, and staged scope. |
| Feature-branch creation, checkout, or scoped rebase after parent drift | G-owned branch transport; Feature Worker owns conflict resolution and revalidation | Exact repository, source/base HEAD, target branch, resulting full HEAD, and a fresh validation record. |
| One candidate branch push and draft PR create/update | G-owned single-PR publication workflow | Implicit authority from the explicit Implement request for the exact declared repository and Feature publication scope; derive `closing_issue_refs` from the parent and verified existing local Task projections, then read back repository, base, branch, full PR HEAD, URL, canonical body/closure intent, and draft state. Any `closingIssuesReferences` field is optional diagnostic readback only. |
| Link one child PR to one immediate parent PR | G-owned pairwise stack-link workflow, invoked separately after Send publication | Implicit authority from the explicit Implement request for the one derived parent/current pair; read back both identities, child base, stack order, and link receipt. |
| Ready transition or issue linkage | G-owned hosted publication or issue workflow for the exact operation | Implicit authority from the explicit Implement request for each declared mutation; read back the resulting state and bind it to the current full PR HEAD or issue identity. |
| Branch protection, rulesets, mergeability policy, merge queue, and auto-merge | Outside Implement completion | Do not invoke or require these policy surfaces; any supplied observation is diagnostic only and cannot block completion. |
| Hosted Codex review and actionable review-thread observation | G-owned review workflow, centrally coordinated by the Implement orchestrator | Reconcile against the current full PR HEAD; pending, stale, ambiguous, or draft-only evidence is non-terminal. Feature Workers do not poll while inactive. |
| Merge, deploy, release, or post-merge closure | No Implement owner; outside this skill | Never perform these operations as part of Implement completion. |

The Feature Worker may decide that evidence is insufficient and return to
implementation, but it may not bypass the owner boundary. A successful
publication and an unverified relation are separate effects and must be
reconciled independently.

## Native review loop

Before review, independently verify Feature Worker/worktree identity, candidate
cleanliness, base and prerequisite ancestry, and exact full SHA. The Feature
Worker runs the available native code-review capability in the same session
against the declared base using its resolved Sol reasoning level. The required
outcome is an independently reported exact-HEAD finding set or clean result;
the skill does not encode an application operation or interface.

Bind every finding and clean result to the exact candidate SHA. The Feature
Worker decides whether a finding is actionable, owns every fix, reruns
validation, and creates a new candidate. Any new HEAD invalidates the previous
review evidence; run a new review cycle in the same Feature Worker session
against the new exact SHA.

## PR publication

Publish only after native review is clean and the exact publication scope is
resolved from the explicit Implement request.

### Minimal durable PR body

The SE-authored PR body is a reviewer-facing summary, not an execution ledger.
Implement owns the semantic content it supplies to G; G owns repository-template
preservation, canonical closing lines, transport, and readback. Limit new or
updated SE-owned content to:

- **Summary:** one short paragraph or at most three bullets describing the
  observable outcome, its reason, and any material scope boundary;
- **Validation:** one compact bullet per distinct command or check category
  actually run against the candidate, collapsing reruns and reporting names
  only rather than counts or output;
- **Operational notes:** only a concrete migration, compatibility, rollout, or
  manual action that a reviewer or operator must know; omit the section when no
  such action exists;
- **Issues:** the canonical closing lines derived from `closing_issue_refs` and
  rendered and verified by G.

Do not copy the Feature Plan, Macro Task list, F-AC/T-AC evidence matrix,
implementation-unit inventory, changed-file list, worker identity, local path,
branch or SHA diagnostics, stack diagnostics, raw command output, review or CI
progress, timestamps, durations, routine test counts, or pass/fail totals into
SE-owned PR content. Exact-HEAD acceptance, validation, review, CI, and topology
proof remains in the Implement delivery record and provider evidence.

A product metric may appear only when that metric is itself an observable
Feature acceptance outcome; bind it to the current exact HEAD and refresh it
after any candidate change. Before every PR create or body update, reconstruct
the SE-owned sections from the current candidate instead of carrying forward an
execution log or patching stale values. Remove disallowed stale SE-owned content
in that same update. Preserve repository-required template fields and unrelated
existing author content through the G-owned publication workflow.

For every implementation-eligible Feature, derive
`closing_issue_refs` deterministically from that parent Feature and the
verified existing subset of its local hosted Task projections:

```text
closing_issue_refs =
  [this parent Feature issue] + [every verified existing Macro Task child issue owned by this Feature]
```
This parent Feature and every verified existing associated local Macro Task
form the source-derived closure set. There is no per-Task opt-out among those
verified refs, no Worker-supplied closure list, and no one-to-one requirement
between Macro Tasks and technical execution units. Sibling Features and their
Tasks are never included. Implement may combine, distribute, or otherwise
realize available local Macro Tasks through its internal execution graph, but
the final candidate is gated by every F-AC and derived T-AC for this Feature,
not by an absent Macro projection.

Include only a real, repository-unambiguous child issue verified under this
exact parent Feature. Quarantine and report a missing, extra, duplicate,
cross-parent, cross-Feature, or ambiguous Task projection instead of treating
it as closure authority. A `partial` or `absent` projection does not block PR
publication when the parent Feature semantic contract is sufficient. Never
invent closure refs from narrative text, include a sibling Feature, or close
an Idea or unrelated source issue.

Pass the verified set unchanged to the G-owned single-PR publication workflow.
G renders the canonical closing lines and reads back the exact body and
source-derived closure intent. The provider's `closingIssuesReferences`
field is not a stable pre-merge contract for stacked PRs: it may be empty,
partial, or unavailable while the PR is still based on an intermediate branch.
Record that field when available, but never require it to equal
`closing_issue_refs` and never block publication or final verification on it.
The PR declares closure intent; GitHub closes this Feature and its local Macro
Tasks only when the PR is merged. Implement does not merge or perform
post-merge closure. The delivery mode, not Send, determines the intended base:
a standalone or stack-root candidate uses the verified selected starting
branch, defaulting to the authoritative provider default when omitted, while a
stacked child uses the verified parent branch.

Apply the shared hosted-content safety gate to the exact final PR title and
body immediately before publication. Verify the SE-owned body against the
minimal durable body contract, then use the G-owned single-PR publication
workflow to push the committed candidate and create or reuse a draft PR.
Independently read back repository, base, branch, full PR HEAD, URL, minimal
durable body/closure intent, and draft state. Optionally record GitHub
`closingIssuesReferences` as provider diagnostics; an empty, partial, or
unavailable value is non-blocking. Verify the PR body carries the exact
source-derived closure intent. The PR HEAD must equal the reviewed candidate
HEAD.

For a stacked candidate, supply the verified parent head branch as the explicit
PR base. Use the G-owned single-PR publication workflow to publish only the
current Feature Worker branch, then invoke the separate G-owned pairwise
stack-link workflow with the already verified parent/current PR identities.
Preserve the parent identity and stack_link_receipt from that separate
operation. Do not use a stack-wide publication, push, sync, rebase, or merge
operation from normal publication, and never install a missing stack dependency
implicitly.

Do not wait for hosted review, CI, or provider readiness before establishing
`candidate-published`. The draft PR and exact publication readback are the
handoff boundary; a draft review is consultative and never satisfies the ready
cycle.

## Stack reconciliation

After a stacked publication and separate stack-link operation, the orchestrator
independently verifies the exact repository, parent and child PR identities,
unchanged draft states, child base, both full heads, immediate parent
relationship, stack order, and link receipt. The child base must equal the
parent head branch, the live parent head must equal the frozen base_sha, and
the child head must equal the reviewed candidate.

Treat a confirmed child PR and an unverified stack link as separate effects.
Preserve successful publication evidence, record an ambiguous link as unknown,
and reconcile authoritative provider state before any repair. Never recreate or
repush the child merely because stack readback failed. A proven stale base or
parent HEAD returns the same child Feature Worker to implementation; an
unreconciled link blocks only that assignment while independent work continues.

## Candidate-published handoff

For a standalone PR, complete publication readback establishes
`candidate-published`. For a stacked PR, require both publication readback and
successful stack reconciliation first. Record the exact repository, PR, base
and head branches, candidate full SHA, minimal durable PR-body readback,
source-derived closure intent, and any parent PR, parent full SHA, stack
position, and link receipt. A provider `closingIssuesReferences` observation
may be retained as diagnostic evidence but is not required for this checkpoint.

The orchestrator then checkpoints `status=delivery-pending` and
`checkpoint=candidate-published`, releases the transient active path claim,
and returns to scheduling. The Feature Worker emits one bounded exact-HEAD
handoff and becomes inactive but resumable. This checkpoint unlocks a
same-repository dependent Feature whose frozen base is this exact branch and
SHA; it does not assert hosted review, CI, provider readiness, mergeability, or
Feature completion.

## Hosted review monitoring

The orchestrator owns the monitoring loop for every delivery-pending PR. It
uses bounded G-owned observations and never asks an inactive Feature Worker to
poll provider state. A pending observation returns to scheduling so newly
unblocked Feature Workers and other PR observations can progress.

After `candidate-published`, when local validation and the published body are
stable, mark the PR ready through the G-owned workflow and independently
observe the transition. Hosted CI and provider review may remain pending and
are reconciled by this monitoring loop.

The first hosted Codex review and every later re-review have different trigger
lineages. Keep them separate:

1. After the G-owned draft-to-ready transition, persist its exact typed ready
   receipt and invoke the G-owned ready-wait operation for the published full
   PR HEAD. This observes the automatic review configured for a PR opened for
   review and never posts an explicit review request for this initial cycle.
2. Accept only G-normalized current-head terminal evidence. A clean formal
   review, authenticated terminal comment, or clean provider reaction may be a
   clean outcome; actionable inline or terminal findings return the assignment
   to the same Feature Worker. Absence of comments, zero unresolved threads,
   zero CI checks, or a generic not-requested observation is not a clean result.
3. After findings, the Feature Worker fixes and validates, creates a new
   candidate, repeats native review, and publishes the new exact HEAD to the
   existing PR. Only then invoke the G-owned request operation with a new
   request key, persist its exact request receipt, and invoke wait against that
   same full SHA. Repeat this fix, publish, explicit-request, and wait cycle
   until the current full PR HEAD has a clean terminal result.

Monitor current-head CI and actionable review threads alongside that
provider-review cycle. CI is terminal only when every applicable check has
passed, or the repository reports that no checks are configured; pending,
failing, stale, ambiguous, or incomplete CI evidence is not terminal. Bind
review and CI observations to the exact published full HEAD. One bounded wait
may return a pending state at its caller-owned deadline; when continued
monitoring remains authorized, the orchestrator returns to schedule and
resumes through later bounded waits without posting a duplicate request or
resetting the existing lineage.

For a stacked child, also monitor the immediate parent PR and base relationship.
A parent HEAD, base, or link change invalidates the child's ancestry, review,
CI, and readiness evidence even when the child head itself did not move; return
the same child Feature Worker for rebase and its complete candidate cycle. A
parent readiness change without topology or HEAD drift affects bottom-to-top
finalization only and does not invalidate child implementation evidence.

If hosted review produces an actionable finding, preserve its exact provider,
PR, head, artifact, and observation fingerprint. Reacquire the Worker's path
envelope, then return that evidence to the same Feature Worker. Never
force-push, merge, enqueue, deploy, release, or perform post-merge closure.

## Optional provider diagnostics

Implement does not invoke `$g:github-delivery-status` as part of its required
completion path. If an outer coordinator supplies a current-head provider
observation, preserve it as diagnostic context only. A missing, incomplete, or
plan-limited branch-protection or ruleset surface must never block an otherwise
verified PR, CI, review, and stack outcome. Implement must still never enable,
disable, enqueue, dequeue, bypass, or merge anything. If another actor merges
or closes the PR during the run, observe the changed lifecycle, stop normal
delivery reconciliation, and report the external event without post-merge
work.

## Final verification

The orchestrator performs read-only final verification. Require:

- exact caller-supplied parent issue ref, Feature Plan Set ref/revision,
  selected Feature ID, repository, and complete hosted sibling readback;
- exact Feature-level registry/dependency readback plus Macro projection state
  (`complete`, `partial`, or `absent`), every verified existing local child,
  and every quarantined projection defect;
- Feature-level scheduling evidence and the repository-sensitive projection
  that justifies standalone or stacked delivery;
- exact current F-AC-NN set with no missing, duplicate, malformed, or
  ambiguous IDs;
- authoritative hosted plan coverage and monotonic Feature acceptance
  high-water marks consistent with every current criterion ID;
- Feature Worker task/project/worktree identity;
- clean implementation worktree and exact current HEAD;
- a complete acceptance matrix for every F-AC-NN whose evidence is bound to
  the same exact current candidate HEAD;
- deterministic T-AC-NN criteria, their F-AC mapping, and complete exact-HEAD
  evidence without replacing or weakening any F-AC;
- available Macro Task contextual coverage evidence bound to the same exact
  current candidate HEAD;
- current-head validation and native review evidence;
- current-head CI evidence with no failing or pending applicable checks;
- evidence that final verification started from
  `delivery-pending @ candidate-published`, plus the exact Worker handoff and
  any later resumption lineage;
- PR publication readback and exact PR HEAD equality;
- minimal durable SE-owned PR-body readback with no routine execution counts or
  internal delivery evidence;
- the exact Feature-local source-derived `closing_issue_refs` set containing
  this parent Feature and every verified existing associated local Macro Task, with the same
  closure intent read back from the PR body and no sibling or unrequested
  source closure; GitHub `closingIssuesReferences`, when available, is
  diagnostic only and cannot block final verification;
- standalone selected-base evidence including refreshed branch and exact base
  SHA, or stacked parent identity, unchanged parent HEAD, exact child base,
  stack order, and verified link receipt;
- ready-transition receipt plus a clean current-head automatic-review
  certificate for an unchanged initial HEAD, or the latest explicit-request
  receipt plus its clean current-head review result after one or more fix
  pushes;
- zero unresolved actionable review threads. Any provider-policy certificate,
  if available, is informational and cannot block this final verification.

When every requirement passes for the same exact HEAD, persist
`delivery-ready @ final-verify`. Until then, preserve
`delivery-pending @ candidate-published` unless a repair, rebase, plan question,
or blocker changes assignment ownership.

Aggregate every current F-AC-NN and derived T-AC-NN through the Feature Worker
evidence map and retain the exact candidate SHA. Every F-AC must have direct
evidence or one or more mapped T-AC criteria, and every T-AC must have
exact-HEAD proof. An uncovered, unverified, stale, or ambiguous criterion
prevents delivery readiness. Map every available local Macro Task outcome as
context, but a `partial` or `absent` projection and a planning-only local Macro
Task status of `blocked` do not block delivery once the final candidate covers
the Feature semantic contract. A Feature-level `blocked_by`
relation controls stack intent or cross-repository scheduling, but it does not
add a sibling to this PR's closing set. This acceptance verification is
evidence-only and never edits the Feature Plan Set or any registry.

On recovery, use the assignment's stored worker_task_id and candidate_sha to
reread the Feature Worker's final acceptance matrix. Accept it only when its
Feature Plan Set ref, Feature ID, observed Macro projection state, complete
F-AC-NN set, T-AC mapping, set/plan revision, and candidate SHA exactly match
current authoritative state. Feature membership or semantic-contract drift,
an unreported Macro projection change, or worker-report invisibility
invalidates the matrix.

Return repairable evidence mismatches to the Feature Worker without diagnosis.
The Feature Worker owns repair and replacement evidence. Final verification
never edits code, reruns review, mutates issues, or merges.

Report a standalone PR as standalone-ready with its exact PR, CI, review, and
stack evidence. Report a child as stack-ready only when every lower parent in
the selected chain is current and the stack topology is verified, while
recognizing that the child is not independently mergeable ahead of those
parents.
