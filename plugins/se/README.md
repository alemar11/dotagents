# SE

SE supports repository-grounded refinement, feature specifications, actionable
task plans, reviewed PR delivery, and durable project knowledge.

| Skill | Responsibility |
| --- | --- |
| `se:learn` | Maintain explicitly authorized local project knowledge and review rules. |
| `se:grilling-session` | Refine a topic through one focused question and recommendation at a time. |
| `se:explore` | Explore evidence, refine the question, and investigate read-only in the current task or session. |
| `se:spec` | Create or revise a coherent spec with an ordered actionable task plan; save to GitHub. |
| `se:adversarial-review` | Independently pressure-test a fixed software change without editing it. |
| `se:review-pr` | Request or resume a hosted Codex PR review, wait, and report the provider result to the calling task. |
| `se:chief-of-staff` | Coordinate one visible Deliver task per repository in the App, through ready PRs and required cross-repository checks. |
| `se:deliver` | Orchestrate isolated workers in one repository through validated ready PRs. |
| `se:implement` | Implement selected local work, optionally consult a UI designer, validate it, and commit scoped files without publication. |
| `se:deslop` | Explicit-only audit and minimal safe cleanup of low-value code across every major directory. |

Learn, Implement and Review PR permit implicit selection within their descriptions. The
other entrypoints require explicit invocation or an authorized composed handoff.
Deslop requires explicit user invocation.

## Feature specifications

One main spec describes a coherent outcome, accepted decisions, acceptance
criteria, and tasks in one repository. Cross-repository coordination belongs to the caller. Tasks have stable IDs,
scoped outcomes, completion checks, validation, and real prerequisites. Their
recommended sequence does not imply dependencies or Git stacks.

Spec saves new specs to GitHub by default: one spec issue containing the complete task plan.
Related specs use ordinary links; prerequisites state the evidence and activity
they gate, allowing dependent work from usable PR candidates. Spec never manages native issue
blockers; explicitly requested blocker changes belong to G. No-write previews remain in the conversation; saved specs use GitHub only.
See the canonical [specification contract](skills/spec/references/specification.md)
and [revision rules](skills/spec/references/existing-specs.md).

Spec runs in the current session with its configured model and reasoning and
updates the task title to `📚 Plan Feature · <outcome>` when supported. It asks
material specification questions through Grilling Session and reviews the complete
spec/task contract before saving. Planning preserves execution progress and
does not start delivery implicitly.

After verifying an authoritative save, Spec asks whether to authorize automatic
delivery to ready PRs unless the answer or authorization is already established.
Approval applies `ready-for-agent` to the main GitHub issue, creating the label
if missing. New specs remain inactive without approval. Ordinary revisions
preserve authorization, and setting
the marker does not start a monitor. The [authorization contract](skills/spec/references/delivery-authorization.md)
owns the pickup decision; shared [readiness states](references/states.md) own
the GitHub label catalog and lifecycle transitions.

The templates use a compact ordered task list; each task owns its repository
scope, acceptance links, prerequisites, and paired verification checks. GitHub
embeds all task bodies in the spec issue.

## Chief of Staff

[`se:chief-of-staff`](skills/chief-of-staff/SKILL.md) runs only in the Codex App,
in the current task without changing its project or execution location. Chief of
Staff must be projectless or in its original saved project location; Deliver
coordinators must use their saved repository checkouts. Separate coordinator
worktrees fail the global gate, including on resume. Only implementation workers
use isolated worktrees. It verifies every selected
repository has a standalone saved project before any dispatch or follow-up, then
reuses or creates one visible Deliver coordinator per repository. A failed mapping
gate blocks coordination while leaving running tasks untouched. Deliver retains
implementation, worker, review and CI ownership; Chief of Staff coordinates
external inputs and verifies required cross-repository results through ready PRs.
Invocation authorizes the selected delivery tasks, not project repair, merging or
deployment. It preserves task identities and results in the conversation for resume.

## Deliver

[`se:deliver`](skills/deliver/SKILL.md) accepts saved specs, selected issues, or
bounded requests in exactly one repository. External specs are inputs; the caller
coordinates separate repository runs. Linked specs define shared contracts and
state whether local contract checks or real-candidate integration makes each PR
ready. Missing required inputs produce a resumable handoff after independent
work finishes. The current task is the delivery lead and orchestrator, designed
for Astra with caller-configured reasoning and explicit profile overrides.
Workers use isolated worktrees: visible App tasks or native CLI subagents. Reuse
a worker and its worktree for compatible serial work, switching branches as needed;
concurrent assignments require separate workers and worktrees. Serial stacked PRs
retain distinct branches and may share a worker/worktree. Each worker owns
implementation, self-checks, independent candidate review, scoped fixes, publication and required CI in one assignment.
The orchestrator owns scope, dependencies, optional stacks and assembled outcomes.
When contributions feed one PR, it assigns a regular worker to integrate their
validated commits, resolve conflicts, verify combined behavior and publish the
result. Contribution workers may finish at a commit handoff; the selected delivery
still ends at verified ready PRs. Parallel work does not require stacked PRs.
Worker creation follows the active runtime's authorization rules; established
authority is preserved across assignments and continuations.

Delivery finishes with all required PRs non-draft, current required CI passing,
and selected outcomes verified. Merge and deployment are separate. There are no
mandatory adversarial/hosted reviews, claims, repair-round ledgers or audits;
repository/user requirements still apply. Complete saved specs transition from
agent-ready to human-ready using the shared states contract, leaving automatic issue closure to a later PR merge and preventing automatic requeue. Other source-progress
writes are opt-in.
Worker setup/recovery and integration details are loaded only when applicable.
The skill returns the selected outcome and resume context to its caller; backlog
monitoring, scheduling and queue persistence remain outside Deliver. It has no
automatic cross-session ownership exclusion.

## Standalone PR review

Review PR obtains the hosted Codex review result for a ready PR's exact HEAD:
reuse a completed result, resume a matching pending request, or request and wait
when review is missing. It preserves the original 30-minute deadline and returns
pending on timeout. Explicit audit-only inspection remains read-only. Standalone
and composed calls have the same scope and run in the calling task with no
subagents, spec or local checkout. Clean and findings both complete monitoring;
the caller decides any repair, rebuttal or acceptance. G owns request transport,
lineage, bounded waits and terminal evidence.

## Shared boundaries

- [Execution scope](references/execution-scope.md) preserves the same subagent
  policy standalone and composed. Implement and Adversarial Review execute work;
  an orchestrator may assign them to agents; Implement may consult its optional UI designer.

- [Execution roles](references/subagents.md) own reusable research, development and review
  definitions. Explore, Spec and Delivery select them while retaining their own delegation,
  lifecycle, fallback, and final decisions.
- G owns GitHub transport, issue lifecycle, review lineage, CI, and stack
  operations. SE runs its dependency preflight before the required handoff;
  it never installs or substitutes G. Previews using only supplied or local sources need no G access.
- The [hosted-content contract](references/hosted-content-safety.md) owns portable
  paths, titles, and bounded readback repair. SE owns semantic projection;
  G owns transport and provider readback.
- [Workflow graphs](references/workflow-graph.md) and each skill's state reference
  distinguish transient workflow position from saved content and external facts.
- Explore stays in the invoking task or session with optional
  bounded native subagents. Delivery alone selects App-visible or CLI-native
  developer transport under its runtime contract. Chief of Staff coordinates visible
  App Deliver tasks across repositories. Learn remains local-only.

This source tree is the maintained SE design surface; installed caches are
verification surfaces, not editable source.
