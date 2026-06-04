# TanStack Skills Coverage Alignment Playbook

Use this playbook when asked to refresh or verify the local `plugins/tanstack/`
plugin against the upstream `tanstack-skills/tanstack-skills` plugin tree.

## Routing Rule

- Treat this as an explicit skill-specific refresh workflow, not generic
  repo-wide maintenance.
- Use `tanstack-skills/tanstack-skills` as the coverage inventory baseline.
- Use TanStack-owned docs as the authority for product-specific API and best
  practice details.
- Keep runtime `plugins/tanstack/skills/*/SKILL.md` files free of maintainer
  routing; maintainer-only procedure stays here.

## Current Local Shape

- This repo ships one broad Codex plugin: `plugins/tanstack/`.
- Do not add separate local plugin packages for upstream product plugins such
  as `tanstack-form` or bundle aliases such as `tanstack-all`.
- Product-level bundled skills are the direct-triggerable coverage units:
  `tanstack-ai`, `tanstack-cli`, `tanstack-config`, `tanstack-db`,
  `tanstack-devtools`, `tanstack-form`, `tanstack-pacer`, `tanstack-query`,
  `tanstack-ranger`, `tanstack-router`, `tanstack-start`, `tanstack-store`,
  `tanstack-table`, and `tanstack-virtual`.
- Focused Router, Start, and CLI skills remain available for direct triggering
  when their narrower concern is already known.
- `tanstack-integration` owns cross-stack Query, Router, Start, and broader
  product-composition decisions.

## Execution Flow

1. `inventory-local-surface`: inspect `plugins/tanstack/.codex-plugin/plugin.json`,
   bundled skill folders, `agents/openai.yaml`, local `references/*.md`, and
   coupled repo docs such as `README.md`.
2. `fetch-upstream-coverage`: inspect the current upstream plugin folders under
   `https://github.com/tanstack-skills/tanstack-skills/tree/main/plugins`.
3. `compare-product-coverage`: compare upstream product plugin names to local
   product-level bundled skills, ignoring upstream bundle aliases such as
   `tanstack-all`, `tanstack-core`, `tanstack-data`, and `tanstack-ui`.
4. `verify-product-facts`: for each changed product skill, check current
   TanStack-owned docs before updating API names, status labels, or best
   practice wording.
5. `refresh-local-guidance-if-needed`: update local skill docs, metadata,
   plugin manifest, README, and repo-level maintainer docs only when upstream
   coverage or official product docs create a meaningful delta.
6. `scoped-check`: run structure, metadata, and no-runtime-maintainer-reference
   checks across touched files.
7. `final-report`: use the release checklist schema and return `PASS (NOOP)`
   when no persistent updates were needed.

## Upstream Fetch Order

1. Upstream skills inventory:
   - `https://github.com/tanstack-skills/tanstack-skills/tree/main/plugins`
   - `https://github.com/tanstack-skills/tanstack-skills/blob/main/.claude-plugin/marketplace.json`
2. TanStack-owned product docs:
   - `https://tanstack.com/ai/latest/docs`
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

- Add a product-level bundled skill when upstream adds a new individual product
  plugin and the product has enough stable or useful TanStack-owned docs to
  support a runtime contract.
- Do not copy upstream skill text verbatim; write concise Codex runtime
  guidance and verify product details against TanStack-owned docs.
- Do not add upstream bundle aliases as local skills unless this repo
  intentionally changes its plugin packaging model.
- Keep focused sub-skills only where they reduce prompt weight for a recurring
  narrow workflow.
- Keep plugin manifest keywords, `README.md`, and `agents/openai.yaml` aligned
  whenever product coverage changes.

## Deliverable

Report:

- Which upstream product plugins were compared
- Which upstream bundle aliases were intentionally ignored
- Which TanStack-owned docs were checked
- Which local files changed, if any
- Which consistency checks were executed
- Why each persistent change was needed
