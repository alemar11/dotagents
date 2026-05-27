# GitStack Measurement

Use this note when evaluating whether GitStack is helping in real sessions.
Run `plugin-eval analyze` before and after changes, then compare that static
report with session evidence from representative workflows.

## Scenarios

- Commit-only: user asks for a scoped commit or commit-and-push with no PR.
- PR publish: user asks to publish local work as a pushed branch and draft PR.
- Actions triage: user asks to inspect, rerun, or monitor failing GitHub checks.
- Release verification: user asks whether a tag is available through GitHub
  Releases, PyPI, Homebrew, npm, or another distribution surface.

## Evidence Commands

```bash
node /Users/alessandro/.codex/plugins/cache/openai-curated/plugin-eval/603a6e80/scripts/plugin-eval.js analyze /Users/alessandro/Developer/dotagents/plugins/gitstack --format markdown
/Users/alessandro/Developer/dotagents/skills/skill-audit/scripts/session-evidence --target gitstack --target github-ci --target github-releases --target yeet --root /Users/alessandro/.codex/sessions --since 2026-05-27 --include-zero
```

## Success Signals

- The right bundled skill owns each workflow without loading unrelated
  GitStack skills.
- Routine work stays on direct `git` and `gh`; `ghflow` is used only where its
  shared behavior is justified.
- Release checks distinguish GitHub tags/releases from package-registry and
  Homebrew availability.
- Plugin-eval trigger warnings decrease, and remaining budget warnings are
  backed by measured session behavior rather than static estimates alone.
