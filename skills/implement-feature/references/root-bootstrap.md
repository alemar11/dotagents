# Root Bootstrap

This file owns the complete pre-registration order. It applies only after the
runtime surface and installed GitStack parity gates in `SKILL.md` pass and before
the ledger exists.

Each entry into this bootstrap is a new bootstrap epoch. Create a new empty
transient directory before producing any derived artifact. Revalidated exact
immutable source snapshot bytes may be reused as inputs. Never copy, reopen, or
reuse derived registration JSON, a command request, execution manifest, receipt,
preflight result, fingerprint, claim, ledger, or task/checkout identity from a
prior or retired epoch. Regenerate all derived artifacts with the currently
loaded skill and helper installation.

## Closed Contract Selection

Build one read-only source snapshot, then select the full bootstrap set from
facts already present in that snapshot:

- Always load `spec-backed-delivery.md`, `execution-manifest.md`, and
  `baseline-validation.md` for snapshot, delivery preflight, intake, and
  validation-plan derivation.
- Also load `multi-repo-workspace.md` when any Spec names more than one affected
  repository or the complete bundle contains partial plus integration Specs.
- Load `app-control-plane-delays.md` only when an App task identity/title or
  root Goal observation is already delayed or ambiguous.
- Load `options.md` and `task-model-policy.md` only after intake and preflight
  succeed and authorization is ready to resolve.
- After authorization is granted, load `run-state.md`, `cache-lifecycle.md`, and
  `packets-registration.md` for claim, maintenance, and registration.

These predicates are final. Never add a contract later from prose or omit a
selected contract. Missing, contradictory, or unreadable selection evidence
fails before claim.

## Snapshot, Preflight, And Intake

Take one exact-byte snapshot of the durable Feature Spec and complete generated
issue graph. Reuse it for canonical bundle preparation, fingerprints, intake,
authorization, and registration. Refetch and rerun preflight before claim when
proven drift occurs; changed identity after authorization is
`authorization-stale`.

Normalize GitHub shorthand `owner/repository#N` to
`https://github.com/owner/repository/issues/N` for helper claim/task identity;
preserve the shorthand as the authoritative artifact ref and never pass it
directly to a helper.

Prepare and verify the delivery-preflight manifest before authorization.
Require authenticated GitHub push/PR capability plus readable lifecycle,
default-base, mergeability/conflicts, repository policy, and definitive CI
classification `configured|not-configured`. Unknown capability returns
`preflight-failed` with no artifacts. `not-configured` is valid.

Validate stable refs, the complete acyclic graphs, earlier-only dependencies,
one executable owner per `(repository,target_branch_name)`, repository and path
scope, validation adapters, acceptance criteria, integration gates, local
tracker destinations, domain-closeout ownership, and fixed model profiles.
Missing or contradictory execution evidence is `planning-required`. An
explicit non-App target is `unsupported-delivery-target`. Never repair or
mutate the source artifacts.

Sort ready candidates by canonical claim/task source id. Greedily select within
the remaining three-task capacity only pairwise path-disjoint work, treating
ancestor/descendant scopes as overlapping. A downstream is ready only after
every upstream ref is merged; merge-ready-but-unmerged is still a dependency
wait. Never serialize, force-bind, or schedule around a duplicate executable
`(repository,target_branch_name)` owner.

## Authorization, Claim, And Registration

Render the deterministic complete scope summary. Resolve an explicit imperative
invocation through `options.md`; ask its single question only when permission
remains `not-requested`. A grant binds the exact execution-scope fingerprint.

Carry the verified GitStack installation evidence and fingerprint during
registration. Derive `execution_manifest_evidence` from the sibling
`scripts/execution-manifest` path and current file bytes in this epoch; bind its
fingerprint into authorization. Run `active-root-claim --json doctor`, canonicalize repository and source
identities, and acquire the complete portfolio claim before cache or ledger
mutation. Qualify local refs with their Git common directory. A live overlap is
`needs-owner`; a stale conflict follows the separately authorized takeover
contract in `run-state.md` and never permits partial replacement.

After claim, synchronously run the cache doctor and fixed 180-day prune once in
root. Then create one schema-10 registration packet through
`packets-registration.md`, create schema-15 state, set and observe the derived
root title, and enter the controller loop. Goal state remains internal
`pending`; do not call `create_goal` yet.

Pre-claim failure reports exact evidence and proves that no claim, ledger,
Goal, task, tracker write, or source mutation exists.
