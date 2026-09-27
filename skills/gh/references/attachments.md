# Image and video attachments

Native `--attach` support starts in `gh` 2.99.0 for GitHub.com and GitHub
Enterprise Cloud. Check the target command's help for the flag; if unavailable,
report the installed version and suggest an upgrade. Uploading requires
repository push access, even when the account can create an issue or comment.
Treat an upload permission failure as that limitation, not as a login failure.

Use `--attach` on `gh issue create`, `gh issue edit`, `gh issue comment`,
`gh pr create`, `gh pr edit`, or `gh pr comment`. It supports images and videos,
not arbitrary files. `gh pr review` has no attachment flag; a conversation
comment does not replace a formal review or inline thread reply.

## Publish and verify

For an authorized issue creation with an image:

```sh
gh issue create --repo OWNER/REPO --title 'Issue title' \
  --body-file /absolute/path/body.md \
  --attach '/absolute/path/screenshot.png#Error state'
gh issue view ISSUE_URL --json url,body
```

Use the URL returned by creation for readback. To add media to an existing
issue without replacing its body:

```sh
gh issue edit ISSUE_URL --attach /absolute/path/recording.mp4
gh issue view ISSUE_URL --json url,body
```

Repeat `--attach` for multiple files, up to 50 distinct files per command.
Image alt text follows `#` in the quoted path; omit alt text for videos.
When supplying Markdown, use `--body-file`. References to the same local paths
passed to `--attach` are rewritten to uploaded URLs; otherwise media is appended.
For edits, `--body-file` replaces the body, so provide the complete intended text.

Read back the exact issue, PR, or comment and confirm the expected media URLs
in its body. A nonzero exit can follow partial publication. Preserve any
returned URL, inspect what was published, and retry only missing attachments
after resolving the cause; do not blindly repeat creation or resend all files.

Sources: [official attachment guide](https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli)
and [gh 2.99.0 release](https://github.com/cli/cli/releases/tag/v2.99.0).
