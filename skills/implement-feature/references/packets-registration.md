# Registration And Root Packet Contract

Load only for registration, root-title observation, or root Goal activation.
`ledger-cache` owns the generic packet envelope, operation id, size limits,
canonical encoding, claim/CAS binding, and template validation. This file owns
only registration inputs and root event families.

## Registration Inputs

Registration schema is exactly `9.0.0`. Supply:

| input | phase-specific contract |
| --- | --- |
| `schema_version` | Exact registration schema `9.0.0`. |
| `bundle_sha256` | Exact immutable execution-bundle bytes. |
| `execution_scope_fingerprint` | Complete deliveries, paths, and validation plans. |
| `authorization_fingerprint` | Execution scope, permission evidence, and GitStack installation fingerprint. |
| `root_task_ref` | Calling App task identity. |
| `root_checkout` | Calling App task absolute checkout. |
| `objective` | Fresh portfolio Goal text containing exact `CI when configured`. |
| `objective_fingerprint` | Digest of the exact objective. |
| `permission_evidence_ref` | Exact grant evidence. |
| `gitstack_installation_evidence` | Complete verified `gitstack-installation-parity:v1` evidence. |
| `repositories` | Sorted claim-identical Git common directories. |
| `repository_checkouts` | Complete, exact `{git_common_dir, checkout}` claim map. |
| `sources` | Nonempty canonical task-source records. |

Each `sources[]` object supplies exactly:

```text
task_key source_id source_spec_ref feature_spec_title feature_slug
source_state source_fingerprint planned_done_ref tracker_backend
tracker_repository deliveries dependency_ids requires_domain_closeout
task_model task_thinking thinking_reason task_assignment_fingerprint
```

Each nonempty `deliveries[]` object supplies exactly:

```text
delivery_key repository github_repository target_branch default_base
allowed_paths ci_availability preflight_key preflight_evidence_ref
validation_plan
```

Each nonempty `validation_plan[]` row supplies validation and command ids,
adapter/policy, authored/projected argv fingerprints, tool-identity fingerprint,
and execution-policy fingerprint exactly as validated by the typed template.
The argv fingerprints intentionally bind only the literal authored or projected
argv so registration can precede App checkout creation. The managed checkout,
cwd, and checkout identity remain separately bound by task registration,
command-manifest identity, baseline observation, and atomic acceptance.

Keys and slug are lower-kebab. GitHub identity is `owner/repository`; CI is
`configured|not-configured`. Source, task, profile, repository, dependency,
delivery, and claim scope are immutable. Registration derives the stable root
title and internal Goal state `pending`.

## Root Events

| event | phase-specific inputs and evidence |
| --- | --- |
| `root-title-observed` | Exact persisted `title` and App `evidence_ref`. |
| `portfolio-goal-activated` | Matching `goal_evidence_ref` and registered `objective_fingerprint`. |

Root-title evidence precedes baseline dispatch. Goal activation is legal only
after the atomic baseline accepts every registered tuple; call `create_goal`
once without a token budget and verify it through `get_goal` before recording.
