# Swift-DocC Skill Maintenance

`skills/swift-docc/` owns the runtime documentation workflow; maintainer refresh mechanics remain repository maintenance.

## Package contract

- Keep Swift-DocC bundled-asset refresh and reference integrity checks in `.agents/skills/maintainer`, and use `.agents/skills/maintainer/references/swift-docc-runbook.md` as the canonical procedure.
- Keep runtime Swift-DocC docs and fast-path reference design in `skills/swift-docc/`; keep maintainer-only refresh routing here. (Codex learning)
