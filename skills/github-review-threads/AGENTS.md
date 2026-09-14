# GitHub Review Threads Maintenance

This skill owns hosted review inspection, requests, waits, discussion writes,
and thread resolution through direct `gh` operations. It ships no CLI.
`references/states.md` owns review states and the caller-retained review record;
keep `review-pr` aligned when that contract changes.

Preserve exact PR/comment/thread identity, current-HEAD checks, file-backed
text, bounded waits, readback, and reconciliation before retries. Validate
reference paths and representative operation contracts without posting reviews
or changing GitHub unless the user authorized those external actions.

The retired CLI's reservation markers and journals at
`~/.cache/dotagents/plugins/g/review-mutations` and
`~/.cache/dotagents/plugins/g/review-operations` are historical recovery evidence.
Do not delete, move, or replay them. Reconcile any resumed operation against
GitHub; new executions do not create or consume these records.
