# Markdown Node-Graph Pilot

Read this reference only when the user explicitly asks to run or inspect the
Code Wiki Markdown node-graph pilot. The ordinary Code Wiki workflow remains
the default.

## Runtime Contract

Start with the shipped artifact:

```bash
scripts/code-wiki --version
scripts/code-wiki --json doctor
```

`doctor` is read-only. It checks Python, Git, the local Codex CLI and required
`codex exec` flags, the workspace-write sandbox mode, both shipped Markdown
graphs, and whether the per-user live-provenance key already exists. It does not
create config, create a signing key, or invoke a model.

Run both modes against the same clean local Git checkout and full commit:

```bash
scripts/code-wiki --json pilot run \
  --mode baseline \
  --repo <clean-repo> \
  --commit <commit> \
  --out <baseline-outside-repo> \
  --model <model> \
  --reasoning-effort <low|medium|high|xhigh>

scripts/code-wiki --json pilot run \
  --mode node-graph \
  --repo <same-clean-repo> \
  --commit <same-commit> \
  --out <candidate-outside-repo> \
  --model <same-model> \
  --reasoning-effort <same-effort>
```

Each mode clones an isolated commit-pinned snapshot under
`~/.cache/dotagents/skills/code-wiki/pilot/`. The first live `pilot run` also
creates a mode-0600 signing key in that authorized disposable per-user cache;
later live runs reuse it. The key never appears in a run output or source
repository. The original checkout must be clean and is never granted to the
nested process as a writable directory. Tracked source symlinks are rejected
before inventory or model execution so a snapshot cannot expose host paths.
Unmaterialized gitlinks/submodules are rejected so a run never claims to have
studied a complete commit while omitting pinned source trees.

Every agent node uses `codex exec --ephemeral --json`, an explicit model,
reasoning effort, a separate temporary writable working directory, and a
`workspace-write` sandbox whose only additional writable root is a per-node
staging directory. The commit snapshot and durable run output are available
only as disjoint read paths. The runner promotes only declared node outputs
after the process exits, rejects symlinks, completes a same-filesystem
replacement first, and restores the previous artifact if promotion fails.
Bypass flags are forbidden. It
keeps stdout JSONL and stderr separately under `<run-out>/raw/`, fails closed on
malformed or missing terminal usage, and checks the snapshot before and after
every model call.

The test-only `--executor-fixture` and `--cache-root` options replay explicit
subprocess fixtures and isolate disposable snapshots. They must not be used as
live-run evidence.

## Run Results

Each output root contains the generated `wiki/`, raw process evidence,
deterministic validation evidence, reader evidence, and `run.json`. The
manifest records:

- source commit, original-checkout proof, snapshot hashes, and mutation result
- graph and node hashes, Code Wiki and Codex CLI versions, model, and effort
- `execution_evidence=live|fixture`; fixture runs are always comparison-inconclusive
- a runner-owned `artifacts/execution-provenance.json` receipt that binds that
  evidence type to the complete manifest evidence and every raw stdout/stderr
  invocation hash; live receipts are HMAC-signed by the per-user cache key
  while fixtures stay unsigned
- node status, attempts, input/output artifact hashes, timestamps, and duration
- generation and reader usage kept in separate metric buckets
- input, cached input, derived uncached input, output, reasoning output, and
  total model tokens
- model-call count, failed terminal calls, strict validation, and reader result

Mutable status exists only in JSON. Markdown files under
`references/pilot-nodes/` are immutable execution contracts and prompts.

## Deterministic Comparison

```bash
scripts/code-wiki --json pilot compare \
  --baseline-run <baseline-out>/run.json \
  --candidate-run <candidate-out>/run.json \
  --out <comparison-out>
```

The comparison output must be disjoint from both run roots. The command treats
both manifests as untrusted, validates current graph and
node hashes, re-hashes both wiki trees, confirms the final wiki matches the
strict-validation hash, re-hashes validation and reader evidence, verifies each
live provenance signature and raw invocation, then checks run identity and all
derived metrics. It writes one canonical decision to `comparison.json` plus a
direct rendering in `comparison.md`.

`promotion_status` is one of `promote`, `revise`, `reject`, or `inconclusive`.
`promote` requires matching source, model, effort, Codex CLI, Code Wiki CLI,
and reader contract; strict validation and identical reader evaluation passing
for both; no candidate-only material gap; candidate uncached input at least
20% lower; candidate total generation model tokens no higher; candidate wall
time at most 125% of baseline; and no source mutation or failed terminal call.

Identity drift, missing or malformed evidence, evaluator failure, invalid
hashes, incomplete runs, or a zero baseline denominator are `inconclusive`.
Fixture-backed inputs are also always `inconclusive`, even when every synthetic
threshold passes.
Candidate-only quality or safety regressions are `reject`. Passing quality and
safety with a missed efficiency threshold is `revise`.

The report never changes Code Wiki's default workflow. Promotion requires a
separate explicit product decision.
