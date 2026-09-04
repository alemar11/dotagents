# Legacy-tag migration

Read this reference only when inspecting or adding canonical aliases for
stable legacy tags such as `2.3.0`. Migration never renames, moves, deletes, or
recreates the legacy source.

Produce a read-only plan with:

```bash
scripts/version-suggestions --mode migration --repo /path/to/project --json
```

The plan must preserve:

- the exact source tag and canonical `vX.Y.Z` target;
- the source commit SHA resolved through the commit object, including an
  annotated source tag;
- whether the target is absent, already present at the same commit, or a
  conflict that blocks migration.

Interpret every result through [the state registry](states.md). No legacy tags
produces `nothing-to-migrate`; an unresolved source or conflicting target is a
hard stop.

The plan is not mutation authority. After showing the source tag, target tag,
exact commit, and intended remote operation, obtain explicit confirmation of
that exact alias. Immediately before the write, re-read both refs and require
the target to be absent. Create only the missing canonical tag at the resolved
source commit, then read both refs again and require them to resolve to the
same commit. Never overwrite an existing canonical tag.
