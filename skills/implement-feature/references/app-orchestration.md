# App Orchestration

Root alone uses App task, title, message, archive, and Goal tools. Workers never
create or manage App tasks and never use Goal tools.

Journal each App mutation with `app-operation begin`. Launch only when it
returns `launch_authorized=true`. Then read the actual App receipt and stable
object state and call `app-operation finish`. A pending or `unknown` effect is
never relaunched under a new key; reconcile it by authoritative readback under
the same key. Typed state stores receipt/readback references and identity facts,
not message bodies or hashes.

## Goal And Worker Creation

After at least one assignment owns its Feature Spec and head-branch claim:

1. Create the root lifecycle Goal and read it back as active.
2. Set and read back the exact root title through a journaled `set-root-title`
   operation. For one assignment use exactly
   `👨🏻‍💻 Feature Orchestrator`. For two or more assignments use exactly
   `👨🏻‍💻 Multi-Feature Orchestrator (R/N)`, where `N` is the immutable total
   assignment count and `R` is the number currently recorded `ready`. Start at
   `0/N` and update the title only when `R` changes. Blocked, active, or waiting
   assignments do not increment it. The title is UI evidence only, never task
   identity or durable run state.
3. Keep Goal progress coarse: scheduling, worker count, blocked, or final
   verification. Do not mirror issue phases in state.
4. For each claimed, dependency-ready, path-disjoint assignment up to the limit
   of three, create one visible task with `environment=worktree` in the current
   App project. Resolve queued creation to one stable thread ID; never create a
   replacement.
5. Read the managed checkout, independently resolve its Git common directory,
   set the exact `🛠️ <Feature Spec title>`, and read the title back.
6. Send one full bootstrap that names the source ref, repository, branch,
   allowed paths, issue graph, acceptance, validation and budget, safety,
   delivery boundary, worker autonomy, reread points, tracker-proof contract,
   and required final evidence.
7. Finish `send-bootstrap` with the actual receipt and thread readback. That
   transition starts implementation authority. There is no baseline-only
   prompt, later GO, validation permission, or recovery permission.

The exact accepted bootstrap is recovered from the authoritative App receipt
and thread readback. After recovery, compare its stable Spec/issue sections to
the current durable sources. Fail closed if the exact baseline cannot be
recovered. Do not replace it with packet or message hashes.

## Scheduling And Monitoring

At most three workers may be live. Inside one root, Specs in one repository run
concurrently only when their current allowed paths are disjoint and no
dependency orders them. Missing path evidence conflicts. Different roots may
own different Specs and head branches in the same repository; Git, provider,
CI, and worker final verification expose any later integration conflict. A
PR-ready worker releases its own claim and frees a slot; dispatch the next
claimed, dependency-ready, non-overlapping Spec.

Use bounded authoritative task reads for coarse progress. Do not send prompts
that choose design, issue order, rewrites, tests, validation, review fixes, or
tracker judgments for a coherent worker. A follow-up message is appropriate only
to deliver recovered App state or authoritative durable-source change; journal
it and preserve worker autonomy.
