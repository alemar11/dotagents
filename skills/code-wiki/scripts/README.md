# code-wiki Helper Scripts

`scripts/code-wiki` is the only public executable surface for this skill. The
`scripts/code_wiki/` package is shipped internal runtime code; docs, tests, and
examples must use the launcher instead of package modules.

Start with:

```bash
scripts/code-wiki --help
scripts/code-wiki --version
scripts/code-wiki --json doctor
```

`scripts/code_wiki/version.py` is the single semver source and currently
reports `0.7.0`. The standard-library-only CLI keeps existing inventory,
synthesize, scaffold, evidence-link, and validate commands compatible.

## Opt-In Pilot

The pilot is never selected by an ordinary Code Wiki request. An explicit run
uses:

```bash
scripts/code-wiki --json pilot run \
  --mode <baseline|node-graph> \
  --repo <clean-git-repo> \
  --commit <commit> \
  --out <output-outside-repo> \
  --model <model> \
  --reasoning-effort <low|medium|high|xhigh>

scripts/code-wiki --json pilot compare \
  --baseline-run <baseline-out>/run.json \
  --candidate-run <candidate-out>/run.json \
  --out <comparison-out>
```

`doctor` is read-only and invokes no model or key creation. Pilot runs create
disposable clean snapshots under `~/.cache/dotagents/skills/code-wiki/pilot/`;
the first live run also creates a mode-0600 provenance key there. Durable
wikis, raw JSONL/stderr, manifests, reader evidence, and comparisons remain
under the selected output. Nested Codex calls use fresh ephemeral contexts,
explicit model and effort, and a non-bypass workspace sandbox whose sole added
writable root is a per-node staging directory.

`--executor-fixture` and `--cache-root` are explicit test-only run options.
They emit `execution_evidence=fixture`, cannot produce a promotion decision,
and may be used together only with a cache root disjoint from source and
output. The runner-owned execution-provenance receipt binds this classification
to complete manifest evidence and raw stdout/stderr invocation hashes. Live
receipts are signed with the per-user key, and comparison independently verifies
them. Under `--json`, command errors return an
`ok=false` object without credentials. See `../references/pilot.md` for typed
manifest fields, safety rules, exact thresholds, and result semantics.
