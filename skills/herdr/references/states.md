# Herdr States

Herdr owns these external lifecycle states; the skill does not persist a task
state machine. `working` means Herdr detects active agent work.

`idle` and `done` both mean the agent is ready for input. The CLI/API uses the server's seen state to distinguish them; explicit focus commands mark the target seen, while reads do not. Each TUI client tracks viewed completions independently, so its Done badge can differ from the CLI or another client's badge. `blocked` means Herdr recognized an approval or question UI. `unknown` means an agent is present but Herdr cannot classify it confidently; it does not prove completion.

Prompt submission from a non-working state must produce observed `working` or
`blocked` activity before a settled-state wait can succeed. `idle` or `done`
alone does not satisfy that activity gate. Waits settle on `idle`, `done`, or
`blocked` by default and track agent lifecycle, not an individual turn. Verify
the requested result from agent output before claiming task completion.

Startup and prompt errors are external command results, not lifecycle states.
Read [operations](operations.md) for `agent_not_ready`, `agent_blocked`,
`agent_prompt_stalled`, timeouts, and recovery before retrying input.
