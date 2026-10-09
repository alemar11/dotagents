---
name: maintainer
description: Audit or maintain this repository's skills, plugins, and coupled tools when explicitly invoked.
---

# Maintainer

Use only when the user explicitly invokes `$maintainer`, asks to run Maintainer,
or an explicitly invoked parent workflow routes here. Do not auto-select it for
ordinary repository changes.

Open [maintenance-router.md](references/maintenance-router.md) to select the
requested scope and playbook. Load only references needed for that operation.
Review-only requests stay read-only; an explicit request to fix findings or
refactor authorizes that scoped work without another approval checkpoint.

A bare `run` starts conservative repository maintenance: apply only concrete,
low-ambiguity improvements to existing packages. Report strategic or
behavior-sensitive candidates. Domain refresh, workflow hardening, package
renames/moves/removals, and new package creation require their matching explicit request.
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
