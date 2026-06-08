# Accessibility, Performance, and Memory

Use these focused workflows after the basic page-control workflow is working.

## Accessibility

Start with Lighthouse for a baseline:

```sh
chrome-devtools lighthouse_audit --mode navigation --outputDirPath ./lighthouse
```

Then inspect semantics and keyboard behavior:

1. `take_snapshot` to read the accessibility tree.
2. Check landmarks, headings, accessible names, form labels, and image text
   alternatives from the snapshot.
3. Use `press_key "Tab"` and repeated snapshots to verify focus order.
4. Use `list_console_messages --types issue --includePreservedMessages true`
   for browser-reported accessibility issues.
5. Use `take_screenshot` only when visual layout, tap target spacing, or color
   contrast needs visual evidence.

## LCP and Core Web Vitals

Record a reload trace:

```sh
chrome-devtools performance_start_trace --reload true --autoStop true --filePath trace.json
```

Use the returned insight set IDs with:

```sh
chrome-devtools performance_analyze_insight "<insightSetId>" "LCPBreakdown"
chrome-devtools performance_analyze_insight "<insightSetId>" "DocumentLatency"
chrome-devtools performance_analyze_insight "<insightSetId>" "RenderBlocking"
chrome-devtools performance_analyze_insight "<insightSetId>" "LCPDiscovery"
```

Then identify the LCP element with `evaluate_script` and correlate its resource
URL against `list_network_requests` / `get_network_request`. Prioritize fixes by
which subpart dominates: TTFB, resource load delay, resource load duration, or
element render delay.

## Emulated performance checks

Use constrained emulation to reveal mobile or slower-device issues:

```sh
chrome-devtools emulate --networkConditions "Fast 3G" --cpuThrottlingRate 4
chrome-devtools emulate --viewport "390x844"
```

Re-run the trace after a fix and compare the same insight names. Do not claim an
LCP improvement from unrelated tests; use the trace evidence.

## Memory leaks

For frontend memory leaks:

1. Navigate to the target state.
2. Take a baseline heap snapshot.
3. Repeat the suspected leaking interaction several times.
4. Take a target heap snapshot.
5. Revert to the original state if possible and take a final snapshot.

Use heap snapshots as files; do not load raw `.heapsnapshot` content into the
model context. Prefer a heap analysis tool such as `memlab` or a purpose-built
Node script to compare snapshots and report growing retained objects.

Enable experimental memory tooling when needed:

```sh
chrome-devtools-mcp --experimentalMemory=true --no-usage-statistics
chrome-devtools take_heapsnapshot ./baseline.heapsnapshot
```
