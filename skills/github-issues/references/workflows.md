# GitHub Issue Workflows

Use these commands for GitHub issue lifecycle work after resolving repository
context, `issue_operation`, and `mutation_mode`. Add `--repo <owner>/<repo>`
when the current checkout is not the target repo or the caller supplied an
explicit repository.

## Mutation Policy

G receives only its own normalized contract:

`md
mutation_mode: apply # apply | dry-run
issue_operation: create # one canonical G issue operation
`

A composed workflow must translate its own write, tracker, or publication
policy before invoking this skill. `mutation_mode=apply` plus the exact target
and `issue_operation` authorizes only that operation. `mutation_mode=dry-run`
returns the body and exact command without mutation.

Direct user instructions such as create, publish, or open the issues resolve
`mutation_mode=apply` for the requested `issue_operation` unless the same
request supplies no-mutation evidence, which resolves `mutation_mode=dry-run`.

Reject caller-owned planning, tracker, orchestration, delivery, or publication
policy fields at this boundary; G must not interpret them.

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

Create each issue through a reviewed JSON request file so its title and body
never enter argv:

```bash
gh api --method POST repos/<owner>/<repo>/issues \
 --input <absolute-request-json>
```

The request file contains the exact `title`, optional complete `body`, and any
exact existing labels supported by the operation. Apply an issue type or parent
relationship separately when the REST create endpoint does not support it.

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

Supply the exact repository and reviewed request file to `gh api`. Verify the
returned issue number and URL, apply any separately requested type or parent
relationship, then read the exact target back before claiming its text is
verified.

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

## Attachments

Use native `gh --attach` for caller-selected images and videos in an authorized
issue create, edit, or comment operation. Check the installed command's
`--help` for `--attach`; version output alone does not establish support. If
missing, report the capability gap without installing an extension, upgrading
`gh`, or falling back to a custom upload endpoint.

[GitHub's CLI attachment guide](https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli)
documents support on `gh issue create`, `gh issue edit`, `gh issue comment`,
`gh pr create`, `gh pr edit`, and `gh pr comment`. Uploads require push access
to the repository. The CLI supports images and videos, not every file accepted
by the web interface; check current supported types and size limits before
publication. Do not disguise an unsupported file by changing its extension.

Resolve the exact repository and caller-selected regular files. Keep body text
and image alt text in a non-interpolating UTF-8 body file. Use the same absolute
media paths in Markdown and `--attach` so resolution does not depend on the body
file's directory. An image reference such as `![Login error](/tmp/login.png)`
is rewritten to its uploaded URL, retaining that alt text. For a video player,
put `![](/tmp/repro.mp4)` alone in its paragraph. Files absent from the body are
appended; repeated `--attach` flags allow up to 50 distinct files per command.

Choose the command for the authorized operation:

```bash
# Append media while preserving the current issue body.
gh issue edit <number-or-url> --repo <owner/repo> --attach <absolute-image-file>

# Replace with the reviewed complete body and rewrite its local media references.
gh issue edit <number-or-url> --repo <owner/repo> \
 --body-file <absolute-body-file> --attach <absolute-image-file> --attach <absolute-video-file>

# Post one comment with its media.
gh issue comment <number-or-url> --repo <owner/repo> \
 --body-file <absolute-message-file> --attach <absolute-image-file>
```

For a new issue, retain the file-backed JSON create above so titles stay out of
argv. Check `gh issue edit --help` before creation, create and read back the
issue with prose that omits unpublished local media references, then attach to
that exact issue with `gh issue edit --attach`. For inline placement, supply the
complete final body file in that edit. These are parts of the same authorized
create request; do not create an extra comment to host the assets. If the edit
fails, retain and report the created issue identity.

For `mutation_mode=dry-run`, prepare the files, command preview, and intended
placement without executing any upload or mutation. Do not treat a mutating
command's `--dry-run` as an upload preview; `gh pr create --dry-run` may still
push Git changes.

Capture stdout, stderr, and exit status. Creation or editing can publish the
successful attachments while exiting nonzero for failed uploads. After any
write attempt, read the exact issue or comment back, including after an error.
Verify the expected stable attachment URLs and placement, preserved text, and
absence of unresolved local media references. When a rendered interface is
available, confirm the media loads. Report published and missing attachments
separately; reconcile uncertain effects before retrying only proven missing
work. Never replay creation or a comment blindly.

Private media may resolve to expiring signed delivery URLs. Retain only the
stable URLs from the published Markdown; do not print tokens, enable shell
tracing around credentials, or store private delivery URLs.

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
new label. Put the exact name, color, and optional description in a reviewed
JSON request file and create it without placing those fields in argv:

```bash
gh api --method POST repos/<owner>/<repo>/labels \
 --input <absolute-request-json>
```

Do not create other labels unless the user or tracker configuration explicitly
asks for new taxonomy.

## Parent And Sub-Issues

Create the child issue first, then attach the exact parent relationship through
the native operation below and verify both identities.

Attach or remove existing relationships only when explicitly requested:

```bash
gh issue edit <parent-number-or-url> --add-sub-issue <issue-number-or-url>
gh issue edit <parent-number-or-url> --remove-sub-issue <issue-number-or-url>
gh issue edit <issue-number-or-url> --parent <parent-number-or-url>
gh issue edit <issue-number-or-url> --remove-parent
```

## Native Issue Dependencies

Represent one directed dependency as `<blocked issue> blocked by <blocker
issue>`. Normalize an add to `issue_operation=add-blocked-by` and a removal to
`issue_operation=remove-blocked-by`. The exact blocked issue is the operation
target; the exact blocker is a separate factual reference, never an option
value. Use a full issue URL whenever the blocker is in another repository.

Read both directions before mutation:

```bash
gh issue view <blocked-issue-number-or-url> --json number,url,blockedBy,blocking
gh issue view <blocker-issue-number-or-url> --json number,url,blockedBy,blocking
```

If the exact edge already has the requested state, return a verified no-op. For
an authorized missing edge, mutate only that edge:

```bash
gh issue edit <blocked-issue-number-or-url> --add-blocked-by <blocker-issue-number-or-url>
gh issue edit <blocked-issue-number-or-url> --remove-blocked-by <blocker-issue-number-or-url>
```

Run only the command selected by `issue_operation`, then repeat both reads.
Require the blocked issue's `blockedBy` set and the blocker's reciprocal
`blocking` set to contain or omit the exact opposite URL as requested. A
one-sided, missing, ambiguous, inaccessible, or stale readback is not success.

Return exactly one terminal result for the edge using the canonical meanings
in [states.md](states.md).

A composing workflow invokes and records each deterministic edge separately
and owns whether a non-success result blocks its wider operation. This skill
never replays an ambiguous mutation or reconciles a full dependency graph.
Never infer native dependencies from titles, labels, issue types,
parent/sub-issue hierarchy, body text, or plan order. Removing a provider edge
requires explicit authority for that exact edge; a caller may not use broad
reconciliation language to remove foreign relationships whose prior ownership
is unproven.

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
