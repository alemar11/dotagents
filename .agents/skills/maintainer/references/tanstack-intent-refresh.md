# TanStack Intent Coverage Refresh Playbook

Use this playbook when asked to review or refresh TanStack Intent coverage for
the local `skills/tanstack/` skill.

## Routing Rule

- Treat this as an explicit skill-specific refresh workflow, not as generic
  repo-wide maintenance.
- Review current upstream TanStack Intent coverage before changing local
  verification wording or skill scope.
- Keep runtime `skills/tanstack/SKILL.md` and `skills/tanstack/references/*.md`
  files free of maintainer routing; any maintainer-only review procedure stays here.

## Current Local Layout

- Treat `skills/tanstack/` as one broad reusable skill surface for the TanStack
  portfolio.
- Product-level references are stable routing units for AI, Charts, CLI,
  Config, DB, Devtools, Form, Highlight, Hotkeys, Markdown, Pacer, Query,
  Ranger, Router, Start, Store, Table, and Virtual.
- `references/integration.md` owns cross-stack composition guidance.
- `references/router.md`, `references/start.md`, and `references/cli.md` own
  dense workflow routing through local focused `references/*.md` files rather
  than separate narrow skill directories.
- When upstream coverage expands, prefer:
  - refreshing `$tanstack` plus `references/*.md` routing first
  - then adding a new product reference only when the workflow boundary truly
    needs its own reference file

## Execution Flow (Mandatory Order)

1. `inventory-local-surface`: inspect `skills/tanstack/SKILL.md`,
   `skills/tanstack/agents/openai.yaml`, product and focused
   `references/*.md` files, and coupled repo docs such as `README.md` to
   capture the current local claims.
2. `review-upstream-coverage`: check the current TanStack Intent registry and the
   relevant official package pages on `tanstack.com` for first-party Intent
   coverage relevant to the local skill, especially Router, Start, CLI, and any
   newly added Query-related surface.
3. `compare-coverage`: identify whether new upstream first-party Intent skills
   materially change the correct local guidance, such as skill scope wording,
   reference routing, verification fallbacks, or which TanStack packages should be
   called out.
4. `refresh-local-guidance-if-needed`: update local skill metadata or docs only
   when upstream coverage changes create a real guidance delta. Keep wording
   precise and avoid speculating about unshipped Intent surfaces.
5. `scoped-check`: run a scoped consistency pass across touched TanStack skill
   files and any directly coupled repo docs.
6. `final-report`: use the release checklist schema and return `result=pass`
   with `change_state=no-change` if
   no persistent updates were needed.

## Read-only Evaluation Mode

When the user asks only for a review:

- Run `inventory-local-surface`.
- Run `review-upstream-coverage`.
- Run `compare-coverage`.
- Do not make persistent edits unless the user explicitly asks to refresh or
  update the local skill guidance.

## Upstream Fetch Order

Use TanStack-owned public sources first and prefer `latest` documentation
surfaces when they exist.

1. TanStack Intent registry index:
   - `https://tanstack.com/intent/registry`
   - Use this to discover which first-party packages currently ship skills.
2. TanStack Intent package pages:
   - `https://tanstack.com/intent/registry/%40tanstack__router-core`
   - `https://tanstack.com/intent/registry/%40tanstack__router-plugin`
   - `https://tanstack.com/intent/registry/%40tanstack__react-start`
   - `https://tanstack.com/intent/registry/%40tanstack__start-client-core`
   - `https://tanstack.com/intent/registry/%40tanstack__start-server-core`
   - `https://tanstack.com/intent/registry/%2540tanstack%252Fcli`
   - `https://tanstack.com/intent/registry/%2540tanstack%252Fcharts`
   - `https://tanstack.com/intent/registry/%2540tanstack%252Fhighlight`
   - `https://tanstack.com/intent/registry/%2540tanstack%252Fmarkdown`
   - `https://tanstack.com/intent/registry/%2540tanstack%252Ftable-core`
   - Use package pages and their skill pages to capture the current skill tree,
     current wording, and any version notes surfaced in the page content.
3. TanStack Intent docs:
   - `https://tanstack.com/intent/latest/docs`
   - `https://tanstack.com/intent/latest/docs/registry`
   - Use these to confirm current Intent packaging, discovery, validation, and
     staleness mechanics.
4. Product docs on `latest` endpoints:
   - `https://tanstack.com/charts/latest/docs`
   - `https://tanstack.com/hotkeys/latest/docs`
   - `https://tanstack.com/markdown/latest/docs`
   - `https://tanstack.com/highlight/latest/docs`
   - `https://tanstack.com/router/latest`
   - `https://tanstack.com/start/latest/docs`
   - `https://tanstack.com/cli/latest/docs`
   - Use these to refresh `$tanstack` guidance and `references/*.md` routing when
     the official docs reorganize task boundaries or terminology.
5. Fallback for ambiguous package-version questions:
   - Use npm package metadata only when the TanStack registry page or product
     docs do not make the currently published package version clear enough for
     the maintainer task.

## Layout Refresh Rules

- Keep macro-area workflows in the `$tanstack` skill plus `references/*.md`.
- Keep narrow Router, Start, and CLI tasks in focused reference files unless
  the domain becomes broad enough to justify a product reference.
- When a new official TanStack domain appears:
  - add it to `references/README.md`
  - decide whether it deserves a new product reference or belongs inside an existing
    macro guide
- When an official domain disappears or merges:
  - update the matching product or focused `references/*.md` first
- Keep `README.md`, `skills/tanstack/SKILL.md`, `agents/openai.yaml`, and
  `references/*.md` files aligned on the skill's product and focused reference maps

## Guardrails

- Use TanStack-owned public sources first for the upstream coverage check.
- Do not assume a missing Query Intent surface is permanent; state it as the
  current observed registry state only.
- Do not broaden `skills/tanstack/` beyond its actual framework coverage
  without a real upstream and local-scope reason.
- Keep local wording aligned with what the plugin actually bundles today, not
  with possible future TanStack Intent expansion.
- Do not reintroduce separate narrow Router, Start, or CLI skill directories
  unless a maintainer deliberately changes the reusable-skill packaging model.

## Branch Report Additions

- Which upstream TanStack Intent surfaces were checked
- Which TanStack `latest` docs surfaces were checked
- Whether new first-party coverage was found

Add these items to the common final report owned by `release-checklist.md`.
