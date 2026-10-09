# OKF Spec Refresh Playbook

Use this playbook when asked to refresh the bundled OKF spec for `skills/okf/`
or review whether the local OKF skill is aligned with the official spec.

## Routing Rule

- Keep `okf` runtime behavior focused on writing, scaffolding, and validating
  OKF bundles.
- Keep official spec refresh scripts, checks, and network mechanics in this
  `Maintainer` skill.
- Run when directly requested or selected by routine maintenance for this
  package. Routine maintenance authorizes refreshing stale managed sources;
  review-only requests remain read-only. Do not expand a direct refresh request
  into unrelated maintenance.

## Execution Flow

1. `syntax-check`: run
   `python3 -m py_compile .agents/skills/maintainer/scripts/okf_spec_refresh.py .agents/skills/maintainer/scripts/okf_spec_check.py`.
2. `staleness-check`: run
   `python3 .agents/skills/maintainer/scripts/okf_spec_refresh.py --check-stale`.
3. `refresh-if-needed`: if the bundled spec or manifest is stale, run
   `python3 .agents/skills/maintainer/scripts/okf_spec_refresh.py`.
4. `runtime-check`: run
   `python3 .agents/skills/maintainer/scripts/okf_spec_check.py`.
5. `cli-tests`: run `python3 -m unittest discover -s skills/okf/tests`.
6. `final-report`: use the release checklist schema and return `result=pass`
   with `change_state=no-change`
   if the spec was already current and no persistent edits were needed.

## Read-only Evaluation Mode

For audit, review, or dry-run, check freshness and integrity without refreshing
or editing references. Report whether the official spec changed. A targeted
`maintain okf` follows routine maintenance, including refresh when stale.

## Guardrails

- Do not add Maintainer commands or routing references to `skills/okf/` runtime
  docs.
- Treat `skills/okf/assets/spec.md` as the bundled official source copy.
- Treat `skills/okf/references/*.md` as task-oriented fast paths, not a second
  full copy of the spec.
- Update curated references only when upstream changes alter runtime guidance
  or local links.
