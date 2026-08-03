---
node_id: intake
kind: action
purpose: normalize-feature-intent-into-one-bounded-candidate
entry_conditions:
  - explicit-feature-intent-or-rehydrated-maintenance-bundle-is-available
inputs:
  - user-intent
  - rehydrated-bundle
  - maintenance-evidence
outputs:
  - normalized-intent
  - entry_route
  - source_route
  - affected-repositories
  - repository-context
  - documentation-update-candidates
  - feature-scope
transitions:
  - to: clarification
    when: material-unknowns-remain
  - to: feature
    when: intent-is-bounded-and-sufficient
  - to: blocked
    when: scope-is-invalid-or-repository-identity-is-missing
stop_if:
  - request-is-implementation-only
  - scope-is-not-bounded
side_effects:
  - none
terminal_states: []
---

# Intake

Normalize a new request or rehydrate the maintenance evidence into one bounded
feature candidate. Preserve the desired outcome, non-goals, affected
repository set and path scopes, constraints, and observable success signals.

For maintenance, compare the external indication with the rehydrated Feature,
Task, and dependency state. Preserve stable identities and carry only a
specific, evidence-backed change into the canonical Feature and Task phases.
Unclear or contradictory maintenance intent transitions to blocked.

For every affected repository, start with its `AGENTS.md` and follow any
descendant `AGENTS.md` files that cover the requested paths. Let that
instruction hierarchy determine which documents and code must be read to
recover repository context. Record the sources and facts used. Record a
documentation-update candidate only when the loaded context or feature
requirements make one necessary; do not assume a particular documentation
system.

Resolve source route once:

- new-source drafts a new Feature definition;
- existing-source consumes one canonical Feature definition without silently
  rewriting its stable content.

If a material decision is missing, emit the unresolved question as a blocker
and transition to clarification. If the scope, repository identity, or
repository context cannot be made explicit, transition to blocked. A
multi-repository request carries one context record and one graph run per
repository; do not infer a shared local root.
