# Codex CLI Model Policy

This is the canonical model, reasoning, and selection policy for the codex-cli
skill. It is independent from autoreview and implement-feature; changing this
file must not change either of those skills.

## Model registry

sol is the default model. terra and luna are opt-in model selections. The
tables are the complete codex-cli reasoning contract for each model. A Yes in
the Default column means the effort used when that model is selected without a
reasoning override.

### Sol

| Reasoning effort | When to use | Default |
| --- | --- | --- |
| low | Routine, narrow, well-specified work where latency matters | No |
| medium | Ordinary analysis or one-repository work with clear scope | Yes |
| high | Several interacting components or meaningful edge cases | No |
| xhigh | Security, compatibility, data, concurrency, or external-boundary risk | No |
| max | Quality-critical work where additional verification is materially useful | No |
| ultra | Exceptional uncertainty or broad independent workstreams | No |

Model ID: gpt-5.6-sol.

### Terra

| Reasoning effort | When to use | Default |
| --- | --- | --- |
| low | Routine, narrow, well-specified work where latency matters | No |
| medium | Ordinary analysis or one-repository work with clear scope | No |
| high | Several interacting components or meaningful edge cases | Yes |
| xhigh | Security, compatibility, data, concurrency, or external-boundary risk | No |
| max | Quality-critical work where additional verification is materially useful | No |
| ultra | Exceptional uncertainty or broad independent workstreams | No |

Model ID: gpt-5.6-terra.

Terra's default is `high`; its implicit task profile is `complex`. An explicit
`--task-profile standard` still selects `medium` because an explicit task
classification overrides the model default.

### Luna

| Reasoning effort | When to use | Default |
| --- | --- | --- |
| low | Routine, narrow, latency-sensitive or high-volume work where max is not worth the tradeoff | No |
| medium | Simple work where some reasoning is warranted but max is not worth it; choose explicitly after the scale-back decision | No |
| high | Nontrivial work where a lower-cost profile remains sufficient; choose explicitly after the scale-back decision | No |
| xhigh | Risky or multi-component work where max is not justified; choose explicitly after the scale-back decision | No |
| max | Luna's quality-first default; use for normal, complex, and quality-sensitive tasks | Yes |

Model ID: gpt-5.6-luna.

## Selection contract

Resolve caller intent before resolving the task profile or reasoning effort:

| Caller selection | Model | Reasoning |
| --- | --- | --- |
| Neither model nor reasoning specified | Sol | Sol default: `medium` |
| Model only | Selected model | That model's default: Sol `medium`, Terra `high`, Luna `max` |
| Reasoning only | Default Sol | The explicitly requested effort; no task profile is inferred |
| Model and reasoning | Selected model | The explicitly requested effort, if supported; no task profile is inferred unless supplied |
| Explicit carte blanche to choose | Skill-selected model | Skill-selected effort from this policy |

“Carte blanche” requires an explicit instruction such as “choose the model and
reasoning yourself” or “use whatever combination you think is best”. Do not
infer it merely because the caller omitted an option. Without that authority,
omitted values resolve to the defaults above.

When Luna is explicitly selected and no reasoning or task profile is supplied,
start at max.
Lower Luna only when the task is clearly routine, latency-sensitive, or
high-volume and the token savings are worth the quality tradeoff. The
codex-cli contract uses the Codex agent reasoning values above; it does not
expose none or minimal.

This quality-first Luna default follows OpenAI's current price-performance
guidance: match intelligence to the outcome, and use evaluations or task
requirements to decide when lower-cost processing is enough. See
[Advancing the price-performance frontier with GPT-5.6](https://openai.com/index/advancing-the-price-performance-frontier-with-gpt-5-6/).

## Task-profile resolution

The skill resolves one task_profile before starting codex exec:

| task_profile | Requested reasoning | Use when |
| --- | --- | --- |
| routine | low | Straightforward read, lookup, formatting, or bounded explanation |
| standard | medium | Ordinary analysis or one-repository task |
| complex | high | Several interacting components or meaningful edge cases |
| risky | xhigh | Security, compatibility, data, concurrency, or external-boundary risk |
| critical | max | Quality-critical work where additional verification is materially useful |
| extreme | ultra | Exceptional uncertainty or broad independent workstreams |

For Sol and Terra, select the lowest profile that credibly covers the task.
For explicitly selected Luna, the automatic mapping is model-specific:

| Luna task profile | Automatic effort | Policy |
| --- | --- | --- |
| routine | low | Use only when the latency/token saving is clearly worth the quality tradeoff |
| standard | max | Normal work keeps Luna's quality-first default |
| complex | max | Complexity alone is not a reason to scale Luna back |
| risky | max | Risk keeps Luna at max unless an explicit lower effort is justified |
| critical | max | Quality-critical work uses max |
| extreme | ultra, capped to max | The highest requested profile is reported and capped because Luna has no ultra |

The skill may pass an explicit Luna `medium`, `high`, or `xhigh` effort only
after deciding that the matching table case justifies the savings. File count,
issue count, or prompt length alone is not enough to select a higher profile or
to scale Luna back.

If the requested effort is unsupported by the selected model, automatic
profile resolution selects the highest supported effort below it and reports
the adjustment. With model=luna, task_profile=extreme therefore resolves to
max. An explicit incompatible --reasoning-effort is rejected rather than
silently changed.

Every launch result exposes:

- model: the canonical user-facing alias;
- model_id: the exact Codex model slug;
- task_profile: the pre-launch classification, or null when a direct reasoning
  override was supplied without a classification;
- requested_reasoning_effort: the profile or explicit request;
- reasoning_effort: the value actually passed to Codex;
- reasoning_adjustment: null or a canonical explanation of an automatic
  model-cap adjustment.
