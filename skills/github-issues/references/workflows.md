# GitHub Issue Workflows

Use these commands for GitHub issue lifecycle work after confirming mutation
authority. Add `--repo <owner>/<repo>` when the current checkout is not the
target repo or the caller supplied an explicit repository.

## Repository Context

```bash
gh repo view --json nameWithOwner,url,defaultBranchRef
gh auth status
```

For an explicit target:

```bash
gh repo view --repo <owner>/<repo> --json nameWithOwner,url,defaultBranchRef
```

## Read Issues

```bash
gh issue list --state open --limit 50 --json number,title,state,url,labels,issueType,parent,subIssues
gh issue view <number-or-url> --comments --json number,title,state,author,body,comments,labels,issueType,parent,subIssues,url
```

If the installed `gh` version rejects a JSON field such as `issueType`,
`parent`, or `subIssues`, rerun without that field and report the fallback.

## Create Issues

Use `--body-file` for non-trivial issue bodies or comments. Create temporary
body files outside checkout-owned artifact paths and remove the temp directory
after the command succeeds or fails, unless the user or calling workflow
explicitly provided a persistent body-file or local mirror path.

```bash
tmpdir="$(mktemp -d)"
body_file="$tmpdir/issue.md"
# Write the generated body to "$body_file", then run one of:
gh issue create --title "<title>" --body-file "$body_file"
gh issue create --title "<title>" --body-file "$body_file" --type "<type>"
gh issue create --title "<title>" --body-file "$body_file" --label "<label>"
gh issue create --title "<title>" --body-file "$body_file" --parent <parent-number-or-url>
rm -rf "$tmpdir"
```

For an explicit target repo:

```bash
tmpdir="$(mktemp -d)"
body_file="$tmpdir/issue.md"
# Write the generated body to "$body_file", then run one of:
gh issue create --repo <owner>/<repo> --title "<title>" --body-file "$body_file"
gh issue create --repo <owner>/<repo> --title "<title>" --body-file "$body_file" --label "<label>"
gh issue create --repo <owner>/<repo> --title "<title>" --body-file "$body_file" --parent <parent-number-or-url>
rm -rf "$tmpdir"
```

## Edit Issue Bodies

Use `--body-file` when replacing non-trivial issue bodies.

```bash
tmpdir="$(mktemp -d)"
body_file="$tmpdir/issue.md"
# Write the replacement body to "$body_file", then run:
gh issue edit <number-or-url> --body-file "$body_file"
rm -rf "$tmpdir"
```

## Issue Types

Use native GitHub Issue Types when the repo supports them and the user or
calling workflow asked for them.

```bash
gh issue edit <number-or-url> --type "<type>"
gh issue edit <number-or-url> --remove-type
```

If issue types are disabled, unsupported, or rejected by the installed `gh`,
publish without a type and report the fallback so the caller can decide whether
to use labels or body conventions.

## Labels

Read labels before changing them:

```bash
gh issue view <number-or-url> --json labels
gh issue edit <number-or-url> --add-label "<label>"
gh issue edit <number-or-url> --remove-label "<label>"
```

Create labels only when the user or calling workflow explicitly requested a
new label:

```bash
gh label list --repo <owner>/<repo> --search "<label>"
gh label create "<label>" --repo <owner>/<repo> --description "<description>"
```

Do not create other labels unless the user or tracker configuration explicitly
asks for new taxonomy.

## Parent And Sub-Issues

Prefer creating child issues with the parent relationship already set, using
the same temporary body-file pattern as issue creation:

```bash
gh issue create --title "<title>" --body-file "$body_file" --parent <parent-number-or-url>
```

Attach or remove existing relationships only when explicitly requested:

```bash
gh issue edit <parent-number-or-url> --add-sub-issue <issue-number-or-url>
gh issue edit <parent-number-or-url> --remove-sub-issue <issue-number-or-url>
gh issue edit <issue-number-or-url> --parent <parent-number-or-url>
gh issue edit <issue-number-or-url> --remove-parent
```

## Comments

Use `--body-file` for non-trivial comments.

```bash
tmpdir="$(mktemp -d)"
message_file="$tmpdir/comment.md"
# Write the generated comment to "$message_file", then run:
gh issue comment <number-or-url> --body-file "$message_file"
rm -rf "$tmpdir"
```

Comments should state observed state, requested action, next owner, and any
remaining blocker. Do not paste raw logs or unrelated session text.

## Closing

Only close when the user or calling workflow explicitly authorizes the
disposition and the issue acceptance criteria are satisfied or intentionally
not planned.

```bash
gh issue close <number-or-url> --comment "<closing rationale>"
gh issue close <number-or-url> --reason completed --comment "<closing rationale>"
gh issue close <number-or-url> --reason "not planned" --comment "<closing rationale>"
```

Before closing partially satisfied work, create or link an owner-visible
follow-up when mutation is authorized. If follow-up mutation is not authorized,
keep the source issue open and report the proposed follow-up title/body.

## Dry Runs

When external mutation is not authorized, do not run mutating commands. Return:

- the exact issue title and body or comment body,
- the exact `gh` command that would be run,
- the target repo,
- the reason mutation was skipped.

It is safe to run read-only commands such as `gh repo view`, `gh issue list`,
and `gh issue view` when the user has not forbidden GitHub reads.
