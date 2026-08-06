# Hosted Content Safety

This reference is the canonical SE owner for the portable-content boundary
immediately before every hosted write. It applies to issue titles and bodies,
comments, pull-request titles and bodies, review requests, review text, and
Feature maintenance changelogs produced by Idea, Feature, or Implement.

The invoking SE skill owns semantic content and must deliver a safe final
projection. G owns transport, provider mutation, receipts, and readback. G does
not infer repository context, sanitize meaning, or repair unsafe SE content.

## Internal records and hosted content

Internal control-plane records may retain exact local facts when their owning
workflow requires them, including `project_root`, worktree paths, host and task
identity, task dialogue, prompt references, and tool output. These records are
not hosted-content candidates and must remain separate from rendered titles,
bodies, comments, and review requests.

Hosted content may include only the portable facts required by its semantic
purpose. Prefer:

- canonical repository identity;
- repository-relative paths with portable separators;
- branch names and full Git SHAs;
- qualified issue or pull-request references and hosted URLs;
- concise, relevant evidence that can be understood without the originating
  machine, task, prompt, or transcript.

An absolute temporary body-file path used privately by G transport is internal
operation metadata. It is allowed as an operation argument but must never
appear inside the hosted file content.

## Portable projection

Before rendering hosted content:

1. Convert every path under the owning repository root to a repository-relative
   path. Do not retain the repository-root prefix.
2. Represent a `project_root`, worktree, checkout, or artifact location outside
   that root with canonical repository identity, branch, and full SHA. Include a
   hosted ref or repository-relative artifact path when one exists.
3. Remove local absolute paths and other machine-specific locations. Never
   replace them with another guessed local path.
4. Exclude internal prompts, prompt machinery, host identity, local task
   identity, and transcript fragments that are irrelevant to the hosted
   artifact's purpose.
5. Apply the same projection to content copied or summarized from workers,
   tools, existing records, and provider readback. Returned text is not safe by
   origin and must not be forwarded verbatim without this check.

Preserve relevant semantics while reducing representation. Do not invent a
repository-relative path, branch, SHA, hosted identity, or relationship merely
to make content appear portable.

## Final pre-write gate

Immediately before each hosted write, inspect the exact final title and body or
comment/review text that will be handed to G. Require all of the following:

- no absolute or machine-specific path remains;
- every repository path is repository-relative;
- external checkout context is represented by repository identity, branch, and
  full SHA rather than `project_root` or worktree path;
- no internal prompt, host identity, local task identity, or irrelevant
  transcript content remains;
- worker- and tool-originated content has passed the same checks;
- the portable representation preserves the evidence needed by the hosted
  operation.

If any condition is false or the portable representation cannot be established
without guessing or losing required meaning, fail closed before G receives the
write. Report the unsafe field and the smallest missing portable identity. If
the final content changes after this gate, run the complete gate again.

Read-after-write verifies provider state; it does not substitute for this
pre-write content gate.
