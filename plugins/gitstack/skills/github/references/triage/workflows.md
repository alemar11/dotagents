# GitHub triage workflows

Use this reference for triage-domain GitHub flows inside the consolidated
`github` skill.

## Direct `gh` first

- Repo orientation:
  `gh repo view --json nameWithOwner,description,defaultBranchRef,url`
- Issue reads and writes:
  `gh issue view <n> --repo <owner/repo>`
  `gh issue create --repo <owner/repo> ...`
  `gh issue edit <n> --repo <owner/repo> ...`
- PR reads and metadata edits:
  `gh pr view <n> --repo <owner/repo>`
  `gh pr edit <n> --repo <owner/repo> ...`

## Shared helper workflows

- Stars:
  `ghflow --json stars list|add|remove ...`
- Star lists:
  `ghflow --json stars lists list|items|delete|assign|unassign ...`

## Raw `gh` workflows that replaced older wrappers

- Close issue with evidence:
  `gh issue comment <number> --repo <owner/repo> --body "..."`
  then `gh issue close <number> --repo <owner/repo>`
- Cross-repo issue copy or move:
  use `gh issue view` to read the source issue, `gh issue create` in the
  target repo, then `gh issue comment` and `gh issue close` on the source when
  you are moving rather than copying.
- Star list creation:
  use `gh api graphql` with `createUserList`, for example
  `gh api graphql -f query='mutation($name:String!,$description:String,$isPrivate:Boolean){createUserList(input:{name:$name,description:$description,isPrivate:$isPrivate}){list{id name slug isPrivate}}}' -F name='<name>' -F description='<description>' -F isPrivate=true`
