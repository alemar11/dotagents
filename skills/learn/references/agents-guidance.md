# Writing and Maintaining AGENTS.md

Use this reference when creating, updating, reviewing, or refactoring agent
instructions, including rules captured through another Learn branch. Apply it
to the selected instruction chain; size measurement is optional unless the
user asks for compaction or a chain-size audit.

## Scope and evidence

Read the applicable ancestor instructions and the target file, reusing current
conversation evidence. Inspect code, commands, or context only to establish the
rules being changed. A small rule edit does not require a repository map or
Project Context bootstrap. Create a local file only for distinct instructions
that need to apply to that path; preserve inherited rules without copying them.

For each candidate instruction, establish the decision it changes, the scope
where it applies, and its evidence or accepted user preference. Keep concrete
ownership, non-obvious constraints, supported commands, authorization boundaries,
and completion requirements. Remove obsolete workarounds, repeated rules, and
generic coaching that adds no repository knowledge. Do not convert one failed
run into a universal restriction without evidence that the constraint persists.

## Write for the decision

- Put a condition before a conditional instruction. For example: “For schema
  changes, consult the migration guide for rollout compatibility.” Avoid
  requiring unrelated documents before every edit.
- Keep rules needed throughout the scope in `AGENTS.md`. Route substantial
  task-specific procedures to their existing owner with a relative link and a
  clear read condition. Add an indexed context topic only when needed; a short,
  self-contained rule needs no new document or routing layer.
- State the invariant and the reason for a fragile ordering requirement.
  Let the agent choose ordinary investigation and implementation steps.
- Express permission in terms of actions and targets. Reuse authorization
  already given in the conversation; an explicit request to update or refactor
  instructions authorizes those local edits. Ask only for an unresolved
  decision that materially changes scope, meaning, or consequences.
- Describe completion with observable evidence and a stopping point. Identify
  repository-specific checks and what they prove. Do not mandate repeated full
  suites, new tests for prose, or further checks after relevant proof passes
  without a new failure, change, or unresolved risk.
- When documenting a safe local workflow, establish the actual isolation and
  access properties before saying its steps may run without further approval.
  Keep external writes and other consequential actions within the user's scope.
- Account for the models that actually use the repository. Preserve operational
  facts shared by all of them; add model-specific guidance only for an observed
  need. A model upgrade does not invalidate a real permission or data constraint.

## Update and refactor

For a new file, write only evidenced rules and useful conditional pointers; no
placeholder sections are required. For an update, reconcile the new instruction
with existing rules and accepted user intent. Resolve a superseded rule directly
when the request establishes its replacement; ask about a conflict only when
the intended behavior remains unclear, and continue unaffected authorized work.

For a refactor, distinguish redundant text from distinct exceptions and
requirements. Preserve scope, precedence, ownership, and downstream contracts.
Move detail together with its links and indexes; verify the new owner before
removing the old copy. Use [compaction](agents-compaction.md) only when chain
measurement or substantial context extraction is part of the request.

Review-only work returns concrete proposed edits. Authorized edits continue
through application and verification without a second approval checkpoint.
Read back the changed chain, resolve links, and inspect the diff for lost
constraints, contradictions, and accidental scope expansion. Check a few
representative requests, including a small edit and an already-authorized
operation. Report changed rules and material limits concisely; use runtime
experiments only when a meaningful behavioral uncertainty remains.
