# AutoReview Fix Loop

Load after implementation has a scoped committed head with no unexplained
Git-visible changes.

`$autoreview` owns request construction, model execution, bounded invalid-output
repair, evidence lineage, result validation, and finding locations. Implement
Feature supplies the exact repository target, head, scope, and accepted prior
evidence; it does not copy AutoReview's schemas.

Journal each AutoReview phase with one `run-state operation begin` before the
owner launch, require `launch_authorized=true`, and use `operation finish`
after its validated result. Interruption or
ambiguous delivery becomes `unknown`; reconcile the original operation and
never launch another phase under a new key merely because output was lost.

Run the owner's normal full review, repair accepted in-scope findings, validate
and commit a new head, then use AutoReview's supported verification flow. Later
hosted findings use the owner's delta/composite evidence path. If every finding
is rejected with evidence, preserve the unchanged-head disposition.

AutoReview evidence is head- and scope-bound. A new head, changed merge base,
material target drift, or changed allowed paths invalidates affected evidence.
No AutoReview result grants provider mutation, merge, enqueue, deploy, Goal,
task, or worktree authority.
