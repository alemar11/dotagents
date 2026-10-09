# Session Retrospective

Use this branch only when the user requests a coding-session retrospective.
It proposes improvements to the agent's working environment; ordinary task
completion does not trigger it. Use the specified session, or the current
conversation when none is named, within the selected repository.

## Evidence and diagnosis

Ground each candidate in observed friction, a failure, or missing information.
Read the relevant session evidence and current repository owner before drawing
a conclusion. This may include searching available local session logs, without
assuming a particular agent, storage path, or format. When the requested session
is unavailable, disclose that limit
and assess only the evidence actually available. Summarize evidence without
copying private transcripts, secrets, or raw logs into durable instructions.

Investigate only the categories supported by that evidence:

- Navigation: a hidden ownership boundary or missing conditional pointer that
  caused repeated searching or incorrect edits.
- Automation: a mechanical error an existing or proposed check could catch.
  Inspect the repository's check commands and their hook or CI wiring first;
  distinguish a missing check from an existing one that was skipped, broken,
  or outside the affected path's selection. Prefer repairing that gap to
  creating a duplicate check or a prose rule. Absence of a particular hook
  alone does not establish an enforcement gap.
- Guidance: a missing judgment rule, conflicting instructions, stale advice,
  or repetition that changed the agent's decisions. Preserve always-active
  invariants and the repository's existing review-rule owner.
- Tool use and information: repeated expensive calls, unusable output, or
  unavailable logs or documentation that prevented a sound decision. Name the
  needed information and least access required; do not provision access.

## Proposals and capture

Report consequential candidates first. For each, identify the observed
problem, supporting evidence, proposed owning surface or tool, and how the
change would prevent recurrence. Distinguish verified causes from hypotheses;
do not turn a single failure into a universal restriction. No worthwhile
candidate is a valid result.

A retrospective request authorizes this read-only assessment. Accepted lessons
with authority to save them use [durable-capture.md](durable-capture.md) and its
destination and verification rules; reuse authority already established in the
conversation. A mechanical fix to a script, hook, CI job, or tool is separate
implementation work, outside Learn's documentation boundary. Return its scope
and validation target to the caller without implementing it here.

Finish once the evidence-backed proposals and material limits are reported,
plus any explicitly authorized durable capture is verified. No report file,
new skill, global instruction edit, or recurring retrospective is implied.
