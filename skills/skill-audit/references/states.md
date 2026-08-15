# Skill Audit State Contract

This reference owns Skill Audit modes, classifications, derived evidence
states, and live annotation state. The skill persists none of them: historical
results and the live annotation registry exist only in the current audit task.
Monitored App task lifecycle and installed/runtime artifacts are external
state and must be reported exactly as observed.

## Audit mode

| Value | Meaning |
| --- | --- |
| `historical` | Evaluate repository, installed, memory, summary, or session evidence from completed or archived activity. |
| `live` | Observe authoritative current App task evidence without steering the monitored task. |

## Target kind

| Value | Meaning |
| --- | --- |
| `standalone-skill` | A reusable or project-local skill owns the behavior directly. |
| `plugin-package` | The plugin manifest or shared package surface owns the behavior. |
| `bundled-plugin-skill` | One skill bundled inside a plugin owns the behavior. |

## Evidence state

Every historical and live finding emits the canonical field `evidence_state`.
Use exactly one of these values:

| Value | Meaning |
| --- | --- |
| `source-confirmed` | Direct inspection of the current editable source, manifest, metadata, link graph, or ownership contract proves the finding. |
| `session-confirmed` | Direct historical session evidence confirms the behavior. |
| `summary-only` | Only a derived memory or rollout summary supports the claim. |
| `heuristic-only` | Inventory or log heuristics support prioritization but not a behavior claim. |
| `no-invocation-evidence-found` | The bounded historical search found no representative invocation evidence. |
| `live-provisional` | A fresh authoritative task read suggests a defect, but the evidence remains incomplete and the live annotation is still `provisional`. |
| `live-confirmed` | A fresh authoritative task read confirms the live behavior. |
| `current-evidence-unavailable` | Required live discovery or authoritative reads are unavailable; stop the live claim. |

## Owning fix surface

| Value | Meaning |
| --- | --- |
| `standalone-skill` | Fix the editable standalone skill owner. |
| `bundled-plugin-skill` | Fix the editable bundled skill owner. |
| `plugin-package` | Fix the plugin-level manifest, shared runtime, or package contract. |
| `docs` | Fix repository documentation outside the runtime owner. |
| `external-runtime` | The observed limitation belongs to the runtime, App, provider, or another external surface. |

## Live annotation status

| Value | Meaning | Allowed next states |
| --- | --- | --- |
| `provisional` | Evidence is incomplete. | `confirmed`, `withdrawn` |
| `confirmed` | A fresh authoritative read proves a contradiction with the active contract. | `resolved`, `withdrawn` |
| `resolved` | The same task later demonstrated recovery; preserve the original evidence. | None |
| `withdrawn` | Later evidence disproved the annotation. | None |

Live annotation severity is `high`, `medium`, or `low`; severity does not
change annotation status or evidence strength.

## Helper status

`usage_scan.status` is transient helper output:

| Value | Meaning |
| --- | --- |
| `completed` | Usage evidence was scanned. |
| `skipped` | The caller selected `--no-logs`; no unused candidates are emitted. |

## Entrypoint size band

`entrypoint_size_band` is a derived diagnostic classification emitted by
`portfolio-health`. It prioritizes review and never makes a skill fail health
checks by size alone. The estimator is `ceil(UTF-8 bytes / 4)`.

| Value | Meaning |
| --- | --- |
| `normal` | At most 2,500 estimated tokens and fewer than 500 lines. |
| `review` | 2,501-4,000 estimated tokens. |
| `high-density` | 4,001-5,000 estimated tokens. |
| `over-guideline` | More than 5,000 estimated tokens or at least 500 lines. |
