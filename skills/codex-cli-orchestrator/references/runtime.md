# tmux And Codex CLI Runtime

## Topology

The root stays in the current interactive CLI session. One deterministic tmux
session hosts worker windows named from the run and Feature Spec ids. One
Feature Spec session may cover several repository worktrees under its Spec
root. A maximum of three Spec sessions may be nonterminal.

## Worktrees

`spec prepare` creates one branch and worktree per repository beneath the
manifest's `worktree_root/<spec-id>/<repo-id>`. The root must be a strict
descendant of `root_cwd`, outside, and must not contain any source checkout. It
refuses overlapping paths, duplicate branches, dirty source assumptions that would be
overwritten, or an unsafe worktree root. It never edits `.gitignore`.
Run creation persists resolved canonical paths. Every later read and mutation
revalidates the cached manifest before filesystem or process operations.

The controller refreshes the shared atomic claim on run and Spec status reads.
While a tmux-hosted Codex process is running, its supervisor also heartbeats the
claim every 30 seconds and stops the worker if claim ownership is lost.
Prepare, start, resume, stop, Spec cleanup, and run cleanup also verify ownership
inside the run lifecycle lock immediately before any Git, tmux, or worktree
mutation. Heartbeat and release compare the persisted acquire-time fingerprint,
and multi-repository operations repeat that check before each individual
mutation.
Each individual Git, tmux, or run-state mutation runs inside the shared helper's
ownership lease, which keeps the authoritative claim-store lock held until the
mutation finishes; takeover cannot pass between ownership validation and the
protected operation.
Worker bootstrap holds the same lease through output reset, anchor creation,
and the Codex-child spawn handshake, then the running supervisor maintains the heartbeat.
Validation and resume failures publish status only while a current lease is
held.
The runtime starts a persistent group leader that spawns Codex inside its
process group, reports the child result, and stays alive until the supervisor
signals the group. It persists the anchor PID/PGID, start-time marker, and group
model before the bootstrap lease is released. Because the anchor cannot exit
during ordinary worker completion, the PGID cannot be reused between identity
validation and `killpg`. Stop removes the tmux window, terminates and waits for
that exact anchored group, and records `stopped` only after it is proven dead.
A reused PGID is not signaled. Legacy running state without the persistent
anchor model and leader marker is unverifiable and requires operator recovery.
The anchor identity is checkpointed while the ownership lease is still held and
before waiting for the Codex-child handshake. Any failed cleanup therefore
leaves enough authoritative state for the current or replacement root to recover.
If ownership is lost while the worker is live, the supervisor keeps escalating
and does not return until the complete process group is proven non-running.

CLI source claims qualify every non-URI repository-local ref, including `#1`
and repo-relative Feature Spec paths, with the repository's Git common directory.
They therefore overlap across linked worktrees of one repository but not across
independent repositories. URI-shaped globally durable refs, including hosted
URLs, remain unchanged and therefore overlap across repositories.

After a worker exits, the supervisor reacquires the run lifecycle lock and
verifies the acquire-epoch fingerprint before publishing a recovered session id,
exit code, or terminal status. Ownership loss leaves prior terminal evidence
untouched for the replacement root.

Workers edit and validate but do not commit. After success, the root inspects
the current diffs, runs gates, and performs authorized Git operations. Cleanup
requires an explicit `integrated` or `abandoned` disposition, a terminal
worker, and clean worktrees. It removes worktrees but retains branches.

## Process And Artifacts

For one repository, start from that Git worktree. For several repositories,
start from their containing Spec root with Codex's explicit non-repository
check bypass so the sandbox covers every child worktree.

Start uses fixed structured execution: `codex exec --cd <execution-root> --sandbox
workspace-write --json --output-schema <schema> --output-last-message
<final.json> -`. `<schema>` is always the shipped
`assets/worker-output-schema.json`; manifests cannot substitute another schema.
The prompt is read from its file. Resume runs `codex exec
resume <uuid>` from the same Spec root with the same structured outputs.

Each Spec directory stores `events.jsonl`, `final.json`, `stderr.log`,
`exit_code`, `codex_session_id`, and `status.json`. The helper extracts the UUID
from `thread.started` only when the canonical session file is absent. A valid
canonical file is authoritative and does not replay historical events. Status
reads these files and tmux liveness; it never reads pane contents.
Process exit zero becomes `succeeded` only when `final.json` exists and matches
the shipped worker-report contract; missing, malformed, or unproved ready
reports become `failed` with artifact-validation evidence.
The helper persists `running` before creating the tmux window. Launch failure
becomes `failed`; a fast worker's terminal status is never overwritten by the
controller.

## Recovery

- A prepared Spec can start without recreating worktrees or be cleaned as
  abandoned before launch.
- Preparation checkpoints each repository. A partial failure becomes
  `prepare-failed` with the exact prepared repository ids, and abandoned cleanup
  removes only those verified worktrees before allowing run cleanup.
- Reusing an existing path requires the same Git common directory as the
  declared source, the exact target branch, and registration in that source's
  current worktree list.
- Start, resume, internal launch, and cleanup revalidate those identities.
- A run-level exclusive file lock serializes capacity reservation, state
  transition, and tmux window creation.
- The three-Spec ceiling counts every prepared or later execution state until
  explicit `cleaned`; succeeded, failed, and stopped Specs retain their slot
  while root integration or abandoned cleanup is still pending.
- A cache-level per-run reservation lock serializes `run create` before claim
  acquisition, including when same-id manifests name non-overlapping repos.
- A running Spec with a live window is observed, not restarted. A persisted
  running state without a live window is derived as stopped with recovery
  evidence so it no longer consumes a slot and may be resumed by UUID.
- A terminal Spec resumes only with its recorded UUID and existing worktrees.
  A present canonical session file must contain the lowercase hyphenated
  canonical UUID rendering; alternate spellings block rather than being
  normalized. When that file is absent, recovery parses every event line and requires exactly one valid
  `thread.started` UUID. Malformed canonical data, malformed fallback JSON or
  UUID data, zero fallback UUIDs, and multiple fallback UUIDs block before
  launch.
- Missing or conflicting UUID, worktree, branch, or manifest evidence blocks.
- A stopped or failed worker remains recoverable until integrated or abandoned.
- Stop and cleanup use the same run-level lifecycle lock as launch. Spec cleanup
  preflights every repository identity and cleanliness, persists `cleaning`
  progress after each removal, and records `cleanup-blocked` with removed and
  pending repositories plus the in-flight repository so a partial filesystem
  failure or interruption can resume safely. Run cleanup checkpoints
  `releasing` before claim release; retry treats an already-absent matching claim
  as released and completes the final `cleaned` checkpoint. Run
  cleanup stops only an empty/terminal tmux session and retains artifacts.
