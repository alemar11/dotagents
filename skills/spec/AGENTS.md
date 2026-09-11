# Specification Maintenance

`references/specification.md` owns content and task identity;
`references/states.md` owns transient operations and results. Templates project
these contracts. Keep criteria, paired verification checks, prerequisites, and
accepted decisions aligned without adding execution progress or PR topology.

For hosted-content changes, run the repository's
`projects/spec/scripts/validate-hosted-content-safety` and inspect the exact
publication projection. Keep GitHub transport in the `github-issues` skill.
