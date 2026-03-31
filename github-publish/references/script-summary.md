# GitHub Publish script summary

Use this as the authoritative script catalog referenced by
`github-publish/SKILL.md`.

## Fast helper picks

- Use `scripts/prs_open_current_branch.sh` for already-pushed current-branch
  PR opening.
- Use `scripts/prs_create.sh` for explicit PR creation.
- Use the PR lifecycle helpers for draft, ready, merge, close, reopen, and
  checkout flows.

## Repository setup and preflight

- `scripts/check_gh_installed.sh [--min-version <version>]`: Validate that `gh` is installed and meets a minimum version.
- `scripts/check_gh_authenticated.sh [--host github.com]`: Verify active GitHub CLI authentication.
- `scripts/preflight_gh.sh [--host github.com] [--min-version <version>] [--expect-repo <owner/repo>] [--allow-non-project]`: Run prerequisite checks before other `gh` operations.
- `scripts/check_docs_script_refs.sh [--skill-dir <path>]`: Verify docs reference existing scripts and documented flags are present in `--help` output.
- `scripts/issue_resolve_repo.sh [--repo <owner/repo>] [--allow-non-project]`: Resolve the target repository, defaulting to current git project.

## Publish scripts

- `scripts/prs_open_current_branch.sh --title <text> [--body <text>] [--base <branch>] [--draft] [--repo <owner/repo>] [--dry-run] [--allow-non-project]`: Open a PR from the already-pushed current branch without staging, committing, or pushing.
- `scripts/prs_create.sh --title <text> [--body <text>] [--base <branch>] [--head <branch>] [--draft] [--labels <label1,label2>] [--repo <owner/repo>] [--allow-non-project]`
- `scripts/prs_draft.sh --pr <number> [--repo <owner/repo>] [--allow-non-project]`
- `scripts/prs_ready.sh --pr <number> [--repo <owner/repo>] [--allow-non-project]`
- `scripts/prs_merge.sh --pr <number> [--merge|--squash|--rebase] [--delete-branch] [--admin] [--auto] [--repo <owner/repo>] [--allow-non-project]`
- `scripts/prs_close.sh --pr <number> [--repo <owner/repo>] [--allow-non-project]`
- `scripts/prs_reopen.sh --pr <number> [--repo <owner/repo>] [--allow-non-project]`
- `scripts/prs_checkout.sh --pr <number> [--branch <name>] [--detach] [--force] [--recurse-submodules] [--repo <owner/repo>] [--allow-non-project]`: Check out a pull request locally. This mutates the local checkout state.
