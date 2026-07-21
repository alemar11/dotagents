# Worker Validation Phase

Load for baseline, focused, full, or post-fix validation.

Execute the literal accepted command in its exact working directory through the
App's normal sandbox and approval surface. Before execution, observe tool
identity, checkout head, and dirty state. Afterwards, record exit status,
bounded output, changed paths, head, and dirty state.

Do not infer safety from `pytest`, `npm`, `cargo`, `go`, `python`, or another
executable name. Do not silently project mutating flags into different flags.
If a command needs unavailable authority or can affect systems outside the
accepted scope, stop.

Focused and full validation must satisfy the accepted non-regression policy.
Every in-scope diagnostic must be resolved. Existing outside-scope debt is
permitted only when the exact baseline evidence remains unchanged.

Require no unexplained untracked paths and keep changes inside scope. Timeout,
output loss, interruption, uncertain cleanup, tool drift, or scope drift is an
execution failure requiring evidence and owner/root handling—not a test result
and not an automatic rerun.
