# Delivery workers

Read before worker creation or assignment; use Recovery only when interrupted,
resuming, or replacing a worker. The shared
[runtime surface](../../../references/codex-runtime-surface.md) owns classification.

## Transport and setup

On the App, use a visible task in the exact matching saved repository project
and an isolated worktree. On CLI, use a native subagent with an isolated worktree.
Creating a subagent does not establish filesystem isolation: prepare and assign
its worktree explicitly, and require the same checkout verification as on App.
An unresolved surface or unavailable required transport/target blocks affected
work. Do not substitute the other surface, an external process, or implementation
in the orchestrator. Apply the entrypoint's authorization boundary before worker
creation. Never create a replacement coordinator.

Where the live runtime permits skill-selected profiles, workers default to
`gpt-5.6-luna` with `max` reasoning; explicit user overrides win. Where profile
selection requires an explicit user request, inherit the configured default
unless that request exists. Do not ask for confirmation merely to select a
profile. Request only permitted settings, without gating editing on effective-model
telemetry or claiming requested settings were independently observed. Use the worker
title `🤖 <assignment>` when supported, naming its bounded work. Include the
repository name only when needed to distinguish otherwise ambiguous tasks.
Do not use the orchestrator's 🚚 prefix. Titles are metadata, not target identity.

Create with the complete initial assignment, not a bootstrap followed by a second
permission message. Pending worktree setup must finish before mutation; the
worker verifies the actual repository/remote, worktree, branch, base and full
starting HEAD against its assignment. Never overwrite dirty content or reuse
an incidental checkout to make the target fit. Resolve a mismatch before editing.
A creation receipt establishes a known creation effect, not a verified checkout.

## Assignment and result

Every worker assignment stays in the orchestrator's single repository. Include
the selected outcome and constraints, exact repository and intended
worktree/branch/base, prerequisite commits, relevant source contracts with spec
identity/revision when applicable, shared-contract reference and declared readiness
boundary, any pinned external input, validation,
publication authority and source references with the exact issues eligible for
closing references under
[Source references](../SKILL.md#source-references). After checkout verification,
the worker's first progress report to the orchestrator includes its permanent
worker/task identity when available and the resolved worktree path. A pending
creation handle or title is not that identity. This report is informational:
editing does not wait for acknowledgment or unavailable identity metadata.
Use exact source and commit pointers for available context, adding only
assignment-specific decisions and constraints. Do not duplicate entire specs or
the orchestration conversation.
Carry the [publication and readiness](#publication-and-readiness) obligations
in each assignment.

The worker owns implementation, self-inspection, tests, PR publication/readiness
and applicable CI for its branch within that assignment. It loads Implement, then
runs the [candidate review](#candidate-review), handles scoped fixes through
Implement, and uses the applicable G workflows through readiness. CI fixes remain within the
original outcome and are revalidated and published by the same worker.

When the orchestrator selects a shared integration PR, contribution assignments
end with validated commits made available to the designated integration worker.
They use Implement and return the result below; separate contribution PRs are
needed only when the selected topology requires them. The integration assignment
uses the same worker profile, transport and result contract under
[integration.md](integration.md#integration-assignment). A contribution handoff
completes that assignment, not the selected feature's delivery.

Workers may delegate Implement's
[optional UI designer](../../implement/SKILL.md#optional-ui-design) and Deliver's
[candidate reviewer](#candidate-review); other agent creation is prohibited.
The reviewer belongs to the Deliver assignment, not Implement's own delegation
contract. Workers cannot broaden scope, mutate another worker's
branch/PR, land PRs, deploy or perform production actions. An integration assignment
may combine assigned commits into its own delivery branch. Honor direct user stops
and corrections; relay material scope/target changes to the orchestrator and
reconcile affected dependencies before conflicting work continues. The
orchestrator is the normal coordination point, not a barrier to user authority.

Return selected source references and, for a spec, its identity and revision;
verified outcomes and outstanding scope; PR URLs when applicable and exact HEAD/base;
verified closing references and ordinary source links; reviewed base/HEAD,
review findings and their dispositions, final fix-validation HEAD or explicit
review skip; checks and CI applicability/results; worker/worktree/branch identities, preserved dirty content,
blockers and the next bounded action when work remains. For missing external
inputs, name the required capability/artifact and resume evidence; do not assign
work to the other repository or claim deferred integration passed. Finish mutation before
returning completion. The orchestrator verifies current facts without asking for
another ritual receipt or a replay of the worker's investigation.
Keep each result bound to its repository, branch/PR and full commits even after
the worker's checkout moves to another assignment.

## Candidate review

Read when preparing a completed PR candidate. The owning worker creates one native
read-only [code-reviewer](../../../references/subagents/code-reviewer.md) for the
whole candidate after implementation, integration and relevant local checks.
Use its Astra/medium default where runtime profile selection is permitted;
otherwise inherit the configured profile, honoring explicit user overrides.
For a combined PR, the integration worker runs this pass after assembly;
contribution-only assignments need no separate pass. Each PR in
a stack has its own candidate review against its actual base.

Commit the candidate and suspend candidate mutations until the reviewer returns.
Supply an immutable base/HEAD snapshot, complete delta, selected scope, repository
rules and validation evidence, without the implementation conversation. Reviewers
never modify code. Wait for a complete result tied to those exact revisions;
missing evidence or failed review execution is a blocker, not a clean pass.
Reconcile an uncertain launch before recovery; reuse a completed attributable
review on resume rather than automatically requesting another.

The worker assesses findings, implements actionable scoped fixes through
Implement, and verifies each disposition and corrected outcome with affected
checks. Document why any finding needs no change. Escalate material scope or
authority decisions to the orchestrator; ordinary fixes need no coordination
roundtrip. Return the review evidence and fix validation with the delivery result
for the orchestrator to verify.
Do not automatically run a second review or create a repair-round ledger.
Explicitly requested or repository-required follow-up reviews retain their own
contract. If corrective work changes HEAD, retain the reviewed HEAD and record
fix verification at the final HEAD; never claim the reviewer reviewed the fixes.
Unrelated scope/base changes invalidate affected evidence and require
reconciliation before readiness, not silent reuse of the earlier clean result.

A worker may publish a draft while review is pending, but must complete review
disposition and verify corrections before marking it ready or reporting an
existing ready PR delivered. No orchestrator acknowledgment is required. Explicit user instructions may skip the pass;
report that exception. Required review capability being unavailable blocks
completion rather than silently substituting worker self-inspection.

## Requested reviews

Read when a requested review returns findings or repairs enter a separately
managed review workflow.

For requested reviews, the orchestrator selects scoped actionable findings and
assigns fixes to the owning worker through Implement, then verifies the corrected
outcome and any required follow-up review. These fixes use the same progress and
blocker rules as other delivery work; they do not create a repair-round ledger.
A separately established managed review workflow retains its owner and budget;
carry its reserved batch when delegating repairs within that workflow.


## Publication and readiness

Read before hosted access or PR publication in the orchestrator and each worker.

Before hosted access, the actual actor applies the host-specific [G
preflight](../../../references/g-dependency-preflight.md) for the workflows it
needs; immediately before every hosted write it applies [hosted-content
safety](../../../references/hosted-content-safety.md). Carry these routes in
worker assignments. Do not install, reload or substitute dependencies.

For publication use G Send; it creates drafts and preserves existing draft state.
The worker owns readiness after publication and completed review/fix verification. Resolve `references/network-execution.md`
and `references/gh-dependency-preflight.md` from the installed G source root
established by G preflight; never assume SE and G are sibling directories.
The assigned worker follows those contracts and reads the exact PR's draft state
and full HEAD. For a draft, mark only that validated PR ready using the supported
GitHub CLI operation, then read back non-draft state and unchanged full HEAD.
For an already-ready PR, verify non-draft state and the validated full HEAD as a
no-op; do not attempt another ready transition. An unexpected HEAD change
requires reconciliation and affected validation before accepting readiness. This is a distinct authorized
transition, not Send behavior or a request for automated review. Use G GitHub
Actions for current checks and CI fixes. Missing readiness capability blocks
completion; do not report a draft as delivered.


CI is conditional on the repository and PR. Reconcile the current candidate's
check results and workflow runs with repository CI configuration and documented
requirements, including external CI. If the PR triggers applicable CI, wait for
it and fix failures within scope before delivery, even when branch protection
does not require those checks. Expected but missing runs and inaccessible results
remain unresolved; an empty check list alone does not establish that CI is absent.
Legitimate skips or filters need applicability evidence, not a claim that tests ran.

When the repository has no configured or required CI, report CI as not applicable
and complete delivery once local validation, review and the other acceptance
criteria pass. Do not add CI or require a plan upgrade merely to deliver a PR.

Branch-protection policy and CI results are separate evidence. Unless the
assignment explicitly requires merge-policy verification, a policy-read failure
alone does not block delivery; it does not make available CI results unknown.
Distinguish an explicit plan-related feature restriction from missing permission
or an unexplained failure, and disclose the limitation. G's full merge-policy
readiness may remain unknown while SE delivery completes; never claim that hidden
merge gates passed. Verified delivery requirements still apply, and merge-policy
verification gates delivery only when explicitly required by the assignment.
Already-incorporated work needs current outcome proof, not a duplicate PR.

## Serial reuse and concurrent work

Assign one writer per branch, PR and shared artifact, including
any requested source-progress edits. Worktrees do not isolate ports, databases
or external services; separate those resources or serialize their use.

Prefer the same worker and worktree for compatible serial assignments in the
same repository. On every reassignment, update the existing worker's title to
the current bounded assignment using the title format above, including repair
and integration work. Verify the rename when supported; unavailable title
updates do not block execution or justify a replacement worker.

Before switching branches, finish the previous assignment,
preserve its commits and PR reference, and stop its branch-dependent processes.
Resolve dirty content without discarding it or carrying it into another
assignment; if safe reuse is unavailable, use another isolated worker/worktree.
Reconcile any existing writer or checkout of the target branch before switching;
never force a switch around conflicting ownership. The worker verifies the
assigned branch, base and full HEAD before editing. Reuse changes the branch,
not the task's worktree binding.

For a serial stack, create each child branch from the exact validated parent
commit under [integration.md](integration.md). Earlier branches and PRs remain
available when the worker moves to a child. Returning to an earlier PR for a fix
is another serial assignment; preserve the current work first and reconcile
affected descendants after the parent changes.

Concurrent assignments require distinct workers and worktrees with one writer
per branch/PR. A reused worker never handles two active assignments at once.
Leave completed App tasks visible and unarchived.

## Recovery

Separate runs have no automatic ownership exclusion or lock replacement;
reconcile known competing work before a conflicting write.

Wait for results or meaningful changes, not repeated generic status updates.
If setup or publication has an uncertain effect, inspect the existing task or
PR/branch evidence before retrying. Never infer failure from a missing reply or
create a duplicate worker/PR while the earlier effect remains unresolved.

Before replacement, confirm the old worker stopped and cannot race the new one;
preserve commits and dirty content, reconcile outstanding writes, and verify
the replacement's exact target. Unknown liveness blocks replacement. Preserve
worktrees by default; do not clean, reset or delete user work to simplify recovery.

On interruption, preserve the assignment/result context above and identify pending
submissions, uncertain effects and active/stopped/unknown worker liveness. Resume
from that handoff plus current Git/PR state.
Reuse an attributable stopped worker/result when safe; never repeat completed
work solely to reconstruct narrative or renew authority.
