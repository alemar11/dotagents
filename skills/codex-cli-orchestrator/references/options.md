# CLI Orchestrator Option Contract

## Canonical Fields

Field names use snake_case and assigned enum values use lower-kebab. Reject
unknown structured fields and retired values.

The CLI adapter has no worker-surface, task-visibility, checkout-strategy,
worker-count, or delivery-owner option. These values are derived:

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `execution_adapter` | `codex-cli-session` | `codex-cli-session` | Derived from this public skill. |
| `worker_host` | `tmux` | `tmux` | Fixed process host. |
| `execution_unit` | `feature-spec` | `feature-spec` | One session per Feature Spec. |
| `delivery_owner` | `root-cli-session` | `root-cli-session` | Fixed integration and delivery owner. |
| `worker_commit_permission` | `not-granted` | `not-granted` | Workers never commit. |

## Run Manifest

`scripts/codex-session run create` accepts one JSON object:

```json
{
  "schema_version": "1.0.0",
  "run_id": "run-20260715-a",
  "root_cwd": "/absolute/workspace",
  "worktree_root": "/absolute/workspace/.worktrees/codex-cli-orchestrator/run-20260715-a",
  "ledger_path": "/absolute/shared-ledger.md",
  "feature_specs": [
    {
      "spec_id": "spec-a",
      "spec_ref": "#42",
      "spec_title": "Example",
      "prompt_path": "/absolute/prompt.md",
      "output_schema_path": "/absolute/path/to/codex-cli-orchestrator/assets/worker-output-schema.json",
      "repositories": [
        {
          "repo_id": "api",
          "source_path": "/absolute/api",
          "base_ref": "main",
          "target_branch": "feature/example-api"
        }
      ]
    }
  ]
}
```

Identifiers must match `[A-Za-z0-9][A-Za-z0-9._-]*`. All paths are absolute.
Repository ids are unique within a Spec; Spec ids are unique within a run;
target branches are unique per source repository. `worktree_root` must be a
strict descendant of `root_cwd`, outside every source checkout, and must not
contain a source checkout. `output_schema_path` must resolve to this skill's
shipped `assets/worker-output-schema.json`; custom or merely compatible schemas
are rejected before a claim or run state is created.

## State And Output

Run states are `created`, `active`, `complete`, `blocked`, `releasing`, and
`cleaned`. Spec states are `declared`, `preparing`, `prepare-failed`, `prepared`, `running`,
`succeeded`, `failed`, `stopped`, `cleaning`, `cleanup-blocked`, and `cleaned`.

JSON success uses `ok`, `command`, `run_id`, optional `spec_id`, `state`, and
relevant tmux, session, artifact, or worktree fields. JSON errors use:

```json
{"ok": false, "error": {"code": "state-conflict", "message": "...", "details": {}}}
```

Exit codes are 0 success, 2 invalid input, 3 missing dependency, 4 state
conflict, 5 subprocess failure, and 6 unsafe cleanup.
