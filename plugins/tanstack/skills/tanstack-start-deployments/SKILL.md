---
name: tanstack-start-deployments
description: Review TanStack Start deployment-sensitive constraints, target-specific assumptions, and runtime packaging tradeoffs.
---

# TanStack Start Deployments

Use this skill when the task is specifically about deployment targets, runtime packaging, or environment-sensitive Start behavior.

## Owns

- Deployment target assumptions and packaging tradeoffs.
- Runtime-sensitive environment behavior.
- Deployment constraints that materially affect app structure.

## Does Not Own

- General framework setup: use `tanstack-react-start`.
- Server-only runtime boundaries without deployment context: use `tanstack-start-server-core`.
- CLI scaffolding: use `tanstack-cli-create-app-scaffold`.

## Workflow

1. Identify the deployment target and its constraints.
2. Check which Start assumptions depend on that target.
3. Keep deployment advice scoped to runtime packaging and environment tradeoffs.

## Verification

Verify against current TanStack Start deployment guidance when exact target support or packaging behavior matters.
