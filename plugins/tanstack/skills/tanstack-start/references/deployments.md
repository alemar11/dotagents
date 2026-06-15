# Deployments

Use this guide when deployment targets or runtime packaging constraints materially affect the right Start advice.

Owns:
- deployment target assumptions
- runtime packaging tradeoffs
- when deployment concerns should override generic Start examples

## Deployment Guidance

Use this section when the task is specifically about deployment targets, runtime
packaging, or environment-sensitive Start behavior.

Workflow:
1. Identify the deployment target and its constraints.
2. Check which Start assumptions depend on that target.
3. Keep deployment advice scoped to runtime packaging and environment tradeoffs.

Do not use this section for general framework setup, server-only runtime
boundaries without deployment context, or CLI scaffolding.

Escalate to:
- `tanstack-integration` when deployment constraints are interacting with Query or hydration boundaries rather than Start alone

Verification: verify against current TanStack Start deployment guidance when
exact target support or packaging behavior matters.
