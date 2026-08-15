# G Session Audit State Contract

This reference owns G Audit's derived coverage and finding states. The skill
persists none of them: the report registry is transient in the audit task.
Observed App task identity, host, project, repository, and lifecycle state are
external and must be preserved exactly as read.

## Coverage

| Field | Allowed values | Meaning |
| --- | --- | --- |
| `coverage` | `complete`, `partial` | `complete` means the live capability surface established all qualifying active-task coverage; `partial` means at least one required discovery, host, wait, read, or evidence frontier was unavailable. |

Never claim `complete` from task age, silence, a single project view, or cached
session evidence.

## Finding kind

| Value | Meaning |
| --- | --- |
| `feedback` | Explicit feedback, observed strength, or friction without a proven contract violation. |
| `bug` | A fresh authoritative read proves a concrete contradiction with the active G contract. |
| `improvement` | An actionable proposal that is not a confirmed contract violation. |

## Bug status

| Value | Meaning | Allowed next states |
| --- | --- | --- |
| `provisional` | Evidence is incomplete. | `confirmed`, `withdrawn` |
| `confirmed` | A fresh authoritative read proves the violation. | `resolved`, `withdrawn` |
| `resolved` | The same task later demonstrates recovery; preserve earlier evidence. | None |
| `withdrawn` | Later evidence disproves the annotation. | None |

## Priority

| Value | Meaning |
| --- | --- |
| `p0` | Data loss, security, unauthorized mutation, or complete audit failure. |
| `p1` | Workflow blocker or repeated materially incorrect behavior. |
| `p2` | Meaningful degradation or recurring operator friction. |
| `p3` | Documentation, clarity, cost, or polish improvement. |
