# Skill Health Playbook

Use this playbook for read-only skill or repository health audits and as the
health-evidence pass inside a generic maintenance run. It is the canonical owner
for structural, discovery, instruction, reference-path, and validation health.

## Scope And Mutation Boundary

- A direct `audit` request is read-only: report findings without editing,
  staging, committing, or publishing.
- When `run-maintenance.md` calls this playbook, return evidence first. The
  maintenance workflow may apply only safe, low-ambiguity findings and must
  defer strategic or behavior-sensitive changes.
- Named packages stay targeted. An unnamed health request covers local reusable
  skills, repo-local plugins, and project-local skills in this repository.

## Health Workflow

1. Resolve the package scope and inspect current repo status without requiring a
   globally clean worktree.
2. Check structural and policy integrity:
   - stable package names and required `SKILL.md` files;
   - expected `agents/openai.yaml`, plugin manifests, and marketplace entries;
   - lowercase `references/*.md` filenames except `README.md` and `AGENTS.md`;
   - existing scripts and references for every active pointer;
   - aligned repo guidance, Codex-dependency classification, and portable
     fallbacks.
3. Run the cheap portfolio signal for the selected roots:

   ```bash
   skills/skill-audit/scripts/portfolio-health --json scan \
     --no-live --no-logs --root <skill-or-skill-root>
   ```

4. Interpret size without turning it into a correctness gate:

   | Band | Entrypoint signal |
   | --- | --- |
   | `normal` | At most 2,500 estimated tokens and fewer than 500 lines. |
   | `review` | 2,501-4,000 estimated tokens. |
   | `high-density` | 4,001-5,000 estimated tokens. |
   | `over-guideline` | More than 5,000 estimated tokens or at least 500 lines. |

   The helper estimates tokens as `ceil(SKILL.md UTF-8 bytes / 4)`. Size alone
   is diagnostic and never produces `result=fail`.
5. Separate the three costs:
   - `catalog_cost`: always-visible name, description, and discovery path;
   - `entrypoint_cost`: the activated `SKILL.md`;
   - `invoked_path_cost`: that entrypoint plus references required by one
     representative branch.

   Do not sum the entire package. Count a disclosed reference when the selected
   branch must load it, even if the text moved out of `SKILL.md`.
6. Invoke `$skill-audit` read-only when any of these signals is present:
   - the entrypoint band is not `normal`;
   - description or duplicate candidates appear;
   - weak pointers, instruction sprawl, ownership overlap, or writing-quality
     problems are suspected;
   - the user asks about prompt cost, trigger quality, overlap, or runtime
     behavior;
   - a behavior claim requires representative session evidence.
7. Select applicable non-mutating proof from `validation-matrix.md`. Validate
   package shape, contracts, scripts, and composed behavior in proportion to the
   audited scope.

## Suggested Structural Commands

```bash
rg --files -g 'SKILL.md' -g 'agents/openai.yaml'
rg --files -g 'references/*.md'
rg -n "scripts/|agents/openai.yaml|SKILL.md|\.agents/skills/" -S
rg -n "request_user_input|subagent|\$CODEX_HOME|~/.codex|Codex CLI|Codex App" -S
```

Use focused package roots and exclude generated caches or installed plugin cache
copies from editable-owner findings.

## Severity And Output

- `result=fail` only for missing required files, broken active pointers, unsafe
  or behavior-breaking policy contradictions, or failed required validation.
- `WARN` for non-blocking drift, diagnostic size signals, weak routing,
  maintainability findings, or deferred behavior-sensitive work.
- `result=pass` when no blocking issue remains. Non-blocking warnings stay in
  findings and do not change the result by themselves.

Add these health details to the common report in `release-checklist.md`:

- packages and roots inspected;
- structural and policy proof;
- portfolio command and entrypoint bands;
- representative invoked paths when reviewed;
- whether `$skill-audit` ran and what evidence status it returned;
- blocking findings, warnings, and deferred maintenance.
