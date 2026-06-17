# GitHub Routing

## Preferred Entry Signals

Start here when the user asks for GitHub help but the domain is still broad or
mixed:

- `check GitHub`
- `look at this issue or PR`
- `is GitHub CLI set up?`
- `handle the GitHub follow-up`
- `inspect the repo on GitHub`

## Skill Map

- Current repo issues or PR queue: `github-triage`.
- Multiple explicit repositories: `github-portfolio-triage`.
- GitHub Actions runs, checks, logs: `github-ci`.
- Review comments, threads, replies: `github-reviews`.
- Releases, tags, generated notes, package availability: `github-releases`.
- Authenticated-user stars or star lists: `github-stars`.
- Local worktree to pushed branch and draft PR: `yeet`.

## Direct Command Map

```bash
gh repo view --json nameWithOwner,description,defaultBranchRef,url
gh issue list --repo <owner/repo> --state open --limit 50 --json number,title,author,labels,createdAt,updatedAt,url
gh pr list --repo <owner/repo> --state open --limit 50 --json number,title,author,isDraft,reviewDecision,mergeStateStatus,createdAt,updatedAt,url
gh issue view <n> --repo <owner/repo>
gh pr view <n> --repo <owner/repo>
gh pr edit <n> --repo <owner/repo> --title "<title>"
```

For ambiguous GitHub work, prefer starting with `gh auth status` plus one of
`gh repo view`, `gh issue view`, or `gh pr view` before widening into a
specialized flow.
