# Tracker Checklists

The worker, not root, owns acceptance judgment and tracker mutation for its
Feature Spec. Before each issue, after recovery, and before final verification,
read the current Feature Spec and complete issue set from GitHub or local
Markdown. Compare their stable sections directly; do not compare a stored
packet, checksum, or text hash.

For each issue:

1. Implement and validate the current accepted contract.
2. Bind proof to the current Git head and, only for `github-pr`, provider
   observation.
3. Check an issue criterion only after that current-head proof exists.
4. Read the authoritative issue again and require the checkbox change to be
   visible.
5. If later work invalidates the proof, uncheck it immediately and read it back.

Update parent Feature Spec criteria only after the complete Spec-level behavior
is proven. Read the parent again after every change. GitHub mutations go through
the current GitStack issue workflow; local Markdown changes stay inside the
worker's assigned worktree, are committed with the implementation, and receive
the same post-change validation and review.

For local Markdown, moving an issue into `issues/done/` is the completion
signal. Preserve its existing canonical `workflow_state`; never write
`workflow_state: done` or invent another completion state.

Recovery repeats the same read-before-write and read-after-write sequence.
Never infer success from an earlier response, stale checkbox, worker summary,
or root opinion. Root must not edit, check, uncheck, reinterpret, or adjudicate
criteria. It only verifies that the authoritative final tracker and current-head
evidence agree before the delivery-specific closeout. Local Markdown moves and
checkbox changes must be committed on the declared delivery branch.
