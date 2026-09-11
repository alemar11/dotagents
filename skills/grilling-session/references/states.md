# Grilling Session State Reference

This reference is the canonical inventory of state used by `$grilling-session`.
All state is transient in the invoking conversation. Grilling Session has no persisted
checkpoint, run ledger, write preference, or repository-owned state.

## Workflow nodes

| Node | Kind | Plain description |
| --- | --- | --- |
| `context-read` | Action | Use supplied context and inspect relevant evidence only when needed. |
| `frame` | Decision | Infer the subject and identify the highest-value ambiguity. |
| `question` | Action | Ask exactly one focused question with a concrete recommended answer and incorporate the user's response. |
| `confirm` | Decision | Present the compact interpretation as one final confirmation question. |
| `complete` | Terminal | Return the user-confirmed refined handoff. |
| `reported` | Terminal | Return the best-supported handoff after the user ends questioning. |
| `blocked` | Terminal | Report why responsible questioning or synthesis cannot continue. |

## Result state

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `grilling_outcome` | `refined`, `user-stopped`, `blocked` | Reports whether the user confirmed the brief, ended questioning early, or the workflow could not continue. |

`grilling_outcome=refined` maps to workflow node `complete`.
`grilling_outcome=user-stopped` maps to `reported` and preserves unconfirmed
items. `grilling_outcome=blocked` maps to `blocked` and names the smallest
recovery input.

The topic, questions, answers, working interpretation, refined handoff,
repository evidence, and durable-knowledge candidates are run data, not state
fields. A durable-knowledge candidate is not evidence that it was captured.

## Transition conditions

This matrix owns every edge condition for the [entrypoint registry](../SKILL.md#workflow-graph).

| from | to | when |
| --- | --- | --- |
| context-read | frame | available context supports framing the topic, including topics without a repository. |
| context-read | blocked | essential evidence is unavailable and no responsible question can proceed. |
| frame | question | one coherent topic and its next material ambiguity are known. |
| frame | blocked | a coherent topic cannot be selected and user input is unavailable. |
| question | question | the latest answer leaves another material ambiguity. |
| question | confirm | no known material ambiguity remains. |
| question | reported | the user asks to stop. |
| question | blocked | required user input cannot be obtained. |
| confirm | question | the user corrects or extends the compact interpretation. |
| confirm | complete | the user confirms the compact interpretation. |
| confirm | reported | the user asks to stop without confirming. |
