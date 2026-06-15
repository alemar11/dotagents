# TanStack AI

Use this reference when a task involves TanStack AI packages, provider-agnostic AI SDK usage, streaming responses, tool calling, structured output, multimodal content, workflows, orchestrators, or AG-UI interoperability.

TanStack AI is currently an alpha-area product. Verify exact package names and APIs against current official docs before making version-sensitive claims.

## What to Optimize For

- Type-safe message, tool, and structured-output contracts.
- Streaming behavior that is explicit about transport, cancellation, and partial state.
- Provider isolation so app code does not hard-code one model vendor unnecessarily.
- Clear runtime ownership for server-only secrets and client-visible state.
- Testable tool handlers and workflow steps.

## Workflow

1. Identify the AI boundary.
   Confirm whether the task is chat UI, structured output, tool execution, workflow orchestration, or AG-UI integration.
2. Check the installed package versions.
   Prefer the app's installed TanStack AI packages and current official docs over examples from blog posts.
3. Define typed contracts.
   Keep input, output, tool schemas, and streamed event shapes explicit.
4. Separate server and client responsibilities.
   Keep provider keys, model calls, and privileged tools server-side; keep UI state and streaming display client-safe.
5. Verify failure paths.
   Handle cancellation, partial streams, tool errors, retries, and provider-specific limits deliberately.

## Review Checklist

- Are tool inputs and structured outputs validated with a real schema?
- Is streaming state handled without assuming a single final response event?
- Are provider credentials and server-only tools kept out of client bundles?
- Does the UI handle cancellation, transient errors, and incomplete output?
- Are workflow or orchestrator steps small enough to test independently?

## Avoid

- Copying provider-specific SDK examples into TanStack AI code without an adapter boundary.
- Treating alpha APIs as stable without checking current docs.
- Letting tools mutate external systems without explicit validation and authorization.
- Hiding streaming and tool-call failures behind a generic catch block.

## Verification

Use current TanStack AI docs for API names, package names, and alpha caveats. For AG-UI or workflow behavior, verify against the exact installed TanStack AI package and any server framework runtime in the target app.
