# GitHub Investigation State Contract

This reference owns GitHub Investigation's derived judgment states. They are
transient report facts and are never persisted by the skill. GitHub issue/PR
lifecycle, repository state, CI, reviews, and commit history remain external
evidence.

## Provenance confidence

| Value | Meaning |
| --- | --- |
| `clear` | Bounded repository and hosted evidence identify the provenance directly. |
| `likely` | Evidence supports one provenance explanation but leaves a material ambiguity. |
| `unknown` | The bounded investigation cannot attribute provenance safely. |

## Refactor disposition

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `refactor_disposition` | `required`, `optional`, `not-required` | `required` means the invariant cannot be fixed soundly at the smaller seam; `optional` means a larger change would improve clarity or maintenance without being necessary for correctness; `not-required` means the focused fix is the correct ownership boundary. |

Derive both fields from evidence. They are not caller-selectable options, and
their rationale remains surrounding prose rather than another state value.
