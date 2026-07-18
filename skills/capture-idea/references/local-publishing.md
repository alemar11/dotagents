# Local Idea Publishing

Load this reference only when `tracker_backend=local` and
`write_mode=apply`.

## Canonical Local Artifact

Write each Idea to exactly:

```text
planning/ideas/<idea-slug>.md
```

The durable workspace-qualified ref is:

```text
<repository-slug>/planning/ideas/<idea-slug>.md
```

The owning repository must be a Project Memory-selected memory-owning root.
Never put Ideas under `project-memory/`, `planning/features/`, `planning/tmp/`,
or a coordination root that does not own the selected tracker artifact.

Render the full local form from `idea-template.md`. The header metadata region
must contain:

- exactly one `artifact_marker: idea` line;
- `workflow_state: needs-triage` only when explicit queue intent exists;
- no workflow-state line for a dormant Idea;
- no `issue_type` line.

Open Questions do not create `needs-info`. No other workflow state is valid at
capture time.

## Preflight And Write

Normalize the slug to lowercase kebab-case and reject path separators, `..`,
absolute paths, or a target outside the resolved tracker-owning repository.
Inspect the exact path and scan canonical Idea titles and markers for semantic
duplicates before writing.

- If the exact path contains a canonical substantively equivalent Idea, reuse
  its qualified durable ref without rewriting it.
- If the exact path exists with different content or incompatible metadata,
  ask whether to reuse, rename, or revise. Never overwrite it.
- If an equivalent canonical Idea exists at another path, reuse that existing
  qualified ref unless the user explicitly chooses a distinct revised Idea.
- Recompute and recheck the path after every rename, merge, or split.

Create `planning/ideas/` only when at least one new local Idea has passed the
complete-set preflight. Write each new file atomically when the runtime supports
it. After each write, read the file back and validate its H1, header metadata,
section order, absence of `issue_type`, and exact qualified ref.

## Failure And Retry

When a write result is ambiguous, inspect the exact target before retrying.
Treat a complete verified artifact as created; retry only a file proven absent.
Treat a partial or malformed artifact as a failed mutation requiring explicit
repair authority, not permission to overwrite silently.

On partial multi-Idea publication, stop and report verified created and reused
refs plus every missing target. Resume only after re-reading current paths and
redoing collision checks for the missing candidates.
