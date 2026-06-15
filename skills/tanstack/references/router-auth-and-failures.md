# Auth And Failures

Use this guide when the issue is about whether the route may be entered at all, or how failure states are owned once it is entered.

Owns:
- `beforeLoad` guards and auth redirects
- route-level not-found behavior
- route error ownership distinct from data-layer or server-runtime errors

## Auth And Guards

Use this section when the task is specifically about `beforeLoad`, auth
redirects, or route-level access checks.

Workflow:
1. Place route preconditions in guards, not scattered components.
2. Make redirect behavior explicit and testable.
3. Keep auth ownership clear between Router guards and Start middleware.

Do not use this section for middleware-wide Start auth concerns, navigation
ergonomics unrelated to guards, or cross-stack session coordination.

## Not Found And Errors

Use this section when the task is specifically about not-found routes, route
error boundaries, or failure-path behavior.

Workflow:
1. Separate not-found handling from other error modes.
2. Place error ownership at the right route boundary.
3. Ensure failure paths do not leak unrelated framework assumptions.

Do not use this section for general route tree design, Start server error
boundaries outside Router concerns, or Query mutation error policy.

Verification: if the task blends Router guards with Start middleware or
cross-stack session state, use `integration.md`; otherwise verify against
current Router guard, not-found, and error-boundary guidance.
