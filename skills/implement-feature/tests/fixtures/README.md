# Historical Run-State Fixtures

The compressed Base64 files are byte-exact copies of shipped
`skills/implement-feature/scripts/run-state` artifacts:

- `run-state-2.0.0.py.gz.b64` — commit
  `52991ddca22cf358503a7572b5716dadbed4ccd4`, SHA-256
  `af1ed9c8d8c685e954dd411f929b762dabee3f1052e2377d630557eb93153d7d`;
- `run-state-3.0.0.py.gz.b64` — commit
  `8c34c213b4ce8de70b56d0b7f30b7d3da7c0b156`, SHA-256
  `8e54d2926bba5aab3d39f79248e351db8f886dcaf24d5bfa31deb80940749068`.

Tests verify the decoded hash before execution, create schema 2 through each
artifact's public CLI, and drain active owners through public `run finish`.
Do not regenerate these fixtures from the current runtime.
