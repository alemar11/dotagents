# Task Preflight

This is the root-level SE2 contract for any workflow that creates, resumes, or
monitors a task in the ChatGPT/Codex application. Feature and Implement skills
must load it before attempting a task handoff. It defines required outcomes and
evidence; it does not define an application interface.

## Contents

- [Scope and ownership](#scope-and-ownership)
- [Required preflight gates](#required-preflight-gates)
- [Canonical preflight record](#canonical-preflight-record)
- [Fail-closed rule](#fail-closed-rule)

## Scope and ownership

The contract owns the common gates for task creation and observation:

- explicit invocation;
- live application capabilities;
- independent identity, project, host, and state observation;
- partial and final update relay;
- repository and project destination verification;
- recovery after an ambiguous effect.

The invoking skill owns its task profile and topology. This contract contains
no model, reasoning, worker, or topology default. GitHub issue planning and
publication remain governed by the invoking skill's own contract.

The invoking skill must pass a reference to its complete task profile and the
roles required by the selected topology. The preflight verifies the live
runtime for every supplied role; it does not select, rewrite, downgrade, or
replace a role. For a multi-role profile, every role must be verified before
the first role starts.

## Required preflight gates

### 1. Explicit invocation

The user must explicitly request the workflow that creates or monitors a task.
Do not infer permission from a feature description, a title, a previous task,
or the fact that the current session can access the application. An implicit or
ambiguous request is `blocked` before any task effect.

### 2. Live application capabilities

Verify the current application runtime immediately before the first task
effect. The live capability check must establish all capabilities required by
the requested topology:

- create or resume a task;
- independently observe the task after the effect;
- receive partial updates and a final update;
- relay those updates to the invoking session.

Documentation, cached metadata, an earlier receipt, or a static validator is
not evidence that a live capability is available. If creation, observation, or
monitoring cannot be verified, fail closed before creating or retrying a task.

The profile capability check is equally strict. If any required role is not
supported by the live runtime, the preflight result is `blocked` with
`blocker: unsupported-runtime`. There is no automatic model, reasoning, worker,
or topology fallback.

### 3. Verifiable destination

Resolve one exact destination for every task before creation. Independently
verify:

- `repository_identity` and the repository root or checkout path;
- `project_identity` and the project binding used for the task;
- `host_identity` for the application execution host.

The project binding must be compatible with the intended repository. A project
that merely mentions a repository, a path copied from the request, or a
cross-repository project assumption is insufficient. In a multi-repository
run, verify each repository/project destination separately.

### 4. Independent observation

After creating or resuming a task, read the resulting state independently from
the authoritative application view. The observation must preserve the exact
`task_identity`, `project_identity`, `host_identity`, repository destination,
and current `state`. A display title, conversation text, or caller-supplied
identifier is not identity evidence.

The same observation boundary applies after a resume, a host change, a
monitoring gap, or a final update. Do not report a task as running or complete
from an unverified receipt.

### 5. Separate authorization scopes

Record these decisions independently:

- `task_creation_authorization`: permission to create or resume the task in
  the application;
- `github_mutation_authorization`: permission for the exact requested GitHub
  issue, branch, pull-request, review, relation, label, or comment mutation.

One authorization never implies the other. A granted task permission does not
authorize GitHub mutation. A granted GitHub publication permission does not
authorize creating or monitoring an application task. If the invoking skill
needs both, it must obtain and verify both explicitly.

### 6. Reconciliation before retry

An error, timeout, disconnected monitor, or incomplete receipt is an
ambiguous effect, not proof that no task was created. Before any retry:

1. re-observe the original destination and the current application state;
2. search for the exact task effect using independently observed identity and
   scope;
3. record whether the prior effect was `applied`, `not-applied`, or
   `unknown`;
4. retry only when authoritative evidence proves `not-applied` and the live
   runtime permits a new attempt.

If reconciliation cannot distinguish those outcomes, keep the run blocked and
do not create a replacement task.

## Canonical preflight record

The following field names are the common minimum record. Values are examples;
the invoking skill may add run-specific evidence without changing their
meaning.

```yaml
preflight:
  invocation:
    explicit: true
  profile:
    reference: "<skill-owned task profile>"
    roles_verified: true
  capabilities:
    create_task: available
    observe_task: available
    monitor_task: available
    relay_partial_updates: available
    relay_final_update: available
  target:
    repository_identity: "<independently observed repository>"
    project_identity: "<independently observed project>"
    project_root: "<verified repository-compatible path>"
    host_identity: "<independently observed host>"
    independently_verified: true
  authorization:
    task_creation: granted
    github_mutation: not-requested
  outcome: ready
```

For a blocked preflight, retain the observations that are available and record
the exact missing capability, authorization, destination proof, or recovery
evidence. Do not replace it with a fabricated task identity or a successful
status.

## Fail-closed rule

If the ChatGPT/Codex application, live task creation, independent observation,
or monitoring/relay path is unavailable, the outcome is `blocked`. The skill
must return the smallest recovery input and stop before the affected task
effect. It must not claim that a task exists, is being monitored, or completed
until the required live evidence is available.
