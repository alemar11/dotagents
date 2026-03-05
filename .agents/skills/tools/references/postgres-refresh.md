# Postgres Refresh Playbook

Use this playbook when asked to refresh Postgres best-practices references.

## Routing Rule
- Keep Postgres regeneration mechanics outside the runtime `postgres` skill.
- Use `references/postgres-best-practices-runbook.md` as the canonical refresh procedure.

## Execution Flow (Mandatory Order)
1. `syntax-check`: run `bash -n` on both scripts.
2. `snapshot`: run `./.agents/skills/tools/scripts/postgres_best_practices_snapshot.sh <limit>`.
3. `review`: apply the meaningful-change gate to each category file.
4. `optional-edits`: update only files with semantic improvements.
5. `cleanup`: run `./.agents/skills/tools/scripts/postgres_best_practices_cleanup.sh`.
6. `final-report`: use the release checklist report schema and mark `PASS (NOOP)` if no persistent edits were required.

## Guardrails
- Do not introduce regeneration internals into `postgres/SKILL.md`.
- Keep recommendations generic to PostgreSQL and prefer official docs validation.
- Preserve existing `DB_*` user-facing environment contract.

## Deliverable
Report:
- Which runbook steps were executed
- Which `postgres/references/postgres_best_practices/*.md` files changed
- Why each change passed the meaningful-change gate
