# Pi Delegate CLI Contract

Read this reference when invoking `scripts/pi-delegate`, parsing its output, or
diagnosing a failure.

## Commands

```bash
scripts/pi-delegate --version
scripts/pi-delegate --json doctor
scripts/pi-delegate --json run "<task>"
scripts/pi-delegate --json run --progress --thinking-level high --task-file <path>
scripts/pi-delegate --json run --progress --timeout 2h --session-id <id> --task-file <path>
scripts/pi-delegate --json run --progress --timeout 45m --resume-last --task-file <path>
```

`doctor` is non-mutating and sends no model request. It may read Pi's user
settings, credentials metadata, and offline model catalog through the installed
`pi` executable.

`run` executes Pi in JSON event-stream mode with its normal coding tools,
`--approve`, the fixed `zai-coding-cn/glm-5.2` model, and the selected thinking
level. The canonical levels are `off`, `minimal`, `low`, `medium`, `high`,
`xhigh`, and `max`. `medium` is the default when `--thinking-level` is omitted.
The launcher passes the selection to Pi unchanged and never constructs a shell
command.

`--approve` grants project trust for each run. Pi may therefore load
project-local settings, skills, prompts, packages, and extensions in addition
to applicable context files. Invoke the launcher only from a trusted project.

## Session Selection

A new run receives an explicit generated Pi session ID. Continue an exact
session with `--session-id <id>`, or use `--resume-last` to pass Pi's
`--continue` flag for the current project. These options are mutually exclusive.

`run_id` is a controller-generated correlation ID that remains stable for the
whole launcher process. This matters for `--resume-last`: progress records may
start with `session_id: null` until Pi emits its session header, while `run_id`
is available immediately. The final result reports Pi's actual session ID.

## Timeout And Termination

Every run has a hard timeout. The default is `30m`; override it with
`--timeout <duration>` using whole-number h/m/s components such as `90s`, `45m`,
`2h`, or `1h30m`.

On timeout or controller `SIGTERM`, `SIGINT`, or `SIGHUP`, the launcher
terminates Pi's complete process tree rather than only the top-level process.
On POSIX it signals the dedicated process group, waits up to five seconds, and
then sends `SIGKILL`. On Windows it uses `taskkill /t`, adding `/f` for the
forced phase.

Terminal status values are:

| Status | Meaning |
| --- | --- |
| `completed` | Pi exited zero with a complete agent event stream and final response. |
| `failed` | Pi exited nonzero, was killed by the host, or otherwise failed. |
| `timeout` | The launcher hard timeout expired and stopped the process tree. |
| `aborted` | The launcher received a controller cancellation signal and stopped the process tree. |

A child `SIGKILL` that was not sent by the launcher timeout is reported with
`error.code=host_killed`. This is a host-limit or supervisor signal, not proof
of a Pi model failure.

## Monitoring And Privacy

`--progress` streams sanitized JSON Lines to stderr. The default heartbeat
interval is 30 seconds and may be set from 1 to 300 seconds with
`--heartbeat-seconds`. Concurrent runs are distinguished by `run_id`, name,
project root, and resolved session ID.

The launcher does not archive raw Pi events. Progress records contain only
phase names, tool names, error booleans, retry counters, delays, compaction
status, heartbeats, and terminal process metadata. Task text, model text, tool
arguments, tool results, credentials, and source contents are never emitted.
Raw Pi stderr is drained without being forwarded or archived. Final and
terminal progress records report only `suppressed_diagnostic_lines`, allowing
the controller to distinguish silence from hidden diagnostics without exposing
their contents.

## Task Input

Provide exactly one task source:

- one positional task string,
- `--task-file <path>` containing UTF-8 text, or
- stdin when neither other source is present.

The launcher rejects empty tasks, a positional task combined with
`--task-file`, and session IDs outside Pi's canonical character contract.

Use `--task-file` for multiline, skill-invoking, quoted, or shell-sensitive
prompts. This preserves literal values such as `$maintainer`, backticks, and
quotes before the launcher receives them. Positional task text is for short
plain text only. Regardless of the input source, the launcher sends the resolved
task to Pi over stdin rather than argv, so it does not appear in Pi's host
process arguments.

## JSON Policy

With `--json`, stdout contains exactly one CLI-owned final JSON object. Pi
diagnostics and optional sanitized progress go to stderr. The launcher does not
emit raw Pi API responses or credentials.

Every progress line uses this stable shape:

```json
{
  "schema_version": "1.0.0",
  "type": "progress",
  "event": "tool_started",
  "sequence": 4,
  "elapsed_seconds": 12.345,
  "run_id": "codex-pi-run-example",
  "session_id": "codex-pi-example",
  "name": "Fix parser",
  "project_root": "/path/to/current-project",
  "model": "zai-coding-cn/glm-5.2",
  "thinking_level": "high",
  "tool_name": "read"
}
```

Progress event values are `process_started`, `session_ready`, `agent_start`,
`turn_start`, `turn_end`, `tool_started`, `tool_finished`,
`compaction_start`, `compaction_end`, `retry_started`, `retry_finished`,
`heartbeat`, `agent_end`, and `process_finished`. The terminal
`process_finished` record includes `status`, `exit_code`, and `signal`.

Doctor success:

```json
{
  "schema_version": "1.0.0",
  "command": "doctor",
  "ready": true,
  "version": "0.3.0",
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
  "status": "completed",
  "version": "0.3.0",
  "model": "zai-coding-cn/glm-5.2",
  "thinking_level": "high",
  "progress_enabled": true,
  "run_id": "codex-pi-run-example",
  "session_id": "codex-pi-example",
  "project_root": "/path/to/current-project",
  "timeout_seconds": 7200,
  "signal": null,
  "suppressed_diagnostic_lines": 0,
  "final_response": "Pi's final response"
}
```

Run timeout:

```json
{
  "schema_version": "1.0.0",
  "command": "run",
  "ok": false,
  "status": "timeout",
  "model": "zai-coding-cn/glm-5.2",
  "thinking_level": "high",
  "run_id": "codex-pi-run-example",
  "session_id": "codex-pi-example",
  "project_root": "/path/to/current-project",
  "timeout_seconds": 7200,
  "signal": "SIGTERM",
  "suppressed_diagnostic_lines": 0,
  "final_response": null,
  "error": {
    "code": "pi_timeout",
    "message": "Pi did not finish within 7200 seconds.",
    "exit_code": 124
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
| `pi_protocol_error` | Pi emitted malformed or incomplete JSON event data. |
| `pi_failed` | Pi started but exited nonzero. |
| `pi_timeout` | The hard timeout expired and the process tree was stopped. |
| `pi_aborted` | Controller cancellation stopped the process tree. |
| `host_killed` | Pi received an external `SIGKILL`; inspect host limits and the working tree. |

Exit zero means the command completed successfully. `doctor` exits one when the
runtime is not ready. `run` exits one for preflight, Pi, timeout, abort, or
protocol failures and two for invalid task input.
