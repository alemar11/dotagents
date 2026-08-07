# Repository Guidelines

## Overview

This repository hosts reusable Codex skills, project-maintainer skills,
repo-local plugins, and MCP installation helpers. Reusable skills live under
`skills/`, maintainer skills under `.agents/skills/`, plugins under `plugins/`,
and MCP helpers under `mcps/`. Every skill has a `SKILL.md` entrypoint and
every plugin has a `.codex-plugin/plugin.json` manifest.

Follow the [Agent Skills specification](https://agentskills.io/specification)
and the [Codex skills reference](https://developers.openai.com/codex/skills/)
when the package is intended for Codex.

## Global Naming and Identity

- Use lower-kebab-case for skill and plugin directory names, public identifiers,
  repository-local slugs, and generated names. Use `snake_case` only for
  machine-readable field names; use lower-kebab values for behavior-affecting
  enums.
- Preserve syntax owned by an external system, including GitHub refs, UUIDs,
  URLs, environment variables, and provider-native names. Do not derive
  ownership from display-title casing or create compatibility aliases for a
  retired identifier.
- Prefer explicit or path-derived slugs over title-derived slugs. Normalize
  them deterministically and keep one canonical spelling throughout metadata,
  references, artifacts, and generated output.

## Creating and Maintaining Skills

- Use `$skill-creator` for a new skill or substantial public reshape, then
  apply repository integration and validation rules here.
- Create reusable skills under `skills/<name>/` and maintainer skills under
  `.agents/skills/<name>/`. Give each a stable lower-kebab name, `SKILL.md`,
  and `agents/openai.yaml` when it is a discoverable Codex skill.
- Keep `skills/plugins-reload/SKILL.md` synchronized with the repo-local plugin
  set in `.agents/plugins/marketplace.json` and update its reload commands when
  a project plugin is added, removed, renamed, or its installation workflow
  changes.
- Keep selection metadata, trigger rules, load-bearing workflow order,
  mutation boundaries, and output contracts in `SKILL.md`. Keep branch-specific
  detail in directly routed lowercase `references/*.md` files.
- Every skill that defines or observes workflow nodes, statuses, checkpoints,
  modes, dispositions, or other behavior-affecting states must own a canonical
  `references/states.md` and route to it from `SKILL.md`. That reference must
  list every state in its owning namespace with a plain-language description,
  distinguish persisted state from transient or external state, and be updated
  in the same change whenever a state is added, renamed, removed, or changes
  meaning.
- Use a package's `SKILL.md` to decide when the runtime skill is applicable;
  use its nearest `AGENTS.md`, when present, for maintenance rules while
  improving, editing, updating, or removing that package. Do not copy either
  contract into the root file.
- Keep `README.md`, `agents/openai.yaml`, install prompts, and any dependency
  declarations synchronized when a skill is added, renamed, reshaped, or
  removed. Keep a `Skill Dependencies` section only when runtime skill
  dependencies actually exist.
- When a package has maintenance rules that are not global and cannot be
  inferred from its tree, manifest, `SKILL.md`, or references, create or update
  the nearest package-local `AGENTS.md`. Do not create a local file that merely
  repeats the runtime skill contract or a root rule.
- When removing a skill, remove its source, metadata, README/install entries,
  registries, and repository-owned installation links together, then scan for
  the retired name and paths. Never edit cache copies as migration targets.
- If `brand_color` is absent, choose a hex color not already used by another
  skill in this repository.

## Creating and Maintaining Plugins

- Use `$plugin-creator` for a new plugin or substantial plugin reshape.
- Create plugins under `plugins/<name>/` with a lower-kebab name and a
  `.codex-plugin/plugin.json` manifest as the source of truth for identity,
  version, assets, and bundled-skill exposure.
- Register every repo-local plugin in
  `.agents/plugins/marketplace.json` in the same change that adds, renames, or
  removes it. Keep manifest paths repository-relative and valid from the
  plugin root.
- Put bundled skills under `plugins/<name>/skills/<skill>/`, shared runtime
  artifacts under `plugins/<name>/scripts/`, and maintenance-only source under
  `plugins/<name>/projects/<tool>/`. Add a nearer `AGENTS.md` only when that
  child has a distinct maintenance contract.
- Any committed change under `plugins/<plugin>/` requires a semantic version
  update in the plugin manifest. Keep any embedded CLI version aligned with
  the owning plugin unless an intentional independent policy is documented.
- Keep plugin README and marketplace descriptions synchronized with the
  manifest and bundled-skill layout. Treat installed plugin caches as
  verification surfaces, never editable sources.

## Repository-Wide Rules

### Codex Integration

- Specify every runtime-skill interaction with Codex semantically in natural
  language: define the intended outcome, topology, authorization, lifecycle,
  verification, and recovery behavior. Runtime skills and their references
  must not name Codex APIs or tools or duplicate their operations, parameters,
  response fields, signatures, enums, target forms, or payloads.
- The model uses the current live Codex capabilities directly. Skills may
  require semantic runtime properties, such as a saved project, local or
  isolated execution, a model profile, or independently verified task state,
  but must not encode how the live interface represents them. If the required
  outcome cannot be established, report the incompatibility instead of
  guessing, substituting another operation, or claiming success.
- Keep requested state, immediate receipts, and independently observed state
  distinct. Treat display metadata as non-identity evidence and reconcile
  uncertain effects before any retry.

### Documentation and Contract Ownership

- Keep `AGENTS.md` files focused on repository structure, ownership boundaries,
  maintenance routing, portability, and durable maintenance learnings. Keep
  user-facing invocation behavior in `SKILL.md` and references.
- Keep one canonical owner for every behavior-affecting field registry,
  template, protocol, and result shape. Cross-reference it instead of copying
  detailed doctrine into multiple packages.
- Keep [`references/codex-model-index.md`](references/codex-model-index.md) as
  the repository-wide inventory of skill-level Codex model and reasoning
  behavior. When a skill or plugin skill adds, removes, renames, or changes a
  model, reasoning value, role, or intentional ambient/default inheritance,
  update the index in the same change. Use one row per skill/model/reasoning
  role, including separate rows when a skill creates multiple profiles. The
  index points to runtime owners and must not duplicate their full policies.
- In `references/` folders, use lowercase Markdown filenames except
  `README.md` and `AGENTS.md`.

### Runtime Contract Design

- Use canonical `snake_case` fields and lower-kebab assigned values. Reject
  noncanonical fields and values unless the owning contract explicitly defines
  an external-syntax exception.
- Separate selectable options from execution facts, derived state, prose,
  and references. Do not turn caller-owned inputs or result state into durable
  configuration merely because a workflow needs to report them.
- Build through progressive disclosure: keep selection-critical and safety
  rules in `SKILL.md`, and route decidable branch detail to one canonical
  reference with an explicit read condition.

### Testing and Validation

- Validate representative usage paths and always-loaded metadata, not package
  size or moved-text volume.
- Do not add tests for Markdown-only packages. For executable scripts, add
  focused tests only when they protect meaningful behavior or a high-risk
  invariant, and verify the shipped artifact when one exists.
- Use forward model tests only when static checks cannot provide enough
  confidence for the changed behavior.

### Runtime and Maintenance Boundaries

- Runtime skills must not reference `.agents/skills/maintainer`, its runbooks,
  or maintainer-only routing. Repository-level guidance may route explicit
  maintenance work there.
- Runtime skills may surface durable guidance candidates but must not perform
  self-upgrade, metadata synchronization, reference refresh, or repository
  maintenance from runtime instructions.
- Keep maintenance-only implementations and refresh helpers outside reusable
  runtime artifacts and install lists.

### Cache, Tooling, and Git

- Scope per-user caches under `~/.cache/dotagents/skills/<skill-name>/` or
  `~/.cache/dotagents/plugins/<plugin-name>/`; bundled plugin skill caches use
  `~/.cache/dotagents/plugins/<plugin-name>/skills/<skill-name>/`.
- Keep `skills-link.sh` as the local install helper: it links `skills/` into
  `~/.agents/skills` only and never rewrites plugin marketplace entries.
- If a change affects multiple skills or plugins, use separate meaningful
  commits by responsibility. Run `git diff --check` before handoff.

## Package-Local AGENTS Contracts

- The root `AGENTS.md` contains only repository-wide rules for creating,
  editing, updating, and removing skills or plugins. Read it before any such
  change, then read the nearest package-local `AGENTS.md` when it exists;
  package behavior and ownership belong to that local contract or the
  package's runtime documentation.
- A package-local `AGENTS.md` is warranted only for maintenance contracts such
  as owned surfaces, authority boundaries, generated-artifact/version rules,
  or package-specific validation. It must not duplicate `SKILL.md`, reference
  prose, manifests, or this root file.
- Before creating or retaining one, inspect the package and its consumers;
  remove local files that contain no actionable package-specific contract or
  merely repeat runtime instructions.
- Keep nested guidance nearest to the surface it governs. A maintenance
  project or bundled plugin skill gets its own file only when its contract
  differs from the parent package.
