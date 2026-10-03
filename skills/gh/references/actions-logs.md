# Actions job logs

Prefer native log viewing once the workflow run has completed:

```sh
gh run view RUN_ID --repo OWNER/REPO --job JOB_ID --log
```

Use `--log-failed` instead of `--log` when only failed steps are needed. Both
require the overall run to finish, even when the selected job has completed.

If a job has completed while its workflow is still active, read that job's log
through `gh api`. Confirm its status first:

```sh
gh api 'repos/OWNER/REPO/actions/jobs/JOB_ID' --jq '{status,conclusion}'
```

A running job can return 404 for its log, and availability can lag completion.
Check status and availability before treating a log 404 as an access failure.
The endpoint requires repository read access; classic OAuth/PAT credentials
need the `repo` scope for a private repository.

If terminal escape sequences prevent the API read, use
`--allow-escape-sequences` while saving the response to a local file:

```sh
gh api --allow-escape-sequences \
  'repos/OWNER/REPO/actions/jobs/JOB_ID/logs' > /absolute/path/job.log
```

Check command success and saved content before analyzing the file. Sanitize
terminal control sequences before displaying its text; keep the raw response
in the file. Check installed `gh api --help` for the escape-sequence flag if
the CLI rejects it.

Sources: [official job-log endpoint](https://docs.github.com/en/rest/actions/workflow-jobs#download-job-logs-for-a-workflow-run),
[run-view implementation](https://github.com/cli/cli/blob/v2.102.0/pkg/cmd/run/view/view.go#L313),
and [API implementation](https://github.com/cli/cli/blob/v2.102.0/pkg/cmd/api/api.go).
