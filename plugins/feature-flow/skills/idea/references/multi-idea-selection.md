# Multiple-Idea Selection

Load this reference only when candidate extraction and semantic deduplication
leave more than one distinct proposal.

## Structured Question Contract

When `request_user_input` is available, ask one question per candidate. Put at
most three candidate questions in one call. For every question, provide exactly
these listed choices:

1. `Save idea (Recommended)` - accept this candidate for capture.
2. `Skip idea` - do not create or propose this candidate.

The client-provided free-form `Other` answer is the third path. Do not add an
`Other` option yourself. Do not set `autoResolutionMs`; silence is not consent
and creates no artifacts.

Give each question a stable snake_case candidate ID and a header of 12 or fewer
characters. State the proposed name and one-sentence summary in the prompt so
the choice is grounded. Give each listed option a one-sentence description.
The `Recommended` suffix communicates the default suggestion but never
authorizes an unanswered write.

If structured questions are unavailable, ask the same questions one at a time
in plain language, offering `Save idea`, `Skip idea`, or a free-form revision.
Preserve every other rule in this reference.

## Free-Form Answers

Interpret a free-form answer only for the candidate it names. It may:

- rename or revise the candidate;
- merge it with another candidate;
- split it into clearer distinct candidates;
- save it and explicitly queue it for triage;
- provide another unambiguous save or skip decision.

After a merge or split, rebuild semantic deduplication, names, slugs, owners,
and collisions. Re-ask only candidates whose identity or meaning changed;
preserve unaffected decisions. If the free-form answer is ambiguous, ask a
focused follow-up before continuing.

## Write Barrier

Finish every questionnaire batch and resolve every free-form consequence
before the first GitHub write. Selection answers are not publication
checkpoints. After selection, preflight the complete accepted set for tracker
owners, duplicate artifacts, names, slugs, labels, and issue collisions.

An explicit Idea request containing exactly one candidate needs no
extra confirmation. Also skip this questionnaire when the user already gave
an explicit per-candidate decision for every distinct proposal.
