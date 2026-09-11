# Suggestion states

This skill does not persist workflow state. The helper returns derived state
from the selected mode, the current tags, and the requested release line.

| State | Kind | Meaning |
| --- | --- | --- |
| `available` | Derived | The suggested tag is unused and may be considered by a later authorized workflow. |
| `bootstrap-required` | Derived | The repository has no SemVer tags; confirm the initial version before creating the first candidate. |
| `release-in-progress` | Derived | The suggested version line already has RC tags; use its `release/vX.Y.Z` branch. |
| `finalized` | Derived | The stable `vX.Y.Z` tag already exists. The line cannot receive another RC or final tag. |
| `blocked-finalized` | Derived | A release-mode candidate or final operation is blocked because the line is finalized. |
| `migration-available` | Derived | A stable legacy `X.Y.Z` tag has a resolvable commit and the canonical `vX.Y.Z` target is absent. |
| `already-present` | Derived | The canonical migration target exists and resolves to the same commit as its legacy source. |
| `target-conflict` | Derived | The canonical target exists but resolves to a different commit; migration must stop. |
| `source-missing` | Derived | The legacy source tag is listed but its commit object cannot be resolved locally. |
| `nothing-to-migrate` | Derived | No stable legacy tags exist, so migration has no work. |
| `canonical-format` | Derived | The exact requested application tag matches `vX.Y.Z` or `vX.Y.Z-rc.N`; availability and confirmation still require separate checks. |
| `blocked-noncanonical` | Mutation gate | The requested application tag is outside the canonical format. Explain the mismatch and stop; confirmation can never authorize this tag. |
| `confirmation-required` | Mutation gate | Any tag application needs explicit confirmation of the exact tag, operation, and commit. |
| `invalid-input` | Transient error | The requested mode, line, or tag does not match the canonical contract. |

`main` and `release` are selectable calculation modes, not persisted release
states. The helper remains read-only in every state. Every JSON preview also
reports `tag_application=explicit-confirmation-required`; a suggestion is not
authorization to create or push a tag. A validation failure instead reports
`tag_application=blocked-noncanonical` and exits nonzero so automation fails
closed.

## GitHub Actions resolver states

These states are derived while creating or upgrading the repository-local
release Actions. They are not persisted workflow state.

| State | Kind | Meaning |
| --- | --- | --- |
| `resolver-absent` | Derived | The project has no `.github/scripts/resolve_release_version.py`; install the bundled asset with both workflows. |
| `resolver-current` | Derived | Project and bundled resolver versions and bytes match. |
| `resolver-upgrade-available` | Derived | The project resolver has a lower SemVer than the bundled asset; review and update the resolver, tests, and workflows together. |
| `resolver-project-newer` | Derived | The project resolver has a higher SemVer than the bundled asset; never downgrade it. |
| `resolver-unversioned` | Derived | The project resolver cannot report a valid SemVer through `--version`; treat it as a legacy local implementation and do not overwrite it silently. |
| `resolver-version-conflict` | Mutation gate | Project and asset report the same version but have different bytes; treat the project as a local fork and require explicit resolution before replacement. |
