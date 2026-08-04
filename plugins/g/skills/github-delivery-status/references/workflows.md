# Delivery Status Workflow

## Preflight

Resolve the exact repository and PR, run the shared G-to-`gh` dependency gate,
and require verified authentication before the shared CLI call. Never infer
provider readiness from a cached response or an earlier HEAD.

## Exact read

From the G plugin root, run:

```sh
scripts/g --json pr delivery-status \
  --repo owner/repository \
  --pr 123 \
  --expected-head 0123456789abcdef0123456789abcdef01234567
```

The command reads GitHub GraphQL pull-request connections and the REST rules
and protection surfaces. It does not create configuration, cache state, hosted
content, or Git references.

## Interpretation

1. Require `ok=true`, the expected repository/PR, and exact-head equality.
2. Preserve lifecycle and automation observations separately.
3. Use `classification.disposition` for provider readiness.
4. Inspect `classification.blockers`, `pending`, `warnings`, and
   `completeness.unavailable_surfaces` before declaring terminal evidence.
5. Let the composing workflow combine provider status with its own acceptance,
   validation, review, topology, and authorization rules.

Do not reinterpret `ready-with-manual-action` as permission to merge. It proves
only that the remaining provider boundary is a manual restricted update.

## Recovery

- On `pending`, repeat a bounded caller-owned observation later without
  changing provider state.
- On head mismatch, discard the stale certificate and inspect the new exact
  HEAD.
- On `unknown`, inspect the reported unavailable surfaces or provider values;
  do not coerce the result to ready.
- On a transport or authentication failure, rerun the shared dependency gate;
  never change credentials or install tools implicitly.
- If the PR was merged or closed externally, report the current lifecycle and
  stop; do not perform post-merge work.
