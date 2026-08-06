---
node_id: intake
kind: action
purpose: normalize-feature-intent-and-source-issue-set
entry_conditions:
  - explicit-feature-intent-or-source-issue-set-is-available
inputs:
  - user-intent
  - source-issues
  - idea-source
outputs:
  - normalized-intent
  - normalized-source-issue-set
  - entry_route
  - source_route
  - affected-repositories
  - repository-identities
  - scope-candidates
transitions:
  - to: analysis
    when: source-set-and-repository-identities-are-resolved
  - to: blocked
    when: scope-is-invalid-or-repository-identity-is-missing
stop_if:
  - request-is-implementation-only
  - scope-is-unbounded
  - source-set-is-empty
side_effects:
  - none
terminal_states: []
---

# Intake

Normalize the explicit intent and every supplied source issue into one
attributable source set. Preserve the desired outcome, source references,
non-goals, affected repositories, constraints, and observable success signals
without treating titles, numbering, or caller-proposed splits as durable
identities.

Multiple source issues may describe one outcome or several independently
deliverable outcomes. Retain their provenance and defer consolidation to the
Convergence node. A multi-repository source set carries one repository identity
per plan member; never infer identity from filesystem proximity or a display
title.

When an Idea source is supplied, keep it tentative. Preserve its open
questions and source identity, but derive every Feature Plan field
independently. Do not promote Idea wording into requirements without evidence.

Resolve entry_route as create or maintenance and source_route as new-source or
existing-source. Maintenance is selected only by an explicit request with an
existing published plan or linked plan set. It does not create a second plan
identity.

If the request is implementation-only, unbounded, contradictory, or missing an
authorized repository identity, retain the smallest recovery input and
transition to blocked. Do not create an application task or hosted issue from
an invalid intake.
