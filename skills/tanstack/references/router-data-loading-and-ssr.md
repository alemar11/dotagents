# Data Loading And SSR

Use this guide when the issue is about loaders, preload behavior, or Router-layer SSR.

Owns:
- route loaders, `loaderDeps`, and route-owned fetch boundaries
- preload freshness and route cache behavior
- Router-specific SSR concerns before the problem becomes a Start-wide SSR issue

## Data Loading

Use this section when the task is specifically about route loaders,
`loaderDeps`, preload freshness, or route-owned data loading.

Workflow:
1. Identify what the route should own directly.
2. Check loader dependencies and invalidation triggers.
3. Align preload behavior with the actual cache owner.

Do not use this section for QueryClient ownership across Router and Query,
search params, or SSR hydration decisions spanning Start.

## Router SSR

Use this section when the task is specifically about TanStack Router SSR
behavior, hydration boundaries, or manual SSR wiring.

Workflow:
1. Confirm whether the app is using Router SSR directly or via Start.
2. Keep hydration boundaries consistent with the actual runtime model.
3. Avoid mixing Start-first SSR assumptions into plain Router SSR without
   evidence.

Do not use this section for full Start SSR/server runtime concerns, Query cache
dehydration across Router and Start, or route-level code splitting unrelated to
SSR.

Escalate to:
- `integration.md` when Query ownership or Start hydration boundaries are the real problem

Verification: verify against current Router loader or SSR docs when exact APIs
matter.
