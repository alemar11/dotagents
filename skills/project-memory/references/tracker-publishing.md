# Tracker Publishing Contract

Use this reference when `$plan-feature` needs to
write local artifacts, mutate a hosted tracker, or return draft publish
commands. `project-memory/config/issue-tracker.md` remains the repo-specific
source of truth; this file defines the shared mechanics.

## Tracker Backend

Use `tracker_backend` to choose the durable artifact target:

- `github`: write Feature Specs and implementation issues as GitHub issues through
  `$gitstack:github-issues`, or return exact draft `gh` commands when the current run is
  non-mutating.
- `local`: write Feature Specs and implementation issues as Markdown files in the
  configured local conventions, or return draft paths and bodies when the
  current run is non-mutating.

By default, `tracker_backend` is the write authority for planning artifacts:
`github` publishes to GitHub and `local` writes local tracker files after
`$plan-feature` resolves setup, planning identity, and blockers. No-mutation,
dry-run, temp, and rehearsal behavior is current-run policy, not a durable
issue-tracker configuration row.

Reject tracker configuration that does not provide a canonical
`tracker_backend`. Run-scoped non-mutation behavior must arrive through the
current Plan Feature fields; do not infer it from obsolete setup keys.

Hosted body-file inputs are temporary transport files. They must live outside
the repo and be removed after mutation unless the resolved Plan Feature option
is `local_mirror=requested`; write that mirror only under the validated
repo-relative `local_mirror_path` carried through both Plan Feature phase
handoffs. For GitHub tracker runs,
`$gitstack:github-issues` owns this transport:
create transient body files with non-interpolating writes, run `gh --body-file`,
verify tracker state after mutation, clean up temp files, and recover partial
publication by inspecting GitHub before retrying missing operations.

## Stable Feature Spec References

Every handoff from a Feature Spec to generated issues must carry `source_spec_ref`:

- Hosted Feature Spec already exists: `source_spec_ref=#<spec-number>`.
- Local Feature Spec exists: `source_spec_ref=<repo-relative-spec-path>`.
- Draft-command or local-dry-run output before hosted mutation: use a
  deterministic draft ref,
  `source_spec_ref=draft-spec:<feature-slug>` for one repo or
  `source_spec_ref=draft-spec:<project-slug>/<feature-slug>` for workspace
  planning.

When using a draft Feature Spec ref, also return the Feature Spec title, `feature_slug`,
`project_slug` when applicable, and a short Feature Spec body fingerprint so later
commands can prove the generated issues still point at the same Feature Spec draft.

Draft issue bodies may use `source_spec_ref: draft-spec:<...>` only in
non-mutating output while no hosted Feature Spec number exists. The draft publish plan
must say how to replace that value before mutation:

1. Create or update the Feature Spec first.
2. Capture the hosted Feature Spec issue number as `SPEC_NUMBER`.
3. Replace `source_spec_ref: draft-spec:<...>` with
   `source_spec_ref: #$SPEC_NUMBER` in
   each implementation issue body before creating those hosted issues.
4. Attach each implementation issue to the Feature Spec parent when the tracker supports
   parent/sub-issues.

Do not dispatch implementation workers from a `draft-spec:<...>` source as if it
were a durable Feature Spec. A dry-run orchestrator may inspect the graph, but real
implementation scheduling requires a hosted Feature Spec number, a local Feature Spec path, or an
exact scoped Orchestrator row with
`temporary_source_execution_permission=granted-by-authorized-user`. That row does not grant
publication or issue mutation.

## Phase Ownership

- The `$plan-feature` Feature Spec phase owns Feature Spec body creation, Feature Spec local writes, Feature Spec
  hosted issue creation, and the `source_spec_ref` value it returns.
- The `$plan-feature` issue phase owns generated implementation issue bodies,
  issue local writes, issue hosted creation, sub-issue attachment, and
  replacement of draft Feature Spec refs in hosted publish commands.
- `$plan-feature` owns passing the same `tracker_backend`, `effective_target`,
  `no_mutation_override`, `no_mutation_output`, `local_mirror`,
  `local_mirror_path`, planning identity, `change_delivery_target`,
  `change_delivery_permission`, `issue_update_permission`, and
  `source_spec_ref` through the full planning pipeline and its phase modes, with
  the verified `option_rows_fingerprint` for each current row set.
- Non-mutating handoffs preserve the resolved canonical run value:
  `no_mutation_override=dry-run`, `no_mutation_override=temp`,
  `no_mutation_override=rehearsal`, `no_mutation_override=validation`,
  `no_mutation_override=disabled-writes`, or
  `no_mutation_override=draft-output`. They are not inferred from older field
  names or prose.
- `$codex-orchestrator` may consume generated issues only after `source_spec_ref`
  is durable enough for the requested action.

## Mode Summary

| Tracker backend | Feature Spec owner output | Issue owner output |
| --- | --- | --- |
| `github` | Feature Spec GitHub issue, linked partial Feature Spec issues for multi-repo work, or Feature Spec body plus draft command | GitHub sub-issues under the Feature Spec, linked repo issues for multi-repo work, or issue bodies plus draft commands |
| `local` | `planning/features/<feature-slug>/SPEC.md` or `orchestration/<project-slug>/features/<feature-slug>/SPEC.md` for local workspace parents | `planning/features/<feature-slug>/issues/<NN>-<slug>.md` or `orchestration/<project-slug>/features/<feature-slug>/issues/<NN>-<slug>.md` for local workspace parents |

Lower-kebab-case values are canonical. Reject noncanonical values instead of
rewriting them.
