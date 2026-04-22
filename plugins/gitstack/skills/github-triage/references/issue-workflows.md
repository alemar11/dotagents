# GitHub issue workflows

Use this reference for issue workflows that no longer justify `ghflow`.

## Close With Evidence

Comment with the implementation evidence, then close the issue:

```bash
gh issue comment <number> --repo <owner/repo> --body "Implemented in commit <sha> (<commit-url>). Implemented via PR <pr-url>."
gh issue close <number> --repo <owner/repo>
```

If you need to confirm the issue is still open first:

```bash
gh issue view <number> --repo <owner/repo> --json state
```

## Copy To Another Repo

Read the source issue, then recreate it in the target repo with provenance in
the new body:

```bash
gh issue view <number> --repo <source-owner/source-repo> --json title,body,url,state
gh issue create --repo <target-owner/target-repo> --title "<source-title>" --body $'Copied from <source-owner/source-repo>#<number> (<source-url>).\n\n<source-body>'
```

## Move To Another Repo

Create the replacement issue first, then comment on and close the source issue
if it is still open:

```bash
gh issue create --repo <target-owner/target-repo> --title "<source-title>" --body $'Moved from <source-owner/source-repo>#<number> (<source-url>).\n\n<source-body>'
gh issue comment <number> --repo <source-owner/source-repo> --body "Moved to <target-owner/target-repo>#<new-number> (<new-url>). Continuing work there."
gh issue close <number> --repo <source-owner/source-repo>
```
