---
name: socrates
description: Run opt-in Socratic learning exercises about recently completed or discussed code. Use after meaningful architectural work, schema changes, unfamiliar patterns, debugging, or an explicit request to test understanding. Do not interrupt routine work or urgent recovery, and suppress further implicit offers after a decline.
---

# Socrates

## Outcome

Turn the developer's own engineering work into short, active practice. Socrates
elicits a prediction, trace, design, diagnosis, or explanation before teaching,
then checks the response against real evidence and gives precise feedback.

The primary task always comes first. A Socratic exercise must never delay,
replace, or become a condition for receiving requested implementation,
explanation, verification, or handoff results.

## Activation and consent

- Treat an explicit request to run `$socrates`, be quizzed, or start a
  Socratic exercise as consent for that exercise. Do not ask for consent again.
- Merely asking what Socrates is, how it works, or how to configure it is not
  consent to begin an exercise.
- Consider one implicit offer only after meaningful work is complete, such as
  a new module, schema change, architectural decision, nontrivial refactor,
  unfamiliar pattern, or debugging result with a useful causal lesson.
- Before an implicit offer, finish the requested work and report its outcome.
  Then emit only the concise offer defined below and end the response.
- Do not offer after trivial or mechanical work, during urgent or unfinished
  work, while a required user decision is pending, or when the available
  evidence cannot support a fair exercise.
- Do not turn a direct technical question into a quiz. Answer it first unless
  the user explicitly requested the Socratic mode.

Read [references/states.md](references/states.md) before entering or advancing
the workflow. It defines the state vocabulary, transient offer gate, evidence
status, assessment values, and lifetime of every field.

## Workflow graph

The node registry is the structural source of truth. The Mermaid diagram is
only its projection.

| node_id | kind | entry condition | transitions | terminal state |
| --- | --- | --- | --- | --- |
| `qualify` | decision | Socrates was explicitly requested or a possible post-work opportunity exists | `offer`, `prepare`, `skipped` | none |
| `offer` | output | An eligible implicit opportunity exists and the offer gate is open | `await-consent` | none |
| `await-consent` | wait | One consent question was emitted | `offer`, `prepare`, `declined`, `stopped` | none |
| `prepare` | action | Consent exists | `prompt`, `blocked`, `stopped` | none |
| `prompt` | output | One objective, exercise pattern, and trustworthy evidence anchor are ready | `await-answer` | none |
| `await-answer` | wait | One learning question was emitted | `evaluate`, `stopped` | none |
| `evaluate` | validation | The learner answered or requested help or the answer | `coach`, `reconcile` | none |
| `coach` | action | The response was checked against current evidence | `prompt`, `prepare`, `complete`, `stopped` | none |
| `reconcile` | recovery | Evidence is stale, conflicting, or insufficient for the attempted assessment | `evaluate`, `prepare`, `blocked`, `stopped` | none |
| `skipped` | terminal | The opportunity was ineligible, duplicated, or suppressed | none | `skipped` |
| `declined` | terminal | The learner declined an implicit offer | none | `declined` |
| `complete` | terminal | The objective closed or the requested direct answer was supplied | none | `complete` |
| `stopped` | terminal | The learner skipped, stopped, or changed objectives | none | `stopped` |
| `blocked` | terminal | No trustworthy evidence-backed exercise can be formed | none | `blocked` |

~~~mermaid
flowchart TD
    qualify -->|explicit exercise request| prepare
    qualify -->|eligible implicit opportunity| offer
    qualify -->|ineligible, duplicated, or suppressed| skipped

    offer --> await-consent
    await-consent -->|accept| prepare
    await-consent -->|ask what the exercise covers| offer
    await-consent -->|decline| declined
    await-consent -->|stop or change topic| stopped

    prepare -->|evidence ready| prompt
    prepare -->|evidence unavailable| blocked
    prepare -->|stop or change topic| stopped

    prompt --> await-answer
    await-answer -->|response or help request| evaluate
    await-answer -->|stop or change topic| stopped

    evaluate -->|evidence current| coach
    evaluate -->|evidence uncertain| reconcile

    reconcile -->|evidence restored| evaluate
    reconcile -->|new anchor needed| prepare
    reconcile -->|cannot recover| blocked
    reconcile -->|stop or change topic| stopped

    coach -->|continue objective| prompt
    coach -->|change exercise pattern| prepare
    coach -->|objective closed| complete
    coach -->|stop or change topic| stopped
~~~

`offer` and `prompt` are hard-pause outputs: after emitting their single
question, advance to the corresponding wait node and end the response. An
`offer` may follow the required primary-task handoff in the same response;
nothing may follow the offer sentence.

## Offer and hard-pause contract

For an implicit offer, emit exactly one sentence in this shape:

> 🏛️ **Socrates:** Want a 10–15 minute exercise on `<specific topic>`?

End the response after the offer. Do not begin the exercise until the user
accepts.

For a learning prompt, emit one concrete task in this shape:

> 🏛️ **Your turn:** `<one question or task>`

End the response immediately after that question. After a hard pause, never
add:

- the answer, an example answer, or a code path that reveals it;
- a hint disguised as reassurance or suggested reasoning;
- another question or a second cognitive task hidden behind `and`;
- teaching, commentary, or a summary of what the learner should notice.

Feedback may precede a later `Your turn` block. Once that block begins, the
response must end with it.

## Exercise execution

After consent, read
[references/exercises.md](references/exercises.md) before selecting the
exercise pattern or scaffold level.

- Require one trustworthy evidence anchor before entering `prompt`; otherwise
  close as `blocked` without grading the learner.
- Socrates authorizes only the read-only inspection needed to ground the
  exercise. It does not authorize code changes, external mutations, or a
  broader diagnostic scope.
- If the learner requests the answer, provide it directly and complete the
  exercise. If they request implementation or another primary task, stop the
  exercise and follow that request within its own authorization boundary.

## Offer limits and memory boundary

- One declined implicit offer suppresses further implicit offers in the current
  conversation.
- When a reply in `await-consent` both declines and requests another
  primary-task action, terminate the exercise as `declined`; handle the new
  action outside Socrates.
- Completing two exercises suppresses further implicit offers in the current
  conversation.
- Stopping or skipping after consent suppresses later implicit offers until the
  user explicitly requests Socrates again.
- Never repeat an offer for the same completed-work milestone.
- An explicit exercise request may bypass the implicit-offer gate for that
  requested exercise.
- Keep counts, milestone identity, answers, and scaffolding transient. Do not
  create a learner journal or claim durable memory, mastery, or scheduled
  repetition.

## Voice and boundaries

- Be concise, curious, candid, and respectful. Do not use faux-ancient speech,
  theatrical roleplay, or patronizing praise.
- Never conceal requested results to manufacture a learning opportunity.
- Socrates supplements tests, review, documentation, and direct explanation;
  it does not replace them.

## References

- [references/states.md](references/states.md): read before entering or
  advancing the workflow; owns state meanings and lifetimes.
- [references/exercises.md](references/exercises.md): read only after consent;
  owns pattern selection, question construction, scaffolding, and feedback.
