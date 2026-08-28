---
node_id: intake
kind: action
purpose: resolve-source-route-repositories-authority-and-plan-scope
entry_conditions:
  - explicit-feature-planning-intent-source-set-or-revision-request-is-available
inputs:
  - user_intent
  - source_references
  - existing_plan_reference
outputs:
  - source_route
  - run_mode
  - normalized_source_set
  - affected_repositories
  - repository_and_source_evidence
  - existing_plan_evidence
  - publication_authority
  - bounded_plan_scope
transitions:
  - to: analysis
    when: sources-repositories-and-scope-are-resolved
  - to: blocked
    when: source-scope-or-required-repository-is-invalid-or-inaccessible
stop_if:
  - request-is-implementation-only
  - scope-is-unbounded
  - existing-source-revision-cannot-preserve-authoritative-identity
side_effects:
  - read
terminal_states: []
---

# Intake

Normalize the requested outcome and attributable source set. Resolve
`new-source` or `existing-source`, every affected repository identity, and
`publish` or explicitly requested `preview`. Publication remains the default;
do not infer preview from missing authority or dependencies.

Read each repository's applicable `AGENTS.md` hierarchy and verify the actual
repository and source identities needed for planning. These observations are
planning evidence, not task-target or saved-project gates. A multi-repository
request has peer repositories and does not acquire an artificial primary
repository from the planner task's application placement.

Before reading a hosted source, apply the shared
[G dependency preflight](../../../references/codex-dependency-preflight.md).
This is source routing inside Intake, not a separate workflow node.

When the source is an Idea handoff, read and validate the canonical
[idea-source.md](../../idea/references/idea-source.md) shape and exclusions.
Keep `source_route` as `new-source`, reload repository context, preserve its
open questions as clarification evidence, and derive all Feature Plan fields
independently. A typed handoff never supplies acceptance criteria, dependencies,
implementation design, or readiness.

For an existing-source request, rehydrate the complete current Plan Set and
every affected parent and child issue before analysis. Freeze their stable
identities, unaffected semantic content, dependency graph, metadata, and any
executor-owned progress as `existing_plan_evidence`. Reject a request that
would silently create a replacement Plan Set or mutate implementation-owned
state. For new-source work, record that evidence as not applicable.

Preserve explicit publication, preview, no-code, no-delegation, repository,
and downstream-handoff constraints in the normalized input.
