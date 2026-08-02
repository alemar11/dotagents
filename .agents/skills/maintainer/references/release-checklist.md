# Release Checklist

Run this checklist before finalizing maintainer updates.

## 1. Resolve Scope And Lanes

- Confirm the requested packages and directly coupled repo docs.
- Select every applicable lane from `validation-matrix.md`.
- Confirm substantial reshapes used `$skill-creator` or `$plugin-creator` first.
- Confirm unrelated dirty worktree changes are preserved and excluded.

## 2. Package And Policy Consistency

- Align skill names/descriptions across `SKILL.md`, `agents/openai.yaml`, README,
  manifests, and marketplace entries in scope.
- Verify required files, lowercase `references/*.md` names, and referenced
  scripts/docs.
- Scan for stale names, paths, invocations, dependencies, install prompts, and
  retired discovery surfaces.
- Reconcile Codex-dependency classification and runtime/maintenance boundaries.
- For plugin changes, verify the semantic version bump, embedded CLI alignment,
  deterministic artifact, install/cache parity, and clean reinstall.

## 3. Execute Validation

- Run every selected validation lane and record its commands and results.
- Run native `codex review` for non-trivial implementations and resolve or explicitly
  disposition accepted findings.
- Treat a missing required lane as `result=fail` unless the user explicitly accepts a
  narrower result.

## 4. Review Evidence Efficiently

During iteration use:

- `git status --short --branch`
- `git diff --stat`
- `git diff --name-only`
- `git diff --check`
- focused `git diff -- <paths>`

Read the complete relevant diff once before final review and publication. Carry
artifact paths/refs, fingerprints, changed sections, proof results, and failed
gate excerpts instead of repeatedly reproducing complete unchanged artifacts.

## 5. Commit And Publication

Resolve commit, push, PR, and other publication authority independently.
Otherwise stop after validation and report the dirty diff without staging or
changing Git history.

- With explicit commit authority, stage only explicit paths, inspect the staged
  diff, and split multiple skills/plugins or distinct migration intents into
  meaningful commits.
- With push-only authority, do not stage or commit. Verify the existing commit
  range and push only those commits.
- With PR or other publication authority, use the matching publication workflow
  and its own scope rules. Do not infer commit authority from a bare PR request,
  or PR/publication authority from commit or push authority.
- Prefer the matching G workflow when installed. Direct scoped `git` is
  the fallback for explicitly authorized commit/push operations when G is
  unavailable.
- After an authorized commit or push, verify the exact commit range, branch
  divergence, and that authorized paths plus the staged set are clean. Confirm
  unrelated pre-existing changes remain unchanged; global worktree cleanliness
  is not required. Do not claim an external mutation from a suggestion or
  attempted command; verify resulting state.

## Final Report

- `result`: `pass` or `fail`
- `change_state`: `changed` or `no-change`
- Scope: `<packages and workflow covered>`
- Validation lanes: `<selected lanes>`
- Commands run: `<key commands in order>`
- Files changed: `<paths>` or `none`
- Why changed: `<rationale per target>`; use `not applicable` when
  `change_state=no-change`
- Runtime evidence: `<sessions/logs/tests used>` or `not applicable`
- Health evidence: `<size band, representative path, escalation, and applicable validation>`
  or `not applicable`
- Artifacts/install state: `<versions, fingerprints, cache/reinstall proof>` or `not applicable`
- Findings: `<blocking and warning items>`
- Follow-ups: `<deferred work>`
