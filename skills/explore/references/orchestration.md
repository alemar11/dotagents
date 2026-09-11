# Explore Research Delegation

Read after Grilling Session returns `refined` or `user-stopped`. The invoking
session owns the investigation and final answer.

## Choose useful assignments

Use research helpers for concrete questions that benefit from separate context or independent
inspection. Work directly when existing evidence is sufficient or delegation
would add little. Respect user limits and available capacity; explain any limit
that prevents the requested parallel work. Do not fill a fixed number of slots.

Give helpers distinct evidence surfaces or questions. Run independent work in
parallel while investigating another relevant part locally. Wait for dependent
evidence before assigning work that relies on it.

## Research brief

Adapt this brief to each assignment:

> Investigate <question> to inform <decision>. Inspect <exact paths, documents,
> or source contents>, using <relevant accepted decisions and domain context>.
> Stay within <scope>; exclude <non-goals>. Read only: do not edit files, change
> Git or hosted state, save artifacts, interview the user, or delegate further.
> Return a concise answer with source or file citations, supporting evidence,
> competing explanations, and anything you could not establish. Distinguish
> observations from inferences. Stop when the question is answered or identify
> the specific missing evidence.

Provide enough context to answer independently, not an entire transcript.
Use subagents available in the current session; do not create a separate
controller, visible task, or external worker process.

No model or reasoning level is prescribed. Use host defaults and explicit user
choices; settings telemetry is not a prerequisite for useful research.

## Follow-up and synthesis

Track each launched helper by its returned identity and assignment. Reuse it
for focused clarification. Reconcile uncertain launch effects before retrying;
do not duplicate active work. If a helper fails, recover the evidence locally
where possible and state any remaining gap. Respect explicit requirements for
independent evidence rather than silently substituting self-review.

Collect each helper's result or failure before final synthesis; resolve active
work through completion or supported cancellation. Use the host's waiting
mechanism without busy polling. Compare claims with the sources, investigate
contradictions, and report unresolved uncertainty. Helpers' conclusions are
inputs to the caller's reasoning, not final authority.

[states.md](states.md) owns completion meanings. A failed optional helper does
not make a complete, independently supported investigation partial; missing
required evidence or independence does.
