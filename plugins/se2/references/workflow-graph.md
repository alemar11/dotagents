# SE2 Workflow Graph Contract

This reference owns the shared structural vocabulary for graph-first SE2
workflows. It applies to Learn, Idea, Feature, Implement, and Audit without turning
every skill into a Feature or Task graph.

The existing workflow-contract.md remains the canonical owner of the Idea
marker and hosted Idea shape. This reference owns workflow structure only.
Feature still owns its Feature/Task semantics; Learn, Idea, Implement, and Audit own
their skill-specific registries and branch details.

## Graph model

A workflow graph describes control state and authority boundaries for one skill
run. It is distinct from the Feature Task DAG:

- a workflow node describes what phase the skill is in;
- a Task node describes an independently valuable implementation outcome;
- a workflow graph may contain decisions, validations, actions, and terminal
  outcomes;
- a Feature Task DAG may contain only implementation Tasks and real
  prerequisite edges.

Each graph registry declares the following fields:

| Field | Requirement |
| --- | --- |
| node_id | Unique lower-kebab identifier within the skill graph. |
| kind | One of action, decision, validation, or terminal. |
| purpose | Observable responsibility of the node. |
| entry_conditions | Evidence required before entering the node. |
| inputs | Caller or prior-node data consumed by the node. |
| outputs | Transient artifacts produced for later nodes. |
| transitions | A list of target node IDs. Conditions belong to the owning node contract or its canonical transition-condition matrix. |
| stop_if | Conditions that stop the run at this node. |
| side_effects | Read, transient, durable, hosted, or none. |
| terminal_states | Empty for non-terminal nodes; the terminal state for terminal nodes. |

The exact field shape may remain Markdown-owned. Do not add runtime
configuration merely to persist a graph run.

## Registry and Mermaid rules

- The skill-owned registry is the structural source of truth.
- Every transition target must be registered in the same graph.
- Every local node must be reachable from an entry route or be explicitly
  declared as a terminal outcome.
- Mermaid is a maintained projection of the registry, never an independent
  source of edges.
- Mermaid node IDs, registry IDs, and transition targets use the same
  lower-kebab spelling.
- Entry-route labels and internal execution envelopes are not graph nodes unless
  the owning skill explicitly registers them.
- A terminal node has no outgoing transitions.

## Transition conditions

Keep the `transitions` field structural: it lists target node IDs and nothing
else. When a registry needs branch conditions, define them in one canonical
Markdown surface owned by the skill:

- a transition-condition matrix in the same `SKILL.md` for a table-owned
  registry;
- the standard node header for Feature step contracts; or
- a routed node reference explicitly assigned by the skill's ownership map.

The owning skill must make condition ownership explicit and cover exactly the
declared edges. A routed reference may own the conditions for the node
contracts it governs. Do not encode conditions as free prose inside the target
list, move outgoing conditions into `entry_conditions`, or treat Mermaid labels
as the source of truth. Explanatory prose may clarify a condition but must not
add an unregistered edge.

Feature keeps its existing step files and registry as its local source of
truth. Learn, Idea, Implement, and Audit keep their registries in their SKILL.md files
while branch-specific details remain in routed references.

## Common terminal meanings

- complete: the requested workflow bundle was fully calculated or verified.
- reported: a read-only or non-durable result was returned.
- deferred: the run is coherent but awaits a required user decision,
  selection, or confirmation.
- blocked: a required contract, evidence, authority, dependency, or
  reconciliation result is unavailable.

Each skill declares the subset it supports. Feature retains its existing
complete and blocked terminal contract. Learn uses all four meanings. Idea
uses reported, deferred, complete, and blocked.
Implement uses complete, deferred, and blocked.
Audit uses reported and blocked.

## Authority and side effects

Preview branches declared local-only must not inspect provider or tracker
hosted state. A read-only branch may inspect external state only when its owning
skill explicitly requires observational reads, as Audit does for application
sessions, and must never mutate that state. A durable or hosted side effect
requires an explicit authority decision and the owning publication workflow's
availability gate. Ambiguous external results must transition to reconciliation
before any retry.

The graph records authority and side effects as run facts. It must not turn
caller-owned publication choices, task state, or provider availability into
durable configuration.

## Cross-skill handoffs

A handoff is a typed transient artifact, not an implicit runtime invocation or
a graph edge between skills. The receiving skill must validate the handoff,
reload its own repository context, and derive its own planning fields.

The Idea-to-Feature handoff is owned by
skills/idea/references/idea-source.md. It preserves tentative source evidence
and open questions while excluding Feature requirements, acceptance criteria,
Tasks, dependencies, implementation plans, and readiness claims.

## Validation

For every changed graph, perform read-only checks for:

- front matter and metadata validity;
- registry/projection reconciliation;
- registered transition targets;
- transition-condition coverage for every declared edge;
- terminal reachability and absence of outgoing terminal edges;
- acyclicity where the owning graph requires it;
- local reference integrity;
- prohibited provider, tracker, task, or worker behavior;
- clean whitespace with git diff --check.

Markdown-owned graphs do not require a new executable validator unless a
shipped runtime invariant proves that static validation is insufficient.
