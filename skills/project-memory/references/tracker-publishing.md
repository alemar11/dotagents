# Tracker Publishing Contract

Use this reference when `$plan-feature` needs to
write local artifacts, mutate a hosted tracker, or return draft publish
commands. `project-memory/agents/issue-tracker.md` remains the repo-specific
source of truth; this file defines the shared mechanics.

## Tracker Backend

Use `tracker_backend` to choose the durable artifact target:

- `github`: write PRDs and implementation issues as GitHub issues through
  `$gitstack:github-issues`, or return exact draft `gh` commands when the current run is
  non-mutating.
- `local`: write PRDs and implementation issues as Markdown files in the
  configured local conventions, or return draft paths and bodies when the
  current run is non-mutating.

By default, `tracker_backend` is the write authority for planning artifacts:
`github` publishes to GitHub and `local` writes local tracker files after
`$plan-feature` resolves setup, planning identity, and blockers. No-mutation,
dry-run, temp, and rehearsal behavior is current-run policy, not a durable
issue-tracker configuration row.

For legacy tracker configs, map old fields before acting:

- `tracker_mode=github` or `tracker_mode=orchestrator-github` maps to
  `tracker_backend=github`.
- `tracker_mode=local`, `tracker_mode=local-markdown`, or
  `tracker_mode=orchestrator-local` maps to `tracker_backend=local`.
- A legacy `effective_target=local-dry-run` with no preserved mutation reason
  maps to `no_mutation_override=dry-run` plus
  `no_mutation_output=local-artifacts`. Preserve a more specific canonical
  legacy reason when one exists.
- A legacy `effective_target=draft-publish-commands` with no preserved mutation
  reason maps to `no_mutation_override=draft-output` plus
  `no_mutation_output=publish-commands`. Preserve a more specific canonical
  legacy reason when one exists.

Hosted body-file inputs are temporary transport files. They must live outside
the repo and be removed after mutation unless the resolved Plan Feature option
is `local_mirror=requested`; write that mirror only under the validated
repo-relative `local_mirror_path` carried through both Plan Feature phase
handoffs. For GitHub tracker runs,
`$gitstack:github-issues` owns this transport:
create transient body files with non-interpolating writes, run `gh --body-file`,
verify tracker state after mutation, clean up temp files, and recover partial
publication by inspecting GitHub before retrying missing operations.

## Stable Source PRD References

Every PRD-to-generated-issues handoff must carry `source_prd_ref`:

- Hosted PRD already exists: `source_prd_ref=#<prd-number>`.
- Local PRD exists: `source_prd_ref=<repo-relative-prd-path>`.
- Draft-command or local-dry-run output before hosted mutation: use a
  deterministic draft ref,
  `source_prd_ref=draft-prd:<feature-slug>` for one repo or
  `source_prd_ref=draft-prd:<project-slug>/<feature-slug>` for workspace
  planning.

When using a draft PRD ref, also return the PRD title, `feature_slug`,
`project_slug` when applicable, and a short PRD body fingerprint so later
commands can prove the generated issues still point at the same PRD draft.

Draft issue bodies may use `source_prd_ref: draft-prd:<...>` only in
non-mutating output while no hosted PRD number exists. The draft publish plan
must say how to replace that value before mutation:

1. Create or update the PRD first.
2. Capture the hosted PRD issue number as `PRD_NUMBER`.
3. Replace `source_prd_ref: draft-prd:<...>` with
   `source_prd_ref: #$PRD_NUMBER` in
   each implementation issue body before creating those hosted issues.
4. Attach each implementation issue to the PRD parent when the tracker supports
   parent/sub-issues.

Do not dispatch implementation workers from a `draft-prd:<...>` source as if it
were a durable PRD. A dry-run orchestrator may inspect the graph, but real
implementation scheduling requires a hosted PRD number, a local PRD path, or an
exact scoped Orchestrator row with
`temporary_source_execution=owner-approved`. That row does not grant
publication or issue mutation.

## Phase Ownership

- The `$plan-feature` PRD phase owns PRD body creation, PRD local writes, PRD
  hosted issue creation, and the `source_prd_ref` value it returns.
- The `$plan-feature` issue phase owns generated implementation issue bodies,
  issue local writes, issue hosted creation, sub-issue attachment, and
  replacement of draft PRD refs in hosted publish commands.
- `$plan-feature` owns passing the same `tracker_backend`, `effective_target`,
  `no_mutation_override`, `no_mutation_output`, `local_mirror`,
  `local_mirror_path`, planning identity, `delivery_mode`,
  `issue_mutation_authority`, and
  `source_prd_ref` through the full planning pipeline and its phase modes, with
  the verified `option_rows_fingerprint` for each current row set.
- `$codex-orchestrator` may consume generated issues only after `source_prd_ref`
  is durable enough for the requested action.

## Mode Summary

| Tracker backend | PRD owner output | Issue owner output |
| --- | --- | --- |
| `github` | PRD GitHub issue, linked partial PRD issues for multi-repo work, or PRD body plus draft command | GitHub sub-issues under the PRD, linked repo issues for multi-repo work, or issue bodies plus draft commands |
| `local` | `.scratch/<feature-slug>/PRD.md` or `projects/<project-slug>/features/<feature-slug>/PRD.md` for local workspaces | `.scratch/<feature-slug>/issues/<NN>-<slug>.md` or `projects/<project-slug>/features/<feature-slug>/issues/<NN>-<slug>.md` for local workspaces |

Lower-kebab-case values are canonical. Treat older uppercase kebab-case values
and legacy tracker modes as aliases when reading existing artifacts, and rewrite
touched structured values to lower-kebab-case.
