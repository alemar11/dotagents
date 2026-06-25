# Tracker Publishing Contract

Use this reference when `$plan-feature`, `$to-prd`, or `$to-issues` needs to
write local artifacts, mutate a hosted tracker, or return draft publish
commands. `project-memory/agents/issue-tracker.md` remains the repo-specific
source of truth; this file defines the shared mechanics.

## Authorization Matrix

- `local_artifact_writes=allowed` permits writing configured local PRD or issue
  files, or an explicitly requested local mirror.
- `external_tracker_mutation=allowed` permits hosted tracker mutation through
  the configured tracker skill, such as `$github-issues`.
- `effective_target=configured-tracker` means use the durable tracker mode.
- `effective_target=local-dry-run` means write only to the configured local dry
  run target and do not mutate hosted trackers.
- `effective_target=draft-publish-commands` means return bodies plus exact
  commands without executing them.

Hosted body-file inputs are temporary transport files. They must live outside
the repo and be removed after mutation unless the user explicitly requests a
local mirror.

## Stable Source PRD References

Every PRD-to-issues handoff must carry `source_prd_ref`:

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

## Skill Ownership

- `$to-prd` owns PRD body creation, PRD local writes, PRD hosted issue creation,
  and the `source_prd_ref` value it returns.
- `$to-issues` owns generated implementation issue bodies, issue local writes,
  issue hosted creation, sub-issue attachment, and replacement of draft PRD refs
  in hosted publish commands.
- `$plan-feature` owns passing the same run authorization, planning identity,
  delivery mode, and `source_prd_ref` through the full planning pipeline.
- `$codex-orchestrator` may consume generated issues only after the `Source PRD`
  is durable enough for the requested action.

## Mode Summary

| Tracker mode | PRD owner output | Issue owner output |
| --- | --- | --- |
| `github` | PRD GitHub issue, or PRD body plus draft command | GitHub sub-issues under the PRD, or issue bodies plus draft commands |
| `local-markdown` | `.scratch/<feature-slug>/PRD.md` | `.scratch/<feature-slug>/issues/<NN>-<slug>.md` |
| `orchestrator-github` | coordination PRD issue with `<project-slug>` label | coordination vertical feature issues under the PRD with the same label |
| `orchestrator-local` | `projects/<project-slug>/features/<feature-slug>/PRD.md` | `projects/<project-slug>/features/<feature-slug>/issues/<NN>-<slug>.md` |

Lower-kebab-case values are canonical. Treat older uppercase kebab-case values
as legacy aliases when reading existing artifacts, and rewrite touched
structured values to lower-kebab-case.
