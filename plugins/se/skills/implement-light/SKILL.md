---
name: implement-light
description: "Use when the user asks to implement a selected local spec, ticket, issue, or directly described unit of work without SE orchestration, repository claims, pull-request publication, or deployment."
---

# Implement Light

Implement exactly the user-selected spec, ticket, or directly described unit of
work in the current repository.

Use this for an actual implementation request with selected work. Route exact
published SE parent Feature delivery to `se:implement`; do not select this
skill merely because the word "implement" appears in discussion or another
skill's instructions.

Use test-driven development where practical, especially at pre-agreed seams.

Run targeted validation during implementation and the appropriate full
validation suite once before completion.

Request an independent code review of the completed change where one is
available.

Commit only the files required for the selected work to the current branch.
Preserve unrelated work, and do not push, publish a pull request, merge,
deploy, or close issues unless the caller explicitly authorizes that next
step.
