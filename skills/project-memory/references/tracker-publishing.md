# Tracker Publishing Contract

Use this reference when `$plan-feature` needs to
write local artifacts, mutate a hosted tracker, or return draft publish
commands. `project-memory/agents/issue-tracker.md` remains the repo-specific
source of truth; this file defines the shared mechanics.

## Tracker Write Policy

Use `tracker_mode` to choose the durable artifact target and `tracker_writes`
to choose write behavior:

- `tracker_writes=disabled`: do not write tracker artifacts. Return bodies plus
  exact local paths or hosted commands without executing them.
- `tracker_writes=prompt`: ask the user immediately before writing issue-ready
  PRD/task content to the configured tracker target.
- `tracker_writes=auto`: write issue-ready content to the configured tracker
  target as soon as repository context, duplicate checks, labels, types, and
  relationships are resolved.

For legacy tracker configs without `tracker_writes`, map old fields before
acting:

- `external_tracker_mutation=allowed` maps to `tracker_writes=prompt` for
  GitHub or hosted targets.
- `local_artifact_writes=allowed` maps to `tracker_writes=auto` for local
  targets.
- `effective_target=local-dry-run` or
  `effective_target=draft-publish-commands` maps to a current-run
  `tracker_writes=disabled` override.

Do not infer `tracker_writes=auto` for hosted trackers from legacy `allowed`
fields; hosted auto-publish must be explicit.

Hosted body-file inputs are temporary transport files. They must live outside
the repo and be removed after mutation unless the user explicitly requests a
local mirror.

## Stable Source PRD References

Every PRD-to-generated-issues handoff must carry `source_prd_ref`:

- Hosted PRD already exists: `source_prd_ref=#<prd-number>`.
- Local PRD exists: `source_prd_ref=<repo-relative-prd-path>`.
- Draft command run before hosted mutation: use a deterministic draft ref,
  `source_prd_ref=draft-prd:<feature-slug>` for one repo or
  `source_prd_ref=draft-prd:<project-slug>/<feature-slug>` for orchestrator
  coordination.

When using a draft PRD ref, also return the PRD title, `feature_slug`,
`project_slug` when applicable, and a short PRD body fingerprint so later
commands can prove the generated issues still point at the same PRD draft.

Draft issue bodies may use `Source PRD: draft-prd:<...>` only while no hosted
PRD number exists. The draft publish plan must say how to replace that value
before mutation:

1. Create or update the PRD first.
2. Capture the hosted PRD issue number as `PRD_NUMBER`.
3. Replace `Source PRD: draft-prd:<...>` with `Source PRD: #$PRD_NUMBER` in
   each implementation issue body before creating those hosted issues.
4. Attach each implementation issue to the PRD parent when the tracker supports
   parent/sub-issues.

Do not dispatch implementation workers from a `draft-prd:<...>` source as if it
were a durable PRD. A dry-run orchestrator may inspect the graph, but real
implementation scheduling requires a hosted PRD number, a local PRD path, or an
explicit owner decision to use the full PRD body as the temporary source.

## Phase Ownership

- The `$plan-feature` PRD phase owns PRD body creation, PRD local writes, PRD
  hosted issue creation, and the `source_prd_ref` value it returns.
- The `$plan-feature` issue phase owns generated implementation issue bodies,
  issue local writes, issue hosted creation, sub-issue attachment, and
  replacement of draft PRD refs in hosted publish commands.
- `$plan-feature` owns passing the same `tracker_writes`, planning identity,
  delivery mode, and `source_prd_ref` through the full planning pipeline and
  its phase modes.
- `$codex-orchestrator` may consume generated issues only after the `Source PRD`
  is durable enough for the requested action.

## Mode Summary

| Tracker mode | PRD owner output | Issue owner output |
| --- | --- | --- |
| `github` | PRD GitHub issue, or PRD body plus draft command | GitHub sub-issues under the PRD, or issue bodies plus draft commands |
| `local` | `.scratch/<feature-slug>/PRD.md` | `.scratch/<feature-slug>/issues/<NN>-<slug>.md` |
| `orchestrator-github` | coordination PRD issue with `<project-slug>` label | coordination vertical feature issues under the PRD with the same label |
| `orchestrator-local` | `projects/<project-slug>/features/<feature-slug>/PRD.md` | `projects/<project-slug>/features/<feature-slug>/issues/<NN>-<slug>.md` |

Lower-kebab-case values are canonical. Treat older uppercase kebab-case values
and `local-markdown` as legacy aliases when reading existing artifacts, and
rewrite touched structured values to lower-kebab-case.
