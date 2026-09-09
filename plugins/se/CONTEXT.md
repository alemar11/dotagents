# SE Context

Repository context: [`../../CONTEXT.md`](../../CONTEXT.md)

Scope: `plugins/se/`

## Project Purpose Delta

SE is the repository's graph-first software-delivery plugin. Its bundled Learn,
Grilling Session, Explore, Spec, Adversarial Review, Review PR,
Deliver, Deslop, and Implement skills have distinct runtime contracts, while `AGENTS.md`
and `README.md` define package maintenance ownership and routing.

Spec owns one repository-scoped spec and actionable task plan, saved to one GitHub issue, with all task contracts embedded. Each invocation selects one repository; tasks inherit their spec's owner. Spec creates no cross-repository issue links or companion specs. Related same-repository specs use ordinary links, with body-backed
prerequisites that can be satisfied by usable PR candidates. Native GitHub
blocker changes belong to G on explicit user request, never to Spec. Deliver owns task-to-PR grouping and integration, with task
prerequisites independent of Git topology. The Spec content contract is at
[`specification.md`](skills/spec/references/specification.md).
Spec also owns the [delivery authorization](skills/spec/references/delivery-authorization.md)
marker and post-save pickup decision. Authorization is separate from semantic
revision and execution progress; No monitor
is started by publishing or marking a spec.

Explore runs in the invoking task or session. It uses Learn for read-only context preparation and explores relevant evidence before
Grilling Session, then investigates remaining questions without a separate
controller or transfer handoff.

Explore and Spec share research/review roles with Deliver in
[`subagents.md`](references/subagents.md). Callers own delegation and lifecycle.
Review PR reports hosted review results without repairs or acceptance decisions.

[Deliver](skills/deliver/SKILL.md) is the worker-to-PR workflow for specs,
issues and bounded requests. Its current-task delivery lead is designed for Astra,
retaining configured reasoning and explicit profile overrides. It
owns its worker role locally.
Workers complete implementation through required CI, or hand validated commits
to an assigned integration worker for a shared PR. Integration is a regular worker
assignment that combines contributions and verifies the assembled behavior; the
orchestrator verifies selected outcomes and integration. Compatible serial work,
including stacked branches, reuses workers/worktrees; concurrent assignments use
separate workers/worktrees. Deliver returns bounded results and resume context;
backlog monitoring and queue persistence belong to its caller. One independent
code-reviewer pass checks each completed PR candidate; the owning worker launches
it, fixes findings and validates corrections. The orchestrator verifies returned
evidence without an automatic second review. Claims,
source-progress writes and retrospectives are not part of its default path.

Deliver owns one implementation repository per invocation. External prerequisites
are inputs coordinated by the caller. Supplied contracts own shared interfaces and
per-repository PR-readiness evidence; local contract checks and real integration
are distinct obligations.
