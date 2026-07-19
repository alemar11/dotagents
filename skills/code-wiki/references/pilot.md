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
non-bypass filesystem sandbox. Source-bearing nodes use `workspace-write`,
whose only additional writable root is a per-node staging directory. The
runner materializes a separate read-only view containing only the node's
declared non-source inputs. The source-free renderer instead runs with an
ephemeral named permission profile: `:minimal` runtime files plus the declared
input view are readable, only its temporary working and staging roots are
writable, direct tool network access is disabled, and all other filesystem
reads are denied. Its ephemeral Codex home contains only runtime config and the
authentication material needed by the Codex process and is removed afterward.
The snapshot, original checkout, and durable run root are therefore not
available to renderer tools. The runner also removes their paths from copied
inventory metadata and the writable scaffold, then restores validator-owned
metadata only after the model exits. It promotes only declared node outputs,
rejects symlinks, completes a same-filesystem replacement first, and restores
the previous artifact if promotion fails.

For provenance, the durable run root keeps a verifier-only copy of each
declared input before renderer-specific metadata sanitization and a separate
copy of the exact sanitized input that the renderer receives. The former may
contain the run's already-recorded local source paths; it is not mounted into
the renderer's permission profile. Comparison re-hashes both copies so an
operator can prove which trusted preparation artifacts were transformed into
the source-free view without granting the renderer access to either the source
or the durable run root.
Bypass flags are forbidden. It
keeps stdout JSONL and stderr separately under `<run-out>/raw/`, fails closed on
malformed or missing terminal usage, and checks the snapshot before and after
every model call.

The test-only `--executor-fixture` and `--cache-root` options replay explicit
subprocess fixtures and isolate disposable snapshots. They must not be used as
live-run evidence.

## Two-Node Candidate Contract

The current candidate's passing path is exactly
`prepare -> study -> render -> validate -> reader`. `study` is the only broad
repository-study call and writes `artifacts/study.md`, with one complete,
evidence-backed section for every required wiki page. The runner validates page
order, coverage topics, repository-relative paths, and line ranges before
`render` may run. `render` consumes only the study brief and deterministic
scaffold, inventory, and claim-matrix artifacts; the source snapshot is not a
declared render input.

The normal candidate therefore records exactly two generation model calls.
After a deterministic validation failure, the graph may traverse
`validate -> repair -> validate` once and records repair as a third generation
call. Reader evaluation is one separate reader-bucket call. The loader rejects
the retired `study-architecture`, `study-interfaces`, `study-operations`, and
`synthesize` candidate node IDs.

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
  total model tokens; reasoning remains a separate output detail, so total is
  input plus output and does not add reasoning twice
- model-call count, failed terminal calls, strict validation, and reader result
- graph-aware call-shape evidence, including whether bounded repair occurred

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
derived metrics. It rejects stale or impossible call traces, requires the
candidate to have exactly two normal generation calls plus at most one repair,
and exposes the actual call count and repair state. It writes one canonical decision to `comparison.json` plus a
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

## 2026-07-19 Matched Canary

The first two-node canary used source commit
`cad0f764d4f3c302b2840068c3e321686faaeb57`, Code Wiki CLI `0.7.0`, Codex CLI
`0.144.5`, and `gpt-5.6-sol` with `xhigh` for both modes.

- Baseline completed one generation call, passed strict validation, and failed
  reader evaluation. Generation recorded input `6,282,478`, cached input
  `6,039,040`, uncached input `243,438`, output `66,112`, reasoning output
  `6,492`, total model tokens `6,348,590`, and wall time `1,479,063 ms`.
- Candidate completed one successful study terminal call with raw input
  `4,618,683`, cached input `4,387,072`, uncached input `231,611`, output
  `21,706`, reasoning output `5,320`, total model tokens `4,640,389`, and
  duration `568,384 ms`. Its deterministic study postcondition then rejected
  the brief, so render, validation, repair, and reader did not run.
- The final decision is `inconclusive`. Live provenance and shared identity
  passed, but evidence completeness and the required two-call shape failed;
  efficiency thresholds were not evaluated. No second paid pair was run.

The canary exposed two fixture-covered corrections in the shipped runner:
required coverage topics now apply across the complete page-by-page brief
while per-page word/evidence checks remain strict, and deterministic
postcondition failures preserve successful terminal usage without incrementing
failed terminal calls. These corrections do not change the canary verdict or
promote the candidate.

Closeout review additionally tightened the source-free render boundary with
the minimal declared-input view described above and made study-evidence path
validation resolve and contain each reference before reading it. Parent
traversal is rejected even when the escaped target exists. The runner now
preserves and hashes the exact sanitized render inputs plus per-node
input/output evidence copies, and comparison re-hashes those copies and the
durable study artifact. These post-canary corrections make the one pair legacy
evidence under the current comparator; its decision remains `inconclusive`,
and the paid pair was not retried.
