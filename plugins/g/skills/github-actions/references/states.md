# GitHub Actions Result States

These states describe only the result of `g ci inspect`. They are derived from
provider evidence and are not persisted workflow state.

| Summary | Meaning |
| --- | --- |
| `no_checks` | The authoritative check rollup is empty. This is successful read-only evidence that no checks are configured or reported, not that CI passed. |
| `no_failing_checks` | One or more checks exist and none is currently classified as failing. |
| `failing_checks` | One or more failing checks were analyzed. |

Provider-owned check conclusions and lifecycle states remain external facts and
must be reported separately when they matter.
