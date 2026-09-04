# Socratic Exercise Patterns

Read this reference only after consent exists and the workflow is in `prepare`.
Select one pattern that serves one narrow learning objective. Pattern names,
scaffold levels, and assessment values are canonical in `states.md`.

## Pattern selection

| Pattern | Use when | First learning task |
| --- | --- | --- |
| `predict-observe-reflect` | A concrete input or event has a checkable outcome. | Predict the outcome before examining or running the observation. |
| `design-compare` | A design choice or refactor has meaningful alternatives. | Sketch one approach before comparing it with the implemented constraints. |
| `trace-path` | Understanding depends on control flow, data flow, ownership, or lifecycle. | Trace one concrete value or event to the next decision point. |
| `debug-scenario` | An edge case can expose a fragile mental model. | Diagnose the failure mechanism before proposing a repair. |
| `teach-back` | The goal is consolidation or onboarding-level explanation. | Explain one component's responsibility and causal behavior in the learner's own words. |
| `retrieve-transfer` | Prior learning is actually available in conversation context, or a known pattern should transfer to a new case. | Retrieve the earlier idea without hints, or apply it to one different but comparable scenario. |

Do not claim to remember a prior lesson unless the current conversation or an
authoritative project artifact establishes it. When no such evidence exists,
use another pattern.

## Question construction

A strong prompt:

- names a concrete scenario, value, or decision point;
- asks for one cognitive act: predict, locate, trace, choose, diagnose, or
  explain;
- can be assessed from evidence already identified during `prepare`;
- reveals no answer through wording, file ordering, quoted code, or suggested
  reasoning;
- is narrow enough to answer in a few sentences or one small sketch.

Avoid generic recall such as “What does this module do?” Prefer a discriminating
scenario such as “Two requests miss this cache before either write completes.
Which call reaches the provider next?” The example is illustrative, not a claim
about the user's code.

Ask one task per hard pause. Split “what happens, why, and how would you fix it?”
across separate turns.

## Evidence-first setup

Before asking, identify:

1. the exact concept the learner should demonstrate;
2. the smallest source, diff, test, log, or decision record that resolves it;
3. the observation that would make an answer accurate, partial, or incorrect;
4. whether the scenario is observed or hypothetical.

Prefer directing the learner into the real repository when navigation itself is
useful. Show code directly only when the relevant fragment is tiny, unfamiliar
syntax is the lesson, repository navigation would be needless friction, or the
learner explicitly asks for it.

For `debug-scenario`, label the scenario `hypothetical` unless an actual defect
has been independently established. Never turn a plausible edge case into a
claim that the project is broken.

## Adaptive scaffolding

Start at the least specific level that remains fair:

| Scaffold | Guidance |
| --- | --- |
| `self-locate` | Ask where the learner would look or which boundary owns the behavior. |
| `area-anchor` | Name the component, subsystem, or relevant test area. |
| `exact-anchor` | Name the file and symbol, or a narrow line neighborhood when stable. |

Increase specificity when the learner is stuck; decrease it after they locate
and explain evidence reliably. Scaffolding changes where to look, not what to
answer. Never smuggle the solution into an anchor or encouragement.

## Assessment and feedback

Assess the expressed answer, not tone or confidence:

- `accurate`: identify the exact supported claim and decisive evidence. Deepen
  the same objective only when a causal or transfer question adds value.
- `partially-accurate`: preserve the correct part, name the missing or mistaken
  branch, and ask one narrower question if useful.
- `incorrect`: state that the prediction does not match the evidence, show the
  decisive contradiction, and explore the specific mental-model gap without
  shaming.
- `stuck`: acknowledge the block, move to a more specific scaffold, and ask a
  simpler question that still requires generation.
- `uncheckable`: do not grade. Move to `reconcile`, obtain a trustworthy anchor,
  or close as `blocked`.

Do not credit the learner with a reason they did not state. A correct predicted
outcome with unsupported reasoning is at most partially accurate on a causal
objective.

Feedback should be compact: assessment, decisive evidence, and the smallest
useful correction. If another prompt follows, end the response with the
hard-pause block from `SKILL.md`.

## Progression and closeout

- Keep one objective active across the loop. Change patterns only when the same
  objective benefits from a different cognitive act.
- Use reflection to surface what changed in the learner's model, not to demand
  praise for the implementation.
- Use transfer only after the concrete case is understood.
- Stop when the learner demonstrates the objective, requests the answer,
  reaches the time boundary, or chooses to stop.
- Target 10-15 minutes unless the learner explicitly asks to continue.
- Close with one concise statement of the established model and any remaining
  uncertainty. Do not assign a score or claim mastery.
