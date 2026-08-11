# TanStack Skills Coverage Alignment Playbook

Use this playbook when asked to refresh or verify the local `skills/tanstack/`
skill against the upstream `tanstack-skills/tanstack-skills` plugin tree and
the current official TanStack product docs.

## Routing Rule

- Treat this as an explicit skill-specific refresh workflow, not generic
  repo-wide maintenance.
- Use `tanstack-skills/tanstack-skills` as the skill coverage inventory
  baseline, then check TanStack-owned product docs for official products that
  are newer than that inventory.
- Use TanStack-owned docs as the authority for product-specific API and best
  practice details.
- Keep runtime `skills/tanstack/SKILL.md` and `skills/tanstack/references/*.md`
  files free of maintainer routing; maintainer-only procedure stays here.

## Current Local Shape

- This repo ships one broad reusable skill: `skills/tanstack/`.
- Do not add separate local plugin packages or standalone product skills for
  upstream product plugins such as `tanstack-form` or bundle aliases such as
  `tanstack-all`.
- Product-level references are the coverage units: `ai.md`, `charts.md`, `cli.md`,
  `config.md`, `db.md`, `devtools.md`, `form.md`, `pacer.md`, `query.md`,
  `ranger.md`, `router.md`, `start.md`, `store.md`, `table.md`, and
  `virtual.md`.
- Focused Router, Start, and CLI concerns live under focused
  `references/*.md` files when their narrower concern is already known.
- `integration.md` owns cross-stack Query, Router, Start, and broader
  product-composition decisions.

## Execution Flow

1. `inventory-local-surface`: inspect `skills/tanstack/SKILL.md`,
   `skills/tanstack/agents/openai.yaml`, local `references/*.md`, and coupled
   repo docs such as `README.md`.
2. `fetch-upstream-coverage`: inspect the current upstream plugin folders under
   `https://github.com/tanstack-skills/tanstack-skills/tree/main/plugins`.
3. `compare-product-coverage`: compare upstream product plugin names and the
   current official TanStack product docs to local product-level references,
   ignoring upstream bundle aliases such as `tanstack-all`, `tanstack-core`,
   `tanstack-data`, and `tanstack-ui`.
4. `verify-product-facts`: for each changed product reference, check current
   TanStack-owned docs before updating API names, status labels, or best
   practice wording.
5. `refresh-local-guidance-if-needed`: update local skill docs, metadata,
   README, and repo-level maintainer docs only when upstream
   coverage or official product docs create a meaningful delta.
6. `scoped-check`: run structure, metadata, and no-runtime-maintainer-reference
   checks across touched files.
7. `final-report`: use the release checklist schema and return `result=pass`
   with `change_state=no-change`
   when no persistent updates were needed.

## Upstream Fetch Order

1. Upstream skills inventory:
   - `https://github.com/tanstack-skills/tanstack-skills/tree/main/plugins`
   - `https://github.com/tanstack-skills/tanstack-skills/blob/main/.claude-plugin/marketplace.json`
2. TanStack-owned product docs:
   - `https://tanstack.com/ai/latest/docs`
   - `https://tanstack.com/charts/latest/docs`
   - `https://tanstack.com/cli/latest/docs`
   - `https://tanstack.com/config/latest/docs`
   - `https://tanstack.com/db/latest/docs`
   - `https://tanstack.com/devtools/latest/docs`
   - `https://tanstack.com/form/latest/docs`
   - `https://tanstack.com/pacer/latest/docs`
   - `https://tanstack.com/query/latest/docs`
   - `https://tanstack.com/ranger/latest/docs`
   - `https://tanstack.com/router/latest`
   - `https://tanstack.com/start/latest/docs`
   - `https://tanstack.com/store/latest/docs`
   - `https://tanstack.com/table/latest/docs`
   - `https://tanstack.com/virtual/latest/docs`
3. Installed package metadata only when docs and upstream skills do not make
   current package names or status clear enough.

## Coverage Rules

- Add a product-level reference when upstream adds a new individual product
  plugin, or when an official TanStack product appears before upstream skill
  coverage, and the product has enough useful TanStack-owned docs to support a
  runtime contract. State maturity caveats for prerelease products.
- Do not copy upstream skill text verbatim; write concise Codex runtime
  guidance and verify product details against TanStack-owned docs.
- Do not add upstream bundle aliases as local skills unless this repo
  intentionally changes its reusable-skill packaging model.
- Keep narrow Router, Start, and CLI guidance in focused references under
  `skills/tanstack/` unless a new direct-trigger skill is deliberately justified.
- Keep `README.md`, `SKILL.md`, and `agents/openai.yaml` aligned whenever
  product coverage changes.

## Branch Report Additions

- Which upstream product plugins were compared
- Which upstream bundle aliases were intentionally ignored
- Which TanStack-owned docs were checked

Add these items to the common final report owned by `release-checklist.md`.
