# Issue creation recovery

`gh issue create` can create an issue before failing to assign users or update
other metadata. A nonzero exit can therefore leave an issue on GitHub even
without printing its URL.

Before retrying creation, inspect any returned URL. If none was returned, look
up candidates in the exact repository and compare the intended title, body,
author, and creation time with the attempted write. If identity remains
uncertain, report that result and stop. Do not create another issue to recover
from an unresolved attempt.

For an assignment failure, verify the intended login against the repository's
assignable users; an organization cannot be assigned. Do not guess a different
login from a similar spelling. Once the issue and assignee are verified, repair
only the missing metadata within the authorized scope:

```sh
gh issue edit ISSUE_URL --add-assignee VERIFIED_LOGIN
gh issue view ISSUE_URL --json url,body,assignees
```

Confirm the assignment and that the original body is preserved. Reconcile any
partial repair before retrying it.

Sources: [post-creation metadata updates](https://github.com/cli/cli/blob/v2.102.0/api/queries_issue.go#L325)
and [creation error handling and URL output](https://github.com/cli/cli/blob/v2.102.0/pkg/cmd/issue/create/create.go#L481).
