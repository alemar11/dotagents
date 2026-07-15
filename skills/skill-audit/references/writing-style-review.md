# Writing Style Review

Use this optional flow when an audit needs to judge a skill's writing quality,
trigger clarity, prompt load, or maintainability. Keep it as an audit lens, not
as a replacement for repo, memory, portfolio, or session evidence.

This flow adapts vocabulary from Matt Pocock's `writing-great-skills` reference:

- https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-great-skills

Do not vendor or copy that skill into audited targets. Use the concepts here to
name problems precisely and to shape compact recommendations.

## When To Run

Open this reference after the target-kind workflow when any of these are true:

- The user asks about skill writing, style, clarity, bloat, compactness,
  instruction density, prompt budget, descriptions, or trigger quality.
- `scripts/portfolio-health` reports long descriptions, duplicate
  descriptions, duplicate bodies, or notable prompt-budget pressure.
- A standalone or bundled skill's `SKILL.md` appears hard to route because its
  main workflow is buried under branch-specific reference material.
- The audit needs to explain why a skill should be trimmed, moved into
  `references/*`, split, merged, or left as-is.

For plugin package audits, apply this flow only to bundled skill contracts or
plugin text that affects bundled skill invocation. Keep package manifest,
versioning, asset, and cache findings in `references/plugins.md`.

## Inputs

- Target `SKILL.md`.
- Target `agents/openai.yaml` when present.
- Directly relevant `references/*` files only when needed to test whether
  branch-specific material is disclosed cleanly.
- `scripts/portfolio-health` output for portfolio-level prompt-budget,
  entrypoint-size, duplicate, or long-description claims.
- Memory, git history, or raw session evidence when the finding claims observed
  runtime behavior, missed invocation, premature completion, or low value.

## Review Steps

1. Preserve the evidence boundary.
   - Separate text-quality observations from behavior claims.
   - Use session or trace evidence before claiming that wording caused a real
     false positive, false negative, premature completion, or low-value run.
2. Check invocation and description.
   - Decide whether the skill needs model discovery or should stay
     user-invoked, when that distinction exists in the target runtime.
   - Check whether the description states distinct trigger branches instead of
     repeating synonyms for the same branch.
   - Check whether `SKILL.md` frontmatter, `agents/openai.yaml`, README text,
     and actual target behavior describe the same surface.
3. Check information hierarchy.
   - Identify the always-needed workflow steps.
   - Identify branch-specific reference material that can move behind a clear
     pointer in `references/*`.
   - Flag pointers that are too vague for the agent to know when to open the
     referenced file.
   - Keep a concept's definition, rules, and caveats together unless a branch
     predicate clearly earns disclosure into a separate reference.
   - Estimate one representative invoked path as `SKILL.md` plus the references
     that branch must load. Do not use total package size as the active cost.
4. Check step quality.
   - For ordered workflows, verify that each step has a checkable completion
     criterion.
   - Prefer criteria that demand the relevant evidence, validation, or output
     shape over vague states such as "understand" or "review".
   - Treat premature completion as a runtime claim: require representative
     session, trace, or reproducible evidence before saying later steps caused
     the agent to rush the current one.
   - Recommend splitting by sequence only when that evidence shows later phases
     distract from satisfying the current phase's completion criterion.
5. Check pruning signals.
   - Flag repeated meanings as duplication, not just repeated words.
   - Flag stale or no-longer-relevant guidance as sediment.
   - Flag live but oversized top-level material as sprawl when it hides the
     main flow.
   - Flag no-op instructions only when they do not change likely model
     behavior in this target context.
6. Map the recommendation to an owner.
   - Use `skill` for contract, trigger, reference, or metadata text.
   - Use `bundled plugin skill` when the issue is isolated inside a plugin's
     bundled skill.
   - Use `plugin` only when package-level text or packaging drives the issue.
   - Use `docs` when the missing context is project-specific and should not
     live in the reusable skill.

## Diagnosis Labels

Use these labels sparingly in audit output when they make the recommendation
clearer:

- `description-branch-duplication`: the description repeats the same trigger
  branch with different words.
- `weak-context-pointer`: a reference pointer exists, but its wording does not
  clearly say when to open it.
- `inline-reference-sprawl`: branch-specific or supporting reference material
  occupies the top-level `SKILL.md` path and obscures the main workflow.
- `vague-completion-criterion`: a step can be declared done without observable
  evidence or output.
- `sediment`: old guidance still exists after its owning behavior, tool, path,
  or decision has changed.
- `no-op-instruction`: a sentence appears relevant but does not change the
  likely agent behavior.
- `split-not-earned`: a proposed new skill would add inventory or description
  load without enough independent invocation value.
- `owner-boundary-mix`: skill, plugin, and repo-doc responsibilities are
  blended in one surface.
- `premature-completion-risk`: representative evidence shows later visible
  phases drawing execution away from an unfinished current phase.

## Output

Keep the final audit format from `references/output-format.md`. Add writing
style results inside the affected target's roadmap instead of creating a
separate style-only report:

- `writing-style diagnosis: <label> - <finding>`
- `evidence: <repo file, metadata, portfolio-health output, memory, or session>`
- `highest-value next update: <compact recommendation>`
- `owner: skill | bundled plugin skill | plugin | docs`

Only include this diagnosis when it changes prioritization or makes the
recommended fix clearer.

## Guardrails

- Do not turn this into a prose taste review.
- Do not force external terminology into the user-facing audit when plain local
  wording is clearer.
- Do not apply edits while the audit is still read-only; record the recommended
  update in the audit roadmap instead.
- Do not call a skill bloated from line count alone; identify the duplicated,
  stale, branch-specific, or misplaced material creating the load.
- Do not turn leading-word vocabulary, negation avoidance, or an external
  glossary into health requirements.
- Do not recommend a split, merge, disable, or new skill without the normal
  `skill-audit` ownership and evidence checks.
