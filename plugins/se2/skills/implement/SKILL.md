---
name: implement
description: "Execute agent-ready SE2 Tasks through explicitly authorized and independently monitored task handoffs; preserve the Feature, Task, and dependency contracts and report verified outcomes."
---

# Implement Task

## Purpose and invocation

Use this skill only for an explicit request to implement one or more agent-
ready SE2 Tasks. It consumes the complete Feature bundle produced by
`se2:feature`; it does not replace the Feature graph, redesign the Feature
definition, or invent missing Task dependencies.

The task is implementation work in the verified repository destination. The
skill may change code and repository-owned documentation only within the Task
contract's scope and must return validation evidence for the Task's acceptance
criteria. A GitHub issue mutation is a separate authorization boundary.

## Task profile ownership

Load the skill-owned [task-profile.md](references/task-profile.md) before
startup. It defines two mandatory roles: a Sol/medium orchestrator and a
Luna/max worker. The implementation profile and topology belong to this skill,
not to the root-level task contract.

Pass the complete profile to the shared preflight before starting either role.
The preflight must verify both roles first. If Luna/max or any other required
role is unavailable, fail closed with `unsupported-runtime`; do not start the
orchestrator, substitute a role, lower a reasoning level, or change topology.
Use the profile's canonical emoji title for the orchestrator and each worker;
title initialization/readback is best-effort and never a task identity or
recovery key.

## Common task preflight

Before creating, resuming, or monitoring an implementation task, load:

- [task-profile.md](references/task-profile.md) for the mandatory orchestrator
  and worker roles;
- [task-preflight.md](../../references/task-preflight.md) for explicit
  invocation, live capability, destination, authorization, observation, and
  recovery gates;
- [task-handoff.md](../../references/task-handoff.md) for the assignment,
  independent observation, update relay, reconciliation, and final-report
  contract.

Do not duplicate those contracts in this skill. The preflight must separately
record permission to create or resume a task and permission to mutate GitHub.
The first never grants the second.

If the live application, task creation, independent observation, monitoring, or
update relay is unavailable, fail closed. Do not fabricate a task identity,
relay a stale update, claim a final state, or retry an ambiguous operation.

## Execution path

1. Confirm the explicit implementation request and select the bounded Task
   set from a complete Feature bundle.
2. Re-read each Task contract, its Feature reference, `dependency_ids`, allowed
   paths, repository identity, acceptance criteria, validation policy, and
   documentation obligations.
3. Resolve the implementation profile and topology owned by this skill, then
   verify both required roles before startup.
4. Run the shared task preflight for every task destination. For a
   multi-repository Feature, keep each Task in its repository-local project;
   cross-repository Feature links do not make a Task destination portable.
5. Create or resume the task only after the preflight is ready, then record the
   exact independently observed task, project, host, repository, and state.
6. Relay partial updates with their observed state and preserve the final
   update as a distinct terminal report.
7. After any timeout, error, or monitoring gap, reconcile the original effect
   before considering a retry. An unknown effect blocks.
8. Finish only with independently observed final state, Task acceptance and
   validation evidence, documentation evidence when required, and the
   authorization record referenced from preflight.

The dependency graph determines which Tasks are eligible to start. A Task may
start only after every unfinished incoming dependency is proven complete and
its repository scope is independently verified. Do not turn a preferred order
into a dependency or mutate the graph from this skill without an explicit
maintenance request governed by `se2:feature`.

## GitHub boundary

Creating or monitoring an implementation task in the ChatGPT/Codex application
does not authorize creating, updating, relating, or commenting on GitHub
issues. Such changes require the invoking workflow's explicit GitHub
authorization and its read-after-write evidence. If that authorization is
absent, report the implementation result without claiming tracker mutation.

## Terminal report

Return a handoff report that points to the canonical task-handoff record and
contains the selected Feature/Task references, observed task identities and
destinations, partial/final relay evidence, validation results, changed paths,
reconciliation evidence, and one terminal `outcome` of `complete` or `blocked`.
