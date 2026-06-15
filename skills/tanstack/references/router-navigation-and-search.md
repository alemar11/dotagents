# Navigation And Search

Use this guide when the issue is about URL state or moving through the app.

Owns:
- validated search params and typed URL-state updates
- `Link`, `navigate`, and route-aware hook narrowing
- separating search-state problems from route-tree or loader problems

## Search Params

Use this section when the task is specifically about `validateSearch`, typed
search state, or synchronizing URL query state with the app.

Workflow:
1. Identify which state belongs in search params.
2. Validate and type the search shape centrally.
3. Ensure updates use Router APIs instead of ad hoc string building.

Do not use this section for path params, route tree design, or Query cache
coordination across loaders and components.

## Navigation

Use this section when the task is specifically about `Link`, `navigate`,
`useNavigate`, or route-aware hook narrowing.

Workflow:
1. Check whether navigation is declarative or imperative for the use case.
2. Tighten type precision with route-aware narrowing where appropriate.
3. Avoid stringly-typed URL construction when Router APIs can express the same
   intent.

Do not use this section for search-state design, loader strategy, or auth
redirects implemented in route guards.

Verification: verify against current TanStack Router search-param or navigation
APIs when exact call shapes matter.
