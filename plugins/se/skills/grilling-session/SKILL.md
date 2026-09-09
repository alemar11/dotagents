---
name: grilling-session
description: "Refine a topic or handoff one question at a time when explicitly requested or composed by SE."
---

# Grilling Session

Follow the shared [execution scope](../../references/execution-scope.md) for
standalone and composed invocation.

## Purpose and boundary

Use `$se:grilling-session` to turn a topic, proposal, plan, or composed handoff into a
clearer decision-ready brief through a demanding but constructive interview.
Infer the topic from the invoking prompt or supplied handoff when it is clear;
ask the user to choose only when multiple materially different topics remain.

Grilling Session is conversational and read-only. It may inspect repository context,
source, documentation, and other read-only evidence, but it never edits project
files, persists the transcript, creates tasks, or delegates work. If the user
asks to preserve an accepted rule or decision, return it as a durable-knowledge
candidate for the caller or a separately authorized knowledge workflow. Do not
capture it during the interview.

Read [references/states.md](references/states.md) before interpreting workflow
or result state. Read the shared
[workflow-graph.md](../../references/workflow-graph.md) before using the
registry below.

## Context use

Start from the topic, conversation and caller evidence; no repository or
knowledge-management skill is required. Callers own context preparation and
subsequent work. Inspect read-only evidence when a question depends on a
checkable fact, reusing supplied findings unless new evidence challenges them.
Evidence grounds the interview but does not replace user intent. Disclose missing
evidence and continue unaffected questions; block only when responsible
questioning cannot continue.

## Interview contract

- Ask exactly one question per turn.
- Pair that question with one concrete recommended answer and a concise reason
  it is the best current default. End by asking the user to accept it or state
  what should change.
- Make the recommendation falsifiable and specific enough to correct. Mark it
  provisional when evidence is incomplete; never hide uncertainty or present
  an unsupported preference as repository fact.
- Ask the highest-leverage unanswered question first: desired outcome, user or
  actor, success boundary, invariant, non-goal, failure behavior, tradeoff, or
  evidence requirement.
- Prefer concrete scenarios, counterexamples, and forced tradeoffs over broad
  invitations such as "tell me more."
- Challenge contradictions, vague nouns, hidden assumptions, and solutions
  presented as requirements. Stay direct and constructive rather than
  adversarial or performative.
- Do not ask for facts available in the repository or supplied handoff.
- After each answer, update the working interpretation silently. Briefly expose
  a correction only when it changes the meaning of the next question.
- Continue until no material ambiguity remains, the user asks to stop, or the
  session is blocked. Never choose a fixed question count.
- Before declaring the brief refined, ask one final confirmation question that
  presents the compact interpretation and invites correction.

Return composed results in the invoking conversation.

## Workflow graph

The registry owns structural edges; Mermaid is its projection. Read
[transition conditions](references/states.md#transition-conditions) for the
canonical conditions governing these node contracts.

| node_id | kind | purpose | entry_conditions | inputs | outputs | transitions | stop_if | side_effects | terminal_states |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| context-read | action | Use supplied context and inspect relevant evidence when needed. | explicit invocation or authorized parent handoff | topic, conversation, or supplied handoff | available context and evidence limitations | frame, blocked | essential evidence is unavailable and responsible questioning cannot continue | read, transient | none |
| frame | decision | Infer the subject and select the highest-leverage ambiguity. | available context assessed | supplied brief and context evidence | working interpretation and next ambiguity | question, blocked | no coherent topic can be selected without unavailable user input | transient | none |
| question | action | Ask exactly one focused question with a recommended answer, then incorporate the user's response. | one material ambiguity or final confirmation remains | working interpretation and latest user answer | recommendation, concise rationale, and updated interpretation or stop request | question, confirm, reported, blocked | required user input cannot be obtained | transient | none |
| confirm | decision | Present the compact interpretation for final user confirmation. | no known material ambiguity remains | working interpretation | confirmation, correction, or stop request | question, complete, reported | none | transient | none |
| complete | terminal | Return the user-confirmed refined handoff. | user confirms the compact interpretation | confirmed brief and evidence | refined handoff | none | terminal | none | complete |
| reported | terminal | Return the best-supported handoff after the user stops questioning. | user asks to stop before confirmation | working interpretation and evidence | handoff with unconfirmed items | none | terminal | none | reported |
| blocked | terminal | Report why responsible questioning or synthesis cannot continue. | required dependency, context, or input is unavailable | retained evidence and blocker | blocker and smallest recovery input | none | terminal | none | blocked |

~~~mermaid
flowchart TD
    context-read --> frame --> question
    context-read --> blocked
    frame --> blocked
    question --> question
    question --> confirm
    question --> reported
    question --> blocked
    confirm --> question
    confirm --> complete
    confirm --> reported
~~~

## Refined handoff

On `complete`, return a compact Markdown handoff containing:

- objective and intended user outcome;
- confirmed scope, non-goals, constraints, and invariants;
- accepted decisions and important terminology;
- success and failure criteria;
- evidence or validation expectations;
- remaining assumptions, risks, and genuinely unresolved questions;
- durable-knowledge candidates, if any, clearly marked as not captured.

On `reported`, return the same shape using the best supported interpretation and
label every unconfirmed item. On `blocked`, return the exact blocker and the
smallest input needed to resume. Do not include the raw interview transcript.
