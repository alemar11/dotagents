# Visible App Worker

## Assignment

Create exactly one visible App task per selected executable Feature Spec. Each
assignment owns one repository, one App project/worktree, one target branch,
and one eventual PR. A Feature Spec naming several repositories is incompatible
with this runtime and returns `planning-required` before state.

Derive the immutable title as `🛠️ <exact authored Feature Spec title>`. The
hammer-and-wrench emoji is fixed; do not choose or infer another emoji.
The thread ID is identity; title is observed evidence. Inherit platform model
and thinking defaults unless the owner explicitly requested exact values.

## Authority

The worker owns implementation, validation, publication, review fixes, and its
final handoff inside the assigned managed worktree. Root owns claims, state,
the Goal, scheduling, sibling tasks, and final portfolio verification.

The worker must not create, fork, title, message, archive, or otherwise manage
App tasks; use Goal tools; implement in another checkout; create raw worktrees;
or merge, enqueue, deploy, release, or perform post-merge closure.

## Bootstrap Prompt

Send the exact:

- source ref and accepted source SHA-256;
- assignment ID and title;
- repository, App project, managed checkout, observed branch and baseline head;
- target branch and allowed paths;
- acceptance criteria and literal validation commands;
- integration gates and optional domain closeout;
- immutable manifest fingerprint;
- root-only authority boundary and successful handoff shape.

Start in baseline-only mode. Verify the assignment and checkout and run only
the baseline procedure from `baseline-validation.md`. Do not edit, commit,
publish, invoke review, or use task/Goal tools until root sends the explicit
message containing `implementation_authority=granted` and the matching baseline
head and scope fingerprint.

After that message, load and follow only the current phase reference supplied by
root. Stop on source, checkout, branch, path, authorization, or evidence drift.

## Reports

Report material transitions only: baseline, changed paths, current head,
validation, commit, PR, review, CI, mergeability, tracker/domain closeout,
blocker, and next action. With no material change, use at most one concise
liveness line per 60 seconds.

The successful worker result is `pull-request-ready-for-merge` with exact
thread, repository, branch, head, and canonical PR URL.
