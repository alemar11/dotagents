# code-wiki Helper Scripts

`scripts/code-wiki` is the only public executable surface for this skill. The
`scripts/code_wiki/` package is shipped internal runtime code; docs, tests, and
examples must use the launcher instead of package modules.

From the repository root, start with:

```bash
skills/code-wiki/scripts/code-wiki --help
skills/code-wiki/scripts/code-wiki --version
skills/code-wiki/scripts/code-wiki --json doctor
```

`scripts/code_wiki/version.py` is the single semver source and currently
reports `0.8.0`. The standard-library-only CLI keeps existing inventory,
synthesize, scaffold, evidence-link, and validate commands compatible.

## Opt-In Pilot

The pilot is never selected by an ordinary Code Wiki request. An explicit run
uses the unchanged baseline or the two-node candidate (`study -> render`):
source-bearing nodes use the non-bypass workspace sandbox, while `render` uses
an ephemeral named permission profile that can read only minimal runtime files
and its declared input view and can write only its working and staging roots.

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

scripts/code-wiki --json pilot aggregate \
  --comparison react=<react-comparison>/comparison.json \
  --comparison cli=<cli-comparison>/comparison.json \
  --out <aggregate-out>
```

`doctor` is read-only and invokes no model or key creation. Pilot runs create
disposable clean snapshots under `~/.cache/dotagents/skills/code-wiki/pilot/`;
the first live run also creates a mode-0600 provenance key there. Durable
wikis, raw JSONL/stderr, manifests, reader evidence, and comparisons remain
under the selected output. Nested Codex calls use fresh ephemeral contexts,
explicit model and effort, and a non-bypass workspace sandbox whose sole added
writable root is a per-node staging directory.

The candidate writes a versioned typed `artifacts/study.json` containing fixed
pages, adaptive deep dives, structured claims, and explicit path/start/end
evidence. Invalid study JSON terminates before render without retry. Render has
no source input. Safe tracked source links are accepted only when relative,
existing, acyclic, and contained; their raw and resolved identities plus target
content hashes are recorded. Generated outputs remain symlink-free.

`--executor-fixture` and `--cache-root` are explicit test-only run options.
They emit `execution_evidence=fixture`, cannot produce a promotion decision,
and may be used together only with a cache root disjoint from source and
output. The runner-owned execution-provenance receipt binds this classification
to complete manifest evidence and raw stdout/stderr invocation hashes. Live
receipts are signed with the per-user key, and comparison independently verifies
them. A passing candidate records exactly two generation calls; its one optional
bounded repair is a visible third call, while reader usage stays in the reader
bucket. A complete reader-failing baseline remains evaluable, but the candidate
must pass quality and safety absolutely. Aggregation accepts exactly two named
comparison objects and applies `reject`, `inconclusive`, `revise`, then
`promote` precedence. Under `--json`, command errors return an
`ok=false` object without credentials. See `../references/pilot.md` for typed
manifest fields, safety rules, exact thresholds, and result semantics.

The retained 2026-07-22 live evidence is React=`reject`, GitHub
CLI=`inconclusive`, aggregate=`reject`. The CLI candidate is historical
incomplete evidence rather than a completed run, and a later React reader
transport failure produced no replacement decision. These results do not
change the pilot's opt-in status or the ordinary Code Wiki default.
