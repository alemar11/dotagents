# Run State CLI

`scripts/run-state` is a standard-library Python CLI. Normal execution always
uses this shipped artifact. `CLI_VERSION` is exactly `1.0.0`; SQLite and JSON
schema are integer `1`. This is a fresh breaking design with no migrations,
aliases, importers, legacy readers, or alternate state files.

All controllers for the same machine user share:

```text
~/.cache/dotagents/skills/implement-feature/run-state.sqlite3
```

The directory and DB are owner-only. There is no lock file. SQLite
`BEGIN IMMEDIATE` transactions plus the fixed 5000 ms busy timeout are the sole
writer coordination.

## Stored Data Allowlist

The schema contains only metadata, runs, assignments, canonical repository
claims, and typed App-operation reconciliation facts. It may retain source refs,
App project/thread/worktree identity, receipts/readbacks, and coarse Git head,
PR, or provider observation refs.

It must not store raw Spec or issue bodies, checklists, issue phases, allowed
path prose, validation attempts, worker technical or domain state, arbitrary
provider payloads, generic request/result JSON, or any text hash. Normal Git
head SHAs remain valid evidence.

## Commands

```bash
scripts/run-state --version
scripts/run-state --json doctor
scripts/run-state --json run start --manifest /absolute/manifest.json
scripts/run-state --json run wait-sweep --run-id RUN --expected-revision N
scripts/run-state --json run show --run-id RUN
scripts/run-state --json run list --status active
scripts/run-state --json claim find --repository-identity github:owner/repository

scripts/run-state --json app-operation begin \
  --run-id RUN --expected-revision N --operation-key KEY \
  --action create-worker --subject-id ASSIGNMENT
scripts/run-state --json app-operation finish \
  --run-id RUN --expected-revision N --operation-key KEY \
  --observation /absolute/observation.json
scripts/run-state --json app-operation list --run-id RUN

scripts/run-state --json assignment ready \
  --run-id RUN --expected-revision N --observation /absolute/ready.json
scripts/run-state --json assignment block \
  --run-id RUN --expected-revision N --assignment-id ASSIGNMENT
scripts/run-state --json run finish \
  --run-id RUN --expected-revision N --outcome pr-ready
```

Read commands and `doctor` never write. Every mutation uses one compare-and-swap
revision transaction. JSON stdout is one object with `schema_version`, `ok`,
and `command`; errors add typed `error.code` and `error.message`.

Canonical GitHub repository identity is `github:owner/repository`. Local-only
identity is derived from the resolved Git common-directory real path, device,
and inode; linked worktrees collide intentionally. Repository claims are root-run
owned, not assignment, branch, worktree, or PR owned. Multi-repository starts
acquire all identities or none.

Typed App observations carry only action-specific fields plus `receipt_ref` and
`readback_ref` when those references were actually observed. They are required
for success, but `unknown` or failed effects may truthfully omit them. `unknown`
preserves ambiguous effect and cannot be relaunched.
Bootstrap success is the implementation-authority boundary. A post-bootstrap
durable-contract block retains claims; only whole-run PR-ready or verified
preimplementation abort releases them.

Pending or unknown bootstrap delivery forbids worker archive until readback
proves the bootstrap failed. Bounded repository waits compare stable repository,
run, and root-task owner identity; worker-list changes do not reset the counter.

Worker creation and bootstrap require the active root Goal. Worker thread and
active-checkout bindings are unique across active roots. Goal completion cannot
launch without this run's active Goal or while another App operation is pending
or unknown. PR-ready evidence
must bind the PR base to the provider-observed default branch.

One root task may own only one unfinished run. One App project may map to
several assignments in one canonical repository, never to distinct repositories.

## CLI Maintenance

Keep normal execution on `scripts/run-state`; there is no maintenance project or
build output. `CLI_VERSION` in the script is the semver source of truth. Re-run
`--help`, `--version`, `--json doctor`, Python compilation, unit/contract tests,
and an isolated lifecycle fixture after changes. `doctor` remains read-only.
