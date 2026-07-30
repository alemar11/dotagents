# Pi Delegate CLI Contract

Read this reference when invoking `scripts/pi-delegate`, parsing its output, or
diagnosing a failure.

## Commands

```bash
scripts/pi-delegate --version
scripts/pi-delegate --json doctor
scripts/pi-delegate --json run "<task>"
scripts/pi-delegate --json run --thinking-level high --task-file <path>
scripts/pi-delegate --json run --thinking-level max --session-id <id> "<follow-up>"
```

`doctor` is non-mutating and sends no model request. It may read Pi's user
settings, credentials metadata, and offline model catalog through the installed
`pi` executable.

`run` executes Pi with its normal coding tools, `--no-approve`, the fixed
`zai-coding-cn/glm-5.2` model, and the selected thinking level. The canonical
levels are `off`, `minimal`, `low`, `medium`, `high`, `xhigh`, and `max`.
`medium` is the default when `--thinking-level` is omitted. The launcher passes
the selection to Pi unchanged and never constructs a shell command.

## Task Input

Provide exactly one task source:

- one positional task string,
- `--task-file <path>` containing UTF-8 text, or
- stdin when neither other source is present.

The launcher rejects empty tasks, a positional task combined with
`--task-file`, and session IDs outside Pi's canonical character contract.

## JSON Policy

With `--json`, stdout contains exactly one CLI-owned JSON object. Pi diagnostics
go to stderr. The launcher does not emit raw Pi API responses or credentials.

Doctor success:

```json
{
  "schema_version": "1.0.0",
  "command": "doctor",
  "ready": true,
  "version": "0.1.0",
  "project_root": "/path/to/current-project",
  "model": "zai-coding-cn/glm-5.2",
  "pi_version": "0.82.1",
  "checks": [
    {"name": "python3", "ok": true, "detail": "/path/to/python3"},
    {"name": "pi", "ok": true, "detail": "/path/to/pi"},
    {"name": "pi_version", "ok": true, "detail": "0.82.1"},
    {"name": "model", "ok": true, "detail": "zai-coding-cn/glm-5.2"}
  ]
}
```

Run success:

```json
{
  "schema_version": "1.0.0",
  "command": "run",
  "ok": true,
  "version": "0.1.0",
  "model": "zai-coding-cn/glm-5.2",
  "thinking_level": "high",
  "session_id": "codex-pi-example",
  "project_root": "/path/to/current-project",
  "final_response": "Pi's final response"
}
```

Run failure:

```json
{
  "schema_version": "1.0.0",
  "command": "run",
  "ok": false,
  "model": "zai-coding-cn/glm-5.2",
  "thinking_level": "high",
  "session_id": "codex-pi-example",
  "project_root": "/path/to/current-project",
  "error": {
    "code": "pi_failed",
    "message": "Pi exited with status 1.",
    "exit_code": 1
  }
}
```

Preflight failures additionally include the complete `doctor` envelope.

## Error Codes And Exit Status

| Error code | Meaning |
| --- | --- |
| `missing_task` | No task source was provided. |
| `ambiguous_task` | Positional and file task sources were both provided. |
| `empty_task` | The selected task source contains no non-whitespace text. |
| `task_file_error` | The task file could not be read. |
| `process_start_failed` | A local subprocess could not start. |
| `preflight_failed` | Python, Pi, or the exact model is unavailable. |
| `pi_failed` | Pi started but exited nonzero. |

Exit zero means the command completed successfully. `doctor` exits one when the
runtime is not ready. `run` exits one for preflight or Pi failures and two for
invalid task input.
