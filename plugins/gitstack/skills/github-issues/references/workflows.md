# GitHub Issue Workflows

Use these commands for GitHub issue lifecycle work after resolving repository
context, `issue_operation`, and `mutation_mode`. Add `--repo <owner>/<repo>`
when the current checkout is not the target repo or the caller supplied an
explicit repository.

## Mutation Policy

GitStack receives only its own normalized contract:

```md
mutation_mode: apply # apply | dry-run
issue_operation: create # one canonical GitStack issue operation
```

A composed workflow must translate its own write, tracker, or publication
policy before invoking this skill. `mutation_mode=apply` plus the exact target
and `issue_operation` authorizes only that operation. `mutation_mode=dry-run`
returns the body and exact command without mutation.

Direct user instructions such as create, publish, or open the issues resolve
`mutation_mode=apply` for the requested `issue_operation` unless the same
request supplies no-mutation evidence, which resolves `mutation_mode=dry-run`.

Reject caller-owned planning, tracker, orchestration, delivery, or publication
policy fields at this boundary; GitStack must not interpret them.

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

Create issues through the structured GitHub connector. The current `gh issue
create` surface requires the free-form title in argv, so it is not an allowed
fallback. If the connector is unavailable, fail closed; do not invent an issue
CLI or interpolate the title into a shell command.

Generated Markdown bodies are untrusted shell input. Do not place them inside
double-quoted shell strings, `echo`, command substitutions, or unquoted heredocs
such as `<<EOF`; backticks and `$...` must remain literal. Use a runtime
file-write tool when available. If writing from a shell, use a quoted heredoc
delimiter such as `<<'EOF'` or another non-interpolating writer.

For multi-issue publication, especially a Feature Spec plus child issues, publish in
checkpoints:

1. Create or update the parent issue.
2. Verify the parent number and metadata.
3. Create child issue body files from sanitized final bodies.
4. Create only missing child issues, attaching the parent relationship when
   supported.
5. Verify issue type, labels, parent/sub-issue state, and URLs before reporting.

If a command fails after an earlier issue was created, stop and inspect the
tracker before retrying. Reuse the created issue numbers and retry only missing
or incorrect operations; do not rerun the full create sequence from local
assumptions.

Supply the exact repository, structured title/body, optional issue type, labels,
and parent relationship to the connector. Verify the returned issue number and
URL, then read the exact target back before claiming its text is verified.

After creating or editing an issue type, verify with `issueType`; `type` is not
a valid JSON field for `gh issue view`:

```bash
gh issue view <number-or-url> --json number,title,state,url,labels,issueType
gh issue view <number-or-url> --repo <owner>/<repo> --json number,title,state,url,labels,issueType
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
new label. Use the structured GitHub connector because `gh label create`
requires free-form name and description text in argv. If connector label
creation is unavailable, fail closed.

Do not create other labels unless the user or tracker configuration explicitly
asks for new taxonomy.

## Parent And Sub-Issues

Prefer creating child issues with the parent relationship already set through
the same structured connector issue-creation operation.

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
disposition and the issue acceptance criteria are satisfied or intentionally not
planned.

When a rationale is required, first post it with a verified file-backed
comment, then change state without an inline comment:

```bash
gh issue comment <number-or-url> --body-file <absolute-message-file>
gh issue close <number-or-url>
gh issue close <number-or-url> --reason completed
gh issue close <number-or-url> --reason "not planned"
```

Read the comment and issue state back. If the comment succeeds and closure
fails, report that partial success and do not repost the rationale blindly.

Before closing partially satisfied work, create or link an owner-visible
follow-up when mutation is authorized. Otherwise keep the source issue open and
report the proposed follow-up title/body.

## Reopening

Reopen only when the user or calling workflow explicitly requests that state
transition. Verify the resulting issue state.

```bash
gh issue comment <number-or-url> --body-file <absolute-message-file>
gh issue reopen <number-or-url>
gh issue view <number-or-url> --json number,state,url
```

Read the comment back before reopening. Preserve the comment identity if the
state transition fails; do not repost it blindly.

## Dry Runs

When `mutation_mode=dry-run`, do not run mutating commands. Return:

- the exact issue title and body or comment body,
- the exact `gh` command that would be run,
- the target repo,
- the reason mutation was skipped.

It is safe to run read-only commands such as `gh repo view`, `gh issue list`,
and `gh issue view` when the user has not forbidden GitHub reads.
