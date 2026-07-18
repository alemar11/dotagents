# Captured Idea Discovery

Run discovery only when the user explicitly asks Plan Feature to find, list,
or plan from captured Ideas and exact `source_idea_refs` are absent. Never scan
an Idea backlog during an ordinary planning request.

Discovery intent and candidate refs are execution data, not selectable options.
Discovery is read-only and does not itself authorize Feature Spec drafting or
tracker mutation.

## Workflow

1. Resolve every candidate tracker-owning repository from Project Memory
   routing and repository topology before listing artifacts.
2. For GitHub, use `$gitstack:github-issues` read operations with no mutation
   fields to list open issues carrying the configured Idea-marker label. Read
   title, body, state, labels, native Issue Type, comments, and qualified URL.
3. For local tracking, inspect only canonical
   `planning/ideas/<idea-slug>.md` files inside the resolved owning
   repositories.
4. Load `idea-source.md` in validation-only mode to validate each candidate's
   durable identity, complete outcome-comment history, and canonical prior
   outcomes. Exclude malformed or fully consumed artifacts from ordinary
   selection. Classify an open GitHub Idea with a latest full outcome as
   reconciliation-pending rather than a planning candidate. Surface
   `needs-info`, queue state, and every prior partial planning outcome rather
   than hiding them.
5. Present each eligible candidate with its globally unambiguous ref, tracker
   owner, title, concise Summary, workflow state, and prior Feature Spec refs.
   Discovery itself never changes labels, files, comments, or issue state.
6. Require an explicit selection before drafting. The selected durable refs
   become the existing `source_idea_refs` execution data. If the user only
   asked to inspect the backlog, report the candidates and stop.
7. When selected Ideas do not form one bounded feature, require separate Plan
   Feature runs rather than silently producing an unrelated batch of Specs.

Discovery uses current tracker state even with `write_mode=propose`, but it
never requests a GitStack dry-run mutation or returns executable commands.

## Output

Return the resolved tracker owners, eligible candidates, excluded-candidate
reasons, and selected refs when selection occurred. Once selection produces
`source_idea_refs`, continue through `idea-source.md`; do not preserve a
parallel discovery selector or add a Plan Feature option.
