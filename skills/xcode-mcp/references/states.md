# Xcode MCP States

This skill may update client-owned MCP configuration when requested. It owns
no checkpoint or ledger. It observes Xcode-owned permission and process state
and reports one transient launch outcome. Normalize external command wording
to the canonical values below.

## `execution_environment`

This is a transient branch selected from the user's request:

- `attended-local`: a person can review the first connection and choose an
  agent authorization on the Mac.
- `unattended-host`: no person is expected at the console, but the machine is
  persistent or otherwise not proven disposable and isolated.
- `isolated-ci`: the user explicitly identifies a disposable, isolated CI
  machine and authorizes the unsafe global-agent permission.

## `permission_state`

This is persisted external state owned by Xcode:

- `disabled`: headless MCP permission is disabled.
- `enabled`: headless MCP permission is enabled without evidence of unsafe
  global-agent authorization.
- `unsafe-global`: headless MCP permission allows every agent without targeted
  approval.
- `unknown`: the selected Xcode did not return an interpretable permission
  state.

## `server_state`

This is transient external process state owned by Xcode:

- `stopped`: the headless server is not running.
- `running`: the headless server is running.
- `unknown`: the selected Xcode did not return an interpretable process state.

## `agent_authorization`

This is external authorization state owned by Xcode:

- `none`: no intended agent authorization is observed.
- `pending`: the intended agent or folder is waiting for a decision.
- `temporary`: access is limited to the observed temporary authorization
  period.
- `persistent`: the verified signed agent and any exact approved folder have
  persistent targeted access.
- `unsafe-global`: all agents are authorized globally.
- `unknown`: authorization could not be reconciled to the intended identity.

## `launch_outcome`

This is the skill's transient result state:

- `already-running`: final status showed the requested server was already
  running and no launch mutation was needed. This is not an early-return gate
  or evidence of client configuration, tool discovery, or project access.
- `started`: final status showed the server running after the authorized
  launch commands.
- `approval-required`: a required persistent, administrator, folder, agent, or
  unsafe-global authorization was not supplied.
- `unsupported`: the selected Xcode does not provide the headless launcher.
- `blocked`: the requested environment or target identity could not be safely
  established.
- `failed`: authorized launch commands completed without a running final state.

## Transitions and completion

Observe permissions and process state before acting. Authorized enablement
changes permission state; client connection or workspace opening can change
`stopped` to `running`. Opening or creating a project can change authorization
from `none` to `pending`, then to the approved duration. Process state alone
does not imply any authorization transition.

Select the outcome after the requested checks, not at the first running status.
If a required approval is missing, report `approval-required` even when the
process is running. For configuration-only work where no connection is attempted,
omit `launch_outcome` and report launch as untested. Report configuration, tool
discovery, requested project access, and observed UI state separately; none is
inferred from a successful command or another successful check.
