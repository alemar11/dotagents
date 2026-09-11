# GitHub Tools Protocol Maintenance

`projects/github-tools/` is maintenance-only canonical source for the shared
provider-text protocol used by Yeet publish and GitHub Review Threads. It is
not a runtime dependency and must not be imported by skill scripts.

## Owned surfaces

- `src/github_provider_protocol/` owns `common.py`, `repository.py`,
  `integrity.py`, and `provider_text.py`.
- `scripts/sync-provider-protocol` resolves the repository root by anchored
  markers (`skills/` plus this project), not by `Path.parents[N]` depth, then
  copies those files into `skills/yeet/scripts/publish_lib/` and
  `skills/github-review-threads/scripts/reviews_lib/`.
- Runtime skills must use their local copies only. Stack, stars, and attachment
  keep narrow local helpers and do not consume this protocol package.

## Naming

Python import packages under this project and the synced skill copies use
underscores (`github_provider_protocol`, `publish_lib`, `reviews_lib`) because
Python import syntax cannot use hyphens. That is the documented compatibility
exception to repository lower-kebab directory naming. Public skill names and
shipped command nouns remain lower-kebab (`yeet`, `publish`, `reviews`).

## Validation

After any protocol edit, run:

```bash
projects/github-tools/scripts/sync-provider-protocol
projects/github-tools/scripts/sync-provider-protocol --check
python3 -m unittest discover -s projects/github-tools/tests -v
```

Also run the Yeet publish and GitHub Review Threads skill tests.
