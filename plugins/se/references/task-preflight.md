# Task Preflight

This is the root-level SE contract for any workflow that creates, resumes, or
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
- authoritative assigned-task bootstrap for effective model, reasoning,
  project, repository, and host readback;
- inventory-backed project selection plus independent stable task identity and
  state observation;
- deterministic display-title capability and bounded correction authority;
- partial and final update relay;
- repository and project destination verification;
- recovery after an ambiguous effect;
- optional runtime capabilities declared by the invoking skill.

The invoking skill owns its task profile and topology. This contract contains
no model, reasoning, worker, or topology default. GitHub issue planning and
publication remain governed by the invoking skill's own contract.

The invoking skill also owns the requested model and reasoning values for each
role and resolves any assignment-specific choice before task creation or
resume. This contract owns the live capability gate for actively requesting
those values and receiving an authoritative bootstrap result from the assigned
task; [Task Handoff](task-handoff.md) owns the typed task-owned observation,
comparison, and controller identity binding.

The same ownership split applies to project identity. This preflight owns
selection of one exact repository-compatible project from the live application
project inventory and freezes that identity as the expected destination. Task
Handoff owns the assigned task's post-effect self-observation and bounded
comparison against that expected identity. A configured project target is not
proof that the resulting task received that binding.

The `task controller` is the session that creates or resumes one assigned
application task, independently observes its stable identity and state, and
binds the task-owned bootstrap result to that exact identity. The `assigned
task` is the planner, orchestrator, Feature Worker, or separately instantiated
optional role named by the handoff. The task controller's own effective model
and reasoning are not assignment evidence and must never be compared with the
assigned role's requested profile. The two profiles may differ intentionally.

Preflight runs in the task controller before the effect and verifies that the
runtime can request the assigned profile, observe the resulting stable task
identity, and relay the assigned task's bootstrap result. It does not perform
the value comparison before the assigned task exists. Task Handoff owns the
assigned task's authoritative bootstrap comparison and the controller's
post-effect identity binding.

An explicit invocation of a task-managed Feature or Implement workflow also
selects the exact required role profiles declared by that workflow. For every
required role, and for every optional role instantiated as its own application
task, the task controller must actively request the resolved model and
reasoning on creation and resume. Omitting either value and relying on an
ambient, inherited, configured, or provider-default profile is prohibited,
even when the resulting effective values happen to match. This selection
authorizes only the profiles declared by the invoked skill; it does not permit
an undeclared model or reasoning substitution.

The invoking skill must pass a reference to its complete task profile and the
roles required by the selected topology. The preflight verifies the live
runtime for every supplied role; it does not select, rewrite, downgrade, or
replace a role. For a multi-role profile, every role's explicit request and
assigned-task bootstrap path must be supported before the first role starts.

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
- inventory the projects currently configured on the intended application
  host;
- independently observe the stable task identity and state after the effect;
- let the exact assigned task read its authoritative task-scoped execution
  context and compare its effective project, model, reasoning, repository, and
  host with the handoff;
- receive a structured bootstrap result whose evidence task identity can be
  bound to the independently observed stable task identity;
- receive partial updates and a final update;
- relay those updates to the invoking session.

An authoritative task-scoped execution context satisfies effective-profile
readback when it is accessible to the exact assigned task, identifies that
same task, and supplies the values used in its structured bootstrap result.
The controller does not need direct access to that raw source; it must
independently observe the stable task identity and require the bootstrap
evidence identity to match it exactly. A generic conversational self-report is
not a structured bootstrap result.

Documentation, cached metadata, an earlier receipt, or a static validator is
not evidence that a live capability is available. If creation, observation, or
monitoring cannot be verified, fail closed before creating or retrying a task.

Before recording a required role as verified, establish that the current
runtime can accept an active request for the complete resolved profile,
observe the resulting stable task identity, and relay the exact assigned
task's authoritative bootstrap result. A request payload, configured default,
creation receipt, unstructured conversation text, or locally inferred value is
not effective-profile evidence. `roles_verified: true` means every required
role supports that request and bootstrap path; it does not claim that a task
has already been created or that its effective profile has matched. The
handoff supplies that proof after stable task identity observation.

If the runtime can create a task only by inheriting one or both required
profile values, the fixed-profile capability gate has not passed. Stop before
the task effect instead of creating a task and checking which defaults it
received afterward.

Project selection and project readback are also separate capabilities. The
ability to request a project, an accepted creation effect, or an echoed target
does not establish the task's effective project binding. The exact assigned
task must read the post-effect project value from its authoritative task-scoped
context and bind it to the stable task identity in the bootstrap result. A
missing value discovered only after creation follows the bounded
reconciliation in [Task Handoff](task-handoff.md); it never becomes an inferred
match.

The profile capability check is equally strict for required roles. If any
required role is not supported by the live runtime, or the exact assigned task
cannot later read its effective profile authoritatively and return the bound
bootstrap evidence, the result is `blocked` with `blocker:
unsupported-runtime`. There is no automatic model, reasoning, or
required-topology fallback. A skill may declare optional roles or optional
capabilities with an explicit parent or serial fallback. Those facts must be
recorded and must not be reported as delegated work unless a worker was
actually started and its bootstrap identity was verified.

### Optional runtime capabilities

When the invoking skill declares them, inspect delegation and goal capability
once before the first optional effect. Record delegation as available,
unavailable, or unknown, and record any observed worker capacity separately
from workers that actually started. Delegation unavailability selects the
skill-owned fallback and does not block a required parent task.

Goal tools are also optional. When unavailable, preserve the skill's objective
in its task or run report and continue. A resumable user-input wait must not be
converted into a blocked goal merely because the goal runtime has no explicit
unblock operation.

For every role whose profile declares a deterministic display title, also
inspect the live capability to request that title, observe it independently,
correct it after the stable task identity is known, and preserve enough
attempt evidence to prevent replay after recovery. Record unavailable title
initialization, correction, or recovery evidence as a display-metadata
limitation. It does not block an otherwise verifiable task topology, but it
must not be omitted from the preflight or later reported as verified.
The handoff's best-effort plain-text title hint does not make title
initialization available and cannot satisfy title observation or correction.

### 3. Verifiable destination

Resolve one exact destination for every task before creation. Independently
verify:

- `repository_identity` and the repository root or checkout path;
- `project_identity` as one exact expected project selected from the current
  live application project inventory;
- `host_identity` for the application execution host.

The project binding must be compatible with the intended repository. A project
that merely mentions a repository, a path copied from the request, or a
cross-repository project assumption is insufficient. In a multi-repository
run, verify each repository/project destination separately.

Freeze the exact expected project identity and inventory evidence before the
task effect. If no repository-compatible project exists in the live inventory,
the preflight is `blocked` before creation. Return the smallest recovery input:
ask the user to add or configure that exact repository as a saved project in
the ChatGPT/Codex application. Never substitute a neighboring project, create
an intentionally projectless task, or treat a repository path as project
identity.

### 4. Task identity and assigned-task bootstrap

After creating or resuming a task, the controller independently observes the
stable `task_identity` and current `state` from the authoritative application
view. The assigned task then performs the bootstrap self-check defined by Task
Handoff and returns its typed effective-role and destination observations
before beginning role-owned work. A display title, caller-supplied identifier,
echoed request profile, or unstructured conversational claim is not identity
or effective-profile evidence.

The task controller owns creation/resume, stable identity observation, and
binding of the structured bootstrap result. The assigned task owns the
authoritative read of its own task-scoped execution context and every
requested-versus-observed comparison. The controller does not duplicate that
profile or project read.

The project identity observed by the assigned task must be present and exactly
equal the frozen preflight identity. Do not infer task-project binding from the
request, the creation receipt, the working directory, a checkout or worktree
path, the display title, or conversation text. A non-null mismatch is a
destination mismatch and blocks normal monitoring. A missing or unobservable
value must complete the handoff's one bounded assigned-task re-read and
refreshed controller project inventory before classification; it is never a
match.

The assigned task compares its effective model and reasoning with the
assignment-specific values resolved from the skill-owned profile and returns
that typed observation in the bootstrap result. Never compare the task
controller's own profile with the assigned role. A missing or unobservable
exact-task observation for a required role is `blocked` with `blocker:
unsupported-runtime`; an authoritative exact-task observation whose effective
model or reasoning differs from the request is `blocked` with `blocker:
effective-profile-mismatch`. Both stop before normal monitoring or update
relay. Preserve and reconcile the observed task identity; do not create a
replacement. For an optional role, use only the invoking skill's declared
parent or serial fallback and do not claim delegated work.

A matching effective readback does not repair a missing explicit profile
request. Require both the pre-effect request evidence owned by the handoff and
the post-effect effective-profile observation for the same task.

The same identity-and-bootstrap boundary applies after a resume, a host
change, a monitoring gap, or a final update. Do not report a task as running
or complete from an unverified receipt or an unbound bootstrap result.

### 5. Separate authorization scopes

Record these decisions independently:

- `task_creation_authorization`: permission to create or resume the task in
  the application;
- `title_adjustment_authorization`: permission to correct the same declared
  deterministic title at most once after the stable task identity is observed;
- `github_mutation_scope`: the exact requested GitHub issue, branch,
  pull-request, review, relation, label, or comment mutations in scope for the
  explicit invoking SE request. These writes are implicitly authorized by the
  invocation; no second confirmation is required.

Task creation and GitHub scope remain separate. A task permission does not
broaden the GitHub mutation scope, and the GitHub mutation scope does not
authorize creating or monitoring an application task. The explicit SE
invocation supplies the in-scope GitHub write authority; the workflow must
still verify exact repository, operation, identity, and read-after-write
evidence. Keep bounded title-adjustment authority separately visible as
described below.

When an explicit invocation authorizes creation of a task whose skill-owned
profile declares a canonical title, the bounded correction of that same title
is part of the requested task initialization unless the user explicitly
forbids renaming. Record that authority separately because correction is a
distinct application effect. It never authorizes arbitrary or later lifecycle
renames.

The same explicit invocation authorizes the task controller to request the
exact model and reasoning declared by the skill-owned profile. This is part of
the bounded task-creation or resume authority, not permission to select a
different profile or rely on ambient inheritance.

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
    request_mode: explicit
    ambient_inheritance: forbidden
    roles_verified: true
  capabilities:
    create_task: available
    inventory_projects: available
    observe_task_identity: available
    request_explicit_role_profile: available
    assigned_task_bootstrap: available
    receive_bootstrap_result: available
    monitor_task: available
    relay_partial_updates: available
    relay_final_update: available
    request_display_title: available
    adjust_display_title: available
  optional_capabilities:
    delegation: available
    observed_worker_capacity: null
    goals: available
    effective_mode: parallel-analysis
  target:
    repository_identity: "<independently observed repository>"
    project_identity: "<inventory-backed expected project>"
    project_inventory_evidence_ref: "<live inventory observation>"
    project_repository_compatible: true
    project_root: "<verified repository-compatible path>"
    host_identity: "<independently observed host>"
    independently_verified: true
  authorization:
    task_creation: granted
    title_adjustment: granted-for-declared-title
    github_mutation_scope: implicit-for-declared-request
  outcome: ready
```

For a blocked preflight, retain the observations that are available and record
the exact missing capability, authorization, destination proof, or recovery
evidence. Do not replace it with a fabricated task identity or a successful
status.

## Fail-closed rule

If the ChatGPT/Codex application, live task creation, independent stable task
identity observation, assigned-task authoritative bootstrap, or
monitoring/relay path is unavailable, the outcome is `blocked`. The skill must
return the smallest recovery input and stop before the affected role-owned
effect. It must not claim that a task is being monitored or completed until
the required live evidence is available.

For project identity, return setup guidance when the exact expected project is
absent from the refreshed live inventory. When that project remains present
but the assigned task's effective project identity is still missing after its
bounded self-read, block with `blocker: unsupported-runtime`: the current
runtime cannot prove the requested binding. Preserve the original task in both
cases. A replacement task is not a readback retry.

The same fail-closed rule applies when the exact resolved model and reasoning
cannot be actively requested. Never omit a required profile value to obtain a
task receipt and never treat a coincidentally matching inherited profile as a
valid task initialization.

`unsupported-runtime` means that the required request, stable task identity,
or authoritative assigned-task bootstrap capability is unavailable, or that
the exact task's values remain missing or unobservable. It does not describe a
successful readback of different effective values; that case is
`effective-profile-mismatch`. A bootstrap profile readback whose evidence
identity differs from the controller-observed assigned task is invalid for
that child: discard it and treat the exact child's readback as unavailable.

A difference between the task controller's profile and the assigned role's
requested profile is not a mismatch. Only the exact assigned task's
authoritatively self-observed profile participates in the comparison.

A missing title-request or title-adjustment capability alone is not a topology
blocker because a title is display metadata. Continue only after recording the
limitation for the handoff's mandatory title-reconciliation outcome; never
convert missing title evidence into successful verification.

Lost or ambiguous title-attempt evidence also never blocks otherwise valid
task work, but it forbids another adjustment. Read the current title,
preserve the stable task identity, and report the resulting title warning.
