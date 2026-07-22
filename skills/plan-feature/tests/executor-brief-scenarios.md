# Executor Brief Contract Scenarios

These scenarios exercise behavior, not exact document phrasing or line counts.

## Scenario: Replace The Recommended Design Safely

Given an agent-ready issue recommends one internal design,
when the implementing Codex task finds a simpler or safer design that preserves
the accepted goal, Non-Goals, scope, dependencies, safety constraints,
acceptance criteria, and material validation constraints,
then it may record and implement the replacement without replanning.

## Scenario: Preserve Checkbox-Only Progress

Given the current Feature Spec or issue differs from its planning-time brief
only because proven acceptance checkbox markers changed,
when convergence or recovery rereads the artifact,
then it retains the artifact and preserves the checkbox state while still
protecting criterion text, count, and order.

## Scenario: Add Or Substitute Equivalent Tests

Given the stable validation outcome and material constraints remain satisfied,
when the implementing Codex task adds coverage or substitutes equivalent proof,
then it records that proof as mutable execution evidence and continues.

## Scenario: Block On Stable Semantic Drift

Given the worker rereads the current Spec and issue set before an issue, after
recovery, or before final verification,
when criterion wording, criterion count or order, allowed paths, dependencies,
safety constraints, attempt budgets, required terminal outcome, or the delivery
type derived from normal App flow versus `non_app_delivery_target` changed,
then it blocks declaratively and does not ask the user from the worker task.

## Scenario: Require A Material-Validation Failure Policy

Given validation is paid, external, non-repeatable, or otherwise constrained,
when its brief does not state the attempt or retry budget, allowed fallback,
evidence to retain, and required terminal outcome,
then Plan Feature withholds `ready-for-agent`.

## Scenario: Enforce Checkbox Ownership

Given an implementing Codex task has current-head proof,
when it updates acceptance state,
then it rereads the GitHub or local artifact, updates only its issue checkboxes,
updates parent Spec criteria only after Spec-level proof, and restores unchecked
state if later evidence invalidates the proof; root coordination never edits or
judges an individual criterion.
