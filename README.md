# dotagents

Reusable agent skills and project maintainer skills.

This repository is organized around reusable installable skills:

- **Reusable skills** under `skills/`, which can be linked locally or installed into Codex.

Project-only maintainer workflows live under `.agents/skills/`. The retained
`.agents/plugins/marketplace.json` registry is empty; the current catalog ships
as skills.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `skills/` | Reusable skills, each with a `SKILL.md` entrypoint and `agents/openai.yaml` metadata. |
| `.agents/skills/` | Project-local maintainer skills for working on this repository. |
| `.agents/plugins/marketplace.json` | Local plugin discovery surface for this checkout. |
| `skills-link.sh` | Local development helper that links reusable skills into `~/.agents/skills`. |

## Reusable Skills

| Skill | Purpose |
| --- | --- |
| `project-tools` | Explicit invocation only: detect the project stack, install missing relevant skills, and update installed ones. Supports Android, Apple plus personal Swift, Vercel React, and TanStack; setup/update narrows the work, and Xcode, Hopper, or Discourse MCP configuration is project-local and on request. |
| `learn` | Maintain AGENTS.md and durable repository knowledge, or assess session lessons when requested; also triggers on user-stated hard repository rules and important durable assumptions. |
| `grilling-session` | Refine a topic or handoff one question at a time, resolving prerequisite decisions first and giving concrete recommended answers. |
| `explore` | Investigate read-only with primary-source evidence and optional research subagents; use an interview only for unresolved user decisions. |
| `why` | Reconstruct historical design rationale from code history and related records, separating documented reasons from inference. |
| `adversarial-review` | Pressure-test a software change read-only, with optional blast-radius analysis of indirect effects and safety assumptions. |
| `review-pr` | Request or resume a hosted Codex PR review, wait, and report the provider result to the calling task. |
| `architect` | Design feature behavior, ownership and interfaces, then a verifiable task plan; publish the specification to GitHub when requested. |
| `prototype` | Build and run an isolated experiment in the project's stack or as a standalone example to resolve a UI, interaction, logic, or state-model question. |
| `implement` | Implement software features and fixes with required self-review and behavioral validation; skip automatic selection for trivial edits. Explicit invocation may cover any selected scope. Commit only when authorized, without orchestration or publication. |
| `deslop` | Explicit-only audit or safe cleanup of low-value code in the requested scope. |
| `unslop` | Write or revise prose to remove filler, vague claims, and formulaic phrasing while preserving meaning, tone, and technical precision. |
| `test-audit` | Gate new tests on behavioral value and audit or prune redundant coverage. A bare invocation starts a read-only audit of the current repository unless a task or scope is already established. |
| `gh` | Route GitHub reads and writes through the authenticated CLI, including stacked-PR workflows through the `github/gh-stack` extension. Suggest installation when needed. |
| `git-commit` | Create or push explicit regular, fixup, or amend-fixup commits without publishing a PR. |
| `yeet` | Confirm scope and caller-provided resolved issues, commit, push, add automatic issue-closing references, and open or update one pull request. Stack linking and review requests are separate. |
| `versioning` | Distinguish versions, tags, and GitHub Releases; suggest SemVer and operate approval-gated release-tag workflows. |
| `crusty` | Skeptical, evidence-backed critique of work decisions and implementations. Use only when explicitly asked for Crusty. |
| `ms-roberts` | Use when medium or long user-authored English prompts contain grammar errors; append corrections and learning tips after the main answer. |
| `socrates` | Offer opt-in exercises about meaningful recent engineering work, or quiz the user when explicitly requested. |
| `okf` | Write, scaffold, inspect, and validate Open Knowledge Format Markdown bundles with the shipped CLI. |
| `skill-cli-creator` | Create or refactor CLIs shipped inside a skill or plugin bundle. |
| `postgres` | Inspect Postgres databases, design or run SQL, and diagnose PostgreSQL through the shipped CLI. |
| `swift-api-design` | Design, rename, or review Swift API surfaces using the bundled official API Design Guidelines. |
| `swift-docc` | Author, review, preview, or publish Swift-DocC symbol documentation, articles, and tutorials. |
| `youtube` | Search YouTube videos and playlists or answer from timestamped transcripts. Use for YouTube links and spoken-content research. |
| `ghostty` | Inspect or arrange Ghostty terminals and edit configuration or keybindings when explicitly requested. |
| `herdr` | Inspect or control Herdr terminal workspaces, panes, and agents when the user explicitly asks to use Herdr. |
| `xcode-whats-new` | Explicitly read official release notes for the active, latest, or requested stable or beta Xcode. |

For repository-installed skill files, `project-tools` uses `.agents/skills/`
for every client. Claude Code shares that collection through the relative
symlink `.claude/skills -> ../.agents/skills`; enabling Claude for an existing
installation requires only the link. Intent-managed skills remain in their
library packages and use project loading guidance.

### Official TanStack Skills

Use `$project-tools` to configure [TanStack Intent](https://tanstack.com/intent/latest/docs/getting-started/quick-start-consumers)
as a repository development dependency and enable skills shipped with the
installed library versions. Setup details live in
[the TanStack reference](skills/project-tools/references/tanstack.md).

## Skill Dependencies

- `explore` explores relevant evidence in the current task or session, clarifies
  material user decisions when needed, then investigates remaining questions.
  Clear requests proceed without an interview or final confirmation. The
  entire investigation is strictly read-only.
  It never creates visible tasks or prepares a controller transfer handoff.
  Independent evidence work may use subagents with focused research briefs,
  subject to user constraints and host capacity. Workers cannot invoke Explore
  or delegate further. Research helpers prescribe no model or reasoning level.
- Install `explore` with `grilling-session` for material user decisions.
  Explore reads relevant repository context directly without a knowledge-maintenance
  pass, then invokes Grilling Session only when user decisions need refinement.
  A required interview asks one question with a recommendation per turn.
  Workers can begin once scope is already established, the interview confirms
  it, or the user stops grilling. Grilling Session is not required for the
  direct investigation path.
- Install `architect` with its `grilling-session` dependency.
  Skill dependencies must be reachable in the current session; the invoking skills
  never install or substitute them automatically.
- `why` is a standalone read-only investigation, also usable by a planning or
  research caller. It follows relevant historical sources without requiring a
  provider or an exhaustive source sweep. Optional evidence helpers inherit
  host defaults; the invoking session owns synthesis. GitHub reads use `gh`.
- `adversarial-review` loads its blast-radius reference when requested or when
  the change warrants it. It returns any required writable experiment to the
  caller; it does not create probes or expand its read-only authority.
- `review-pr` obtains one hosted Codex review result for a PR through
  authenticated `gh`, with no other skill dependency. Other authorized review
  discussion and resolution operations use `gh` directly. Use
  `$adversarial-review` for local independent change
  review; use `$crusty` only when explicitly asked for Crusty.
- `maintainer` uses its local health and validation workflows for diagnosis; it requires `$skill-creator` or `$plugin-creator` for substantial public reshapes and native `codex review` for non-trivial implementation closeout.
- Architect uses installed `$grilling-session` for material clarification and
  authenticated `gh` for hosted reads and publication when saving to GitHub.
- `prototype` can be invoked directly or selected for a requested experiment.
  It uses temporary directories for standalone examples and isolated project
  worktrees for app integration, then verifies the relevant native or browser
  behavior. It adds no mandatory dependency to planning or implementation and
  does not turn a read-only caller into authority to build or publish.
- `learn` runs in the invoking task and performs only authorized local-repository context changes; it has no external dependency preflight, task profile, GitHub transport, publication, or worker delegation contract.
- A requested Learn retrospective proposes environment improvements from
  observed session evidence. Accepted lessons use existing capture authority;
  implementing tooling fixes remains separate work.
- `grilling-session` is read-only and explicit or parent-composed. It uses supplied
  context and relevant evidence without requiring Learn or a repository, returns
  a transient refined handoff, and
  never creates tasks or captures durable knowledge automatically.
- `architect` targets one repository per invocation, with no cross-repository issue
  references or companion specs. It starts from realistic usage, settles changed
  ownership and contracts, and compares alternatives when a consequential choice
  needs them. It produces a design and task plan without implementation or runnable
  prototypes. It saves coherent specs with stable task identities, recommended
  order, real prerequisites, and completion checks. Targeted revisions preserve legacy
  task issues unless consolidation is requested. GitHub is the only saved destination;
  no-write previews stay in the conversation and require no GitHub skill access when using
  only supplied or local sources. GitHub is the sole saved-spec authority.

- Engineering skills retain the same delegation policy standalone and composed. Implement
  implements, self-reviews, and validates, then commits only with user or
  composed-assignment authority; independent review is a separate caller-owned
  gate, with no reviewer delegation inside Implement.
- `review-pr` reuses a completed current-target review, resumes a pending
  request, or requests and waits when needed. It returns the provider result to
  the calling task, standalone or composed, with no subagents, repairs, CI or
  acceptance decisions. Explicit inspect-only scope remains read-only.


## Project-Local Skills

| Skill | Path | Purpose |
| --- | --- | --- |
| maintainer | `.agents/skills/maintainer/` | Audit or maintain repository skills, optional plugins, and coupled tools when explicitly invoked. |

Project-local skills are repository-specific and are not included in reusable install commands.

## Installation

### Link Reusable Skills For Local Development

Run this from the repository root to link `skills/` into `~/.agents/skills`:

```sh
./skills-link.sh
```

This helper only links reusable skills. It does not install, mirror, or rewrite plugin marketplace entries.
It excludes `swift-api-design` and `swift-docc` and removes existing links to
those skills owned by this checkout. Install them per project with `project-tools`.

### Install Reusable Skills With `skill-installer` (Codex-only)

Inside Codex, install all reusable skills with:

```text
Use $skill-installer to install skills from alemar11/dotagents --path skills/gh skills/git-commit skills/yeet skills/versioning skills/crusty skills/ms-roberts skills/socrates skills/okf skills/skill-cli-creator skills/postgres skills/swift-api-design skills/swift-docc skills/youtube skills/xcode-whats-new skills/ghostty skills/herdr skills/learn skills/grilling-session skills/explore skills/why skills/adversarial-review skills/review-pr skills/architect skills/implement skills/deslop skills/unslop skills/test-audit skills/prototype skills/project-tools
```

Install one reusable skill by passing only its path:

```text
Use $skill-installer to install skills from alemar11/dotagents --path skills/crusty
```

Replace `skills/crusty` with any path listed in the reusable skills table.

### Install Reusable Skills With `npx skills`

These commands use the [`vercel-labs/skills`](https://github.com/vercel-labs/skills) CLI and target Codex directly.

List the skills available in this repository:

```sh
npx skills add alemar11/dotagents --list
```

Install all reusable skills globally for Codex:

```sh
npx skills add alemar11/dotagents -a codex -g -y \
  --skill project-tools \
  --skill gh \
  --skill git-commit \
  --skill yeet \
  --skill versioning \
  --skill crusty \
  --skill ms-roberts \
  --skill socrates \
  --skill okf \
  --skill skill-cli-creator \
  --skill postgres \
  --skill swift-api-design \
  --skill swift-docc \
  --skill youtube \
  --skill xcode-whats-new \
  --skill ghostty \
  --skill herdr \
  --skill learn \
  --skill grilling-session \
  --skill explore \
  --skill why \
  --skill adversarial-review \
  --skill review-pr \
  --skill architect \
  --skill prototype \
  --skill implement \
  --skill deslop \
  --skill unslop \
  --skill test-audit
```

Install one reusable skill globally for Codex:

```sh
npx skills add alemar11/dotagents -a codex -g -y --skill crusty
```

Replace `crusty` with any skill name from the reusable skills table. Omit `-g` to install into the current project's `.agents/skills/` instead of your global `~/.codex/skills/`.

Restart Codex after installing or updating skills.
