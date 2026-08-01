# AutoReview Maintenance

`skills/autoreview/` owns the read-only closeout reviewer and its shipped
launcher. Runtime behavior belongs in `SKILL.md`, `references/review-policy.md`,
and `references/evidence-chain.md`.

## Owned surfaces

- `scripts/autoreview` is the public artifact; `scripts/autoreview-protocol`,
  `scripts/*.py`, and `tests/` are its coupled implementation and regression
  surfaces.
- `scripts/autoreview` contains the CLI version source of truth. Keep the
  protocol and evidence schema versions distinct from the CLI version.
- The helper is Codex-dependent and remains read-only: it must not gain tracker,
  merge, deployment, or repository-fix authority.

## Validation

- For runtime changes, run the focused unittest suite from the repository root
  and verify the shipped artifact with `--help`, `--version`, `--json doctor`,
  and a safe local/dry-run fixture.
- Keep review-policy and evidence-chain changes synchronized with the structured
  result contract and its tests. Do not encode caller-owned orchestration state
  in this package.
