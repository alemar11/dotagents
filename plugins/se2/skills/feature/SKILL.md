---
name: feature
description: "Converge feature intent into repository-scoped Feature issues and complete vertical Task dependency graphs with explicit dependencies, parallel or serial execution waves, repository context from AGENTS.md hierarchy, and readiness evidence; never implement code."
---

# Feature Graph

## Purpose and invocation

Use this skill only for an explicit SE2 Feature-graph request. Accept either a
new feature request or an explicit Feature maintenance indication for an
existing bundle. For one repository, converge one bounded feature into:

- one durable Feature issue that contains the canonical Feature definition;
- a nonempty set of vertical Task issues attached to that Feature;
- an acyclic Task dependency graph whose edges represent real implementation
  prerequisites;
- a complete acceptance-coverage map from Feature criteria to Tasks;
- a terminal bundle report.

For a multi-repository feature, execute the same graph once per affected
repository. Produce one linked Feature issue per repository and one local Task
graph under each Feature. Link the repository-owned Features; Tasks and Task
dependencies remain repository-local. Do not create an artificial integration
issue merely to coordinate them.

Keep planning and implementation separate. This skill never edits repository
code, chooses implementation designs on behalf of the executor, schedules
workers, merges changes, or decides delivery completion.

## Task profile and application dependency

For a task-managed Feature run, load the skill-owned
[task-profile.md](references/task-profile.md). It requires one principal
planner role with the declared Sol/medium profile and no fallback. Pass that
complete profile to the shared [task-preflight.md](../../references/task-preflight.md)
before creating, resuming, or monitoring the planner task, then use
[task-handoff.md](../../references/task-handoff.md) for assignment and relay
evidence.

The profile's canonical emoji title is requested and read back as best-effort
display metadata for the planner task; title uncertainty never changes the
Feature graph or authorizes a duplicate task.

The planner must use the invoking session's exact saved local project and
local environment. `se2:feature` is planning-only, so its planner task must
not create or use a Git worktree, isolated checkout, or task fork. If the
destination cannot be independently verified, fail closed before creating,
resuming, or monitoring the planner task.

The application task is an execution envelope for the current Feature graph
run, not an additional Feature-graph node. The shared references own the live
capability, destination, identity, authorization, update-relay, and
reconciliation gates; this skill owns only the Feature profile.

Task creation permission and GitHub issue mutation permission remain separate.
The Feature graph may calculate its complete bundle without turning either
permission into a graph transition.

## Source route and terminal operation

Resolve `source_route` from Intake evidence:

- new-source: draft a new Feature definition from bounded intent;
- existing-source: consume one canonical existing Feature definition unchanged,
  or the complete linked Feature set for a multi-repository feature, unless the
  invocation explicitly supplies a separate semantic repair request.

Every graph node calculates transient artifacts. Only the `complete` terminal
node chooses the internal operation after the complete bundle is calculated:

- preview: retain the bundle as report data without external writes;
- publish: publish the same bundle to GitHub only when the invocation
  explicitly authorizes it, with read-after-write verification for every
  mutation.

These operations are not graph nodes, are not Mermaid branches, and are never
presented as the conceptual result. The conceptual result is always the
complete Feature-and-Task bundle.

Resolve `entry_route` as either `create` or `maintenance`. Maintenance is an
alternate entry into this same graph: it starts from an existing Feature issue,
existing Task issues and Task dependencies, plus an explicit external
indication; it rehydrates the current bundle and then enters the Feature node.
It does not create a second graph or bypass Feature definition, Task, or Task
dependency-graph validation.

Do not create a second Feature for an existing feature, infer repository identity
from the current task or filesystem proximity, or turn run-scoped publication
facts into durable project configuration.

## Repository context precondition

Before the graph is allowed to leave Intake or Maintenance, resolve the
affected repository set and load repository-scoped context. Start by reading `AGENTS.md` at each
repository root, then follow any `AGENTS.md` files in descendant directories
that cover the paths or systems in scope. From those instructions, determine
which documents and code must be read to recover the context needed for safe
planning. Do not assume a documentation system, filename, or directory beyond
what the repository's instruction hierarchy requires.

Record the sources read, the repository facts they establish, and any
documentation or instruction update that the context and feature requirements
actually make necessary. Do not edit those sources from this skill, and do not
invent missing context. An unresolved repository identity, contradictory
instruction, or missing context needed to establish safe ownership blocks the
graph.

For multi-repository work, keep one context record per repository and apply the
same graph contract independently to every repository run. Cross-repository
coordination is represented only by linked Feature issues and their
cross-repository dependencies; `dependency_ids` remain local to Tasks under one
Feature.

## Graph overview

~~~mermaid
flowchart TD
    start((Start)) --> intake["Intake"]
    start --> maintenance["Maintenance"]
    maintenance -->|bundle rehydrated| feature["Feature"]
    maintenance -->|conflict| blocked["Blocked"]
    intake -->|material unknowns| clarification["Clarification"]
    intake -->|intent sufficient| feature
    intake -->|invalid scope| blocked["Blocked"]
    clarification -->|resolved| feature
    clarification -->|unresolved| blocked
    feature -->|definition complete| tasks["Vertical Tasks"]
    feature -->|conflict or incomplete| blocked
    tasks -->|slices complete| task_dependency_graph["Task Dependency Graph"]
    tasks -->|incomplete| blocked
    task_dependency_graph -->|acyclic and covered| complete["Complete"]
    task_dependency_graph -->|invalid| blocked
~~~

Mermaid is the human-readable projection applied once per repository run. The
node registry and standardized headers are the structural contract. Never infer
a transition from Mermaid alone, and never add a context, linking, preview, or
publication node to this graph.

## Node registry

| node_id | file | kind | entry condition | transitions |
| --- | --- | --- | --- | --- |
| maintenance | steps/maintenance.md | action | existing Feature, Tasks, dependencies, and external indication | feature, blocked |
| intake | steps/intake.md | action | explicit Feature intent | clarification, feature, blocked |
| clarification | steps/clarification.md | decision | material unknowns remain | feature, blocked |
| feature | steps/feature.md | action | bounded intent or rehydrated Feature bundle | tasks, blocked |
| tasks | steps/tasks.md | action | Feature definition is stable | task-dependency-graph, blocked |
| task-dependency-graph | steps/task-dependency-graph.md | validation | Tasks have been derived | complete, blocked |
| complete | steps/complete.md | terminal | bundle and graph are calculated | none |
| blocked | steps/blocked.md | terminal | a required contract cannot be satisfied | none |

Only files under steps/ are local graph nodes. Templates are resources and
must not be added to the registry.

## Feature and Task contract

The Feature is the durable umbrella for one repository-owned member of one
bounded capability. Its Feature definition owns the outcome, non-goals,
repository and path scope, context evidence, links to peer Features,
acceptance criteria, safety constraints, required documentation updates, and
validation policy. A single-repository feature has exactly one Feature; a
multi-repository feature has one linked Feature per affected repository.

The Feature definition is the canonical contract. There is no separate Spec
entity in this plugin. When published, the Feature is a GitHub issue of type
Feature; that type is publication metadata and never carries the semantics.

Every Task must:

- reference exactly one Feature through the tracker's parent/sub-issue relation
  or a canonical issue reference;
- describe one independently valuable vertical outcome across all required
  layers;
- carry explicit scope, acceptance criteria, validation, safety constraints,
  and executor-facing context;
- use generated `dependency_ids` only for other Tasks of the same Feature and
  repository;
- identify the owning repository and the context evidence relevant to the
  slice;
- carry any required documentation update in its own scope or link it to the
  Feature-owned update;
- remain agent-ready only when its contract and graph position are complete.

When published, a Task is a GitHub issue of type Task. The type is metadata;
the Task content, Feature relation, and dependency graph remain authoritative.
Do not create Tasks that are only database, API, UI, test, documentation, or
tracker slices unless that layer is independently valuable and testable as an
enabling capability. Fold layer work into the first vertical consumer when it
does not have independent value.

The Feature, Task, and dependency contracts support both creation and
maintenance. Maintenance may retain, update, create, or remove relationships
only when the rehydrated bundle, canonical Feature definition review, and
explicit change indication justify the operation.

## Task dependency and execution contract

`dependency_ids` form a directed acyclic graph inside one Feature and one
repository run:

- no Task depends on itself;
- every dependency resolves to a Task in the same graph;
- an edge means a real implementation prerequisite, not a preferred order;
- reverse edges are derived, never stored;
- hosted issue numbers and cross-Feature references are not dependency IDs;
- cross-Feature or cross-repository prerequisites belong in the owning Feature
  links and the relevant Task context.

For a multi-repository feature, link repository-owned Features with globally
qualified issue references or URLs. Tasks and Task dependencies stay local to
their Feature; do not introduce a cross-repository integration issue.

Execution waves are derived from the graph and scope:

- Tasks with no unfinished incoming edges may run in parallel;
- a Task waits until every incoming dependency is proven complete;
- overlapping allowed paths may force serial execution even when the DAG has no
  edge;
- independent outcomes with disjoint safe scopes should remain parallel;
- do not add a scheduling option merely to force parallelism or serialism.

Report the topological waves, the reason for every serialized edge, and any
scope-overlap gate that prevents otherwise independent execution.

## Workflow rules

### Maintenance entry

Load steps/maintenance.md when the invocation starts from an existing Feature,
Tasks, Task dependencies, and an external change indication. Re-read the
authoritative current state, rehydrate the bundle, preserve stable identities,
and carry the indication into the Feature node as transient maintenance
evidence. Do not mutate during rehydration. Conflicts, missing references, or
an unclear indication transition to blocked.

### Intake

Read the explicit intent or rehydrated maintenance evidence, resolve
`entry_route` and `source_route`, identify the
affected repository set, and run the repository context precondition. Freeze
one feature boundary and one context record per affected repository. Stop when
the scope is implementation-only, unbounded, contradictory, or missing an
authorized repository identity.

### Clarification

Resolve only material unknowns that would change the parent outcome, scope,
ownership, acceptance criteria, or dependency graph. Ask or resolve one
blocking decision at a time. Preserve accepted assumptions separately from
confirmed evidence. Do not silently broaden the feature.

### Feature

Load steps/feature.md and templates/feature.md. Draft, review, or update one
repository-owned Feature definition and its Feature issue per affected
repository. On maintenance, review the canonical Feature definition against
the explicit indication and rehydrate stable content before proposing changes.
Require unique, individually provable acceptance criteria, explicit links to
peer Features, and an explicit failure policy for constrained validation. A
complete Feature definition must be stable enough to derive Tasks without
inventing requirements.

Resolve one durable Feature identity for each affected repository. For an
existing Feature, preserve stable identity and calculate only justified body
updates. For a new Feature, render the body from templates/feature.md and link
the Feature set after every identity is known. Stop on duplicates, stale
bodies, conflicting relationships, or an ambiguous Feature target. Every
Feature must exist or be proposed before Tasks are synthesized; no extra
integration issue is created merely to join Features.

### Tasks

Load steps/tasks.md and templates/task.md for each repository run. Decompose
uncovered Feature scope, harden candidate boundaries, and build or update
Tasks with one observable outcome each. Retain stable Task identities, create
only justified missing slices, and calculate removals only when the
maintenance indication and current state make them safe. Include every
required layer in each Task's safe path envelope, preserve the Feature
boundary, and record any documentation update required by repository context.

Compress redundant candidates before freezing generated IDs. Retain a Task
only when it has independent value, distinct acceptance and validation proof,
and a safe landing state once its real dependencies finish. Re-harden changed
unpublished Tasks after any graph repair.

### Task Dependency Graph

Load steps/task-dependency-graph.md for each repository run. Recalculate and
reconcile the desired Task dependency graph against current relationships, then
validate Feature criterion coverage, dependency ID resolution, acyclicity, path
overlap, cross-Feature boundaries, readiness, and the derived topological
waves. Withhold the bundle when any criterion lacks an owning Task or when an
edge encodes preference rather than necessity.

### Complete

Load steps/complete.md and templates/graph-report.md. Always calculate the
complete repository bundles, linked Features, Task attachments, issue state,
relationships, coverage, required documentation updates, and Task dependency
projection before deciding how to operate them.

In preview, retain that projection as report data without writing. In publish,
re-read the complete current state immediately before mutation, publish the
repository-owned Feature issues to GitHub, link the Feature set, publish and
attach every Task through the parent/sub-issue relation or canonical issue
reference, apply the authorized Feature/Task issue-type projection as
publication metadata only, create local Task dependency relationships, and
verify read-after-write state for every mutation. For maintenance, emit a separate
Feature-issue changelog comment for every significant change, covering the
reason, Feature definition changes, affected Tasks, and dependency changes;
verify that comment after publication. Inspect current state before any retry;
never replay an uncertain mutation blindly.

## Graph state and terminal reporting

Keep current_node_id, entry_route, run_mode, source_route, Feature identities,
Task identities, rehydrated maintenance evidence, artifacts, blockers,
transition evidence, and terminal state explicit and transient. Do not store
runtime state in Markdown files.

A complete report must contain:

- every repository-owned Feature issue reference and the shared feature
  identity;
- every Task issue reference, Feature attachment, vertical outcome, and scope;
- cross-repository Feature links;
- Task dependency edges, topological execution waves, and parallel or serial
  reasons;
- Feature-criterion-to-Task coverage;
- loaded repository-context sources and required documentation updates;
- readiness and issue-relation evidence;
- the calculated bundle and, only for publish, persistence verification;
- for maintenance, the lateral changelog plan or verified Feature comment;
- retained identities, no-op operations, or missing operations when applicable.

Terminal states:

- complete: the bundle is complete and the selected operational mode has the
  required evidence;
- blocked: the exact blocker, affected node, retained artifacts, and smallest
  recovery input are reported.
