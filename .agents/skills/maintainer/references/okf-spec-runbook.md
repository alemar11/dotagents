# OKF Spec Runbook

This runbook is the canonical procedure for refreshing the bundled OKF spec
asset and validating the runtime OKF skill from within `Maintainer`.

## Scope

- Refresh `skills/okf/assets/spec.md` from
  `GoogleCloudPlatform/knowledge-catalog/okf/SPEC.md`.
- Refresh `skills/okf/assets/manifest.json`.
- Review and update `skills/okf/references/*.md` only when local routing or
  guidance materially drifts from the official spec.
- Keep refresh tooling under `.agents/skills/maintainer/`.

## Source Of Truth

- Repository: `GoogleCloudPlatform/knowledge-catalog`
- Ref: `main`
- Source path: `okf/SPEC.md`
- Official tree: `https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf`

Do not switch source repositories unless the official OKF project moves.

## Tooling

- Refresh script:
  `./.agents/skills/maintainer/scripts/okf_spec_refresh.py`
- Check script:
  `./.agents/skills/maintainer/scripts/okf_spec_check.py`

## Refresh Flow

1. Check freshness:
   - `python3 .agents/skills/maintainer/scripts/okf_spec_refresh.py --check-stale`
2. If stale, refresh:
   - `python3 .agents/skills/maintainer/scripts/okf_spec_refresh.py`
3. Validate runtime package shape:
   - `python3 .agents/skills/maintainer/scripts/okf_spec_check.py`
4. Run runtime CLI tests:
   - `python3 -m unittest discover -s skills/okf/tests`
5. Review fast-path references only if the spec changed:
   - `skills/okf/references/README.md`
   - `skills/okf/references/writing-okf.md`
   - `skills/okf/references/validation-modes.md`
   - `skills/okf/references/examples.md`

## Validation

- `python3 -m py_compile .agents/skills/maintainer/scripts/okf_spec_refresh.py .agents/skills/maintainer/scripts/okf_spec_check.py`
- `python3 .agents/skills/maintainer/scripts/okf_spec_refresh.py --check-stale`
- `python3 .agents/skills/maintainer/scripts/okf_spec_check.py`
- `python3 -m unittest discover -s skills/okf/tests`
- `git diff --check`
