# Improve Codebase Architecture Option Contract

Load this reference before ranking architecture candidates. It is the
canonical registry for behavior-affecting candidate classification.

## Registry

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `recommendation_strength` | `strong`, `worth-exploring`, `speculative` | Derived from evidence, benefit, risk, and migration cost | Explanations, evidence, risks, and proposed moves remain separate data. |

Every candidate emits one `recommendation_strength=<value>` assignment.
Natural-language descriptions may explain the ranking but are not alternate
values.
