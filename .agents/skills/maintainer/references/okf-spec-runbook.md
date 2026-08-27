# OKF Spec Runbook

This runbook is the canonical procedure for refreshing the bundled OKF spec
asset and validating the runtime OKF skill from within `Maintainer`.

## Scope

- Refresh `skills/okf/assets/spec.md` from
  `GoogleCloudPlatform/open-knowledge-format/SPEC.md`.
- Refresh `skills/okf/assets/manifest.json`.
- Review and update `skills/okf/references/*.md` only when local routing or
  guidance materially drifts from the official spec.
- Keep refresh tooling under `.agents/skills/maintainer/`.

## Source Of Truth

- Repository: `GoogleCloudPlatform/open-knowledge-format`
- Ref: `main`
- Source path: `SPEC.md`
- Official tree: `https://github.com/GoogleCloudPlatform/open-knowledge-format/tree/main`

The former `GoogleCloudPlatform/knowledge-catalog/okf` tree is a frozen
snapshot. Do not use it for freshness checks. If the official OKF project moves
again, update the refresh constants, checker expectations, this runbook, and
the task menu together before refreshing assets.

## Tooling

- Refresh script:
  `./.agents/skills/maintainer/scripts/okf_spec_refresh.py`
- Check script:
  `./.agents/skills/maintainer/scripts/okf_spec_check.py`

## Refresh Flow

1. Check freshness:
   - `python3 .agents/skills/maintainer/scripts/okf_spec_refresh.py --check-stale`
   - Add `--fail-if-stale` when the check is being used as a CI freshness gate.
2. If stale, refresh:
   - `python3 .agents/skills/maintainer/scripts/okf_spec_refresh.py`
3. Validate runtime package shape:
   - `python3 .agents/skills/maintainer/scripts/okf_spec_check.py`
4. Run runtime CLI tests:
   - `python3 -m unittest discover -s skills/okf/tests`
5. Review fast-path references only if the spec changed:
   - `skills/okf/references/README.md`
   - `skills/okf/references/writing-okf.md`
   - `skills/okf/references/validation.md`
   - `skills/okf/references/examples.md`

## Validation

- `python3 -m py_compile .agents/skills/maintainer/scripts/okf_spec_refresh.py .agents/skills/maintainer/scripts/okf_spec_check.py`
- `python3 .agents/skills/maintainer/scripts/okf_spec_refresh.py --check-stale`
- `python3 .agents/skills/maintainer/scripts/okf_spec_check.py`
- `python3 -m unittest discover -s skills/okf/tests`
- `git diff --check -- . ':(exclude)skills/okf/assets/spec.md'`

Also inspect raw `git diff --check`. If it reports whitespace copied verbatim
from `skills/okf/assets/spec.md`, accept that asset-only output only after
`okf_spec_check.py` proves the bundled content hash matches the manifest. Do not
normalize the official asset independently.
