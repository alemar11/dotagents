# Xcode MCP States

This skill owns no persisted configuration, checkpoint, or ledger. It observes
Xcode-owned permission and process state and reports one transient launch
outcome. Normalize external command wording to the canonical values below.

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
  running and no launch mutation was needed.
- `started`: final status showed the server running after the authorized
  launch commands.
- `approval-required`: a required persistent, administrator, folder, agent, or
  unsafe-global authorization was not supplied.
- `unsupported`: the selected Xcode does not provide the headless launcher.
- `blocked`: the requested environment or target identity could not be safely
  established.
- `failed`: authorized launch commands completed without a running final state.
