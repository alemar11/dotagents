---
name: maintainer
description: Run complete routine maintenance of this repository's skills, plugins, and coupled tools when explicitly invoked; arguments narrow the scope or select read-only audits.
---

# Maintainer

Use only when the user explicitly invokes `$maintainer`, asks to run Maintainer,
or an explicitly invoked parent workflow routes here. Do not auto-select it for
ordinary repository changes.

Open [maintenance-router.md](references/maintenance-router.md) to select the
requested scope and playbook. Load only references needed for that operation.
Review-only requests stay read-only; an explicit request to fix findings or
refactor authorizes that scoped work without another approval checkpoint.

A bare `$maintainer`, `run`, or request to run Maintainer starts all applicable
routine maintenance through [run-maintenance.md](references/run-maintenance.md),
including managed source refreshes and concrete repairs. Do not ask the user to
choose tasks or repeat that authority. Arguments narrow this default: a package
name limits the inventory; `audit`, review, or dry-run makes the work read-only.
Capability questions and requests to edit this skill do not start maintenance.

Propose structural decisions such as renaming, merging, removing, or creating
packages, redistributing responsibilities, or introducing new tools. Apply them
only when specifically authorized. Preserve established behavior and invocation
policy when making routine repairs; report unresolved behavioral decisions.
Preserve unrelated work. Commit, push, PR, and publication authority are separate
from maintenance authority.

## Dependencies

This project-local skill uses repository files, shell, and Git. Substantial skill
or plugin reshapes start with `$skill-creator` or `$plugin-creator`, then return
for integration. Its non-trivial implementation closeout requires native
`codex review`. Use local checks and supplied
runtime evidence for health or workflow claims; report unavailable required
capabilities rather than substituting an unsupported outcome.

## Completion

[release-checklist.md](references/release-checklist.md) owns common validation
and closeout. Run it once for the selected work, reusing branch evidence. Report
canonical `result` and `change_state` values from
[states.md](references/states.md). A verified no-op is `result=pass` and
`change_state=no-change`.
