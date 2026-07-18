# Setup Questions

Use this reference only when repository and workspace evidence plus the defaults
in [setup-workflow.md](setup-workflow.md) cannot resolve a materially ambiguous
setup target or behavior-affecting value.

Normally ask no questions. When a question is required:

- ask one question at a time;
- identify the concrete evidence that conflicts or is incomplete;
- use actual project names, repository names, tracker names, and paths;
- ask about the user's project rather than Project Memory's internal model;
- offer only relevant choices and mark the evidence-backed recommendation;
- translate the answer to canonical configuration internally; and
- ask a follow-up only for a selected custom or split choice that remains
  unresolved.

Do not expose terms such as `memory-owning root`, `scoped route`,
`repository_layout`, `tracker_backend`, or `translation memory` in the
user-facing question. Canonical fields and values belong in the resulting
configuration and completion report, not in the first-time-user prompt.

## Setup Target

Ask only when the request and current location leave more than one plausible
setup root or the requested setup area is unclear. Resolve those as two
separate decisions and ask only the unresolved one. Skip both questions when an
explicit full setup and named root already resolve the target.

> I found these project roots:
>
> - `<project-a-path>`
> - `<project-b-path>`
>
> Which projects should I set up?
>
> - The current project only: `<current-project-path>` (Recommended)
> - All listed projects
> - A different selection

If the user chooses a different selection, ask only which listed paths to
include. The selected Git repositories or coordination workspace become the
setup scope internally.

When the project root is clear but the requested area is not, ask:

> Do you want me to review and update the complete Project Memory setup, or
> only a specific area?
>
> - Complete setup (Recommended)
> - A specific area

If the user selects a specific area, ask which one: issue tracking and workflow
labels, Idea labels, project structure, project context, localization
conventions, or agent pointers. Translate the answer to the corresponding
`memory_slice` internally.

## Project Structure

Ask only when durable evidence supports conflicting project-layout
classifications. Name the conflict instead of asking the user to understand a
topology field.

> I found `<evidence-a>`, which suggests `<interpretation-a>`, but
> `<evidence-b>` suggests `<interpretation-b>`. How should planning treat this
> workspace?
>
> - One project
> - One repository containing projects or packages that are planned separately
> - A workspace coordinating separate repositories

Map the answer internally to `single-repository`, `monorepo`, or
`multi-repository-workspace`, in that order. Mark a choice Recommended only
when the inspected evidence favors it.

## Issue Location

Ask only when active GitHub and local-planning evidence conflict. Do not ask
merely because a GitHub remote exists or an unused planning directory is
present.

> I found active GitHub issue tracking at `<github-evidence>` and local planning
> files at `<local-evidence>`. Where should future Feature Specs and
> implementation issues be stored?
>
> - GitHub Issues
> - Local Markdown files

Map the answer internally to `github` or `local`. Recommend the destination
that owns the current durable planning artifacts when that ownership is clear.

## Separate Project Contexts

Ask when concrete internal projects appear independently meaningful but the
repository cannot prove whether they need different vocabulary, rules, or
decision history.

> `<project-a-path>` and `<project-b-path>` appear to be maintained separately.
> Do they use different product vocabulary, development rules, or decisions
> that agents need to read separately?
>
> - They should share the main project context (Recommended when no distinct
>   rules are evident)
> - Each should have its own context
> - Only one of them needs its own context

If only one needs its own context, ask which named project. If separate
ownership is selected but its path boundary remains unclear, ask:

> Which folders belong to `<project-name>`?

The skill decides whether the available evidence can populate a scoped
`CONTEXT.md`. Never ask the user to judge evidence sufficiency. Root
`CONTEXT.md` creation remains mandatory for every root selected by authorized
setup.

## Overlapping Project Ownership

Ask only when two proposed project contexts would match the same concrete
path.

> Both `<project-a>` and `<project-b>` currently include `<overlapping-path>`.
> Which project should define the rules for that path?
>
> - `<project-a>`
> - `<project-b>`
> - Split ownership between specific folders

If split ownership is selected, ask only for the concrete folder boundary. Do
not persist overlapping routes.

## Workspace Or Repository Rule

Ask only when evidence cannot establish whether a durable rule is local to one
repository or coordinates several repositories.

> I found this rule: `<rule-summary>`. Where does it apply?
>
> - Only to `<repository-name>` (Recommended)
> - To every repository in this workspace

Place the rule in the child repository unless the answer or evidence proves it
is genuinely cross-repository.

## Localization Conventions

Ask only when active localization signals exist but durable localization rules
cannot be confirmed. Name the evidence; do not ask whether to enable an
internal memory feature.

> I found active localization support in `<evidence-paths>`, but no documented
> localization conventions. Does this project maintain translation or
> localized-copy rules that agents should follow?
>
> - Yes
> - No
> - Not yet

`Yes` confirms that localization is applicable; create or update
`TRANSLATION.md` only when the selected scope already has write authority. `No`
resolves localization as not applicable. `Not yet` creates no translation file
and reports the missing durable guidance explicitly.

## Artifact-Marker Mapping

Ask only when the active GitHub tracker already uses the proposed Idea label
for a conflicting purpose or exposes a different established label for saved
proposals. Show the evidence-backed proposal before requesting correction.

> I found these labels for saved proposals in `<tracker-name>`:
> `<available-labels>`. I propose using:
>
> - Ideas saved for possible later planning -> `<tracker-value>`
>
> Is this mapping correct?
>
> - Use the proposed mapping (Recommended)
> - Change the mapping

Map that row internally to canonical `artifact_marker: idea`. If the user
chooses to change it, ask only for the replacement GitHub label. Local
Markdown's canonical `idea` marker and an unmodified GitHub `idea` label
require no question.

## Issue-Type Mapping

Ask only when the active tracker exposes customized or conflicting issue types.
Show an evidence-backed proposal before requesting correction.

> I found these issue categories in `<tracker-name>`: `<available-types>`. I
> propose using:
>
> - Broken or regressed behavior -> `<tracker-value>`
> - New capabilities or product enhancements -> `<tracker-value>`
> - Implementation, maintenance, documentation, or cleanup -> `<tracker-value>`
>
> Is this mapping correct?
>
> - Use the proposed mapping (Recommended)
> - Change the mapping

Map those rows internally to canonical `bug`, `feature`, and `task`. If the
user chooses to change the mapping, ask only for the incorrect row or rows.
Local Markdown's canonical mapping and an unmodified GitHub default require no
question.

## Workflow-State Mapping

Ask only when the active tracker exposes customized or conflicting workflow
labels or states. Show an evidence-backed proposal before requesting
correction.

> I found these workflow labels or states in `<tracker-name>`:
> `<available-states>`. I propose using:
>
> - Needs initial review -> `<tracker-value>`
> - Waiting for more information -> `<tracker-value>`
> - Fully specified and ready for the agent queue -> `<tracker-value>`
> - Requires human implementation or judgment -> `<tracker-value>`
> - Will not be actioned -> `<tracker-value>`
>
> Is this mapping correct?
>
> - Use the proposed mapping (Recommended)
> - Change the mapping

Map those rows internally to `needs-triage`, `needs-info`, `ready-for-agent`,
`ready-for-human`, and `wontfix`. If the user chooses to change the mapping,
ask only for the incorrect row or rows. Canonical local values and an
unmodified GitHub default require no question.

## Questions Setup Must Not Ask

Do not ask:

- whether root `CONTEXT.md` should be created during authorized setup;
- how deeply to seed root context;
- whether repository evidence is sufficient;
- whether setup should create any Idea issue or file;
- which execution context, write mode, or capture outcome to use;
- whether to choose a context-creation mode; or
- which abstract domain-layout classification the user prefers after project
  structure is already resolved.

When domain evidence is sparse, create the required minimal root `CONTEXT.md`
and record explicit unknowns instead of converting missing evidence into a
configuration question.
