# Historical Evidence

Use this branch for audits of completed or prior behavior. Live monitoring uses
`live-monitoring.md` instead and never falls back here to fill a current-state
gap.

## Canonical Order

1. Read the editable target's current discovery metadata, entrypoint, directly
   relevant references, owning manifest, and adjacent repository docs.
2. Check cheap current consistency and maintenance evidence such as `git log`
   for the resolved target.
3. Search the memory index, then open only the one to three rollout summaries
   most relevant to the target and question.
4. Inspect a representative raw session when claiming runtime behavior, false
   or missed triggers, correctness, orchestration behavior, or low value. If no
   representative trace is available, state that limitation.
5. Treat helper output as evidence, never cleanup or mutation authority.

## Targeted Session Evidence

Run from the `skill-audit` owner root:

```bash
scripts/session-evidence \
  --target my-skill \
  --target-path /path/to/my-skill/SKILL.md \
  --runtime-pattern 'my-skill=my-tool|my-command' \
  --root "$CODEX_HOME/sessions" \
  --since 2026-04-01 \
  --include-zero
```

The helper reports `explicit-user`, `skill-injection`, `opened-skill-doc`, and
`runtime-command` evidence records from direct function calls and code-mode
custom tool calls. Examples retain stable item identity, transport,
`thread_source`, `parent_thread_id`, and raw `forked_from_id` where available.
It excludes tool output and tool discovery as usage.

Read a representative trace before making a high-risk behavioral claim. A
zero-evidence result is not proof that the surface has no value.
