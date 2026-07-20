# Worker Validation Phase

Load only when the controller selects validation.

Run only registered validation command manifests through
`scripts/execution-manifest`. Verify manifest and receipt fingerprints, pinned
tools, dependencies, exact cwd/argv, write policy, outputs, cleanup, and current
checkout/revision binding. One command id permits one physical attempt.

Focused and full validation must satisfy the registered non-regression policy.
Every in-scope diagnostic is gone. The only permitted outside-scope debt is the
exact baseline diagnostic and file-content set accepted under
`unchanged-outside-scope-allowed`; any changed diagnostic, content, adapter,
tool, argv, or policy fails.

Record canonical changed paths, require no untracked paths, keep every path in
scope, and require AutoReview target scope to equal that exact set. Timeout,
output limit, interruption, uncertain cleanup, tool drift, or scope drift
blocks; never relaunch or substitute an unpinned tool.
