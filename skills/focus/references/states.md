# Focus State Contract

This reference owns Focus state labels. Focus has no persisted ledger: the
receipt and derived labels are transient, while the created App task and its
observed operational state are external authoritative state.

## Identity state

| Value | Meaning | Terminal |
| --- | --- | --- |
| `pending-setup` | Creation returned only a provisional setup identity; reconcile without replacement. | No |
| `stable` | An authoritative task read established the real task identity. | No |

## Title state

| Value | Meaning | Effect |
| --- | --- | --- |
| `title-verified` | The observed title exactly matches the requested title. | None |
| `title-unverified` | Title readback is unavailable or missing after the one allowed setup attempt. | Warning only unless the user required an exact title. |
| `title-drift` | The authoritative observed title differs from the requested title after the one allowed setup attempt. | Warning only unless the user required an exact title. |

## Outcome

| Value | Meaning | Terminal |
| --- | --- | --- |
| `complete` | One structurally verified focused task exists; title warnings may still be present. | Yes |
| `partial` | Creation may have occurred but authoritative reconciliation could not establish a complete ready result. | Yes |
| `failed` | A required saved-project or destination precondition failed, or authoritative reconciliation proves that no task exists after the allowed creation attempt. | Yes |
| `unsupported-runtime` | A required structural creation or verification capability is unavailable. | Yes |

Never infer identity or outcome from display title, prompt preview, timing, or
the immediate creation receipt. Preserve external App task status exactly as
observed rather than translating it into another Focus-owned state.
