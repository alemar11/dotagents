# Swift API Design Skill Maintenance

`skills/swift-api-design/` owns the runtime API-design guidance and bundled source usage.

## Package contract

- Keep Swift API Design bundled-asset refresh and reference integrity checks in `.agents/skills/maintainer`, and use `.agents/skills/maintainer/references/swift-api-design-runbook.md` as the canonical procedure.
- Keep runtime Swift API Design docs and bundled-source usage details in `skills/swift-api-design/`; keep maintainer-only refresh routing here.
- Refresh `swift-api-design` from `swiftlang/swift-org-website/documentation/api-design-guidelines/index.md` until the live Swift.org page demonstrably migrates to a different substantive source. (Codex learning)
