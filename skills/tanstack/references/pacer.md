# TanStack Pacer

Use this reference when a task involves TanStack Pacer, debouncing, throttling, rate limiting, queuing, batching, async work control, or replacing ad hoc timing utilities with TanStack-owned primitives.

TanStack Pacer is currently a beta-area product. Verify exact primitive and hook names against current docs and installed packages.

## What to Optimize For

- Timing semantics that match the product requirement.
- Cancellation and cleanup behavior that is explicit.
- Backpressure controls for network calls, search inputs, event streams, and background work.
- Small wrappers that keep debounce/throttle/rate-limit choices visible at call sites.

## Workflow

1. Identify the timing problem.
   Decide whether the behavior is debounce, throttle, rate limit, queue, batch, or async coordination.
2. Choose the smallest primitive.
   Prefer one Pacer primitive or hook that directly matches the timing contract.
3. Define leading/trailing and cancellation behavior.
   Be explicit about when work runs, what is dropped, and how pending work is flushed or canceled.
4. Wire lifecycle cleanup.
   For async debouncers, `cancel()` clears pending calls and `abort()` handles
   active work; the operation must consume its abort signal to stop underlying
   I/O. A custom React `onUnmount` replaces default cleanup, so preserve both
   responsibilities when applicable.
5. Test with time control.
   Use fake timers or deterministic timing tests for edge cases.

## Review Checklist

- Does the chosen primitive match debounce vs throttle vs rate-limit semantics?
- Are leading/trailing behavior intentional? `useDebouncer` has no `maxWait`
  option; choose throttling when continuous input must still execute periodically.
- Is async work protected from stale result commits?
- Are pending timers canceled on unmount or input replacement?
- Are high-frequency events batched or queued without unbounded memory growth?

## Avoid

- Replacing simple one-off `setTimeout` usage when no reusable timing behavior exists.
- Mixing multiple timing layers around the same callback.
- Ignoring stale async responses after debounced or throttled calls.
- Leaving queues unbounded for user-controlled event streams.

## Verification

Check the official [overview](https://tanstack.com/pacer/latest/docs/overview),
[React debouncing](https://tanstack.com/pacer/latest/docs/framework/react/guides/debouncing),
and [async debouncing](https://tanstack.com/pacer/latest/docs/framework/react/guides/async-debouncing)
against installed beta packages. Callback-only hooks do not expose instance
controls; select reactive state explicitly when using full utility hooks.

`@tanstack/pacer-lite` targets libraries needing smaller bundles and omits
reactivity, framework adapters, devtools, and some advanced options. Prefer
regular Pacer packages for applications that need those capabilities.
