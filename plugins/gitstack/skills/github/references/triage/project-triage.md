# GitHub project triage

Use `../../../github-triage/references/project-triage.md` as the authoritative
runbook for current-repo maintainer issue and PR queue triage.

The umbrella `github` skill should route focused maintainer triage requests to
the bundled `github-triage` skill, keep ordinary reads on direct `gh`, and use
`github-ci` or `<resolved-ghflow> ci inspect` only when failing PR checks need
deeper log extraction.
