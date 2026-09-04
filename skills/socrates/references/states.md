# Socrates State Contract

This reference defines the state vocabulary used by `$socrates`. The workflow
registry and allowed transitions live in `SKILL.md`; do not add a workflow node
here without updating that registry and its Mermaid projection in the same
change.

Socrates persists no learner or workflow state. Workflow position, counters,
offer suppression, exercise selection, scaffolding, and assessments exist only
in the current conversation. Repository contents, diffs, test results, logs,
documentation, and explicit user replies are external evidence rather than
Socrates-owned state.

## Workflow nodes

| Node | Kind | Plain description |
| --- | --- | --- |
| `qualify` | Decision | Determine whether the activation is an explicit exercise request, an eligible implicit opportunity, or no exercise. |
| `offer` | Output | After any required primary-task handoff, emit one optional implicit offer; emit nothing after the offer. |
| `await-consent` | Wait | Wait for the user to accept, decline, stop, or ask what the proposed exercise covers. |
| `prepare` | Action | Resolve the objective, pattern, scaffold, and trustworthy evidence anchor. |
| `prompt` | Output | Emit exactly one learning task and no answer or hint. |
| `await-answer` | Wait | Wait for the learner's answer, help request, skip, stop, or objective change. |
| `evaluate` | Validation | Compare the learner's actual claims with current evidence. |
| `coach` | Action | Give evidence-linked feedback and either continue, change pattern, or close. |
| `reconcile` | Recovery | Refresh or replace evidence that is stale, conflicting, or initially insufficient for assessment. |
| `skipped` | Terminal | End without an exercise because the candidate was ineligible, duplicated, or suppressed. |
| `declined` | Terminal | End after the learner declines an implicit offer. |
| `complete` | Terminal | End after the learning objective closes or a requested direct answer is supplied. |
| `stopped` | Terminal | End because the learner skips, stops, or switches to another objective. |
| `blocked` | Terminal | End because a trustworthy evidence-backed exercise cannot be formed. |

`offer` must advance to `await-consent` before its response ends. `prompt` must
advance to `await-answer` before its response ends. Both waits continue only
after new user input; silence is not an event to fill with more content.

## Field-qualified states

| Owner | Allowed values | Class and lifetime | Meaning |
| --- | --- | --- | --- |
| `activation_source` | `explicit`, `implicit` | Derived run fact; transient | Distinguishes a user-requested exercise from a post-work candidate. |
| `offer_gate` | `open`, `suppressed-after-decline`, `suppressed-after-limit`, `suppressed-by-user` | Conversation control; transient | Controls implicit offers only. An explicit exercise request may start a new run despite suppression. |
| `evidence_status` | `ready`, `stale`, `conflicting`, `insufficient` | Derived evidence fact; transient | Records whether the selected anchor can support a fair assessment. |
| `exercise_pattern` | `predict-observe-reflect`, `design-compare`, `trace-path`, `debug-scenario`, `teach-back`, `retrieve-transfer` | Selected run field; transient | Chooses the exercise shape defined in `exercises.md`. |
| `scaffold_level` | `exact-anchor`, `area-anchor`, `self-locate` | Selected run field; transient | Controls how specifically the learner is directed to relevant evidence without revealing the answer. |
| `answer_assessment` | `accurate`, `partially-accurate`, `incorrect`, `stuck`, `uncheckable` | Derived response fact; transient | Describes only the learner's expressed answer relative to current evidence. |
| `allow_implicit_invocation` | `true` | Persisted skill metadata | Lets Socrates consider a post-work offer; it does not authorize starting an exercise without consent. |

The current objective, evidence anchors, learner response, offered milestone,
and `completed_exercise_count` are transient run data rather than additional
configuration or enum states. Keep the count in the inclusive range `0..2`.

## Terminal effects

| Terminal node | Counter effect | Offer-gate effect |
| --- | --- | --- |
| `skipped` | None | Preserve the current gate. |
| `declined` | None | Set `suppressed-after-decline`. |
| `complete` | Increment `completed_exercise_count`; cap at 2. | Set `suppressed-after-limit` when the count reaches 2; otherwise preserve the current gate. |
| `stopped` | None | Set `suppressed-by-user`. |
| `blocked` | None | Do not implicitly repeat the same topic; preserve the broader gate. |

Terminal nodes end the current exercise. A later explicit request begins a new
run at `qualify`; it does not mutate the prior terminal node.

## Evidence ownership

- Source files, diffs, tests, logs, and documentation are external evidence.
  Their existence is not proof that they are current or mutually consistent.
- Consent, decline, stop, skip, and answers come from explicit user turns. Do
  not infer them from silence, sentiment, or an earlier unrelated request.
- Socrates owns only its transient interpretation of that evidence. It never
  persists a learner model, schedule, score, milestone ledger, or mastery
  claim.
