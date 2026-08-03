<!-- SE2-owned reference derived from the durable repository-context contract. -->

# Official Documentation

Use these sources when current product behavior, exact setup, or citations
matter. Prefer the OpenAI documentation pages over remembered behavior.

## Primary Sources

| Source | URL | Use |
| --- | --- | --- |
| Custom Code Review rules for Codex | https://developers.openai.com/blog/custom-code-review-rules-for-codex | Rationale, rule-writing guidance, the `rawResponseItem/*` compatibility example, evaluation dimensions, and the recommended violation/safe/unrelated rollout. |
| Codex code review in GitHub | https://developers.openai.com/codex/third-party/github | Setup, `@codex review`, automatic reviews, P0/P1 behavior, exact `## Code Review Rules` heading, nested scoping, one-off review focus, and fix follow-up behavior. |
| Custom instructions with AGENTS.md | https://developers.openai.com/codex/agent-configuration/agents-md | General instruction discovery, root-to-current-directory precedence, overrides and fallbacks, the local 32 KiB default, setup verification, and the Code Review Rules section. |
| Evaluation best practices | https://developers.openai.com/api/docs/guides/evaluation-best-practices | Task-specific datasets, positive and negative examples, grader design, human calibration, and continuous evaluation. |
| Agent approvals and security | https://developers.openai.com/codex/agent-approvals-security | Permission and mutation boundaries when a review follow-up could modify code or external state. |
| Review code changes for security | https://learn.chatgpt.com/codex/security/plugin/code-changes | Dedicated Codex Security change-review workflow; use it to distinguish security scanning from ordinary GitHub Code Review. |

## Primary Implementation Example

| Source | URL | Use |
| --- | --- | --- |
| OpenAI Codex `AGENTS.md` Code Review Rules | https://github.com/openai/codex/blob/5c18cc0acc3734f0e78e422a7fd94ea4a2be652e/AGENTS.md#code-review-rules | Concrete rules for API surface, model-visible context, breaking changes, test guidance, and change size. The commit is pinned because the developer article cites this version. |
| Compatibility-rule pull request | https://github.com/openai/codex/pull/29086 | Provenance for adding the `rawResponseItem/*` compatibility rule protecting Codex Cloud consumers. |

## Interpretation Boundaries

- The local `AGENTS.md` discovery page documents a combined 32 KiB default.
  The GitHub Code Review page documents repository search and changed-file
  scoping separately. Do not claim those discovery implementations or limits
  are identical without newer explicit documentation.
- The developer article reports 98% recovery of required custom findings versus
  58.3% for its baseline suite, but does not publish enough suite, model,
  sampling, grader, or confidence-interval detail to treat that figure as a
  general production guarantee.
- Code Review Rules guide an additional reviewer. They do not grant permission
  to modify code and do not replace deterministic enforcement or human review.
