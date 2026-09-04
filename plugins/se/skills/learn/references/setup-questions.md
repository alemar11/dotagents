<!-- SE-owned reference derived from the durable repository-context contract. -->

# Setup Questions

Use this reference only when repository evidence plus the defaults
in [setup-workflow.md](setup-workflow.md) cannot resolve a materially ambiguous
setup target or behavior-affecting value.

Normally ask no questions. When a question is required:

- ask one question at a time;
- identify the concrete evidence that conflicts or is incomplete;
- use actual project names, repository names, and paths;
- ask about the user's project rather than Project Context's internal model;
- offer only relevant choices and mark the evidence-backed recommendation;
- translate the answer to canonical configuration internally; and
- ask a follow-up only for a selected custom or split choice that remains
  unresolved.

Do not expose terms such as `context-owning scope`, `scoped route`, or
`translation memory` in the
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
include. The selected Git repositories become the setup scope internally; run
setup independently in each selected repository.

When the project root is clear but the requested area is not, ask:

> Do you want me to review and update the complete Project Context setup, or
> only a specific area?
>
> - Complete setup (Recommended)
> - A specific area

If the user selects a specific area, ask which one: project context,
localization conventions, agent pointers, or Code Review Rules.
Translate the answer to the corresponding `memory_slice` internally.

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
> - Each should have its own local context tree
> - Only one of them needs its own context

If only one needs its own context, ask which named project. If separate
ownership is selected but its path boundary remains unclear, ask:

> Which folders belong to `<project-name>`?

The skill decides whether the available evidence supports first-class
subproject ownership. During explicit monorepo setup, each selected first-class
subproject receives a minimal local `AGENTS.md` and `CONTEXT.md`; local
`project-context/` and `TRANSLATION.md` are created only when supported content
exists. Never ask the user to judge evidence sufficiency. Root `CONTEXT.md`
creation remains mandatory for every Git root selected by authorized setup.

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

## Repository Rule Ownership

Ask only when a composed cross-repository update cannot establish which
selected Git repository should own a durable rule.

> I found this rule: `<rule-summary>`. Where does it apply?
>
> - Only to `<repository-name>` (Recommended)
> - To every selected repository

Place the rule in the named repository unless the answer or evidence proves it
must be represented in every selected repository.

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

## Questions Setup Must Not Ask

Do not ask:

- whether root `CONTEXT.md` should be created during authorized setup;
- how deeply to seed root context;
- whether repository evidence is sufficient;
- whether setup should create any feature artifact or file;
- which execution context or capture outcome to use;
- whether to choose a context-creation mode; or
- which abstract repository-shape classification the user prefers.

When domain evidence is sparse, create the required minimal root `CONTEXT.md`
and record explicit unknowns instead of converting missing evidence into a
configuration question.
