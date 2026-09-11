---
name: implement
description: "Implement and validate selected local work or a bounded workflow assignment, without PR publication."
---

# Implement

Implement exactly the selected spec, ticket, directly described work, or
caller-assigned repair batch. Read the main spec and detailed task contract when
provided; a spec is not required for a direct implementation or review fix.
Discussion of implementation does not itself select work. Publication and
independent review remain separate caller-owned actions.

## Assignment and execution

Standalone work uses the current repository and branch. A composed assignment
supplies the bounded contribution or selected findings, accepted requirements,
exact repository/worktree/branch/base and starting HEAD, relevant instructions,
and validation requirements. Verify the actual target before mutation; report
an unresolved mismatch to the owner. Preserve unrelated work and never add
unselected prerequisites or change requirements to make checks pass.

Implement creates no tasks and never operates claims. Its only delegation is
the optional UI designer below, with the same policy standalone or composed.
Preserve any separately established caller-owned budget.

Use test-driven development where practical, especially at pre-agreed seams.
Run checks covering the changed behavior and repository-required gates. Broaden
validation only for unresolved risks or failures.

## Optional UI design

For new screens, substantial redesigns, or unresolved visual and interaction
choices, consider one read-only designer subagent under
[designer role](references/designer.md). Skip routine component work, small fixes,
and work with an already precise design. Implementation invocation authorizes
this bounded helper when useful, subject to explicit caller constraints and
available capabilities. The executing worker owns its selection and result;
do not add a delivery-coordinator gate.

Use one helper with the role's brief, supplying the user outcome, relevant UI
paths and rendered views, design-system constraints, interaction states, and
expected proposal. Continue implementation work independent of pending design
choices where useful. Evaluate its proposal against the selected scope,
and resolve routine choices locally. Reuse that helper for bounded clarification;
do not fan out or invoke Implement recursively. Finish or stop it before candidate
handoff. If delegation is unavailable or fails, continue with local design
judgment and report the limitation. Reconcile an uncertain launch before replacing
it; optional design help does not block otherwise feasible work.

Implement owns the code and verifies the rendered UI in the browser or relevant
native interface, including responsive behavior and accessibility appropriate
to the change. A design proposal does not establish implementation quality;
report any unavailable visual verification.

## Review and handoff

Return the validated candidate to the caller. Independent review is a separate
workflow owned by the user or orchestrator; it is never launched by Implement.
Local checks and self-inspection do not satisfy a caller-required independent
review gate. This boundary is the same for standalone and composed work.

Commit only files required for the selected work to the verified target branch,
and only when the user or composed assignment authorizes a local commit.
Otherwise leave the validated changes in the worktree and report that state.
When the assignment includes later publication, use repository-relative paths,
verified repository identities, and portable validation evidence in new commit
messages. Keep machine paths and internal conversation details in the private
handoff. Report issues in existing messages without rewriting history.
Return the committed HEAD and base when a commit was authorized, otherwise the
uncommitted candidate state, plus changed scope, validation evidence, worktree
state, any reserved batch identity/count, and blockers. Become quiescent before
handoff so the owner can review a stable candidate. Preserve unrelated dirty
work and disclose it; a composed caller may require a clean isolated lane.

This skill ends at local implementation. A separately authorized push,
publication, hosted review, merge, deployment, or issue action belongs to its
owning workflow after this handoff; authorization for that later phase does not
bypass the caller's review gate.
