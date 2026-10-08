# TanStack AI

Use this reference for TanStack AI chat, tools, structured output, typed
decisions, media, agents, persistence, memory, MCP, sandbox execution, runtime
skills, UI adapters, or AG-UI interoperability.

TanStack AI remains a 0.x product. Inspect the installed core, provider,
framework, and companion packages together; verify API and capability support
against their version's docs and packaged first-party skills via [Intent](intent.md).

## Choose the Boundary

| Concern | Package or official guide |
| --- | --- |
| Chat, typed tools, streaming, middleware, subagents | `@tanstack/ai`; [core overview](https://tanstack.com/ai/latest/docs/getting-started/overview) |
| Client state, transport, framework UI, React Native | `@tanstack/ai-client` and the matching framework adapter; [quick start](https://tanstack.com/ai/latest/docs/getting-started/quick-start) |
| Structured extraction or streamed objects | Core `chat({ outputSchema })`; [structured outputs](https://tanstack.com/ai/latest/docs/structured-outputs/overview) |
| Typed choice, score, or boolean decisions | Core `decide()` and a supported evaluate adapter; [evaluate](https://tanstack.com/ai/latest/docs/evaluate/evaluate) |
| Embeddings, reranking, image, audio, video, live or world generation | Select the provider and activity from the current docs; a chat adapter does not imply every modality is supported |
| Server transcripts and run state | `@tanstack/ai-persistence`; [persistence](https://tanstack.com/ai/latest/docs/persistence/overview) |
| Reconnecting to an in-flight run | Core memory streams or `@tanstack/ai-durable-stream`; [resumable streams](https://tanstack.com/ai/latest/docs/resumable-streams/overview); separate from transcript persistence |
| Cross-conversation recall | `@tanstack/ai-memory`; [memory](https://tanstack.com/ai/latest/docs/memory/overview) |
| MCP clients, tools, resources, prompts, or servers | `@tanstack/ai-mcp`; [client integration](https://tanstack.com/ai/latest/docs/tools/mcp) or [server](https://tanstack.com/ai/latest/docs/mcp/server) |
| Harness execution and workspace lifecycle | `@tanstack/ai-sandbox` plus a provider and harness adapter; [sandboxes](https://tanstack.com/ai/latest/docs/sandbox/overview) |
| Model-written code calling tools | `@tanstack/ai-code-mode`; [Code Mode](https://tanstack.com/ai/latest/docs/code-mode/code-mode) |
| The application's model loading portable skills | `@tanstack/ai-skills`; [runtime skills](https://tanstack.com/ai/latest/docs/skills/agent-skills) |

The runtime skills above are distinct from Intent's guidance for the coding
assistant and from provider-hosted skills. Install only the companion packages
required by the application; inspect their packaged skills for narrower tasks.

## Workflow

1. Establish ownership and contracts.
   Identify the provider activity, framework, transport, message schema, tool
   schemas, and storage owner. Keep application credentials and privileged
   tools server-side; use explicit BYOK design only when the user owns a
   browser-supplied credential.
2. Use the installed TanStack API.
   Prefer `chat()`, `toolDefinition()` and provider adapters from the matching
   packages. Do not transplant another SDK's `streamText`, lifecycle callbacks,
   or provider factory names. Use middleware for supported lifecycle behavior.
3. Separate streaming, persistence, and execution.
   Decide who owns the transcript and whether reconnection must resume an
   active run. A saved transcript or sandbox workspace does not itself make
   the running computation durable.
4. Model human decisions explicitly.
   Follow [interrupts](https://tanstack.com/ai/latest/docs/interrupts/overview)
   for tool approvals and typed client input. An interrupted run ends; answers
   start a new continuation run. Preserve run and thread identity on replay.
5. Validate observable failure paths.
   Exercise cancellation, partial streams, schema failures, tool rejection,
   reconnects, reloads, and provider-specific limits for the selected boundary.
   Check tenant authorization on persisted state and externally executing tools.

## Verification

Use the official [package skills guide](https://tanstack.com/ai/latest/docs/getting-started/agent-skills)
for current first-party coverage. Check installed provider capabilities rather
than inferring support from a common interface. Keep streaming Markdown's trust
and rendering policy in [Markdown](markdown.md), and verify framework UI,
AG-UI events, and server behavior together in the target app.
